# LCP Manufacturing Investigation Agent

An AI-powered manufacturing investigation assistant for leadless cardiac pacemaker assembly records. The agent combines tool calling, Azure AI Search retrieval-augmented generation (RAG), and multi-turn conversations to investigate device history, assembly status, quality events, scrap records, and controlled holds.

## Features

- **AI agent and tool calling:** Selects relevant backend tools to retrieve manufacturing records and investigate device-specific questions.
- **Manufacturing data retrieval:** Queries device records, process history, assembly status, controlled holds, quality events, and scrap records stored in Azure Cosmos DB.
- **Retrieval-augmented generation (RAG):** Searches documented manufacturing procedures using Azure AI Search keyword and vector search.
- **Evidence-grounded responses:** Uses retrieved records and procedure content to support investigation findings rather than inventing manufacturing facts.
- **Multi-turn conversations:** Maintains conversation continuity using response IDs.
- **Streaming chat interface:** Streams investigation findings to a Next.js and React frontend with dynamic status updates.

## Architecture

- **Frontend:** Next.js, React, TypeScript
- **Backend:** Python, FastAPI
- **LLM and agent orchestration:** Azure OpenAI Responses API
- **Manufacturing data:** Azure Cosmos DB
- **Procedure retrieval:** Azure AI Search
- **Communication:** HTTP API and server-sent events (SSE)

## Project Structure

lcp-agent/
├── agent.py
├── api.py
├── requirements.txt
├── .env.example
├── .gitignore
├── data/
│   ├── assembly_status.json
│   ├── devices.json
│   ├── holds.json
│   ├── process_events.json
│   ├── quality_events.json
│   └── scrap_events.json
├── procedures/
│   ├── contamination_protocol.md
│   ├── controlled_hold.md
│   └── scrap_policy.md
├── tools/
│   ├── __init__.py
│   ├── database.py
│   ├── manufacturing.py
│   ├── procedures.py
│   └── quality.py
└── web/
    ├── app/
    │   └── api/
    │       └── investigate/
    │           └── route.ts
    ├── public/
    ├── package.json
    └── package-lock.json



## Prerequisites

- Python 3.11 or a compatible Python version
- Node.js and npm
- Azure OpenAI access with a configured model deployment
- An Azure Cosmos DB database containing the expected synthetic manufacturing collections
- An Azure AI Search service with a configured index and vector search support

## Configuration

Create a `.env` file or configure the following environment variables in your shell. Never commit real credentials.

| Variable | Purpose |
|---|---|
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI API endpoint |
| `AZURE_OPENAI_DEPLOYMENT` | Model deployment name |
| `AZURE_OPENAI_API_KEY` | Azure OpenAI API key |
| `COSMOS_ENDPOINT` | Azure Cosmos DB endpoint |
| `COSMOS_KEY` | Azure Cosmos DB key |
| `AZURE_SEARCH_ENDPOINT` | Azure AI Search endpoint |
| `AZURE_SEARCH_INDEX` | Search index name |
| `AZURE_SEARCH_KEY` | Azure AI Search API key |

The Cosmos DB database is configured as `lcp-manufacturing`. Its containers include devices, process events, quality events, scrap events, holds, and assembly status.

The Azure AI Search index is expected to contain the `title`, `chunk`, and `text_vector` fields used by the procedure search implementation.

## Running Locally

### 1. Set up the Python backend

From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Configure the required Azure environment variables in your shell, then start the API:

```powershell
python -m uvicorn api:app --reload
```

The FastAPI backend will be available at `http://127.0.0.1:8000`.

### 2. Set up the frontend

Open a second terminal:

```powershell
cd web
npm install
npm run dev
```

Open the local URL printed by Next.js, typically `http://localhost:3000`.

The frontend API route forwards investigation requests to the local FastAPI backend.

## Example Investigations

Example questions for the synthetic dataset include:

- What happened during the manufacturing process for device LCP-10482?
- Why was LCP-10482 scrapped?
- What is the current status of LCP-10501, and what hold information is available?
- What is the next assembly step for LCP-10517?
- Which documented procedure applies to a potential contamination event?

Results depend on the records and procedure documents available in the configured Azure resources.

## Scope and Safety

This is a portfolio demonstration using synthetic manufacturing data. It is not a validated medical device manufacturing system and must not be used to make real production, quality disposition, or patient-care decisions. The agent is designed to report evidence from available records and documented procedures, not to perform unsupported actions such as releasing holds or changing manufacturing records.

## Future Improvements

Potential extensions include automated evaluation of investigation quality, additional observability, stronger deployment configuration, and broader test coverage.
