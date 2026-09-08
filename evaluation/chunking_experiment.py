import pickle
from pathlib import Path


# ============================================================
# CHUNKING EXPERIMENT
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CHUNKS_PATH = PROJECT_ROOT / "vectorstore" / "chunks.pkl"


# Load the existing processed chunks.
# We use their text as representative document content.
with open(CHUNKS_PATH, "rb") as f:
    existing_chunks = pickle.load(f)


# Combine chunks belonging to each document.
documents = {}

for chunk in existing_chunks:
    document = chunk["document"]

    if document not in documents:
        documents[document] = ""

    documents[document] += " " + chunk["text"]


def create_experimental_chunks(text, chunk_size, chunk_overlap):
    """
    Simple character-based chunking used only for comparison.

    This experiment does NOT modify the production vector store.
    """

    chunks = []

    start = 0

    while start < len(text):

        end = start + chunk_size

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(text):
            break

        start = end - chunk_overlap

    return chunks


# Configurations to compare
configurations = [
    (300, 50),
    (500, 100),
    (700, 150),
]


print("=" * 70)
print("CHUNKING EXPERIMENT")
print("=" * 70)

print("Documents:", len(documents))
print()


for chunk_size, overlap in configurations:

    all_chunks = []

    for document, text in documents.items():

        chunks = create_experimental_chunks(
            text,
            chunk_size,
            overlap
        )

        all_chunks.extend(chunks)

    lengths = [len(chunk) for chunk in all_chunks]

    average_length = sum(lengths) / len(lengths)

    print("-" * 70)
    print(f"Chunk size       : {chunk_size}")
    print(f"Overlap          : {overlap}")
    print(f"Total chunks     : {len(all_chunks)}")
    print(f"Average length   : {average_length:.2f}")
    print(f"Minimum length   : {min(lengths)}")
    print(f"Maximum length   : {max(lengths)}")
    print()


print("=" * 70)
print("Experiment completed.")
print("Production vector store was NOT modified.")
print("=" * 70)