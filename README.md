# 🚀 AstroGPT – Space Science RAG Chatbot

**AstroGPT** is an AI-powered chatbot built using **Retrieval-Augmented Generation (RAG)** to provide informative, factual, and contextual answers in the field of **astronomy and space science**. It includes streaming responses, prompt control, and basic identity filtering.

---

## ✨ Features

* 🔭 **Domain-specific RAG** using a curated space science knowledge base
* 💬 **Real-time streaming** responses using Flask and Server-Sent Events (SSE)
* 🧠 Built on top of **OpenAI GPT-4 / GPT-3.5** for generation
* 📚 Semantic search using `FAISS` and text embeddings
* 🛡️ Identity query filtering to skip generic assistant identity responses
* 🌐 Easy-to-use frontend for chat interaction

---

## 🛠️ Tech Stack

| Layer      | Technology                   |
| ---------- | ---------------------------- |
| Backend    | Python, Flask                |
| RAG Engine | FAISS + SentenceTransformers |
| Streaming  | Server-Sent Events (SSE)     |
| Frontend   | React + Vite + TS            |

---

## 🧰 Folder Structure

```
astro-ai/
│
├── client
├── server
```

---

## 🚀 How It Works

1. **User query** → Received via frontend
2. **Identity filter** → Skips generic assistant prompts like “who are you?”
3. **RAG pipeline**:
   * Embed query
   * Retrieve top relevant chunks from space documents
   * Combine with prompt template
4. **LLM generation** → GPT-4 generates answer using prompt + context
5. **Streaming** → Partial tokens streamed back via SSE to frontend

---

## 🔧 Setup Instructions

1. **Clone the repo**

2. **Set your Gemini API key**

```bash
GEMINI_API_KEY = your_key_here # in .env inside /server
```

4. **Run the server**

```bash
cd server
python main.py
```

4. **Run the client**

```bash
cd client
npm i
npm run dev
```

5. **Access the UI** at `http://localhost:8080`
