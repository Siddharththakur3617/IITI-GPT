from pathlib import Path
from typing import Annotated, TypedDict

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_cohere import ChatCohere, CohereEmbeddings
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, Send
from pypdf import PdfReader
from tavily import TavilyClient

BASE = Path(__file__).parent
load_dotenv(BASE / ".env")
MAX_TRIES = 3  # Hallucination -> Query Router repeats

llm = ChatCohere(model="command-a-03-2025", temperature=0)
tavily = TavilyClient()
db = Chroma(
    collection_name="docs",
    embedding_function=CohereEmbeddings(model="embed-english-v3.0"),
    persist_directory=str(BASE / "chroma_db"),
)

# Embed any PDF in data/ that is not in ChromaDB yet
loaded = {m["source"] for m in db.get(include=["metadatas"])["metadatas"] if m}
for pdf in (BASE / "data").glob("*.pdf"):
    if pdf.name in loaded:
        continue
    text = "".join(page.extract_text() or "" for page in PdfReader(pdf).pages)
    chunks = [text[i:i + 1000] for i in range(0, len(text), 800)]
    for i in range(0, len(chunks), 90):
        db.add_texts(chunks[i:i + 90], metadatas=[{"source": pdf.name}] * len(chunks[i:i + 90]))


def ask(prompt):
    return llm.invoke(prompt).content.strip()


def merge(old, new):  # None clears the answers before a retry
    return [] if new is None else old + new


def chat_log(history):  # [[question, answer], ...] -> text
    return "\n".join(f"User: {q}\nAssistant: {a}" for q, a in history)


class State(TypedDict):
    query: str
    history: list[list[str]]  # last few [question, answer] pairs
    subqueries: list[str]
    routes: list[tuple[str, str]]
    answers: Annotated[list[str], merge]
    final: str
    ok: bool
    tries: int


def query_formation(state):
    out = ask(
        f"Conversation so far:\n{chat_log(state.get('history', []))}\n\n"
        "If the query uses words like 'it', 'that' or 'he' that refer to the conversation, first rewrite it as a standalone query. "
        "If the query is about the conversation itself (e.g. 'what did I ask?'), keep it unchanged. "
        "If the query asks two or more clearly different questions, break it down into sub-queries, one per line. "
        "A query about a single topic (even with extra words like a place or name) must be returned unchanged as one line. "
        "Output only the queries.\n"
        f"Query: {state['query']}"
    )
    subqueries = [line.strip("-•* ").strip() for line in out.splitlines() if line.strip()]
    return {"subqueries": subqueries or [state["query"]], "tries": 0}


def query_router(state):
    routes = []
    for q in state["subqueries"]:
        method = ask(
            "Decide which method to use to answer this query. Reply with one word:\n"
            "web - needs current or online information\n"
            "database - about IIT Indore (our PDF knowledge base): its people, projects, courses, rules, events\n"
            "direct - general knowledge, or about this conversation itself\n"
            f"Query: {q}"
        ).lower()
        node = "web_search" if "web" in method else "database" if "database" in method else "direct_llm"
        routes.append((q, node))
    return {"routes": routes, "answers": None}


def web_search(p):
    results = tavily.search(p["q"], max_results=3)["results"]
    return Command(goto=Send("check", {"q": p["q"], "results": results}))


def check(p):
    # If Tavily returned nothing, the LLM answers without context
    context = "\n".join(r["content"] for r in p["results"]) if p["results"] else ""
    return Command(goto=Send("llm", {"q": p["q"], "context": context}))


def database(p):
    docs = db.similarity_search(p["q"], k=3)
    context = "\n".join(d.page_content for d in docs)
    return Command(goto=Send("llm", {"q": p["q"], "context": context}))


def generate(p):
    return {"answers": [ask(
        "Using the context, give the user all the information relevant to their query. "
        "Focus on the main subject they are asking about.\n"
        f"Context:\n{p['context']}\nQuery: {p['q']}"
    )]}


def direct_llm(p):
    return {"answers": [ask(f"Conversation so far:\n{p['history']}\n\nUser: {p['q']}")]}


def all_answered(state):
    return len(state["answers"]) == len(state["routes"])


def hallucination(state):
    if not all_answered(state):  # other subquery branches are still running
        return {}
    final = "\n\n".join(state["answers"])
    verdict = ask(
        "Does this answer actually answer (or, for a statement, properly respond to) the query? Reply yes or no.\n"
        f"Query: {state['query']}\nAnswer: {final}"
    )
    return {"final": final, "ok": verdict.lower().startswith("yes"), "tries": state["tries"] + 1}


g = StateGraph(State)
g.add_node("query_formation", query_formation)
g.add_node("query_router", query_router)
g.add_node("web_search", web_search)
g.add_node("check", check)
g.add_node("database", database)
g.add_node("llm", generate)
g.add_node("direct_llm", direct_llm)
g.add_node("hallucination", hallucination)

g.add_edge(START, "query_formation")
g.add_edge("query_formation", "query_router")
g.add_conditional_edges(
    "query_router",
    lambda s: [Send(node, {"q": q, "history": chat_log(s.get("history", []))}) for q, node in s["routes"]],
)
g.add_edge("llm", "hallucination")
g.add_edge("direct_llm", "hallucination")
g.add_conditional_edges(
    "hallucination",
    lambda s: "query_router" if all_answered(s) and not s["ok"] and s["tries"] < MAX_TRIES else END,
)
graph = g.compile()

if __name__ == "__main__":
    print(graph.invoke({"query": input("Ask: ")})["final"])
