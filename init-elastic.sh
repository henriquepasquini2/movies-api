#!/bin/bash
set -e

# Wait for Elasticsearch to be up
until curl -s http://localhost:8200/_cluster/health | grep -q '"status":"green"\|"status":"yellow"'; do
  echo "Waiting for Elasticsearch..."
  sleep 2
done

# Create the 'movie' index with a basic mapping
curl -X PUT "localhost:8200/movie" -H 'Content-Type: application/json' -d'
{
  "mappings": {
    "properties": {
      "id": { "type": "integer" },
      "imdb_id": { "type": "keyword" },
      "title": { "type": "text" },
      "title_normalized": { "type": "text" },
      "release_year": { "type": "integer" },
      "genre": { "type": "keyword" },
      "director": { "type": "keyword" },
      "additional_data": { "type": "object", "enabled": true }
    }
  }
}
' || true

# Bulk load the mock data
curl -X POST "localhost:8200/_bulk" -H "Content-Type: application/json" --data-binary @/usr/local/bin/movies.json

echo "Elasticsearch initialized with mock movie data." 