#!/bin/bash
set -e

# Wait for OpenSearch to be up
until curl -s http://localhost:9200/_cluster/health | grep -q '"status":"green"\|"status":"yellow"'; do
  echo "Waiting for OpenSearch..."
  sleep 2
done

# Create the 'movie' index with a mapping that includes a .keyword field for title
curl -X PUT "localhost:9200/movie" -H 'Content-Type: application/json' -d'
{
  "mappings": {
    "properties": {
      "id": { "type": "integer" },
      "imdb_id": { "type": "keyword" },
      "title": {
        "type": "text",
        "fields": {
          "keyword": { "type": "keyword" }
        }
      },
      "title_normalized": { "type": "text" },
      "release_year": { "type": "integer" },
      "genre": { "type": "keyword" },
      "director": { "type": "keyword" },
      "additional_data": { "type": "object", "enabled": true }
    }
  }
}
' || true

# Ensure final newline for bulk file
echo >> /usr/local/bin/movies.json

# Bulk load the mock data
curl -X POST "localhost:9200/_bulk" -H "Content-Type: application/json" --data-binary @/usr/local/bin/movies.json

echo "OpenSearch initialized with mock movie data."
