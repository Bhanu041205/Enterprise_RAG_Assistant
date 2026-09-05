
# ============================================================
# TECHNOVA ENTERPRISE RAG ENGINE
# ============================================================

from pathlib import Path
import pickle
import time

import faiss
from sentence_transformers import SentenceTransformer
from google import genai
from google.genai.errors import ClientError, ServerError
from dotenv import load_dotenv
load_dotenv()

# ============================================================
# PATHS
# ============================================================

PROJECT_DIR = Path(__file__).resolve().parent.parent

VECTORSTORE_DIR = PROJECT_DIR / "vectorstore"

FAISS_PATH = VECTORSTORE_DIR / "tech_nova.index"
CHUNKS_PATH = VECTORSTORE_DIR / "chunks.pkl"


# ============================================================
# CONFIGURATION
# ============================================================

MODEL_NAME = "all-MiniLM-L6-v2"

GEMINI_MODEL = "gemini-3.5-flash-lite"

# Minimum FAISS similarity score required for a result
# to be considered relevant.
RELEVANCE_THRESHOLD = 0.20


# ============================================================
# LOAD EMBEDDING MODEL
# ============================================================

print("Loading embedding model...")

embedding_model = SentenceTransformer(MODEL_NAME)

print("Embedding model loaded:", MODEL_NAME)


# ============================================================
# LOAD FAISS INDEX
# ============================================================

print("Loading FAISS index...")

index = faiss.read_index(str(FAISS_PATH))

print("FAISS index loaded!")
print("Vectors:", index.ntotal)
print("Dimension:", index.d)


# ============================================================
# LOAD CHUNKS
# ============================================================

print("Loading chunks...")

with open(CHUNKS_PATH, "rb") as f:
    chunks = pickle.load(f)

print("Chunks loaded:", len(chunks))


# ============================================================
# GEMINI CLIENT
# ============================================================

def get_gemini_client():
    """Create Gemini client only when generation is requested."""
    import os

    api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY is not configured. "
            "Please configure your Gemini API key before generating answers."
        )

    return genai.Client(api_key=api_key)


# ============================================================
# RETRIEVAL
# ============================================================

def retrieve(
    query,
    top_k=3,
    document_name=None
):
    """
    Retrieve the most relevant document chunks for a query.

    Parameters:
    - query: User's question.
    - top_k: Maximum number of chunks to retrieve.
    - document_name: Optional document filename.

    If document_name is provided, only chunks belonging
    to that document are considered.

    If document_name is None, the entire knowledge base
    is searched normally.
    """

    # Convert the user's question into an embedding.
    query_embedding = embedding_model.encode(
        [query],
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    # ----------------------------------------------------
    # SEARCH MORE RESULTS WHEN DOCUMENT FILTERING
    # ----------------------------------------------------
    #
    # We search the complete index first and then filter
    # the results by document name.
    #
    # This avoids rebuilding the FAISS index.
    # ----------------------------------------------------

    search_k = index.ntotal

    scores, indices = index.search(
        query_embedding,
        search_k
    )

    results = []

    # Process retrieved results.
    for score, idx in zip(
        scores[0],
        indices[0]
    ):

        # FAISS can return -1 for invalid results.
        if idx < 0:
            continue

        score = float(score)

        # Ignore low-relevance chunks.
        if score < RELEVANCE_THRESHOLD:
            continue

        # Get corresponding chunk.
        chunk = chunks[idx]

        # ------------------------------------------------
        # DOCUMENT FILTER
        # ------------------------------------------------
        #
        # If a document name was supplied, ignore chunks
        # belonging to other documents.
        # ------------------------------------------------

        if (
            document_name is not None
            and chunk["document"] != document_name
        ):
            continue

        results.append({
            "document": chunk["document"],
            "chunk_id": chunk["chunk_id"],
            "text": chunk["text"],
            "score": score
        })

        # Stop once we have enough relevant results.
        if len(results) >= top_k:
            break

    return results


# ============================================================
# RAG PROMPT
# ============================================================

def build_rag_prompt(question, retrieved_results):

    context_parts = []

    for i, result in enumerate(
        retrieved_results,
        start=1
    ):

        context_parts.append(
            f"""
SOURCE {i}
Document: {result["document"]}
Chunk ID: {result["chunk_id"]}

Content:
{result["text"]}
"""
        )

    context = "\n".join(context_parts)

    prompt = f"""
You are TechNova Solutions' internal knowledge assistant.

Answer the user's question using ONLY the information
provided in the retrieved company documents below.

Rules:
1. Do not invent information.
2. Do not use outside knowledge.
3. If the retrieved documents do not contain enough information,
   say that the information is not available in the provided
   company documents.
4. Give a concise and clear answer.
5. Mention the relevant document name in the answer when useful.

RETRIEVED COMPANY DOCUMENTS:

{context}

USER QUESTION:
{question}

ANSWER:
"""

    return prompt


# ============================================================
# GEMINI RETRY
# ============================================================

def generate_with_retry(prompt, max_retries=4):
    """
    Generate a Gemini response with intelligent retry handling.

    Temporary errors such as:
    - 429 RESOURCE_EXHAUSTED
    - 503 UNAVAILABLE

    are retried with exponential backoff.

    Permanent errors such as:
    - Invalid API key
    - Invalid request

    are raised immediately.
    """

    for attempt in range(max_retries):

        try:

            client = get_gemini_client()

            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt
            )

            return response.text.strip()

        except ServerError as e:

            # Server errors such as 503 can be temporary.
            if attempt < max_retries - 1:

                wait_time = 2 ** attempt

                print(
                    f"Gemini server temporarily unavailable. "
                    f"Retrying in {wait_time} seconds..."
                )

                time.sleep(wait_time)

            else:
                raise e


        except ClientError as e:

            error_message = str(e)

            # Retry only quota/rate-limit errors.
            if (
                "429" in error_message
                or "RESOURCE_EXHAUSTED" in error_message
            ) and attempt < max_retries - 1:

                wait_time = 2 ** attempt

                print(
                    f"Gemini rate limit reached. "
                    f"Retrying in {wait_time} seconds..."
                )

                time.sleep(wait_time)

            else:
                # Invalid API key, bad request, etc.
                # should not be retried.
                raise e


        except Exception as e:

            # Unknown errors are not blindly retried.
            raise e


    raise RuntimeError(
        "Gemini generation failed after all retry attempts."
    )



# ============================================================
# COMPLETE RAG PIPELINE
# ============================================================

def answer_question(question, top_k=3, document_name=None):
    """
    Complete Enterprise RAG pipeline.

    Returns a consistent dictionary containing:

    - question
    - answer
    - sources
    - retrieved_count
    """

    # --------------------------------------------------------
    # Validate question
    # --------------------------------------------------------

    if not question or not question.strip():

        return {
            "question": question,
            "answer": "Please enter a question.",
            "sources": [],
            "retrieved_count": 0
        }

    # Remove unnecessary whitespace.
    question = question.strip()

    # --------------------------------------------------------
    # STEP 1 — RETRIEVE
    # --------------------------------------------------------

    retrieved_results = retrieve(
        question,
        top_k=top_k,
        document_name=document_name
    )

    # --------------------------------------------------------
    # STEP 2 — NO RELEVANT INFORMATION
    # --------------------------------------------------------

    if not retrieved_results:

        return {
            "question": question,

            "answer": (
                "This information is not available in "
                "the provided company documents."
            ),

            "sources": [],

            "retrieved_count": 0
        }

    # --------------------------------------------------------
    # STEP 3 — BUILD GROUNDED PROMPT
    # --------------------------------------------------------

    prompt = build_rag_prompt(
        question,
        retrieved_results
    )

    # --------------------------------------------------------
    # STEP 4 — GENERATE ANSWER
    # --------------------------------------------------------

    try:

        answer = generate_with_retry(
            prompt
        )

    except Exception as e:

        # Keep the error away from the user-facing answer.
        print(
            "Gemini generation error:",
            type(e).__name__,
            str(e)
        )

        return {
            "question": question,

            "answer": (
                "I’m temporarily unable to generate an answer. "
                "Please try again later."
            ),

            "sources": [],

            "retrieved_count": len(retrieved_results)
        }

    # --------------------------------------------------------
    # STEP 5 — PREPARE SOURCE INFORMATION
    # --------------------------------------------------------

    sources = []

    for result in retrieved_results:

        sources.append({
            "document": result["document"],
            "chunk_id": result["chunk_id"],
            "score": round(
                float(result["score"]),
                4
            )
        })

    # --------------------------------------------------------
    # STEP 6 — RETURN FRONTEND-FRIENDLY RESPONSE
    # --------------------------------------------------------

    return {
        "question": question,
        "answer": answer,
        "sources": sources,
        "retrieved_count": len(retrieved_results)
    }
