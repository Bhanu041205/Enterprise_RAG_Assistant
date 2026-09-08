import re
import pickle
from pathlib import Path

import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

RESULTS_FILE = (
    PROJECT_ROOT
    / "evaluation"
    / "RAG_Evaluation_Results_150.csv"
)

CHUNKS_FILE = (
    PROJECT_ROOT
    / "vectorstore"
    / "chunks.pkl"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "evaluation"
    / "RAG_Quality_Evaluation_150.csv"
)


# ============================================================
# SETTINGS
# ============================================================

MODEL_NAME = "all-MiniLM-L6-v2"

# Threshold used for semantic support between generated
# answer sentences and retrieved document chunks.
GROUNDING_THRESHOLD = 0.40

# Threshold used for reference-answer coverage.
COMPLETENESS_THRESHOLD = 0.40


# ============================================================
# TEXT HELPERS
# ============================================================

def clean_text(text):
    """Normalize text for comparison."""
    if pd.isna(text):
        return ""

    text = str(text)
    text = text.lower()

    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^\w\s.%/-]", "", text)

    return text.strip()


def split_sentences(text):
    """Split generated answer into simple sentences."""
    if not text:
        return []

    sentences = re.split(r"(?<=[.!?])\s+", str(text).strip())

    return [
        s.strip()
        for s in sentences
        if s.strip()
    ]


def extract_numbers(text):
    """Extract numerical values from text."""
    if not text:
        return set()

    return set(
        re.findall(
            r"\b\d+(?:\.\d+)?\b",
            str(text)
        )
    )


# ============================================================
# BINARY ANSWER HANDLING
# ============================================================

def binary_answer(expected, generated):
    """
    Handle references such as Yes. / No.

    Returns:
        True  -> generated answer agrees
        False -> generated answer contradicts
        None  -> not a binary reference
    """

    expected_clean = clean_text(expected)
    generated_clean = clean_text(generated)

    if not expected_clean:
        return None

    if expected_clean.startswith("yes"):
        # Explicit positive indicators.
        positive_patterns = [
            r"\byes\b",
            r"\bshould\b",
            r"\bmust\b",
            r"\brequired\b",
            r"\ballowed\b",
            r"\bexpected\b",
            r"\bcan\b",
            r"\bpermitted\b",
        ]

        negative_patterns = [
            r"\bnot allowed\b",
            r"\bnot permitted\b",
            r"\bprohibited\b",
            r"\bcannot\b",
            r"\bno\b",
        ]

        positive = any(
            re.search(pattern, generated_clean)
            for pattern in positive_patterns
        )

        negative = any(
            re.search(pattern, generated_clean)
            for pattern in negative_patterns
        )

        if positive and not negative:
            return True

        if positive and negative:
            # Look at the beginning of the answer.
            first_part = generated_clean[:100]

            if re.search(r"\bno\b", first_part):
                return False

            return True

        return False

    if expected_clean.startswith("no"):
        negative_patterns = [
            r"\bno\b",
            r"\bnot\b",
            r"\bcannot\b",
            r"\bprohibited\b",
            r"\bnot allowed\b",
            r"\bnot permitted\b",
            r"\bdoes not\b",
            r"\bdo not\b",
        ]

        positive_patterns = [
            r"\byes\b",
            r"\bis allowed\b",
            r"\bis permitted\b",
            r"\bcan\b",
        ]

        negative = any(
            re.search(pattern, generated_clean)
            for pattern in negative_patterns
        )

        positive = any(
            re.search(pattern, generated_clean)
            for pattern in positive_patterns
        )

        if negative and not positive:
            return True

        if positive and not negative:
            return False

        # If answer begins with "no", accept.
        if generated_clean.startswith("no"):
            return True

        return False

    return None


# ============================================================
# CHUNK LOADING
# ============================================================

def load_chunks():
    """Load vectorstore chunk metadata."""

    print("Loading chunks...")

    with open(CHUNKS_FILE, "rb") as f:
        chunks = pickle.load(f)

    chunk_map = {}

    for item in chunks:

        if not isinstance(item, dict):
            continue

        chunk_id = item.get("chunk_id", "")
        text = item.get("text", "")
        document = item.get("document", "")

        if chunk_id:
            chunk_map[str(chunk_id)] = {
                "text": str(text),
                "document": str(document),
            }

    print(f"Chunks loaded: {len(chunk_map)}")

    return chunk_map


# ============================================================
# RETRIEVED CHUNK PARSING
# ============================================================

def parse_chunk_ids(value):
    """
    Extract chunk IDs from the evaluation runner format.

    Example:
        Leave_Policy.docx | Leave_Policy.docx_chunk_0010
        ||
        Leave_Policy.docx | Leave_Policy.docx_chunk_0011
    """

    if pd.isna(value):
        return []

    text = str(value).strip()

    if not text:
        return []

    parts = text.split("||")

    chunk_ids = []

    for part in parts:

        part = part.strip()

        if "|" in part:
            # Format:
            # Document.docx | chunk_id
            chunk_id = part.split("|")[-1].strip()
        else:
            chunk_id = part.strip()

        chunk_id = chunk_id.strip("'\"[] ")

        if chunk_id:
            chunk_ids.append(chunk_id)

    return chunk_ids


# ============================================================
# GROUNDING SCORE
# ============================================================

def calculate_groundedness(
    generated_answer,
    retrieved_texts,
    model,
):
    """
    Calculate how much of the generated answer is supported
    by the retrieved chunks.

    Each answer sentence is compared with every retrieved chunk.
    The best similarity is used.
    """

    sentences = split_sentences(generated_answer)

    if not sentences:
        return 0.0

    if not retrieved_texts:
        return 0.0

    answer_embeddings = model.encode(
        sentences,
        normalize_embeddings=True,
    )

    chunk_embeddings = model.encode(
        retrieved_texts,
        normalize_embeddings=True,
    )

    similarities = cosine_similarity(
        answer_embeddings,
        chunk_embeddings,
    )

    supported = 0

    for row in similarities:

        best_score = float(np.max(row))

        if best_score >= GROUNDING_THRESHOLD:
            supported += 1

    return supported / len(sentences)


# ============================================================
# COMPLETENESS SCORE
# ============================================================

def calculate_completeness(
    expected_answer,
    generated_answer,
    model,
):
    """
    Measures how much of the expected answer is represented
    in the generated answer.

    Uses sentence-level semantic similarity.
    """

    expected_sentences = split_sentences(expected_answer)
    generated_sentences = split_sentences(generated_answer)

    if not expected_sentences:
        return 0.0

    if not generated_sentences:
        return 0.0

    expected_embeddings = model.encode(
        expected_sentences,
        normalize_embeddings=True,
    )

    generated_embeddings = model.encode(
        generated_sentences,
        normalize_embeddings=True,
    )

    similarities = cosine_similarity(
        expected_embeddings,
        generated_embeddings,
    )

    covered = 0

    for row in similarities:

        best_score = float(np.max(row))

        if best_score >= COMPLETENESS_THRESHOLD:
            covered += 1

    return covered / len(expected_sentences)


# ============================================================
# ANSWER CORRECTNESS
# ============================================================

def calculate_correctness(
    expected_answer,
    generated_answer,
    model,
):
    """
    Hybrid correctness score.

    1. Special handling for Yes/No references.
    2. Numeric fact matching.
    3. Semantic similarity.
    """

    if not expected_answer or not generated_answer:
        return 0.0

    # --------------------------------------------------------
    # Binary questions
    # --------------------------------------------------------

    binary = binary_answer(
        expected_answer,
        generated_answer,
    )

    if binary is not None:
        return 1.0 if binary else 0.0

    # --------------------------------------------------------
    # Numeric information
    # --------------------------------------------------------

    expected_numbers = extract_numbers(
        expected_answer
    )

    generated_numbers = extract_numbers(
        generated_answer
    )

    if expected_numbers:

        number_matches = (
            expected_numbers
            .intersection(generated_numbers)
        )

        number_score = (
            len(number_matches)
            / len(expected_numbers)
        )
    else:
        number_score = 1.0

    # --------------------------------------------------------
    # Semantic similarity
    # --------------------------------------------------------

    embeddings = model.encode(
        [
            expected_answer,
            generated_answer,
        ],
        normalize_embeddings=True,
    )

    semantic_score = float(
        cosine_similarity(
            embeddings[0:1],
            embeddings[1:2],
        )[0][0]
    )

    # Convert cosine range approximately [-1,1]
    # to [0,1].
    semantic_score = (
        semantic_score + 1
    ) / 2

    # --------------------------------------------------------
    # Final hybrid score
    # --------------------------------------------------------

    if expected_numbers:
        score = (
            0.60 * number_score
            + 0.40 * semantic_score
        )
    else:
        score = semantic_score

    return float(
        max(0.0, min(1.0, score))
    )


# ============================================================
# SOURCE ATTRIBUTION
# ============================================================

def source_attribution(
    expected_source,
    retrieved_documents,
):
    """Check whether expected source document was retrieved."""

    if not expected_source:
        return False

    expected_source = str(
        expected_source
    ).strip().lower()

    documents = [
        str(doc).strip().lower()
        for doc in retrieved_documents
        if str(doc).strip()
    ]

    return expected_source in documents


# ============================================================
# MAIN EVALUATION
# ============================================================

def main():

    print("=" * 70)
    print("RAG QUALITY EVALUATION")
    print("=" * 70)

    # --------------------------------------------------------
    # Load result file
    # --------------------------------------------------------

    print("\nLoading evaluation results...")

    df = pd.read_csv(
        RESULTS_FILE
    )

    print(
        f"Questions loaded: {len(df)}"
    )

    # --------------------------------------------------------
    # Load chunks
    # --------------------------------------------------------

    chunk_map = load_chunks()

    # --------------------------------------------------------
    # Load embedding model
    # --------------------------------------------------------

    print("\nLoading embedding model...")

    model = SentenceTransformer(
        MODEL_NAME
    )

    print("Embedding model loaded.")

    # --------------------------------------------------------
    # Prepare output columns
    # --------------------------------------------------------

    df["source_attribution"] = 0.0
    df["answer_correctness_score"] = 0.0
    df["groundedness_score"] = 0.0
    df["completeness_score"] = 0.0
    df["retrieved_chunk_count"] = 0
    df["quality_status"] = ""

    # --------------------------------------------------------
    # Evaluate each question
    # --------------------------------------------------------

    total = len(df)

    print("\nEvaluating questions...")

    for index, row in df.iterrows():

        question_id = row.get(
            "question_id",
            f"Q{index + 1:03d}",
        )

        expected_answer = str(
            row.get(
                "expected_answer",
                "",
            )
        )

        generated_answer = str(
            row.get(
                "generated_answer",
                "",
            )
        )

        expected_source = str(
            row.get(
                "expected_source",
                "",
            )
        )

        # --------------------------------------------
        # Parse retrieved chunks
        # --------------------------------------------

        chunk_ids = parse_chunk_ids(
            row.get(
                "retrieved_chunks",
                "",
            )
        )

        retrieved_texts = []
        retrieved_documents = []

        for chunk_id in chunk_ids:

            chunk = chunk_map.get(
                chunk_id
            )

            if chunk:

                retrieved_texts.append(
                    chunk["text"]
                )

                retrieved_documents.append(
                    chunk["document"]
                )

        # --------------------------------------------
        # Source attribution
        # --------------------------------------------

        source_ok = source_attribution(
            expected_source,
            retrieved_documents,
        )

        # --------------------------------------------
        # Unanswerable questions
        # --------------------------------------------

        answerable = str(
            row.get(
                "answerable",
                "Yes",
            )
        ).strip().lower()

        if answerable == "no":

            generated_clean = clean_text(
                generated_answer
            )

            refusal_patterns = [
                "not available",
                "not provided",
                "not mentioned",
                "cannot determine",
                "does not provide",
                "no information",
                "not specified",
                "not covered",
                "outside the provided",
            ]

            refused = any(
                pattern in generated_clean
                for pattern in refusal_patterns
            )

            correctness = (
                1.0 if refused else 0.0
            )

            groundedness = (
                1.0 if refused else 0.0
            )

            completeness = (
                1.0 if refused else 0.0
            )

            hallucination = (
                0.0 if refused else 1.0
            )

            status = (
                "PASS"
                if refused
                else "HALLUCINATION"
            )

        else:

            # ----------------------------------------
            # Answerable questions
            # ----------------------------------------

            correctness = calculate_correctness(
                expected_answer,
                generated_answer,
                model,
            )

            groundedness = calculate_groundedness(
                generated_answer,
                retrieved_texts,
                model,
            )

            completeness = calculate_completeness(
                expected_answer,
                generated_answer,
                model,
            )

            hallucination = (
                0.0
                if groundedness >= 0.50
                else 1.0
            )

            status = "PASS"

        # --------------------------------------------
        # Store results
        # --------------------------------------------

        df.at[
            index,
            "source_attribution"
        ] = (
            1.0 if source_ok else 0.0
        )

        df.at[
            index,
            "answer_correctness_score"
        ] = correctness

        df.at[
            index,
            "groundedness_score"
        ] = groundedness

        df.at[
            index,
            "completeness_score"
        ] = completeness

        df.at[
            index,
            "retrieved_chunk_count"
        ] = len(retrieved_texts)

        df.at[
            index,
            "quality_status"
        ] = status

        # Progress
        if (
            (index + 1) % 10 == 0
            or index == total - 1
        ):
            print(
                f"Processed {index + 1}/{total}"
            )

    # --------------------------------------------------------
    # Save detailed results
    # --------------------------------------------------------

    print("\nSaving detailed results...")

    df.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    # --------------------------------------------------------
    # Calculate summary metrics
    # --------------------------------------------------------

    answerable_df = df[
        df["answerable"]
        .astype(str)
        .str.lower()
        .eq("yes")
    ]

    unanswerable_df = df[
        df["answerable"]
        .astype(str)
        .str.lower()
        .eq("no")
    ]

    print("\n")
    print("=" * 70)
    print("FINAL RAG EVALUATION RESULTS")
    print("=" * 70)

    print(
        f"\nTotal questions: "
        f"{len(df)}"
    )

    print(
        f"Answerable questions: "
        f"{len(answerable_df)}"
    )

    print(
        f"Unanswerable questions: "
        f"{len(unanswerable_df)}"
    )

    # --------------------------------------------------------
    # Source attribution
    # --------------------------------------------------------

    if len(answerable_df) > 0:

        source_accuracy = (
            answerable_df[
                "source_attribution"
            ].mean()
            * 100
        )

    else:
        source_accuracy = 0.0

    print(
        f"\nSource attribution accuracy: "
        f"{source_accuracy:.2f}%"
    )

    # --------------------------------------------------------
    # Correctness
    # --------------------------------------------------------

    if len(answerable_df) > 0:

        correctness = (
            answerable_df[
                "answer_correctness_score"
            ].mean()
            * 100
        )

    else:
        correctness = 0.0

    print(
        f"Answer correctness score: "
        f"{correctness:.2f}%"
    )

    # --------------------------------------------------------
    # Groundedness
    # --------------------------------------------------------

    if len(answerable_df) > 0:

        groundedness = (
            answerable_df[
                "groundedness_score"
            ].mean()
            * 100
        )

    else:
        groundedness = 0.0

    print(
        f"Groundedness score: "
        f"{groundedness:.2f}%"
    )

    # --------------------------------------------------------
    # Completeness
    # --------------------------------------------------------

    if len(answerable_df) > 0:

        completeness = (
            answerable_df[
                "completeness_score"
            ].mean()
            * 100
        )

    else:
        completeness = 0.0

    print(
        f"Completeness score: "
        f"{completeness:.2f}%"
    )

    # --------------------------------------------------------
    # Hallucination handling
    # --------------------------------------------------------

    if len(unanswerable_df) > 0:

        hallucination_handling = (
            1
            - unanswerable_df[
                "quality_status"
            ]
            .eq("HALLUCINATION")
            .mean()
        ) * 100

    else:
        hallucination_handling = 0.0

    print(
        f"Unanswerable-question handling: "
        f"{hallucination_handling:.2f}%"
    )

    print(
        f"\nDetailed results saved to:"
    )

    print(OUTPUT_FILE)

    print("\n")
    print("=" * 70)
    print("EVALUATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()