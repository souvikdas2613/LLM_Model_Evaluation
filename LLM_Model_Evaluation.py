import os
import time

from dotenv import load_dotenv
from openai import OpenAI


# --------------------------------------------------
# Load environment variables
# --------------------------------------------------

load_dotenv(override=True)


# --------------------------------------------------
# OpenAI configuration
# --------------------------------------------------

print("\nLOADING OPENAI API KEY and MODEL .....")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL") or os.getenv("MODEL_NAME")

print("\nOPENAI MODEL:", OPENAI_MODEL)


# --------------------------------------------------
# Red Hat Granite configuration
# --------------------------------------------------

print("\nLOADING RED HAT GRANITE API KEY , URL and MODEL.....")

GRANITE_API_KEY = os.getenv("REDHAT_GRANITE_API_KEY")
GRANITE_BASE_URL = os.getenv("REDHAT_GRANITE_BASE_URL")
GRANITE_MODEL = os.getenv("REDHAT_GRANITE_MODEL")

print("\nRED HAT GRANITE BASE URL:", GRANITE_BASE_URL)
print("\nRED HAT GRANITE MODEL:", GRANITE_MODEL)


# --------------------------------------------------
# Approximate USD prices per 1 million tokens
# (update these if your provider pricing changes)
# --------------------------------------------------

# Example rates for a small OpenAI model (approximate learning defaults)
##  For GPT-4.1 nano, the current official OpenAI API pricing is:

## Model	        Input / 1M tokens	Output / 1M tokens
## GPT-4.1-nano	        $0.10	        $0.40


OPENAI_INPUT_PRICE_PER_1M = 0.10
OPENAI_OUTPUT_PRICE_PER_1M = 0.40

# granite-4-0-h-tiny subscription pricing
# Input: $0.05/1M Tokens • Output: $0.05/1M Tokens
# Context Length: 4,000,000 tokens
GRANITE_INPUT_PRICE_PER_1M = 0.05
GRANITE_OUTPUT_PRICE_PER_1M = 0.05

## 1 M (Million) = 1000000

# --------------------------------------------------
# Validate configuration
# --------------------------------------------------

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set in .env")

if not OPENAI_MODEL:
    raise ValueError("OPENAI_MODEL / MODEL_NAME is not set in .env")

if not GRANITE_API_KEY:
    raise ValueError("REDHAT_GRANITE_API_KEY is not set in .env")

if not GRANITE_BASE_URL:
    raise ValueError("REDHAT_GRANITE_BASE_URL is not set in .env")

if not GRANITE_MODEL:
    raise ValueError("REDHAT_GRANITE_MODEL is not set in .env")


# --------------------------------------------------
# Create clients
# --------------------------------------------------

REQUEST_TIMEOUT_SECONDS = 45

print("\nCREATING OPENAI CLIENT .....")
openai_client = OpenAI(
    api_key=OPENAI_API_KEY,
    timeout=REQUEST_TIMEOUT_SECONDS,
)

print("CREATING RED HAT GRANITE CLIENT .....")
granite_client = OpenAI(
    api_key=GRANITE_API_KEY,
    base_url=GRANITE_BASE_URL,
    timeout=REQUEST_TIMEOUT_SECONDS,
)


# --------------------------------------------------
# Token / cost helpers
# --------------------------------------------------

def get_usage(response):
    """Read token counts from an OpenAI-style response."""

    try:
        usage = response.usage
    except Exception:
        usage = None

    if usage is None:
        return {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
        }

    prompt_tokens = usage.prompt_tokens
    completion_tokens = usage.completion_tokens
    total_tokens = usage.total_tokens

    if prompt_tokens is None:
        prompt_tokens = 0
    if completion_tokens is None:
        completion_tokens = 0
    if total_tokens is None:
        total_tokens = 0

    return {
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
    }


def estimate_cost_usd(prompt_tokens, completion_tokens, input_per_1m, output_per_1m):
    """Estimate USD cost from token counts and $/1M rates."""

    if input_per_1m <= 0 and output_per_1m <= 0:
        return None

    cost = (
        (prompt_tokens / 1000000) * input_per_1m
        + (completion_tokens / 1000000) * output_per_1m
    )
    return round(cost, 6)


def format_cost(cost):
    """Pretty print a cost value for the table."""

    if cost is None:
        return "n/a".rjust(10)
    return f"${cost:.6f}"


# --------------------------------------------------
# Ask OpenAI
# --------------------------------------------------

def ask_openai(question):

    start_time = time.perf_counter()
    usage = {
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "total_tokens": 0,
    }

    try:
        response = openai_client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": question,
                }
            ],
        )
        answer = response.choices[0].message.content
        usage = get_usage(response)
        error = None
    except Exception as exc:
        answer = None
        error = str(exc)

    latency = time.perf_counter() - start_time
    cost = estimate_cost_usd(
        usage["prompt_tokens"],
        usage["completion_tokens"],
        OPENAI_INPUT_PRICE_PER_1M,
        OPENAI_OUTPUT_PRICE_PER_1M,
    )

    return {
        "model": OPENAI_MODEL,
        "answer": answer,
        "latency": round(latency, 3),
        "error": error,
        "prompt_tokens": usage["prompt_tokens"],
        "completion_tokens": usage["completion_tokens"],
        "total_tokens": usage["total_tokens"],
        "cost_usd": cost,
    }


# --------------------------------------------------
# Ask Granite
# --------------------------------------------------

def ask_granite(question):

    start_time = time.perf_counter()
    usage = {
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "total_tokens": 0,
    }

    try:
        response = granite_client.chat.completions.create(
            model=GRANITE_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": question,
                }
            ],
        )
        answer = response.choices[0].message.content
        usage = get_usage(response)
        error = None
    except Exception as exc:
        answer = None
        error = str(exc)

    latency = time.perf_counter() - start_time
    cost = estimate_cost_usd(
        usage["prompt_tokens"],
        usage["completion_tokens"],
        GRANITE_INPUT_PRICE_PER_1M,
        GRANITE_OUTPUT_PRICE_PER_1M,
    )

    return {
        "model": GRANITE_MODEL,
        "answer": answer,
        "latency": round(latency, 3),
        "error": error,
        "prompt_tokens": usage["prompt_tokens"],
        "completion_tokens": usage["completion_tokens"],
        "total_tokens": usage["total_tokens"],
        "cost_usd": cost,
    }


# --------------------------------------------------
# Display results
# --------------------------------------------------

def display_results(results):

    # 1) Print ALL answers from both LLMs first
    print("\n" + "=" * 80)
    print("                 ANSWERS FROM BOTH LLMs")
    print("=" * 80)

    for index, result in enumerate(results, start=1):
        print("\n" + "-" * 80)
        print(f"QUESTION {index}: {result['question']}")
        print("-" * 80)

        print("\n========== OPENAI ==========")
        if result["openai_error"]:
            print("ERROR:", result["openai_error"])
        else:
            print(result["openai_answer"])

        print("\n========== GRANITE ==========")
        if result["granite_error"]:
            print("ERROR:", result["granite_error"])
        else:
            print(result["granite_answer"])

    # 2) Latency table
    print("\n" + "=" * 80)
    print("                 LATENCY TABLE")
    print("=" * 80)
    print(f"{'Question':<50} {'OpenAI':>12} {'Granite':>12}")
    print("-" * 80)

    for result in results:
        oai = (
            f"{result['openai_latency']:>10.2f}s"
            if not result["openai_error"]
            else "ERROR".rjust(12)
        )
        gran = (
            f"{result['granite_latency']:>10.2f}s"
            if not result["granite_error"]
            else "ERROR".rjust(12)
        )
        print(f"{result['question']:<50} {oai} {gran}")

    print("=" * 80)

    # 3) Tokens / cost table
    print("\n" + "=" * 100)
    print("                 TOKENS / COST TABLE")
    print("=" * 100)
    print(
        f"{'Question':<30} "
        f"{'OPEN_AI_TOKENS':>16} {'OPEN_AI_COST($)':>16} "
        f"{'GRANITE_TOKENS':>16} {'GRANITE_COST($)':>16}"
    )
    print("-" * 100)

    openai_token_total = 0
    granite_token_total = 0
    openai_cost_total = 0.0
    granite_cost_total = 0.0
    openai_cost_known = False
    granite_cost_known = False

    for result in results:
        if result["openai_error"]:
            openai_tokens = "ERROR".rjust(16)
            openai_cost = "ERROR".rjust(16)
        else:
            openai_tokens = f"{result['openai_total_tokens']:>16}"
            openai_cost = format_cost(result["openai_cost_usd"]).rjust(16)
            openai_token_total += result["openai_total_tokens"]
            if result["openai_cost_usd"] is not None:
                openai_cost_total += result["openai_cost_usd"]
                openai_cost_known = True

        if result["granite_error"]:
            granite_tokens = "ERROR".rjust(16)
            granite_cost = "ERROR".rjust(16)
        else:
            granite_tokens = f"{result['granite_total_tokens']:>16}"
            granite_cost = format_cost(result["granite_cost_usd"]).rjust(16)
            granite_token_total += result["granite_total_tokens"]
            if result["granite_cost_usd"] is not None:
                granite_cost_total += result["granite_cost_usd"]
                granite_cost_known = True

        question_short = result["question"]
        if len(question_short) > 30:
            question_short = question_short[:27] + "..."

        print(
            f"{question_short:<30} "
            f"{openai_tokens} {openai_cost} {granite_tokens} {granite_cost}"
        )

    print("-" * 100)
    print(
        f"{'TOTAL':<30} "
        f"{openai_token_total:>16} "
        f"{format_cost(openai_cost_total if openai_cost_known else None).rjust(16)} "
        f"{granite_token_total:>16} "
        f"{format_cost(granite_cost_total if granite_cost_known else None).rjust(16)}"
    )
    print("=" * 100)
    print(
        "Note: costs are approximate estimates from the $/1M rates set in the script."
    )


# --------------------------------------------------
# Main function
# --------------------------------------------------

def main():

    questions = [
        "What is an embedding?",
        "What is RAG?",
        "What is a vector database?",
    ]

    results = []

    for question in questions:
        openai_result = ask_openai(question)
        granite_result = ask_granite(question)

        results.append(
            {
                "question": question,
                "openai_latency": openai_result["latency"],
                "granite_latency": granite_result["latency"],
                "openai_error": openai_result["error"],
                "granite_error": granite_result["error"],
                "openai_answer": openai_result["answer"],
                "granite_answer": granite_result["answer"],
                "openai_total_tokens": openai_result["total_tokens"],
                "granite_total_tokens": granite_result["total_tokens"],
                "openai_prompt_tokens": openai_result["prompt_tokens"],
                "granite_prompt_tokens": granite_result["prompt_tokens"],
                "openai_completion_tokens": openai_result["completion_tokens"],
                "granite_completion_tokens": granite_result["completion_tokens"],
                "openai_cost_usd": openai_result["cost_usd"],
                "granite_cost_usd": granite_result["cost_usd"],
            }
        )

    print("\nDISPLAYING RESULTS .....")
    display_results(results)


# --------------------------------------------------
# Run program
# --------------------------------------------------

if __name__ == "__main__":
    print("\nRUNNING MAIN FUNCTION .....")
    main()
    print("\nMAIN FUNCTION COMPLETED .....")
