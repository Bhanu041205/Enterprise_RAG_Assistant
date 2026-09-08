"""
RAG Evaluation Runner
---------------------
Runs the existing Enterprise RAG system against the
150-question evaluation dataset.

IMPORTANT:
- This script does NOT modify rag_engine.py.
- Requests are throttled to avoid Gemini free-tier rate limits.
- Progress is saved periodically.
- Rate-limit failures are NOT counted as successful evaluations.
"""

import sys
import time
from pathlib import Path

import pandas as pd


# ============================================================
# 1. PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


# ============================================================
# 2. IMPORT EXISTING RAG ENGINE
# ============================================================

from rag_engine import answer_question


# ============================================================
# 3. FILE PATHS
# ============================================================

INPUT_FILE = (
    PROJECT_ROOT
    / "evaluation"
    / "RAG_Evaluation_Dataset_150_Questions.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "evaluation"
    / "RAG_Evaluation_Results_150.csv"
)


# ============================================================
# 4. RATE LIMIT SETTINGS
# ============================================================

# Gemini free tier allows approximately 15 requests/minute.
#
# 5 seconds between questions gives us approximately
# 12 requests/minute, leaving some safety margin.

REQUEST_DELAY = 5

# If Gemini returns a rate-limit error, wait this long
# before retrying.

RATE_LIMIT_WAIT = 65

# Number of attempts for a rate-limited question.

MAX_RETRIES = 3

# Save progress after every N questions.

SAVE_EVERY = 5


# ============================================================
# 5. LOAD DATASET
# ============================================================

print("=" * 70)
print("ENTERPRISE RAG ASSISTANT - RAG EVALUATION")
print("=" * 70)

print("\nLoading evaluation dataset...")

df = pd.read_csv(INPUT_FILE)

print(f"Total evaluation questions: {len(df)}")


# ============================================================
# 6. PREPARE RESULT COLUMNS
# ============================================================

result_columns = {
    "retrieved_chunks": "",
    "generated_answer": "",
    "retrieval_relevance": "",
    "retrieved_source_documents": "",
    "evaluation_status": "",
}

for column, default_value in result_columns.items():

    if column not in df.columns:
        df[column] = default_value

    # Force evaluation result columns to text.
    # This prevents pandas from treating empty CSV
    # columns as float64 and rejecting generated answers.
    df[column] = df[column].astype("string")

# ============================================================
# 7. HELPER FUNCTION
# ============================================================

def is_rate_limit_error(error):
    """
    Check whether an exception appears to be caused by
    Gemini API rate limiting / quota exhaustion.
    """

    error_text = str(error).lower()

    rate_limit_keywords = [
        "429",
        "quota exceeded",
        "rate limit",
        "resource exhausted",
        "too many requests",
        "generate_content_free_tier_requests",
    ]

    return any(
        keyword in error_text
        for keyword in rate_limit_keywords
    )


# ============================================================
# 8. RUN EVALUATION
# ============================================================

for index, row in df.iterrows():

    question_number = index + 1

    question_id = row["question_id"]

    question = row["question"]

    print("\n" + "-" * 70)
    print(
        f"Question {question_number}/{len(df)}"
    )
    print(f"ID: {question_id}")
    print(f"Question: {question}")

    # --------------------------------------------------------
    # Skip questions that already completed successfully.
    # This allows the script to resume after interruption.
    # --------------------------------------------------------

    if df.at[index, "evaluation_status"] == "SUCCESS":

        print("Already completed - skipping.")

        continue


    # --------------------------------------------------------
    # Retry loop
    # --------------------------------------------------------

    success = False

    for attempt in range(1, MAX_RETRIES + 1):

        try:

            print(
                f"Running RAG engine "
                f"(attempt {attempt}/{MAX_RETRIES})..."
            )

            # ------------------------------------------------
            # Call the SAME RAG engine used by Streamlit
            # ------------------------------------------------

            result = answer_question(question)


            # ------------------------------------------------
            # Extract answer and sources
            # ------------------------------------------------

            if isinstance(result, dict):

                answer = result.get(
                    "answer",
                    result.get("response", "")
                )

                sources = result.get(
                    "sources",
                    []
                )

                retrieved_count = result.get(
                    "retrieved_count",
                    len(sources)
                )

            else:

                answer = str(result)

                sources = []

                retrieved_count = 0


            # ------------------------------------------------
            # Detect fake/temporary quota response
            # ------------------------------------------------

            temporary_error_phrases = [
                "temporarily unable to generate",
                "try again later",
                "quota exceeded",
                "rate limit",
            ]

            answer_lower = str(answer).lower()

            temporary_failure = any(
                phrase in answer_lower
                for phrase in temporary_error_phrases
            )

            if temporary_failure:

                raise RuntimeError(
                    "Gemini returned a temporary "
                    "rate-limit/quota response."
                )


            # ------------------------------------------------
            # Store generated answer
            # ------------------------------------------------

            df.at[index, "generated_answer"] = answer


            # ------------------------------------------------
            # Process retrieved sources
            # ------------------------------------------------

            source_documents = []

            source_chunks = []

            relevance_scores = []


            for source in sources:

                document = source.get(
                    "document",
                    "Unknown document"
                )

                chunk_id = source.get(
                    "chunk_id",
                    "Unknown chunk"
                )

                score = source.get(
                    "score",
                    0
                )

                source_documents.append(
                    document
                )

                source_chunks.append(
                    f"{document} | {chunk_id}"
                )

                try:

                    relevance_scores.append(
                        float(score)
                    )

                except (TypeError, ValueError):

                    relevance_scores.append(
                        0.0
                    )


            # ------------------------------------------------
            # Save retrieved chunks
            # ------------------------------------------------

            df.at[index, "retrieved_chunks"] = (
                " || ".join(source_chunks)
            )


            # ------------------------------------------------
            # Save source documents
            # ------------------------------------------------

            df.at[index, "retrieved_source_documents"] = (
                " || ".join(source_documents)
            )


            # ------------------------------------------------
            # Save relevance scores
            # ------------------------------------------------

            df.at[index, "retrieval_relevance"] = (
                " || ".join(
                    f"{score:.4f}"
                    for score in relevance_scores
                )
            )


            # ------------------------------------------------
            # Mark successful
            # ------------------------------------------------

            df.at[index, "evaluation_status"] = "SUCCESS"

            success = True


            # ------------------------------------------------
            # Display result
            # ------------------------------------------------

            print(
                f"Generated answer: {answer}"
            )

            print(
                f"Retrieved passages: "
                f"{retrieved_count}"
            )

            print(
                f"Sources: {len(sources)}"
            )

            print("Status: SUCCESS")

            break


        except Exception as error:

            # ------------------------------------------------
            # Rate-limit error
            # ------------------------------------------------

            if is_rate_limit_error(error):

                print(
                    "\nGemini rate limit detected."
                )

                if attempt < MAX_RETRIES:

                    print(
                        f"Waiting "
                        f"{RATE_LIMIT_WAIT} seconds "
                        f"before retry..."
                    )

                    time.sleep(
                        RATE_LIMIT_WAIT
                    )

                    continue

                else:

                    print(
                        "Maximum retries reached."
                    )

                    df.at[index, "evaluation_status"] = (
                        "RATE_LIMITED"
                    )

                    df.at[index, "generated_answer"] = (
                        "[RATE LIMIT - NOT EVALUATED]"
                    )

                    success = False

                    break


            # ------------------------------------------------
            # Other error
            # ------------------------------------------------

            print(
                f"ERROR while processing "
                f"{question_id}: {error}"
            )

            df.at[index, "evaluation_status"] = (
                f"ERROR: {error}"
            )

            success = False

            break


    # ========================================================
    # SAVE PROGRESS
    # ========================================================

    if (
        question_number % SAVE_EVERY == 0
        or question_number == len(df)
    ):

        df.to_csv(
            OUTPUT_FILE,
            index=False
        )

        print(
            f"\nProgress saved "
            f"after question {question_number}."
        )


    # ========================================================
    # WAIT BEFORE NEXT GEMINI REQUEST
    # ========================================================

    if success:

        print(
            f"Waiting {REQUEST_DELAY} seconds "
            f"before next question..."
        )

        time.sleep(
            REQUEST_DELAY
        )


# ============================================================
# 9. FINAL SAVE
# ============================================================

print("\n" + "=" * 70)
print("Saving final evaluation results...")
print("=" * 70)

df.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# 10. FINAL SUMMARY
# ============================================================

successful = (
    df["evaluation_status"] == "SUCCESS"
).sum()

rate_limited = (
    df["evaluation_status"] == "RATE_LIMITED"
).sum()

errors = (
    df["evaluation_status"]
    .astype(str)
    .str.startswith("ERROR:")
).sum()

not_completed = len(df) - successful - rate_limited - errors


print("\nEvaluation completed.")

print(
    f"Total questions : {len(df)}"
)

print(
    f"Successful      : {successful}"
)

print(
    f"Rate limited    : {rate_limited}"
)

print(
    f"Other errors    : {errors}"
)

print(
    f"Not completed   : {not_completed}"
)

print(
    f"\nResults saved to:\n{OUTPUT_FILE}"
)

print("\n" + "=" * 70)
print("EVALUATION RUN FINISHED")
print("=" * 70)