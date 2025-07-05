# IITI-GPT: Personalized Fullstack Chatbot for IIT Indore

IITI-GPT is a fullstack AI-powered chatbot tailored for the IIT Indore campus. It integrates Retrieval-Augmented Generation (RAG), user feedback, and interactive campus navigation. Built with Django and designed for edge devices like Raspberry Pi, it delivers fast, contextual answers powered by LLM APIs.

## 🌟 Features

- 🔐 **User Authentication** — Secure login/signup using Django sessions.
- 💬 **Chatbot** — Cohere LLM API + Tavily web search integration using LangChain.
- 📍 **Campus Navigation** — Interactive map generation with fuzzy search.
- 📦 **Raspberry Pi Compatible** — Lightweight client; heavy LLM queries offloaded via API.

## 🛠 Tech Stack

- **Backend**: Django, LangChain,
- **Frontend**: HTML, CSS, JS
- **LLM**: Cohere
- **Search API**: Tavily

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Git

### Clone the Repository

```bash
git clone https://github.com/Siddharththakur3617/IITI-GPT.git
cd IITI-GPT
