from flask import Flask, request, jsonify, Response, stream_with_context
import pandas as pd
import random
import os
import time
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.prompts import PromptTemplate
from flask_cors import CORS

import google.generativeai as genai
from dotenv import dotenv_values

app = Flask(__name__)
CORS(app, origins=["http://localhost:8080"])

config = dotenv_values(".env")
GEMINI_KEY = config.get("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_KEY)
gmodel = genai.GenerativeModel("gemini-2.0-flash")

VECTOR_STORE_PATH = "cache/faiss_vectorstore"
EMBEDDING_MODEL_CACHE = "cache/embeddings"
DATA_HASH_FILE = "cache/data_hash.txt"

def create_cache_dir():
    """Create cache directory if it doesn't exist"""
    os.makedirs("cache", exist_ok=True)

def get_data_hash():
    """Get hash of the dataset to detect changes"""
    try:
        synthetic_path = "data/synthetic_space_data_30k.csv"
        if os.path.exists(synthetic_path):
            # Get file modification time as simple hash
            return str(os.path.getmtime(synthetic_path))
        return None
    except:
        return None

def load_datasets():
    synthetic_path = "data/synthetic_space_data_30k.csv"
    df_synth = pd.read_csv(synthetic_path)
    return df_synth

def df_to_documents(df, prefix):
    docs = []
    for _, row in df.iterrows():
        text = f"{prefix}:\n"
        for col, val in row.items():
            text += f"{col}: {val}\n"
        docs.append(Document(page_content=text))
    return docs

def should_rebuild_vectorstore():
    """Check if vector store needs to be rebuilt"""
    create_cache_dir()
    
    # Check if cached files exist
    # if not os.path.exists(VECTOR_STORE_PATH) or not os.path.exists(f"{VECTOR_STORE_PATH}.faiss"):
    if not os.path.exists(VECTOR_STORE_PATH):
        print("No cached vector store found. Building new one.")
        return True
    
    # Check if data has changed
    current_hash = get_data_hash()
    if current_hash is None:
        print("Cannot access dataset. Building new vector store.")
        return True
    
    try:
        if os.path.exists(DATA_HASH_FILE):
            with open(DATA_HASH_FILE, 'r') as f:
                cached_hash = f.read().strip()
            if cached_hash != current_hash:
                print("Dataset has changed. Rebuilding vector store.")
                return True
        else:
            print("No hash file found. Building new vector store.")
            return True
    except:
        print("Error reading hash file. Rebuilding vector store.")
        return True
    
    print("Using cached vector store.")
    return False

def build_and_save_vectorstore():
    """Build vector store and save to cache"""
    print("🔄 Building vector store (this may take a moment)...")
    
    print("  📊 Loading datasets...")
    df_synth = load_datasets()

    print("  📝 Converting datasets to documents...")
    docs_synth = df_to_documents(df_synth, "Synthetic Planet Data")

    print("  ✂️ Splitting documents...")
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    split_docs = splitter.split_documents(docs_synth)

    print("  🤖 Creating embeddings...")
    embedding_model = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        cache_folder=EMBEDDING_MODEL_CACHE  # Cache the embedding model too
    )

    print("  🏗️ Building FAISS vector store...")
    vectorstore = FAISS.from_documents(split_docs, embedding_model)
    
    print("  💾 Saving vector store to cache...")
    vectorstore.save_local(VECTOR_STORE_PATH)
    
    # Save data hash
    current_hash = get_data_hash()
    if current_hash:
        with open(DATA_HASH_FILE, 'w') as f:
            f.write(current_hash)
    
    print("  ✅ Vector store built and cached successfully!")
    return vectorstore

def load_cached_vectorstore():
    """Load vector store from cache"""
    print("⚡ Loading cached vector store...")
    
    try:
        # Load embedding model (cached)
        embedding_model = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            cache_folder=EMBEDDING_MODEL_CACHE
        )
        
        # Load vector store
        vectorstore = FAISS.load_local(
            VECTOR_STORE_PATH, 
            embedding_model,
            allow_dangerous_deserialization=True  # Required for newer versions
        )
        
        print("  ✅ Cached vector store loaded successfully!")
        return vectorstore
        
    except Exception as e:
        print(f"  ❌ Error loading cached vector store: {e}")
        print("  🔄 Falling back to building new vector store...")
        return build_and_save_vectorstore()

def prepare_vectorstore():
    """Main function to get vector store (cached or new)"""
    create_cache_dir()
    
    if should_rebuild_vectorstore():
        return build_and_save_vectorstore()
    else:
        return load_cached_vectorstore()

print("🚀 Initializing AstroAI...")
vectorstore = prepare_vectorstore()
print("🌟 AstroAI ready to explore the universe!")

rag_prompt_template = """
# AstroAI - Advanced Space Science Assistant

## SYSTEM IDENTITY & ROLE
You are **AstroAI**, a highly specialized expert assistant in:
- Space Science
- Astronomy
- Astrophysics
- Related Fields

## INSTRUCTIONS
1. First, analyze the provided scientific documents carefully
2. If the context contains relevant information to answer the question, use it as your primary source
3. If the context lacks sufficient information or is not relevant, respond with exactly: "INSUFFICIENT_CONTEXT"
4. Be accurate, structured, and formal in your responses
5. Only use the provided context - do not add external knowledge

---

## Context:
{context}

## Question:
{question}

## Answer:
""".strip()

gemini_prompt_template = """
You are **AstroAI**, an expert assistant specializing in space science, astronomy, and astrophysics.

## INSTRUCTIONS:
- Provide comprehensive, accurate information about space science topics
- Use scientific terminology appropriately
- Structure your response clearly with proper formatting
- Include specific details, measurements, and facts when relevant
- Maintain a professional, educational tone
- Format properly don't give codes which have soo much spacing between 2 lines

## Question:
{question}

## Answer:
""".strip()

rag_prompt = PromptTemplate(input_variables=["context", "question"], template=rag_prompt_template)
gemini_prompt = PromptTemplate(input_variables=["question"], template=gemini_prompt_template)

def is_space_related(query):
    space_keywords = [
        # Basic space terms
        "space", "nasa", "astronomy", "telescope", "universe", "planet",
        "black hole", "cosmos", "galaxy", "mars", "moon", "satellite",
        "astro", "solar", "rocket", "ISS", "spacecraft", "cosmology",
        
        # Celestial objects
        "star", "sun", "jupiter", "saturn", "venus", "mercury", "neptune",
        "uranus", "pluto", "asteroid", "comet", "meteor", "nebula",
        "pulsar", "quasar", "supernova", "neutron star", "white dwarf", "earth"
        
        # Space missions and technology
        "james webb", "hubble", "voyager", "cassini", "curiosity", "perseverance",
        "apollo", "artemis", "spacex", "falcon", "dragon", "starship",
        "international space station", "iss", "spacewalk", "eva",
        
        # Astronomical phenomena
        "orbit", "gravity", "gravitational", "light year", "parsec",
        "redshift", "cosmic", "interstellar", "intergalactic", "exoplanet",
        "habitable zone", "goldilocks", "dark matter", "dark energy",
        "big bang", "cosmic microwave background", "expansion",
        
        # Space science fields
        "astrophysics", "planetary science", "astrobiology", "astrochemistry",
        "stellar evolution", "galactic", "extragalactic", "cosmological"
        
        # Popular space terms
        "alien", "extraterrestrial", "ufo", "seti", "milky way",
        "andromeda", "solar system", "space exploration", "space travel", "quantum physics"
    ]
    
    query_lower = query.lower()
    return any(keyword in query_lower for keyword in space_keywords)

def assess_context_relevance(context, question):
    """Assess if the retrieved context is relevant to the question"""
    if not context or len(context.strip()) < 50:
        return False
    
    # Simple keyword overlap check
    question_words = set(question.lower().split())
    context_words = set(context.lower().split())
    
    # Remove common words
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'what', 'how', 'when', 'where', 'why'}
    question_words -= stop_words
    context_words -= stop_words
    
    # Calculate overlap
    overlap = len(question_words.intersection(context_words))
    relevance_score = overlap / len(question_words) if question_words else 0
    
    return relevance_score > 0.2  # At least 20% keyword overlap

def get_rejection_message():
    messages = [
        # Original responses
        "Sorry, I can only help with topics related to space science, astronomy, or astrophysics.",
        "I'm built specifically to answer questions about space, the universe, celestial bodies, and scientific space research.",
        "This assistant focuses solely on space science and astronomy. Please ask something within that domain.",
        "Oops! That question is outside my scope. Try something related to stars, planets, telescopes, or space missions.",
        "I specialize in space-related topics only. Ask me about the cosmos, NASA, black holes, or the solar system!",
        
        # Additional responses - Formal tone
        "I'm designed exclusively for space science and astronomy topics. Please rephrase your question to focus on these areas.",
        "My expertise is limited to astronomical and space science subjects. Could you ask something about the universe instead?",
        "That falls outside my specialized domain of space science and astrophysics. Try asking about galaxies, nebulae, or space exploration.",
        "I'm programmed to discuss only space-related phenomena and research. Please ask about astronomical objects or space missions.",
        "My knowledge base covers space science exclusively. Consider asking about planetary science, stellar evolution, or cosmology.",
        
        # Additional responses - Friendly tone
        "I'm your space science expert! Let's talk about something cosmic like supernovas, exoplanets, or the Big Bang instead.",
        "That's not in my wheelhouse, but I'd love to chat about anything space-related! How about Mars exploration or the Milky Way?",
        "I'm all about the stars and beyond! Ask me something about space telescopes, asteroid belts, or distant galaxies.",
        "Space is my thing! Try asking about rocket science, the International Space Station, or Jupiter's moons.",
        "I'm your go-to for all things astronomical! Let's explore topics like dark matter, space weather, or lunar missions.",
        
        # Additional responses - Explanatory tone
        "As an astronomy-focused assistant, I can only address questions about space science, celestial mechanics, and astrophysical phenomena.",
        "My capabilities are specifically tailored for space science discussions. Please ask about topics like stellar formation, planetary atmospheres, or space technology.",
        "I'm specialized in astronomical and space science topics only. Try questions about quasars, satellite missions, or the search for extraterrestrial life.",
        "My programming centers on space science expertise. Ask me about cosmic radiation, space missions, or the structure of the universe.",
        "I focus exclusively on space and astronomy topics. Consider asking about meteor showers, space probes, or gravitational waves.",
        
        # Additional responses - Redirective tone
        "That's outside my space science specialty, but I'd be happy to discuss anything from Saturn's rings to gamma-ray bursts!",
        "Let's keep it cosmic! Ask me about something like the Hubble Space Telescope, neutron stars, or the asteroid belt instead.",
        "I'm here for space talk only! How about we explore topics like the James Webb telescope, Mars rovers, or stellar nurseries?",
        "Space science is my domain! Try asking about things like orbital mechanics, the cosmic microwave background, or SpaceX missions.",
        "I'm built for the cosmos! Let's discuss something astronomical like binary star systems, the Kuiper Belt, or space colonization.",
        
        # Additional responses - Enthusiastic tone
        "That's not my area, but I'm excited to talk about anything space-related! Think rockets, aliens, or the edge of the universe!",
        "I live and breathe space science! Ask me about something stellar like pulsars, wormholes, or the latest Mars discoveries.",
        "Space is where I shine! Let's blast off into topics like the solar wind, exoplanet hunting, or interstellar travel.",
        "I'm passionate about all things astronomical! Try asking about cosmic phenomena, space agencies, or the mysteries of dark energy.",
        "The universe is my playground! Ask me about anything from tiny asteroids to massive galaxy clusters!"
    ]
    return random.choice(messages)

def run_rag_with_fallback(user_query):
    """Try RAG first, fallback to Gemini if context is insufficient"""
    
    # Step 1: Retrieve relevant documents
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
    docs = retriever.get_relevant_documents(user_query)
    context_text = "\n\n".join([doc.page_content for doc in docs])
    
    # Step 2: Assess context relevance
    context_is_relevant = assess_context_relevance(context_text, user_query)
    
    if context_is_relevant and len(context_text.strip()) > 100:
        # Try RAG approach first
        try:
            filled_prompt = rag_prompt.format(context=context_text, question=user_query)
            rag_response = gmodel.generate_content(filled_prompt)
            
            # Check if RAG found sufficient information
            if "INSUFFICIENT_CONTEXT" not in rag_response.text:
                return {
                    "message": rag_response.text,
                    "response_type": "rag_context",
                    "source": "Scientific Documents"
                }
        except Exception as e:
            print(f"RAG error: {e}")
    
    # Step 3: Fallback to Gemini general knowledge
    print("Using Gemini fallback for general space knowledge...")
    try:
        filled_gemini_prompt = gemini_prompt.format(question=user_query)
        gemini_response = gmodel.generate_content(filled_gemini_prompt)
        
        return {
            "message": gemini_response.text,
            "response_type": "gemini_fallback",
            "source": "General Space Science Knowledge"
        }
    except Exception as e:
        return {
            "message": "I apologize, but I'm unable to provide an answer at the moment. Please try asking about a specific space science topic.",
            "response_type": "error",
            "source": "error"
        }

@app.route("/generate", methods=["POST"])
def generate():
    data = request.json
    user_query = data.get("text", "").strip()

    if not user_query:
        return jsonify({"error": "Empty query"}), 400

    if not is_space_related(user_query):
        return jsonify({
            "response_type": "rejection",
            "message": get_rejection_message()
        }), 404

    @stream_with_context
    def generate_stream():
        try:
            retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
            docs = retriever.get_relevant_documents(user_query)
            context_text = "\n\n".join([doc.page_content for doc in docs])
            context_is_relevant = assess_context_relevance(context_text, user_query)

            if context_is_relevant and len(context_text.strip()) > 100:
                filled_prompt = rag_prompt.format(context=context_text, question=user_query)
                rag_response = gmodel.generate_content(filled_prompt)
                if "INSUFFICIENT_CONTEXT" not in rag_response.text:
                    for chunk in rag_response.text.split('. '):
                        yield chunk.strip() + '. '
                        time.sleep(0.1)
                    return

            # Fallback to Gemini
            filled_prompt = gemini_prompt.format(question=user_query)
            gemini_response = gmodel.generate_content(filled_prompt)
            for chunk in gemini_response.text.split('. '):
                yield chunk.strip() + '. '
                time.sleep(0.1)

        except Exception as e:
            yield f"Error: {str(e)}"

    return Response(generate_stream(), mimetype='text/plain')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)