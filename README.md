This API is responsible for providing movie data.

## Instructions

### 1. Install Python

### 2. Install poetry:

```bash
pip install poetry
```

### 3. Install dependencies:
```bash
make install
```

### 4. Create a `settings.ini` file in the project root.
### 5. Copy the contents of the `.env.template` file to the `.env` file
### 6. Fill in the settings in the `.env` file as needed
#### Example `.env`:
```
IS_LOCAL=True
LOG_LEVEL=DEBUG
STACKDRIVER_LOGGER=False
REDIS_URL=redis://localhost:6279
ES_MOVIES_URL=http://localhost:8200
```

---

## Running with Docker Compose (Recommended for Local Development)

This project now uses **OpenSearch** (compatible with Elasticsearch) and Redis for local testing.

### Steps:

1. Make sure you have Docker and Docker Compose installed.
2. In the project root, run:
   ```bash
   chmod +x init-opensearch.sh
   docker-compose up
   ```
3. This will start:
   - Redis at `localhost:6279`
   - OpenSearch at `localhost:8200` with the `movie` index and sample data
4. Start the API (in another terminal):
   ```bash
   make run
   ```

Your API will be able to connect to the local Redis and OpenSearch instances with mock data for testing.

---

## Running Tests

This project uses `pytest` and `pytest-asyncio` for async and regular unit tests.

To run all tests:
```bash
pytest tests
```
Or, if using Makefile:
```bash
make test
```

**Note:** Async tests require `pytest-asyncio`, which is included as a dev dependency.

---

**Note:**
- The search service is OpenSearch (`opensearchproject/opensearch:2.14.0`), but the URL and API remain compatible with Elasticsearch for basic operations.
- The initialization script is `init-opensearch.sh`.
- The OpenSearch data volume is `osdata`.




