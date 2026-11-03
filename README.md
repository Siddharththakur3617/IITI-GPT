# IITI GPT

A campus assistant for IIT Indore. It has a chatbot that answers from PDF documents, the web, or general knowledge, and a campus map with walking routes.

**Tech:** Django · SQLite · LangGraph · Cohere · ChromaDB · Tavily · Folium · OSRM

## Features

- **Accounts:** sign up, log in and log out with Django's built-in auth. Passwords are hashed and stored in SQLite.
- **Chatbot:** a LangGraph pipeline that picks the best source for each question.
- **Chat memory:** remembers your last 5 questions and answers, so follow-ups like "who coordinated it?" work.
- **Campus navigation:** pick two of 57 campus places from a searchable list and see the walking route, distance and time on a map.

## How the chatbot works

```
START → Query formation → Query router ─┬→ Web search (Tavily) → Check → LLM ─┐
                                         ├→ Database (ChromaDB, your PDFs) → LLM ┼→ Hallucination check → END
                                         └→ Direct LLM ─────────────────────────┘         │
                                         ↑                                                │
                                         └──────── answer doesn't fit (up to 3 tries) ────┘
```

1. **Query formation:** rewrites follow-up questions using the chat history, and splits a question that asks several things into sub-questions.
2. **Query router:** an LLM picks a method for each sub-question: web search for current information, the PDF database for IIT Indore topics, or a direct LLM answer.
3. **Web search → Check:** searches with Tavily. If nothing comes back, the LLM answers without web context.
4. **Database:** semantic search over the PDFs in `data/`, embedded with Cohere into ChromaDB.
5. **Hallucination check:** checks whether the answer actually answers the question. If it doesn't, the question goes back to the router, up to 3 times.

## Setup

**1. Clone and install** (Python 3.11+):

```bash
git clone https://github.com/Siddharththakur3617/IITI-GPT.git
cd IITI-GPT
python -m venv .venv
.venv\Scripts\activate          # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

**2. Add API keys.** Create a file named `.env` in the project folder:

```
COHERE_API_KEY=your-cohere-key
TAVILY_API_KEY=your-tavily-key
```

Get the keys from [dashboard.cohere.com](https://dashboard.cohere.com/api-keys) and [app.tavily.com](https://app.tavily.com/). Never commit `.env`.

**3. Create the database and run:**

```bash
python manage.py migrate
python manage.py runserver
```

Open http://127.0.0.1:8000/signup/ and create an account.

On the first run, the PDFs in `data/` are embedded into `chroma_db/`. This takes a moment.

## Adding documents

Put PDF files in `data/` and restart the server. New files are loaded automatically. If you edit or delete a PDF, delete the `chroma_db/` folder and restart, so the database is rebuilt.

## Project structure

```
├── pipeline.py        # LangGraph chatbot pipeline
├── navigation.py      # campus places + walking routes
├── urls.py            # pages: signup, login, logout, chat, navigation
├── settings.py        # Django settings (SQLite)
├── manage.py
├── templates/         # base, chat, login/signup form, navigation pages
├── data/              # PDFs for the chatbot's database
└── requirements.txt
```

## Notes

- Walking routes come from the free OSRM server at routing.openstreetmap.de, using OpenStreetMap data. If it's unavailable, the map shows a straight line instead.
- Campus coordinates come from [Monik17/IITI-GPT](https://github.com/Monik17/IITI-GPT). A few of them, such as the bus stop and the sports complex, may need checking.
- `settings.py` uses a development `SECRET_KEY` and `DEBUG = True`. Change both before deploying.
