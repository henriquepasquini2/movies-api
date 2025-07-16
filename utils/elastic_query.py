from typing import List, Union

from schemas.requests.movies import SearchMoviesRequest

PREPOSITIONS = [
    "a",
    "de",
    "em",
    "ao",
    "aos",
    "na",
    "nas",
    "no",
    "nos",
    "da",
    "das",
    "do",
    "dos",
]

def _get_variacoes_nomes_split(nome: str) -> List[str]:
    variacoes = []
    s_name_list = nome.split()
    variacoes.extend(s_name_list)
    return variacoes


def build_term_or_terms_query(field: str, values: list) -> dict:
    if len(values) == 1:
        return {"term": {field: values[0]}}
    else:
        return {"terms": {field: values}}


def build_span_near_query(field: str, values: List[str], fuzziness: str, slop: int):
    """Gerador de query para busca por span_multi.
    Args:
        field (str): Campo do mapping do ES
        values (List[str]): Nome a ser buscado
        fuzziness (str): Valor fuzzy do ES
        slop (int): Número de variações entre os nomes
    Returns:
        dict: Query de busca ES
    """
    queries_should_list = []
    for nome in values:
        for s_value_list in _get_variacoes_nomes_split(nome):
            clauses = []
            extra_slop = 0
            if len(s_value_list) < 2:
                fuzziness = "AUTO:8,13"
            for s_value in s_value_list:
                if s_value in PREPOSITIONS:
                    extra_slop += 1
                    continue

                clauses.append(
                    {
                        "span_multi": {
                            "match": {
                                "fuzzy": {
                                    field: {
                                        "fuzziness": fuzziness,
                                        "value": s_value.lower(),
                                    }
                                }
                            }
                        }
                    }
                )

            if clauses:
                query = {
                    "span_near": {
                        "clauses": clauses,
                        "in_order": "true",
                        "slop": f"{slop + extra_slop}",
                    }
                }

                queries_should_list.append(query)
    if len(queries_should_list) == 1:
        query = queries_should_list[0]
    else:
        query = {"bool": {"should": queries_should_list}}
    return query


def build_match_query(
    field: Union[str, List[str]], values: List[str], fuzziness: str = "AUTO:6,13"
):
    """Gerador de query para busca por match.
    Args:
        field (str or List[str]): Campo do mapping do ES. Se for uma lista,
            será feita uma busca em todos os campos por multi_match.
        values (List[str]): Nome a ser buscado
        fuzziness (str): Valor fuzzy do ES
    Returns:
        dict: Query de busca ES
    """
    queries_should_list = []

    for value in values:
        if isinstance(field, list):
            query = {
                "multi_match": {
                    "query": value,
                    "fields": field,
                    "fuzziness": fuzziness,
                    "fuzzy_transpositions": "false",
                    "minimum_should_match": "3<75%",
                    "operator": "and",
                }
            }
        else:
            query = {
                "match": {
                    field: {
                        "query": value,
                        "fuzziness": fuzziness,
                        "fuzzy_transpositions": "false",
                        "minimum_should_match": "3<75%",
                        "operator": "and",
                    }
                }
            }

        queries_should_list.append(query)
    if len(queries_should_list) == 1:
        query = queries_should_list[0]
    else:
        query = {"bool": {"minimum_should_match": 1, "should": queries_should_list}}
    return query


def build_query_movie(query: SearchMoviesRequest):
    """Builds a bool query with movie title fields for the movie index.
    Args:
        query (class): SearchMoviesRequest model.
    Returns:
        dict: Elasticsearch query for searching movies in the movie index.
    """
    queries_should_list = []
    queries_must_not_list = []
    if query.titles:
        movie_titles = sorted(set(query.titles))
        if query.exact_match:
            query_titles = build_term_or_terms_query(
                field="title_normalized.keyword", values=movie_titles
            )
        elif query.keep_order_span:
            query_titles = build_span_near_query(
                field="title_normalized",
                values=movie_titles,
                fuzziness=query.fuzziness,
                slop=query.slop,
            )
        else:
            query_titles = build_match_query(
                field="title_normalized",
                values=movie_titles,
                fuzziness=query.fuzziness,
            )
        queries_should_list.append(query_titles)
    if query.n_titles:
        n_movie_titles = sorted(set(query.n_titles))
        if query.n_titles_exact_match:
            query_titles = build_term_or_terms_query(
                field="title_normalized.keyword", values=n_movie_titles
            )
        elif query.n_titles_keep_order_span:
            query_titles = build_span_near_query(
                field="title_normalized",
                values=n_movie_titles,
                fuzziness=query.n_titles_fuzziness,
                slop=query.n_titles_slop,
            )
        else:
            query_titles = build_match_query(
                field="title_normalized",
                values=n_movie_titles,
                fuzziness=query.n_titles_fuzziness,
            )
        queries_must_not_list.append(query_titles)
    query_dict = {"bool": {}}
    if queries_should_list:
        query_dict["bool"]["should"] = queries_should_list
    if queries_must_not_list:
        query_dict["bool"]["must_not"] = queries_must_not_list
    return query_dict
