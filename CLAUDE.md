# CLAUDE.md - AI Assistant Guide for Legal Document Assistant

This document provides comprehensive guidance for AI assistants working with the Legal Document Assistant codebase. It covers architecture, conventions, workflows, and best practices.

## Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture & Technology Stack](#architecture--technology-stack)
3. [Directory Structure](#directory-structure)
4. [Key Components](#key-components)
5. [Development Workflows](#development-workflows)
6. [Database Schema](#database-schema)
7. [Code Conventions](#code-conventions)
8. [Testing & Evaluation](#testing--evaluation)
9. [Common Tasks](#common-tasks)
10. [Troubleshooting](#troubleshooting)

---

## Project Overview

**Purpose**: A Retrieval-Augmented Generation (RAG) system that helps legal professionals efficiently search and retrieve information from legal documents, case laws, and statutes.

**Core Functionality**:
- Full-text search across legal documents using Elasticsearch
- Answer generation using Google BERT (fine-tuned on SQuAD)
- Automated daily data ingestion via Apache Airflow
- Real-time performance monitoring with Grafana
- User feedback collection for quality tracking

**Target Users**: Lawyers and legal professionals needing quick access to relevant case laws, precedents, and statutes.

---

## Architecture & Technology Stack

### Core Technologies
- **Python 3.8**: Primary language
- **Streamlit**: Web UI framework (port 8501)
- **Apache Airflow 2.9.3**: Workflow orchestration (port 8080)
- **Elasticsearch 8.4.3**: Search engine (ports 9200, 9300)
- **PostgreSQL 13**: Relational database (port 5432)
- **Docker & Docker Compose**: Containerization

### AI/ML Stack
- **Model**: `google-bert/bert-large-uncased-whole-word-masking-finetuned-squad`
- **API**: Hugging Face Inference API
- **Required**: `HUGGINGFACE_KEY` environment variable

### Supporting Services
- **Grafana**: Monitoring dashboards (port 3000)
- **pgAdmin**: Database admin UI (port 5050)
- **Redis 7.2**: Airflow message broker

### Data Flow Architecture
```
CSV/JSON Files → Airflow ETL → PostgreSQL → Elasticsearch Index
                                     ↓
User Query → Streamlit → Elasticsearch Search → Top 5 Docs
                                     ↓
            Context Assembly → BERT API → Generated Answer
                                     ↓
            Evaluation Metrics → PostgreSQL Storage → Grafana
```

---

## Directory Structure

```
Legal-Document-Assistant-Global/
├── llm-app/                          # Main Streamlit application
│   ├── streamlit/
│   │   ├── app.py                    # ENTRY POINT: Main UI application
│   │   └── src/
│   │       ├── connection.py         # Database connection management
│   │       ├── elasticSearch.py      # Elasticsearch search operations
│   │       ├── llm.py                # BERT integration & data tracking
│   │       ├── evaluation.py         # Hit Rate & MRR calculations
│   │       ├── exportData.py         # Data export utilities
│   │       └── ground_truth/
│   │           ├── allDocument.json
│   │           ├── ground-truth-data.csv
│   │           └── generateGroundTruth.ipynb
│   ├── Dockerfile                    # App container definition
│   ├── requirements.txt              # Python dependencies
│   └── dashboard.json                # Grafana dashboard configuration
│
├── orchestration/                    # Apache Airflow ETL pipeline
│   ├── dags/
│   │   ├── pipeline.py               # ENTRY POINT: Main DAG (Get_All_LLM_Data)
│   │   ├── src/
│   │   │   ├── connection.py         # Database connections
│   │   │   ├── getData.py            # Data retrieval functions
│   │   │   └── insertData.py         # Data insertion & Elasticsearch indexing
│   │   └── dataset/
│   │       ├── qa.jsonl              # 2,124 legal Q&A pairs (Kaggle)
│   │       └── legal_text_classification.csv  # 24,986 legal texts (Kaggle)
│   ├── config/
│   │   └── airflow.cfg               # Airflow configuration
│   ├── dockerfile                    # Airflow container definition
│   └── requirements.txt              # Airflow Python dependencies
│
├── images/                           # Documentation screenshots
├── docker-compose.yaml               # CRITICAL: Multi-container orchestration
├── readme.md                         # User-facing documentation
└── CLAUDE.md                         # This file (AI assistant guide)
```

**Key Files to Know**:
- `docker-compose.yaml`: Service orchestration, environment variables, networking
- `llm-app/streamlit/app.py`: Main UI logic and RAG flow
- `llm-app/streamlit/src/llm.py`: BERT API calls and database tracking
- `orchestration/dags/pipeline.py`: Daily ETL DAG definition
- `orchestration/dags/src/insertData.py`: Data loading and Elasticsearch indexing

---

## Key Components

### 1. Streamlit Application (`llm-app/streamlit/app.py`)

**Location**: `/home/user/Legal-Document-Assistant-Global/llm-app/streamlit/app.py`

**Purpose**: User-facing web interface for querying legal documents

**Key Functions & Flow**:

1. **User Input**: Text input field for legal questions
2. **Search Process** (triggered by "Ask" button):
   ```python
   # Pseudocode flow:
   user_question = st.text_input()
   if st.button("Ask"):
       # 1. Search Elasticsearch for top 5 relevant documents
       search_results = elasticSearch.elasticSearch(user_question)

       # 2. Assemble context from retrieved documents
       context = "\n\n".join([doc['answer'] for doc in search_results])

       # 3. Query BERT with question + context
       bert_response = llm.query({
           "inputs": {
               "question": user_question,
               "context": context
           }
       })

       # 4. Calculate evaluation metrics
       hit_rate = evaluation.hit_rate(search_results, ground_truth)
       mrr = evaluation.mrr(search_results, ground_truth)

       # 5. Store query data and metrics
       llm.captureUserInput(doc_id, question, answer, llm_score,
                           response_time, hit_rate, mrr)

       # 6. Display answer to user
       st.write(bert_response['answer'])
   ```

3. **Feedback Collection**: "Satisfied" button stores user feedback

**Important Session State Variables**:
- `disabled`: Controls button states
- `answer`: Stores BERT response
- `doc_id`: Unique identifier for the query
- `result`: Retrieved context text

**Error Handling**: Catches Elasticsearch startup delays with user-friendly message

### 2. Elasticsearch Module (`llm-app/streamlit/src/elasticSearch.py`)

**Location**: `/home/user/Legal-Document-Assistant-Global/llm-app/streamlit/src/elasticSearch.py`

**Search Strategy**:
```python
def elasticSearch(input_text):
    query = {
        "size": 5,  # Return top 5 results
        "query": {
            "multi_match": {
                "query": input_text,
                "fields": ["question^2", "text"],  # Boost question field 2x
                "type": "best_fields"
            }
        }
    }
    # Returns list of {doc_id, question, answer} dictionaries
```

**Key Details**:
- Index name: `"legal-documents"`
- Connection: `elasticsearch:9200`
- Fields: `question` (boosted 2x), `text`
- Returns maximum 5 documents per query

### 3. LLM Module (`llm-app/streamlit/src/llm.py`)

**Location**: `/home/user/Legal-Document-Assistant-Global/llm-app/streamlit/src/llm.py`

**Core Functions**:

1. **`query(payload)`**: Calls Hugging Face BERT API
   ```python
   API_URL = "https://api-inference.huggingface.co/models/google-bert/..."
   headers = {"Authorization": f"Bearer {HUGGINGFACE_KEY}"}
   # Returns: {"score": float, "start": int, "end": int, "answer": str}
   ```

2. **`captureUserInput(doc_id, user_input, result, llm_score, response_time, hit_rate, mrr)`**
   - Inserts into `evaluation_data` table
   - Records: All query metadata and performance metrics
   - Timestamp: `created_time` (auto-generated)

3. **`captureUserFeedback(doc_id, user_input, result, is_satisfied)`**
   - Inserts into `feedback_data` table
   - Records: User satisfaction boolean
   - Timestamp: `created_time` (auto-generated)

4. **`generate_document_id(text, question)`**
   - Creates MD5 hash of concatenated text + question
   - Returns first 8 characters as unique identifier

**Database Connection**:
- Uses connection from `connection.py`
- PostgreSQL connection pooling
- Database: `airflow`, Host: `postgres:5432`

### 4. Evaluation Module (`llm-app/streamlit/src/evaluation.py`)

**Location**: `/home/user/Legal-Document-Assistant-Global/llm-app/streamlit/src/evaluation.py`

**Metrics**:

1. **Hit Rate**:
   - Formula: `1.0` if correct doc in results, else `0.0`
   - Measures: Whether correct answer was retrieved at all

2. **Mean Reciprocal Rank (MRR)**:
   - Formula: `1 / rank` of first correct document
   - Example: If correct doc is 3rd result, MRR = 1/3 = 0.333
   - Measures: Quality of ranking (higher is better)

**Ground Truth**:
- Located: `/llm-app/streamlit/src/ground_truth/ground-truth-data.csv`
- Used for: Validation and metric calculation

### 5. Airflow DAG (`orchestration/dags/pipeline.py`)

**Location**: `/home/user/Legal-Document-Assistant-Global/orchestration/dags/pipeline.py`

**DAG Configuration**:
```python
DAG_NAME = "Get_All_LLM_Data"
SCHEDULE = "0 0 * * *"  # Daily at midnight
START_DATE = datetime(2024, 11, 1)
CATCHUP = False
```

**Task Sequence** (sequential execution):
```
createTable → insertJson → insertCsv → ingestData
```

**Task Details**:

1. **`createTable`**:
   - Function: `insertData.createTable()`
   - Creates/truncates `legal_document` table
   - Schema: `(id, doc_id, question, answer)`

2. **`insertJson`**:
   - Function: `insertData.insertJsonData()`
   - Source: `/opt/airflow/orchestration/dags/dataset/qa.jsonl`
   - Loads: First 25 records (of 2,124 total)
   - Format: JSONL with `{question, answer}` pairs

3. **`insertCsv`**:
   - Function: `insertData.insertCsvData()`
   - Source: `/opt/airflow/orchestration/dags/dataset/legal_text_classification.csv`
   - Loads: First 25 records (of 24,986 total)
   - Format: CSV with `case_title, case_text` columns

4. **`ingestData`**:
   - Function: `insertData.createIndex()`
   - Deletes existing Elasticsearch index
   - Creates new index with mappings
   - Indexes all documents from PostgreSQL

**Important Notes**:
- Currently limited to 25 records per source (performance constraint)
- Full rebuild daily (no incremental indexing)
- Manual trigger required on first run

### 6. Data Insertion Module (`orchestration/dags/src/insertData.py`)

**Location**: `/home/user/Legal-Document-Assistant-Global/orchestration/dags/src/insertData.py`

**Critical Functions**:

1. **`createIndex()`**: Elasticsearch index creation
   ```python
   index_settings = {
       "settings": {
           "number_of_shards": 1,
           "number_of_replicas": 0
       },
       "mappings": {
           "properties": {
               "question": {"type": "text"},
               "text": {"type": "text"}
           }
       }
   }
   # Steps:
   # 1. Delete existing index if present
   # 2. Create new index with settings
   # 3. Bulk index all docs from PostgreSQL
   ```

2. **`insertJsonData()`**: JSONL file processing
   - Uses `orjsonl` library for parsing
   - Bulk insert to PostgreSQL
   - Limit: First 25 records

3. **`insertCsvData()`**: CSV file processing
   - Uses `pandas` for reading
   - Maps: `case_title` → `question`, `case_text` → `answer`
   - Bulk insert to PostgreSQL
   - Limit: First 25 records

**Connection Management**:
- PostgreSQL: Via `connection.createConnection()`
- Elasticsearch: Via `connection.createConnectionES()`

---

## Development Workflows

### Initial Setup

**Prerequisites**:
1. Docker & Docker Compose installed
2. Hugging Face account with API token
3. Minimum 8GB RAM recommended

**Setup Steps**:
```bash
# 1. Clone repository
cd /home/user/Legal-Document-Assistant-Global

# 2. Configure Hugging Face API key
# Edit docker-compose.yaml:
# Under 'app' service, add:
#   environment:
#     - HUGGINGFACE_KEY=<YOUR_API_KEY>

# 3. Build and start all containers
docker-compose up --build -d

# 4. Wait for containers to initialize (2-3 minutes)
docker-compose ps  # Check status

# 5. Access Airflow and trigger initial data load
# Open: http://localhost:8080
# Login: airflow / airflow
# Enable and trigger DAG: Get_All_LLM_Data

# 6. Wait for Elasticsearch indexing to complete
# Check Airflow UI for task completion

# 7. Access application
# Open: http://localhost:8501
```

**Access Points**:
- **Streamlit App**: http://localhost:8501
- **Airflow UI**: http://localhost:8080 (airflow/airflow)
- **Grafana**: http://localhost:3000 (admin/admin)
- **pgAdmin**: http://localhost:5050 (llm@example.com/123456)
- **Elasticsearch**: http://localhost:9200

### Making Code Changes

**For Streamlit App Changes**:
```bash
# 1. Edit files in llm-app/streamlit/
# Files are volume-mounted, so changes reflect immediately

# 2. Restart container to pick up changes
docker-compose restart app

# 3. Check logs for errors
docker-compose logs -f app
```

**For Airflow DAG Changes**:
```bash
# 1. Edit files in orchestration/dags/
# Files are volume-mounted

# 2. Wait for Airflow to detect changes (30-60 seconds)
# OR manually trigger DAG refresh in Airflow UI

# 3. Test changes by triggering DAG manually
```

**For Dependency Changes**:
```bash
# If requirements.txt changed:
docker-compose build app  # or airflow-worker, etc.
docker-compose up -d

# Note: Requires full rebuild
```

### Git Workflow

**Current Branch**: `claude/claude-md-micd4kgklv5x7f40-017h45Tw4QmRFxKrcyoiG6tx`

**Standard Workflow**:
```bash
# 1. Make changes
# Edit files as needed

# 2. Check status
git status
git diff

# 3. Stage changes
git add <files>

# 4. Commit with descriptive message
git commit -m "Description of changes"

# 5. Push to remote
git push -u origin claude/claude-md-micd4kgklv5x7f40-017h45Tw4QmRFxKrcyoiG6tx

# Retry logic if network fails:
# - Retry up to 4 times with exponential backoff (2s, 4s, 8s, 16s)
```

**Important Git Rules**:
- Always develop on designated feature branch
- Never push to main/master without permission
- Branch naming: Must start with `claude/` and end with session ID
- Use clear, descriptive commit messages
- Never commit secrets or API keys

### Adding New Features

**Before Starting**:
1. Read relevant existing code first
2. Understand data flow and dependencies
3. Check database schema if adding new data fields
4. Consider impact on evaluation metrics

**Feature Addition Pattern**:
```python
# Example: Adding a new search field to Elasticsearch

# 1. Update database schema (orchestration/dags/src/insertData.py)
def createTable():
    cursor.execute("""
        CREATE TABLE legal_document (
            id SERIAL PRIMARY KEY,
            doc_id VARCHAR(10),
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            new_field TEXT  -- Add new field
        );
    """)

# 2. Update Elasticsearch mapping (same file)
index_settings = {
    "mappings": {
        "properties": {
            "question": {"type": "text"},
            "text": {"type": "text"},
            "new_field": {"type": "text"}  -- Add new field
        }
    }
}

# 3. Update search query (llm-app/streamlit/src/elasticSearch.py)
query = {
    "multi_match": {
        "query": input_text,
        "fields": ["question^2", "text", "new_field"]  # Add field
    }
}

# 4. Test in development:
# - Rebuild containers
# - Re-run Airflow DAG
# - Test searches in Streamlit UI

# 5. Commit and push changes
```

### Testing Changes

**Manual Testing Checklist**:
1. **Data Ingestion**: Trigger Airflow DAG, verify completion
2. **Search Functionality**: Test queries in Streamlit UI
3. **BERT Integration**: Verify answers are generated correctly
4. **Metrics Calculation**: Check evaluation_data table for correct values
5. **Feedback System**: Test satisfaction button, verify feedback_data table
6. **Grafana Dashboard**: Verify metrics appear correctly

**Example Test Queries** (from readme.md):
1. "Why did the plaintiff wait seven months to file an appeal?"
2. "What was the outcome of the case?"
3. "Can you provide more details on the clarification provided in Note 1?"
4. "Can the landlord avoid liability for breaching this obligation if the state of disrepair is caused by the tenant's actions?"
5. "What is the Commonwealth Bank of Australia fixed deposit account?"

**Database Verification**:
```bash
# Connect to PostgreSQL via pgAdmin (localhost:5050)
# Or via command line:
docker exec -it llm_postgres psql -U airflow -d airflow

# Check tables:
\dt

# Query recent evaluation data:
SELECT * FROM evaluation_data ORDER BY created_time DESC LIMIT 10;

# Check feedback:
SELECT * FROM feedback_data ORDER BY created_time DESC LIMIT 10;
```

**Elasticsearch Verification**:
```bash
# Check index health:
curl http://localhost:9200/_cat/indices?v

# Check document count:
curl http://localhost:9200/legal-documents/_count

# Sample search:
curl -X GET "http://localhost:9200/legal-documents/_search?pretty" \
  -H 'Content-Type: application/json' \
  -d '{"query": {"match": {"question": "appeal"}}}'
```

---

## Database Schema

### PostgreSQL Tables

**Connection Details**:
- Host: `postgres:5432`
- Database: `airflow`
- User: `airflow`
- Password: `airflow`

#### 1. `legal_document`
**Purpose**: Stores all legal documents from CSV/JSON sources

**Schema**:
```sql
CREATE TABLE legal_document (
    id SERIAL PRIMARY KEY,
    doc_id VARCHAR(10),        -- MD5 hash (first 8 chars) of text+question
    question TEXT NOT NULL,     -- Legal question or case title
    answer TEXT NOT NULL        -- Legal answer or case text
);
```

**Populated By**: Airflow DAG (`insertJson` and `insertCsv` tasks)
**Record Count**: ~50 (25 from each source, limited for performance)

#### 2. `evaluation_data`
**Purpose**: Stores query performance metrics for monitoring

**Schema**:
```sql
CREATE TABLE evaluation_data (
    id SERIAL PRIMARY KEY,
    doc_id VARCHAR(10) NOT NULL,          -- Query identifier
    user_input TEXT NOT NULL,              -- User's question
    result TEXT NOT NULL,                  -- Retrieved context
    llm_score DOUBLE PRECISION NOT NULL,   -- BERT confidence score (0-1)
    response_time DOUBLE PRECISION NOT NULL, -- Query execution time (seconds)
    hit_rate_score DOUBLE PRECISION NOT NULL, -- Hit rate metric (0 or 1)
    mrr_score DOUBLE PRECISION NOT NULL,   -- MRR metric (0-1)
    created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Populated By**: `llm.captureUserInput()` after each query
**Used By**: Grafana dashboard for performance visualization

#### 3. `feedback_data`
**Purpose**: Stores user satisfaction feedback

**Schema**:
```sql
CREATE TABLE feedback_data (
    id SERIAL PRIMARY KEY,
    doc_id VARCHAR(10) NOT NULL,    -- Query identifier
    user_input TEXT NOT NULL,        -- User's question
    result TEXT NOT NULL,            -- Retrieved context
    is_satisfied BOOLEAN NOT NULL,   -- User satisfaction (True/False)
    created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Populated By**: `llm.captureUserFeedback()` when user clicks "Satisfied"
**Used By**: Grafana dashboard for satisfaction rate calculation

### Elasticsearch Index

**Index Name**: `legal-documents`
**Connection**: `elasticsearch:9200`

**Index Settings**:
```json
{
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0
    },
    "mappings": {
        "properties": {
            "doc_id": {"type": "keyword"},
            "question": {"type": "text"},
            "text": {"type": "text"}
        }
    }
}
```

**Document Structure**:
```json
{
    "doc_id": "a1b2c3d4",
    "question": "In the case of Nasr v NRMA Insurance [2006] NSWSC 1018, why was the plaintiff's appeal lodged out of time?",
    "text": "In Nasr v NRMA Insurance [2006] NSWSC 1018, the plaintiff's appeal was lodged out of time because..."
}
```

**Refresh Strategy**: Daily full rebuild via Airflow DAG
**Query Type**: Multi-match on `question^2` (boosted) and `text` fields

---

## Code Conventions

### Python Style

**General Guidelines**:
- Python 3.8 compatible code
- No strict PEP 8 enforcement (existing code varies)
- Functional programming style preferred
- Minimal error handling (improve as needed)

**Naming Conventions**:
- Functions: `camelCase` (e.g., `elasticSearch()`, `captureUserInput()`)
- Variables: `snake_case` (e.g., `user_input`, `llm_score`)
- Constants: `UPPER_CASE` (e.g., `HUGGINGFACE_KEY`, `API_URL`)

**Import Organization**:
```python
# Standard library
import os
from datetime import datetime

# Third-party
import streamlit as st
from elasticsearch import Elasticsearch
import pandas as pd

# Local modules
from src import connection
from src import llm
```

### Database Operations

**Pattern for PostgreSQL**:
```python
# Always use connection pooling from connection.py
conn = connection.createConnection()
cursor = conn.cursor()

try:
    # Execute queries
    cursor.execute("SELECT * FROM table")
    results = cursor.fetchall()

    # For inserts/updates
    cursor.execute("INSERT INTO table VALUES (%s)", (value,))
    conn.commit()

finally:
    cursor.close()
    conn.close()
```

**Pattern for Elasticsearch**:
```python
# Use connection from connection.py
es = connection.createConnectionES()

# Search
results = es.search(index="legal-documents", body=query)

# Index
es.index(index="legal-documents", id=doc_id, document=doc_body)

# Bulk operations
from elasticsearch.helpers import bulk
bulk(es, actions)
```

### Streamlit Patterns

**Session State Management**:
```python
# Initialize state variables
if 'answer' not in st.session_state:
    st.session_state.answer = None

# Update state
st.session_state.answer = "New value"

# Access state
if st.session_state.answer:
    st.write(st.session_state.answer)
```

**Button Handling**:
```python
# Use callbacks for complex logic
def on_click():
    st.session_state.disabled = True
    # Process...

st.button("Label", on_click=on_click)

# Or inline for simple cases
if st.button("Label"):
    # Process...
```

**Error Messages**:
```python
# User-friendly error handling
try:
    result = operation()
except Exception as e:
    st.error(f"An error occurred: {str(e)}")
    st.info("Please try again or contact support")
```

### Airflow DAG Patterns

**Task Definition**:
```python
from airflow.decorators import task

@task
def task_name():
    # Task logic here
    return result

# Task dependencies
task1 = task_name()
task2 = another_task()
task1 >> task2  # Sequential execution
```

**Connection Management**:
```python
# Import from src.connection
from src.connection import createConnection, createConnectionES

# Use in tasks
conn = createConnection()
# ... operations ...
conn.close()
```

### Environment Variables

**Required Variables**:
```bash
HUGGINGFACE_KEY=<your-token>  # Required for BERT API access
```

**Access Pattern**:
```python
import os

HUGGINGFACE_KEY = os.getenv("HUGGINGFACE_KEY")
if not HUGGINGFACE_KEY:
    raise ValueError("HUGGINGFACE_KEY environment variable not set")
```

---

## Testing & Evaluation

### Evaluation Metrics

**1. Hit Rate**
- **Definition**: Binary metric indicating if correct document was retrieved
- **Calculation**: `1.0` if correct doc in top 5 results, else `0.0`
- **Location**: `llm-app/streamlit/src/evaluation.py`
- **Usage**: Measures recall effectiveness

**2. Mean Reciprocal Rank (MRR)**
- **Definition**: Reciprocal of rank of first correct document
- **Formula**: `1 / rank` (e.g., rank 3 → MRR = 0.333)
- **Range**: 0.0 to 1.0 (higher is better)
- **Usage**: Measures ranking quality

**3. BERT Score**
- **Definition**: Confidence score from BERT model
- **Range**: 0.0 to 1.0
- **Source**: Returned by Hugging Face API
- **Usage**: Measures answer quality

### Ground Truth Data

**Location**: `/llm-app/streamlit/src/ground_truth/ground-truth-data.csv`

**Format**:
```csv
question,doc_id
"Why did the plaintiff wait seven months...",a1b2c3d4
"What was the outcome of the case?",b2c3d4e5
```

**Usage**:
- Loaded during evaluation
- Compared against search results
- Used to calculate Hit Rate and MRR

**Generation**:
- Notebook: `generateGroundTruth.ipynb`
- Source: Sample queries with known correct documents

### Manual Testing Procedure

**Step-by-Step Test**:
```bash
# 1. Verify services are running
docker-compose ps

# 2. Trigger Airflow DAG
# Open http://localhost:8080
# Manually trigger "Get_All_LLM_Data"
# Wait for completion (~2-5 minutes)

# 3. Verify data in PostgreSQL
docker exec -it llm_postgres psql -U airflow -d airflow -c \
  "SELECT COUNT(*) FROM legal_document;"
# Expected: ~50 records

# 4. Verify Elasticsearch index
curl http://localhost:9200/legal-documents/_count
# Expected: {"count":50,...}

# 5. Test Streamlit UI
# Open http://localhost:8501
# Enter test question
# Click "Ask"
# Verify answer appears
# Click "Satisfied"

# 6. Verify metrics recorded
docker exec -it llm_postgres psql -U airflow -d airflow -c \
  "SELECT * FROM evaluation_data ORDER BY created_time DESC LIMIT 1;"

# 7. Check Grafana dashboard
# Open http://localhost:3000
# Import dashboard.json if needed
# Verify metrics display correctly
```

### Performance Benchmarks

**Expected Performance**:
- **Query Response Time**: 2-5 seconds
- **Elasticsearch Search**: < 500ms
- **BERT API Call**: 1-4 seconds (depends on Hugging Face load)
- **Database Writes**: < 100ms

**Monitoring**:
- Real-time: Grafana dashboard
- Historical: `evaluation_data` table
- Query: `SELECT AVG(response_time), MAX(response_time) FROM evaluation_data;`

---

## Common Tasks

### Task 1: Adding a New Data Source

**Scenario**: Add a new CSV file with legal documents

**Steps**:
```bash
# 1. Add CSV file to orchestration/dags/dataset/
cp new_legal_data.csv orchestration/dags/dataset/

# 2. Edit orchestration/dags/src/insertData.py
# Add new function:
def insertNewCsvData():
    conn = createConnection()
    cursor = conn.cursor()

    df = pd.read_csv('/opt/airflow/orchestration/dags/dataset/new_legal_data.csv')

    # Map columns to question/answer format
    for _, row in df.iterrows():
        question = row['your_question_column']
        answer = row['your_answer_column']
        doc_id = generate_document_id(answer, question)

        cursor.execute(
            "INSERT INTO legal_document (doc_id, question, answer) VALUES (%s, %s, %s)",
            (doc_id, question, answer)
        )

    conn.commit()
    cursor.close()
    conn.close()

# 3. Edit orchestration/dags/pipeline.py
# Add task to DAG:
insertNewCsv = insertNewCsvData()

# Update dependencies:
createTable >> insertJson >> insertCsv >> insertNewCsv >> ingestData

# 4. Restart Airflow
docker-compose restart airflow-worker airflow-scheduler

# 5. Trigger DAG manually to test
```

### Task 2: Modifying Search Relevance

**Scenario**: Change field boosting in Elasticsearch

**Steps**:
```python
# Edit llm-app/streamlit/src/elasticSearch.py

# Original:
"fields": ["question^2", "text"]

# Boost question 3x instead of 2x:
"fields": ["question^3", "text"]

# Or boost both fields differently:
"fields": ["question^3", "text^1.5"]

# Or add more fields:
"fields": ["question^3", "text^1.5", "new_field^2"]

# Restart app:
# docker-compose restart app

# Test searches to evaluate impact
```

### Task 3: Changing BERT Model

**Scenario**: Switch to a different Hugging Face model

**Steps**:
```python
# Edit llm-app/streamlit/src/llm.py

# Original:
API_URL = "https://api-inference.huggingface.co/models/google-bert/bert-large-uncased-whole-word-masking-finetuned-squad"

# Change to different model:
API_URL = "https://api-inference.huggingface.co/models/deepset/roberta-base-squad2"

# Note: Verify model accepts same input format (question + context)

# Restart app:
# docker-compose restart app

# Test with sample questions
```

### Task 4: Adjusting Number of Search Results

**Scenario**: Return top 10 documents instead of top 5

**Steps**:
```python
# Edit llm-app/streamlit/src/elasticSearch.py

# Original:
query = {
    "size": 5,
    # ...
}

# Change to 10:
query = {
    "size": 10,
    # ...
}

# Restart app:
# docker-compose restart app

# Note: More results = longer context = longer BERT processing time
```

### Task 5: Adding Grafana Dashboard Panels

**Scenario**: Add a new metric visualization

**Steps**:
```bash
# 1. Access Grafana: http://localhost:3000
# Login: admin/admin

# 2. Open existing dashboard (imported from dashboard.json)

# 3. Click "Add panel" → "Add a new panel"

# 4. Configure data source:
# - Data source: PostgreSQL
# - Database: airflow

# 5. Write SQL query:
# Example: Average LLM score over time
SELECT
  created_time AS "time",
  AVG(llm_score) as "avg_score"
FROM evaluation_data
GROUP BY created_time
ORDER BY created_time

# 6. Configure visualization (Graph, Stat, Gauge, etc.)

# 7. Save panel and dashboard

# 8. Export dashboard JSON:
# Dashboard settings → JSON Model → Copy

# 9. Save to llm-app/dashboard.json for version control
```

### Task 6: Increasing Dataset Size

**Scenario**: Load more than 25 records per source

**Steps**:
```python
# Edit orchestration/dags/src/insertData.py

# For JSON data:
def insertJsonData():
    # Find line:
    for i, item in enumerate(data):
        if i < 25:  # Current limit
            # ...

    # Change to:
    for i, item in enumerate(data):
        if i < 100:  # New limit: 100 records
            # ...

# For CSV data:
def insertCsvData():
    # Find line:
    for i, row in dataFrame.iterrows():
        if i < 25:  # Current limit
            # ...

    # Change to:
    for i, row in dataFrame.iterrows():
        if i < 100:  # New limit: 100 records
            # ...

# Or remove limit entirely:
    for i, row in dataFrame.iterrows():
        # Process all rows

# Restart Airflow services:
docker-compose restart airflow-worker airflow-scheduler

# Trigger DAG to reload data
```

### Task 7: Debugging BERT API Issues

**Scenario**: BERT API returns errors or timeouts

**Steps**:
```bash
# 1. Check Hugging Face API status
# Visit: https://status.huggingface.co/

# 2. Verify API key is valid
# Visit: https://huggingface.co/settings/tokens

# 3. Test API directly with curl
curl https://api-inference.huggingface.co/models/google-bert/bert-large-uncased-whole-word-masking-finetuned-squad \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"inputs": {"question": "What is AI?", "context": "AI is artificial intelligence"}}'

# 4. Check API quota/rate limits
# Hugging Face free tier has limits

# 5. Add retry logic in llm.py
def query(payload):
    for attempt in range(3):
        try:
            response = requests.post(API_URL, headers=headers, json=payload)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            if attempt == 2:
                raise
            time.sleep(2 ** attempt)  # Exponential backoff

# 6. Check app logs
docker-compose logs -f app
```

---

## Troubleshooting

### Common Issues

#### 1. "It seems Elastic Search is still running, please refresh again"

**Cause**: Elasticsearch hasn't finished indexing or is still starting up

**Solution**:
```bash
# Check Elasticsearch status
curl http://localhost:9200/_cluster/health

# Wait for status: "green" or "yellow"
# Then refresh Streamlit app

# If stuck for >5 minutes:
docker-compose restart elasticsearch
# Wait 2-3 minutes, then try again
```

#### 2. "No data found" or Empty Search Results

**Cause**: Airflow DAG hasn't run or failed

**Solution**:
```bash
# 1. Check if DAG ran successfully
# Open http://localhost:8080
# Check "Get_All_LLM_Data" DAG status

# 2. Verify data in PostgreSQL
docker exec -it llm_postgres psql -U airflow -d airflow -c \
  "SELECT COUNT(*) FROM legal_document;"

# 3. Verify Elasticsearch index
curl http://localhost:9200/legal-documents/_count

# 4. If count is 0, manually trigger DAG
# Or run tasks individually in Airflow UI

# 5. Check task logs for errors
# Airflow UI → DAG → Task → Logs
```

#### 3. BERT API Returns 503 Error

**Cause**: Hugging Face model loading or rate limiting

**Solutions**:
```bash
# 1. Wait 30-60 seconds and try again
# Model may be loading (cold start)

# 2. Check Hugging Face status
# https://status.huggingface.co/

# 3. Verify API key is set
docker exec llm_app env | grep HUGGINGFACE_KEY

# 4. Check if key is valid
# Login to https://huggingface.co/settings/tokens

# 5. Consider using local model instead of API
# Requires code changes to load model locally
```

#### 4. Airflow DAG Tasks Failing

**Cause**: Various (connection errors, data issues, etc.)

**Diagnosis**:
```bash
# 1. Check task logs in Airflow UI
# Click failed task → Logs

# 2. Common issues:

# Connection to PostgreSQL failed:
docker-compose ps postgres  # Ensure running
docker-compose logs postgres  # Check logs

# Connection to Elasticsearch failed:
docker-compose ps elasticsearch
curl http://localhost:9200  # Should return JSON

# File not found:
docker exec -it llm_airflow ls /opt/airflow/orchestration/dags/dataset/
# Verify files exist

# 3. Restart specific service:
docker-compose restart <service-name>

# 4. Clear task state and retry:
# Airflow UI → Task → Clear → Confirm
```

#### 5. Grafana Dashboard Shows No Data

**Cause**: No queries have been run or data source not configured

**Solution**:
```bash
# 1. Run some test queries in Streamlit
# Open http://localhost:8501
# Ask 3-5 questions

# 2. Verify data in PostgreSQL
docker exec -it llm_postgres psql -U airflow -d airflow -c \
  "SELECT COUNT(*) FROM evaluation_data;"

# 3. Configure Grafana data source:
# Grafana → Configuration → Data Sources → Add PostgreSQL
# Host: postgres:5432
# Database: airflow
# User: airflow
# Password: airflow
# SSL Mode: disable

# 4. Import dashboard:
# Dashboards → Import → Upload JSON
# Select llm-app/dashboard.json

# 5. Adjust time range:
# Top-right corner → Last 24 hours (or appropriate range)
```

#### 6. Docker Containers Keep Restarting

**Cause**: Resource constraints or dependency issues

**Solution**:
```bash
# 1. Check container status
docker-compose ps

# 2. Check logs for specific container
docker-compose logs <container-name>

# 3. Common fixes:

# Insufficient memory:
# Edit docker-compose.yaml
# Reduce worker memory limit or increase Docker memory

# Port conflict:
# Change port mapping in docker-compose.yaml
# e.g., "8502:8501" instead of "8501:8501"

# Dependency not ready:
# Add healthchecks and depends_on conditions

# 4. Restart all services
docker-compose down
docker-compose up -d

# 5. Monitor startup
docker-compose logs -f
```

#### 7. Git Push Returns 403 Error

**Cause**: Branch name doesn't match required pattern

**Solution**:
```bash
# Branch must start with 'claude/' and end with session ID

# Current branch:
git branch --show-current

# If incorrect, create new branch with correct format:
git checkout -b claude/claude-md-micd4kgklv5x7f40-017h45Tw4QmRFxKrcyoiG6tx

# Push to new branch:
git push -u origin claude/claude-md-micd4kgklv5x7f40-017h45Tw4QmRFxKrcyoiG6tx
```

### Performance Optimization

#### Slow Query Response Times

**Diagnosis**:
```sql
-- Check average response times
SELECT AVG(response_time), MAX(response_time), MIN(response_time)
FROM evaluation_data
WHERE created_time > NOW() - INTERVAL '1 day';
```

**Optimizations**:

1. **Reduce number of search results**:
   ```python
   # In elasticSearch.py, reduce from 5 to 3
   "size": 3
   ```

2. **Add Elasticsearch caching**:
   ```python
   # In elasticSearch.py
   query = {
       "query": {...},
       "request_cache": True  # Enable caching
   }
   ```

3. **Optimize BERT context length**:
   ```python
   # In app.py, truncate context
   context = "\n\n".join([doc['answer'][:500] for doc in search_results])
   ```

4. **Use local BERT model** (advanced):
   ```python
   # Replace API call with local transformers
   from transformers import pipeline
   qa_pipeline = pipeline("question-answering")
   result = qa_pipeline(question=question, context=context)
   ```

#### High Memory Usage

**Solutions**:
```bash
# 1. Monitor memory usage
docker stats

# 2. Reduce Airflow worker memory
# Edit docker-compose.yaml:
# mem_limit: 512m  # Instead of 1024m

# 3. Limit Elasticsearch heap
# Edit docker-compose.yaml under elasticsearch:
environment:
  - "ES_JAVA_OPTS=-Xms512m -Xmx512m"

# 4. Restart services
docker-compose down
docker-compose up -d
```

---

## Important Reminders for AI Assistants

### Before Making Changes

1. **Always read existing code first** - Never propose changes to code you haven't read
2. **Understand data flow** - Trace how data moves through the system
3. **Check dependencies** - Identify what other components depend on your changes
4. **Consider side effects** - Think about evaluation metrics, monitoring, database schema

### Code Quality Principles

1. **Avoid over-engineering** - Make minimal necessary changes
2. **No premature optimization** - Don't add complexity for hypothetical future needs
3. **Keep it simple** - Three similar lines > premature abstraction
4. **Follow existing patterns** - Match the style and structure of surrounding code
5. **Security first** - Watch for injection vulnerabilities (SQL, command, XSS)

### Development Best Practices

1. **Test manually before committing** - Use the test queries provided
2. **Check logs after changes** - Ensure no new errors appear
3. **Verify metrics still work** - Confirm Grafana dashboard still populates
4. **Document significant changes** - Update this CLAUDE.md if architecture changes
5. **Commit frequently** - Small, focused commits with clear messages

### Common Pitfalls to Avoid

1. **Don't commit secrets** - Never commit API keys, passwords
2. **Don't skip Airflow testing** - Always trigger DAG manually after changes
3. **Don't assume Elasticsearch is ready** - Always check index status
4. **Don't modify schema without migration** - Plan database changes carefully
5. **Don't break existing queries** - Maintain backward compatibility

### When to Ask User for Clarification

1. **Ambiguous requirements** - Multiple valid implementation approaches
2. **Breaking changes** - Changes that affect existing functionality
3. **Performance trade-offs** - Speed vs accuracy, cost vs quality
4. **Data loss risk** - Operations that might delete or overwrite data
5. **Unclear scope** - "Improve search" could mean many things

---

## Additional Resources

### External Documentation
- **Streamlit**: https://docs.streamlit.io/
- **Apache Airflow**: https://airflow.apache.org/docs/
- **Elasticsearch**: https://www.elastic.co/guide/en/elasticsearch/reference/8.4/index.html
- **Hugging Face**: https://huggingface.co/docs
- **BERT Model**: https://huggingface.co/google-bert/bert-large-uncased-whole-word-masking-finetuned-squad
- **Docker Compose**: https://docs.docker.com/compose/

### Dataset Sources
- **Australian Legal Q&A**: https://www.kaggle.com/datasets/umarbutler/open-australian-legal-qa/data
- **Legal Text Classification**: https://www.kaggle.com/datasets/amohankumar/legal-text-classification-dataset

### Internal References
- **Main README**: `/home/user/Legal-Document-Assistant-Global/readme.md`
- **Grafana Config**: `/home/user/Legal-Document-Assistant-Global/llm-app/dashboard.json`
- **Docker Compose**: `/home/user/Legal-Document-Assistant-Global/docker-compose.yaml`

---

## Changelog

### 2025-11-23
- Initial CLAUDE.md creation
- Documented complete architecture and workflows
- Added troubleshooting guide
- Added common tasks reference

---

*This document is maintained for AI assistants working with the Legal Document Assistant codebase. Keep it updated when significant architectural changes occur.*
