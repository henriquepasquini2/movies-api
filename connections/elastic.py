from typing import List, Union

from opensearchpy import AsyncOpenSearch
from opensearchpy.helpers import async_scan
from fastapi import HTTPException
from pydantic import ValidationError

from config import settings
from models.elastic import ElasticsearchResponse, ESBaseRequest, ESSearchRequest
from utils.logger import Logger
from utils.singleton import Singleton


class Elasticsearch(metaclass=Singleton):

    def __init__(self):
        self.logger = Logger()
        self.client = None

    async def initialize(self):
        """
        Initialize the OpenSearch client.
        """
        self.client = AsyncOpenSearch([settings.ES_WITCHER_URL], maxsize=25)
        self.logger.info("OpenSearch client initialized successfully.")

    async def close(self):
        """
        Close the OpenSearch client.
        """
        await self.client.close()

    async def search_async_scan(self, request: ESBaseRequest) -> ElasticsearchResponse:
        """
        Execute a search query on OpenSearch using async_scan.
        """
        try:
            hits = []
            async for hit in async_scan(
                client=self.client,
                index=request.index,  # Pass index as a parameter
                query=request.body,   # Pass only the query/body
                scroll=request.scroll,
                size=request.size,
            ):
                hits.append(hit)

            return ElasticsearchResponse(
                hits=hits,
                total=len(hits),
            )

        except ValidationError as e:
            self.logger.error(f"Error validating search request: {e}")
            raise HTTPException(status_code=400, detail="Invalid search request")
        except Exception as e:
            self.logger.error(f"Error executing search query: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")

    async def search(self, request: ESSearchRequest) -> ElasticsearchResponse:
        """
        Execute a search query on Elasticsearch.
        """
        try:
            response = await self.client.search(**request.model_dump())
            scroll_id = response["_scroll_id"]
            while True:
                scroll_response = await self.client.scroll(
                    scroll_id=scroll_id, scroll="1m"
                )
                if not scroll_response["hits"]["hits"]:
                    break

                return ElasticsearchResponse(
                    hits=scroll_response["hits"]["hits"],
                    total=scroll_response["hits"]["total"]["value"],
                )

            return ElasticsearchResponse(
                hits=response["hits"]["hits"], total=response["hits"]["total"]["value"]
            )
        except ValidationError as e:
            self.logger.error(f"Error validating search request: {e}")
            raise HTTPException(status_code=400, detail="Invalid search request")
        except Exception as e:
            self.logger.error(f"Error executing search query: {e}")
            raise

    @staticmethod
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

    def scan_with_aggs(self, index, query, aggs):
        """Faz um scan com agregações

        Args:
            index (str): nome do index
            query (dict): corpo da query
            aggs (dict): corpo da agregação

        Returns:
            first: resultado da agregação
            second: resultado da query
        """
        result = self.client.search(
            index=index, query=query, aggregations=aggs, scroll="1m", source=False
        )
        yield result["aggregations"]
        yield result["hits"]["hits"]
        scroll_id = result["_scroll_id"]
        while True:
            result = self.client.scroll(scroll_id=scroll_id, scroll="1m")
            if not result["hits"]["hits"]:
                break
            yield result["hits"]["hits"]
