# Healthy Eating AI Chatbot

A Python-based AI chatbot that conducts role-playing conversations about healthy eating and evaluates user responses using keyword detection and semantic matching.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Implementation Steps](#implementation-steps)
- [Project Structure](#project-structure)
- [How It Works](#how-it-works)
- [API Endpoints](#api-endpoints)
- [Running the Project](#running-the-project)
- [Testing](#testing)

---

## Overview

This chatbot engages users in natural conversations about healthy eating habits, monitors for specific keywords across 5 categories, and assigns a score (0-100) based on how well the user addresses each topic.

**Key Features:**
- OpenAI GPT-4o-mini for natural conversation
- Hybrid keyword detection (string matching + semantic similarity)
- Redis-based conversation history
- RESTful API + CLI demo
- Comprehensive test suite

---

## Architecture

I chose a **layered architecture** to ensure clear separation of concerns:

```
┌─────────────────────────────────────────┐
│         Presentation Layer              │
│    (FastAPI Router + CLI Demo)          │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│           Service Layer                 │
│   (ChatService + ScoringService)        │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│          Repository Layer               │
│  (OpenAIRepository + RedisRepository)   │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│         External Services               │
│       (OpenAI API + Redis)              │
└─────────────────────────────────────────┘
```

**Why this approach?**
- Each layer has a single responsibility
- Easy to test with mocks
- Swappable components (e.g., replace OpenAI with another LLM)

---

## Implementation Steps

### Step 1: Define the Data Models

Created Pydantic models for type safety and validation:
- `Message` - Single chat message with role and content
- `Conversation` - Collection of messages with metadata
- `ScoreResult` - Detailed scoring breakdown
- `KeywordCategory` - Keyword groups for each topic

### Step 2: Set Up Keyword Categories

Defined 5 categories as specified in the task, each with:
- English and Turkish keywords for broader matching
- Related terms (e.g., "apple" maps to "Fruits & Vegetables")
- Max score of 20 points per category (total: 100)

### Step 3: Build the Repository Layer

**OpenAIRepository:**
- `chat_completion()` - Sends messages to GPT-4o-mini
- `create_embedding()` - Generates embeddings for semantic matching

**RedisRepository:**
- `save_message()` / `get_history()` - Conversation persistence
- `cache_embedding()` - Reduces API calls for repeated keywords

### Step 4: Implement the Scoring Service

Two-phase keyword detection:

1. **String Matching** - Fast, exact keyword lookup
2. **Semantic Matching** - Uses embeddings + cosine similarity for indirect references

Scoring logic:
- 3+ keyword matches → Full points (20)
- 2 matches → 70% (14 points)
- 1 match → 40% (8 points)

### Step 5: Create the Chat Service

- Manages conversation lifecycle
- Injects system prompt for role-playing behavior
- Calls ScoringService after each user message
- Stores history in Redis

### Step 6: Expose via API and CLI

**FastAPI Endpoints:**
- `POST /chat/start` - Begin new conversation
- `POST /chat/message` - Send message, get response + score
- `GET /chat/score/{id}` - Detailed score breakdown

**CLI Demo:**
- Interactive terminal chat
- Real-time score display
- Commands: `score`, `reset`, `quit`

### Step 7: Write Tests

Created comprehensive test suite:
- Unit tests for models
- Mocked repository tests
- Service integration tests
- API endpoint tests

---

## Project Structure

```
src/
├── model/
│   ├── conversation.py    # Pydantic models
│   └── keywords.py        # 5 keyword categories
├── repository/
│   ├── openai_repository.py
│   └── redis_repository.py
├── service/
│   ├── chat_service.py    # Conversation logic
│   └── scoring_service.py # Evaluation logic
├── router/
│   └── chat_router.py     # API endpoints
└── cli.py                 # Terminal demo

tests/
├── test_models.py
├── test_repositories.py
├── test_services.py
└── test_api.py
```

---

## How It Works

### Conversation Flow

```
1. User starts conversation
2. Bot greets and asks about healthy eating
3. User responds with their thoughts
4. For each user message:
   a. Save to Redis
   b. Send full history to OpenAI
   c. Get bot response
   d. Analyze user messages for keywords
   e. Calculate score
   f. Return response + current score
5. User can request detailed score anytime
```

### Scoring Example

User says: *"I eat fruits and vegetables daily. I drink 8 glasses of water."*

| Category | Matched Keywords | Score |
|----------|-----------------|-------|
| Fruits & Vegetables | fruits, vegetables, daily | 20/20 |
| Hydration | drink, water, 8 glasses | 20/20 |
| Balanced Meals | - | 0/20 |
| Processed Foods | - | 0/20 |
| Meal Timing | - | 0/20 |
| **Total** | | **40/100** |

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/chat/start` | Start new conversation |
| POST | `/chat/message` | Send message |
| GET | `/chat/score/{id}` | Get detailed score |
| POST | `/chat/reset/{id}` | Reset conversation |
| GET | `/chat/history/{id}` | Get message history |

---

## Running the Project

### Prerequisites

- Python 3.10+
- Redis server (port 6380)
- OpenAI API key

### Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY="sk-..."
export REDIS_URL="redis://localhost:6380"
export REDIS_PASSWORD="your-password"

# Run API server
python app.py

# Or run CLI demo
python -m src.cli
```

---

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_services.py -v
```

---

## Technologies Used

| Technology | Purpose |
|------------|---------|
| FastAPI | REST API framework |
| OpenAI GPT-4o-mini | Conversation generation |
| OpenAI Embeddings | Semantic keyword matching |
| Redis | Conversation history & caching |
| Pydantic | Data validation |
| Pytest | Testing framework |

---

## Design Decisions

1. **Hybrid Keyword Detection**: Combines exact string matching (fast) with semantic similarity (flexible) for better coverage.

2. **Redis for State**: Chose Redis over in-memory storage for persistence and scalability.

3. **Async/Await**: All I/O operations are async for better performance under concurrent requests.

4. **Layered Architecture**: Enables easy testing and future modifications (e.g., swap LLM provider).

5. **Bilingual Keywords**: Included Turkish translations to demonstrate extensibility.

