# LLM_Model_Evaluation

**GitHub:** [https://github.com/souvikdas2613/LLM_Model_Evaluation](https://github.com/souvikdas2613/LLM_Model_Evaluation)

A practice AI project that compares **two LLMs side by side** on the **same questions**:

- **OpenAI** (cloud API)
- **Red Hat Granite** (OpenAI-compatible API)

You run one script → each question is asked to both models → you see **all answers first**, then a **latency table at the end**.

---

## What it does

1. Loads secrets from `.env`
2. Prints which OpenAI model is loaded
3. Prints Granite base URL + model
4. Checks that required settings exist
5. Creates an **OpenAI client** (timeout 45s)
6. Creates a **Granite client** (same OpenAI SDK, different `base_url`, timeout 45s)
7. Asks **3 questions** to both models
8. Prints **OpenAI + Granite answers for every question**
9. Prints a **latency comparison table**
10. Prints a **tokens / cost table** (with totals)

---

## Architecture (simple)

```text
                         .env
                  (keys + model names)
                            |
                            v
                 LLM_Model_Evaluation.py
                            |
              +-------------+-------------+
              |                           |
              v                           v
         OpenAI client              Granite client
         (default URL)              (custom base_url)
              |                           |
              +-------------+-------------+
                            |
                            v
              1) Print ALL answers (both LLMs)
              2) Print LATENCY TABLE
              3) Print TOKENS / COST TABLE
```

**Rule of thumb used in this project**

| Job | Who does it |
|-----|-------------|
| Generate answers | **Each LLM** |
| Measure speed (latency) | **Your Python code** (`time.perf_counter`) |
| Count tokens | **API response** (`response.usage`) |
| Estimate cost | **Your Python code** (tokens × $/1M rates) |
| Decide which answer is “better” | **You** (read both answers) |

---

## Requirements

- Python 3.10+ recommended
- [OpenAI API key](https://platform.openai.com/api-keys)
- Red Hat Granite access through an **OpenAI-compatible** endpoint + API key

---

## How to create an OpenAI API key

OpenAI gives you the first LLM in this comparison.

1. Open [https://platform.openai.com/](https://platform.openai.com/) and **sign up / log in**.  
   (This is the **API platform**, not the regular ChatGPT chat website.)
2. Complete email / phone verification if asked.
3. Create or select a **project** (Default project is fine for learning).
4. Go to **API keys**: [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
5. Click **Create new secret key**.
6. Give it a name like `llm-model-evaluation`.
7. Click create, then **copy the key immediately** (OpenAI shows it only once).  
   It usually starts with `sk-` or `sk-proj-`.
8. Add billing / credits under **Settings → Billing** if your account requires it (API usage is paid; set a low monthly limit while learning).

Put it in your `.env` file:

```env
OPENAI_API_KEY=sk-your-key-here
MODEL_NAME=gpt-4.1-nano
```

`MODEL_NAME` is which OpenAI model the app calls.  
The script also accepts `OPENAI_MODEL` if you prefer that name.

**Safety tips**

- Never commit `.env` to GitHub.
- Never paste your key in public chats, screenshots, or README.
- If a key leaks, revoke it on the API keys page and create a new one.

Official page: [OpenAI API keys](https://platform.openai.com/api-keys)

---

## How to configure Red Hat Granite

Granite is called with the **same OpenAI Python SDK**, but pointed at a different URL.

Your provider gives you:

1. an API key  
2. a base URL (often ends with `/v1`)  
3. a model id string  

Put them in `.env`:

```env
REDHAT_GRANITE_API_KEY=your-granite-key-here
REDHAT_GRANITE_BASE_URL=https://your-granite-endpoint/v1
REDHAT_GRANITE_MODEL=your-granite-model-id
```

This is a common enterprise pattern: **OpenAI-compatible APIs**.  
You keep the same Python code style (`chat.completions.create`), and only change the server URL + key + model name.

---

## Setup

```bash
git clone https://github.com/souvikdas2613/LLM_Model_Evaluation.git
cd LLM_Model_Evaluation

python -m venv .venv
# Linux / macOS:
source .venv/bin/activate
# Windows:
# .venv\Scripts\activate

pip install -r requirements.txt
cp .env.example .env
```

**Where to keep `.env`**

Keep `.env` in the **project root** — the same folder as `LLM_Model_Evaluation.py`, `requirements.txt`, and `.env.example`.

```text
LLM_Model_Evaluation/
├── LLM_Model_Evaluation.py
├── requirements.txt
├── .env.example      ← safe template (committed)
├── .env              ← your real keys (local only, never commit)
└── README.md
```

Then run the script from that same folder so it can find `.env`.

Edit `.env`:

```env
OPENAI_API_KEY=sk-your-openai-key-here
MODEL_NAME=gpt-4.1-nano

REDHAT_GRANITE_API_KEY=your-granite-key-here
REDHAT_GRANITE_BASE_URL=https://your-granite-endpoint/v1
REDHAT_GRANITE_MODEL=your-granite-model-id
```

---

## Run

```bash
python LLM_Model_Evaluation.py
```

Expected flow:

```text
RUNNING MAIN FUNCTION .....

LOADING OPENAI API KEY and MODEL .....
OPENAI MODEL: gpt-4.1-nano

LOADING RED HAT GRANITE API KEY , URL and MODEL.....
RED HAT GRANITE BASE URL: ...
RED HAT GRANITE MODEL: ...

CREATING OPENAI CLIENT .....
CREATING RED HAT GRANITE CLIENT .....

DISPLAYING RESULTS .....

================================================================================
                 ANSWERS FROM BOTH LLMs
================================================================================

--------------------------------------------------------------------------------
QUESTION 1: What is an embedding?
--------------------------------------------------------------------------------

========== OPENAI ==========
...answer text...

========== GRANITE ==========
...answer text...

--------------------------------------------------------------------------------
QUESTION 2: What is RAG?
--------------------------------------------------------------------------------
...

--------------------------------------------------------------------------------
QUESTION 3: What is a vector database?
--------------------------------------------------------------------------------
...

================================================================================
                 LATENCY TABLE
================================================================================
Question                                                 OpenAI      Granite
--------------------------------------------------------------------------------
What is an embedding?                                      4.07s       11.60s
What is RAG?                                               2.54s        8.15s
What is a vector database?                                 3.08s       12.32s
================================================================================

====================================================================================================
                 TOKENS / COST TABLE
====================================================================================================
Question                        OPEN_AI_TOKENS  OPEN_AI_COST($)   GRANITE_TOKENS  GRANITE_COST($)
----------------------------------------------------------------------------------------------------
What is an embedding?                      204       $0.000078              258       $0.000013
What is RAG?                               154       $0.000058              186       $0.000009
What is a vector database?                 291       $0.000112              272       $0.000014
----------------------------------------------------------------------------------------------------
TOTAL                                      649       $0.000248              716       $0.000036
====================================================================================================
Note: costs are approximate estimates from the $/1M rates set in the script.

MAIN FUNCTION COMPLETED .....
```

---

## Project files

| File | Purpose |
|------|---------|
| `LLM_Model_Evaluation.py` | Full comparison script |
| `requirements.txt` | Python dependencies |
| `.env.example` | Safe template for keys |
| `.env` | Your real keys (**never commit**) |
| `.gitignore` | Keeps secrets / junk out of git |
| `LICENSE` | Apache 2.0 |
| `README.md` | This guide |

---

## Notes

- Latency depends on network, region, model size, and provider load. Use it for **relative** comparison.
- Granite is often slower than a small OpenAI model — that is normal.
- Token counts come from `response.usage` (object attributes like `usage.prompt_tokens`). If a provider does not return usage, tokens show as `0`.
- Cost formula: `(prompt_tokens / 1000000) * input_rate + (completion_tokens / 1000000) * output_rate`.
- Default rates in the script: OpenAI GPT-4.1-nano `$0.10` / `$0.40` per 1M; Granite `granite-4-0-h-tiny` `$0.05` / `$0.05` per 1M. Update if pricing changes. If both rates for a model are `0.0`, that model’s cost shows as `n/a`.
- Each request has a **45 second timeout** so a bad endpoint does not hang forever.
- Keep `.env` in the project root, private. Only commit `.env.example`.
- The script may look quiet while waiting for APIs (no per-call progress prints by design).
- Run the script from the project folder so `.env` is found.

---

## Code walkthrough (beginner-friendly)

This section is written for someone learning AI for the first time.  
You do **not** need to know advanced Python. Read it like a story of how the script thinks.

### Words you will see a lot

| Word | Simple meaning |
|------|----------------|
| **API** | A website / service that answers computer requests. Your code asks OpenAI or Granite, they reply with text. |
| **API key** | Like a password that proves “this request is allowed.” Kept secret in `.env`. |
| **LLM** | Large Language Model (like ChatGPT / Granite). It reads text and writes text back. |
| **Client** | A Python object that knows how to talk to an API. |
| **Prompt** | The text you send to the LLM (here: just the question). |
| **Latency** | How long one API call took, in seconds. |
| **Tokens** | How much text the model processed / generated (rough size units). |
| **Cost estimate** | Rough USD price from tokens × your `$ / 1M` rates. |
| **Timeout** | Max wait time. If the API is too slow, fail instead of hanging forever. |
| **f-string** | A string with `{...}` placeholders, like `f"Hello {name}"`. |
| **enumerate** | Loop helper that gives `(index, item)` together. |
| **Function** | A small named block of code that does one job. |
| **OpenAI-compatible** | Same request style as OpenAI (`chat.completions`), different server URL. |

### The most important idea in this project

```text
Same 3 questions
     |
     +-- OpenAI answers
     +-- Granite answers
     |
     v
Print ALL answers first
     |
     v
Print latency table
     |
     v
Print tokens / cost table
```

We do **not** train a model here.  
We **do** compare two models fairly on the same prompts.

---

### Big picture: the pipeline

```text
1. load_dotenv                 -> read secrets from .env
2. read OPENAI / GRANITE vars  -> print model + URL
3. set $/1M price constants    -> OpenAI + Granite rates
4. validate config             -> stop early if something missing
5. create openai_client        -> talk to OpenAI (timeout=45s)
6. create granite_client       -> talk to Granite (custom base_url)
7. main() loop                 -> ask both models for each question
8. display_results()           -> answers, then latency, then tokens/cost
```

Think of it like a taste test:

- same questions for both chefs (models)
- stopwatch for each dish (latency)
- receipt for ingredients used (tokens / cost)
- you taste both answers (human judgment)
- scoreboard tables come after the answers

---

### 1) Imports

```python
import os
import time

from dotenv import load_dotenv
from openai import OpenAI
```

**What it does:** Brings in the tools this script needs.

| Import | Why |
|--------|-----|
| `os` | Read environment variables (`os.getenv`) |
| `time` | Measure latency with `time.perf_counter` |
| `load_dotenv` | Load `.env` into the environment |
| `OpenAI` | Official OpenAI Python client class |

**Why these imports?**  
Without them, the script cannot read secrets, talk to APIs, or time the calls.

**Input:** none  
**Output:** none — only imports

This is not AI yet. It is just setup.

---

### 2) `load_dotenv(override=True)`

**What it does:** Reads your secret values from a `.env` file.

**Why `.env`?**  
API keys should never be typed into code (and never uploaded to GitHub).  
`.env` is a private file on your computer. The script loads it at start.

**Where to put it:** in the project root (same folder as this script).  
Copy `.env.example` → `.env`, then fill in your keys. Do not commit `.env`.

`override=True` means values from `.env` can replace older environment values if they already exist.

**Input:** none  
**Output:** environment variables filled in memory

---

### 3) OpenAI configuration

```python
print("\nLOADING OPENAI API KEY and MODEL .....")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL") or os.getenv("MODEL_NAME")

print("\nOPENAI MODEL:", OPENAI_MODEL)
```

**What it does:** Loads OpenAI key + model name, and prints the model.

| Variable | Meaning |
|----------|---------|
| `OPENAI_API_KEY` | Your OpenAI secret key |
| `OPENAI_MODEL` | Which OpenAI model to call |

**Why `MODEL_NAME` fallback?**

Your `.env` may use either name:

```env
MODEL_NAME=gpt-4.1-nano
```

or `OPENAI_MODEL`.

So this line accepts either:

```python
os.getenv("OPENAI_MODEL") or os.getenv("MODEL_NAME")
```

If the first is missing / `None`, use the second.

**Why print the model?**  
So you can confirm the script loaded the value you expected before any API call starts.

**Input:** environment variables  
**Output:** Python variables + print lines

---

### 4) Granite configuration

```python
print("\nLOADING RED HAT GRANITE API KEY , URL and MODEL.....")

GRANITE_API_KEY = os.getenv("REDHAT_GRANITE_API_KEY")
GRANITE_BASE_URL = os.getenv("REDHAT_GRANITE_BASE_URL")
GRANITE_MODEL = os.getenv("REDHAT_GRANITE_MODEL")

print("\nRED HAT GRANITE BASE URL:", GRANITE_BASE_URL)
print("\nRED HAT GRANITE MODEL:", GRANITE_MODEL)
```

**What it does:** Loads Granite settings and prints URL + model.

| `.env` name | Python variable | Meaning |
|-------------|-----------------|---------|
| `REDHAT_GRANITE_API_KEY` | `GRANITE_API_KEY` | Auth for Granite gateway |
| `REDHAT_GRANITE_BASE_URL` | `GRANITE_BASE_URL` | Server URL (often ends with `/v1`) |
| `REDHAT_GRANITE_MODEL` | `GRANITE_MODEL` | Model id the gateway expects |

**Why print URL + model?**  
Most Granite mistakes are wrong URL or wrong model id. Printing them early makes debugging easier.

**Input:** environment variables  
**Output:** Python variables + print lines

---

### 5) Validate configuration

```python
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
```

**What it does:** Checks that the important values are not empty.

**Why this matters:** Better to stop early with a clear message than crash later with a confusing API error.

`raise ValueError(...)` means: crash on purpose with this explanation.

**Input:** config variables  
**Output:** continue, or stop with an error

---

### 6) Create clients

```python
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
```

**What it does:** Builds two API clients.

| Client | Difference |
|--------|------------|
| `openai_client` | Default OpenAI servers |
| `granite_client` | Same SDK + custom `base_url` |

**Why timeout?**  
`timeout=45` means: if a call takes longer than 45 seconds, fail instead of hanging forever.  
This keeps the learning script usable when a remote endpoint is slow or stuck.

**Input:** keys / URL / timeout  
**Output:** two client objects

---

### 7) Approximate prices + token / cost helpers

#### 7A) Price constants (near the top of the script)

```python
# GPT-4.1-nano (OpenAI API pricing)
OPENAI_INPUT_PRICE_PER_1M = 0.10
OPENAI_OUTPUT_PRICE_PER_1M = 0.40

# granite-4-0-h-tiny subscription pricing
GRANITE_INPUT_PRICE_PER_1M = 0.05
GRANITE_OUTPUT_PRICE_PER_1M = 0.05
```

**What it does:** Stores USD prices per **1 million tokens**.

Remember: **1M = 1,000,000 = `1000000`** in the code.

| Constant | Meaning | Current value |
|----------|---------|---------------|
| `OPENAI_INPUT_PRICE_PER_1M` | OpenAI input (prompt) price | `$0.10` per 1M tokens |
| `OPENAI_OUTPUT_PRICE_PER_1M` | OpenAI output (answer) price | `$0.40` per 1M tokens |
| `GRANITE_INPUT_PRICE_PER_1M` | Granite input price | `$0.05` per 1M tokens |
| `GRANITE_OUTPUT_PRICE_PER_1M` | Granite output price | `$0.05` per 1M tokens |

OpenAI model pricing used here:

| Model | Input / 1M tokens | Output / 1M tokens |
|-------|-------------------|--------------------|
| GPT-4.1-nano | `$0.10` | `$0.40` |

Granite subscription card used here:

| Field | Value |
|-------|-------|
| Model | `granite-4-0-h-tiny` |
| Status | Active |
| Pricing | Input `$0.05/1M` • Output `$0.05/1M` |
| Context length | 4,000,000 tokens |

**Why approximate?**  
Provider prices can change. Update these constants if your billing page changes.  
If both rates for a model are `0.0`, that model’s cost prints as `n/a`.

**Input:** none (hardcoded learning defaults)  
**Output:** four price numbers used later by `estimate_cost_usd`

---

#### 7B) `get_usage(response)`

```python
def get_usage(response):

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
```

**What it does:** Reads token counts from the API response.

**Important:** the OpenAI SDK response is an **object**, not a normal dictionary.  
So we use:

```python
response.usage
usage.prompt_tokens
```

not:

```python
response["usage"]["prompt_tokens"]
```

| Field | Meaning |
|-------|---------|
| `prompt_tokens` | tokens in your question (input) |
| `completion_tokens` | tokens in the model answer (output) |
| `total_tokens` | prompt + completion |

**Why try/except?**  
If `usage` is missing, return zeros instead of crashing.

**Input:** API `response` object  
**Output:** dictionary `{prompt_tokens, completion_tokens, total_tokens}`

---

#### 7C) `estimate_cost_usd(...)`

```python
def estimate_cost_usd(prompt_tokens, completion_tokens, input_per_1m, output_per_1m):

    if input_per_1m <= 0 and output_per_1m <= 0:
        return None

    cost = (
        (prompt_tokens / 1000000) * input_per_1m
        + (completion_tokens / 1000000) * output_per_1m
    )
    return round(cost, 6)
```

**What it does:** Turns token counts into an approximate USD cost.

**Formula:**

```text
cost =
  (prompt_tokens / 1000000) * input_price_per_1M
+ (completion_tokens / 1000000) * output_price_per_1M
```

`1000000` means one million. Prices are listed as **$ per 1 million tokens**, so we divide token count by one million first.

**Worked example (Granite):**

```text
prompt_tokens = 20
completion_tokens = 460
input_price = 0.05
output_price = 0.05

input cost  = (20  / 1000000) * 0.05 = 0.000001
output cost = (460 / 1000000) * 0.05 = 0.000023
total cost  = 0.000024   → printed as $0.000024
```

**Worked example (OpenAI):**

```text
prompt_tokens = 12
completion_tokens = 300
input_price = 0.10
output_price = 0.40

input cost  = (12  / 1000000) * 0.10 = 0.0000012
output cost = (300 / 1000000) * 0.40 = 0.0001200
total cost  = 0.0001212  → rounded to 0.000121
```

**Input:** token counts + `$ / 1M` rates  
**Output:** float cost, or `None` if both rates are `0` / negative

---

#### 7D) `format_cost(cost)`

```python
def format_cost(cost):

    if cost is None:
        return "n/a".rjust(10)
    return f"${cost:.6f}"
```

**What it does:** Makes the cost look nice in the table.

| Value | Printed as |
|-------|------------|
| `0.000024` | `$0.000024` |
| `None` | `n/a` |

**Input:** cost number or `None`  
**Output:** printable string for the tokens/cost table

---

### 8) `ask_openai(question)`  ← OpenAI AI step

**What it does:** Sends one question to OpenAI, measures time, reads tokens, estimates cost, returns all of that (+ error if failed).

```python
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
```

#### What goes into the LLM

One **user message** with the question text.  
(No system message in this simple version.)

#### How the call looks (conceptually)

```text
Your app  --question-->  OpenAI model
Your app  <--answer----  text reply
Your app also reads:     response.usage (tokens)
Your app also computes:  latency + estimated cost
```

#### Important lines

| Piece | Meaning |
|-------|---------|
| `time.perf_counter()` | Start / stop a precise stopwatch |
| `chat.completions.create(...)` | Send a chat request |
| `messages=[{"role":"user","content":question}]` | The prompt |
| `response.choices[0].message.content` | The text answer |
| `get_usage(response)` | Read `response.usage` token counts (object attributes, not dict keys) |
| `estimate_cost_usd(...)` | `(tokens / 1000000) * price_per_1M` for input + output |
| `try/except` | Catch API failures instead of crashing the whole script |
| `round(latency, 3)` | Keep 3 decimals (example `1.234`) |

**Why try/except?**  
If OpenAI fails (timeout, bad key, network), Granite can still be tested for that same question.  
The script stores the error string and continues.

**Input:** question string  
**Output:** dictionary

```text
{
  "model": "gpt-4.1-nano",
  "answer": "...",
  "latency": 1.234,
  "error": None,
  "prompt_tokens": 12,
  "completion_tokens": 300,
  "total_tokens": 312,
  "cost_usd": 0.000086
}
```

---

### 9) `ask_granite(question)`  ← Granite AI step

**What it does:** Same job as `ask_openai`, but uses `granite_client`, `GRANITE_MODEL`, and Granite price rates.

**Why a separate function?**  
So beginners can clearly see:

```text
ask_openai  -> openai_client  + OPENAI_MODEL  + OpenAI rates
ask_granite -> granite_client + GRANITE_MODEL + Granite rates
```

Same stopwatch idea. Same return shape. Different endpoint / pricing.

**Input:** question string  
**Output:** dictionary `{model, answer, latency, error, prompt_tokens, completion_tokens, total_tokens, cost_usd}`

---

### 10) `main()` — ask both models for every question

```python
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
                "openai_cost_usd": openai_result["cost_usd"],
                "granite_cost_usd": granite_result["cost_usd"],
                # (+ prompt/completion token fields also saved)
            }
        )

    print("\nDISPLAYING RESULTS .....")
    display_results(results)
```

**What it does:** Runs the full evaluation for 3 questions.

For each question:

1. Call OpenAI  
2. Call Granite  
3. Save one result dictionary  

**Why save every key?**  
`display_results()` later reads latency, errors, answers, tokens, and costs.  
If you remove a key here, display will crash with `KeyError`.

**Input:** none  
**Output:** calls `display_results(results)`

---

### 11) `display_results(results)` — answers, then latency, then tokens/cost

**What it does:** Prints the final report in this exact order:

1. **All answers from both LLMs** (every question)  
2. **Latency table**  
3. **Tokens / cost table** (plus TOTAL row)

**Why this order?**  
Read the answers first, then speed, then efficiency (tokens / money).

**Input:** `results` list from `main()`  
**Output:** printed report only (no file saved in this version)

---

#### 11A) Print all answers (uses `enumerate`)

```python
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
```

**What it does:** Loops through every result and prints both answers.

**Why `enumerate`?**  
It gives you both:

1. a counter (`index`) → `QUESTION 1`, `QUESTION 2`, `QUESTION 3`  
2. the item (`result`) → the dictionary with answers

`start=1` means numbering starts at 1, not 0.

Alternatives (same idea):

```python
# manual counter
index = 1
for result in results:
    print(f"QUESTION {index}: ...")
    index += 1

# no numbers
for result in results:
    print(f"QUESTION: {result['question']}")
```

`enumerate` is the usual clean Python way when you need numbers.

**Note about IDE `enumerate[Any]`:**  
If your editor shows `enumerate[Any]`, that is only a type-hint display from Pylance.  
Your real code is still plain `enumerate(results, start=1)`. You do not type `Any`.

**Input:** one `result` dictionary per loop  
**Output:** printed OpenAI + Granite answers (or ERROR text)

---

#### 11B) Latency table header (f-string alignment)

```python
print(f"{'Question':<50} {'OpenAI':>12} {'Granite':>12}")
```

**What it does:** Prints the table header with fixed column widths.

| Piece | Meaning |
|-------|---------|
| `f"..."` | f-string |
| `'Question':<50` | left-align the word `Question` inside 50 spaces |
| `'OpenAI':>12` | right-align the word `OpenAI` inside 12 spaces |
| `'Granite':>12` | right-align the word `Granite` inside 12 spaces |

```text
<  = left align
>  = right align
50 / 12 = column width
```

Looks roughly like:

```text
Question                                           OpenAI      Granite
|----------- about 50 chars ---------| |--12--| |--12--|
```

**Why fixed widths?**  
So every row lines up like a real table, not messy free text.

**Input:** none  
**Output:** one printed header line

---

#### 11C) Latency table rows

```python
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
```

**What it does:** Builds one latency table row per question.

OpenAI cell (`oai`):

| Piece | Meaning |
|-------|---------|
| `if not result["openai_error"]` | Call succeeded (`error` is `None`) |
| `:>10.2f` | number, right-aligned, width 10, 2 decimals |
| `s` | add seconds label → looks like `      4.07s` |
| `"ERROR".rjust(12)` | if failed, show `ERROR` padded to width 12 |

Same idea for Granite → `gran`.

Example successful row:

```text
What is an embedding?                                      4.07s       11.60s
```

**Why show ERROR in the table?**  
So you can still compare the other model, and clearly see which call failed.

**Input:** each `result` dictionary  
**Output:** one printed latency row

---

#### 11D) Tokens / cost table

```python
print(
    f"{'Question':<30} "
    f"{'OPEN_AI_TOKENS':>16} {'OPEN_AI_COST($)':>16} "
    f"{'GRANITE_TOKENS':>16} {'GRANITE_COST($)':>16}"
)
```

**What it does:** Prints a second scoreboard for efficiency.

For each question it shows:

| Column | Meaning |
|--------|---------|
| `OPEN_AI_TOKENS` | OpenAI `total_tokens` |
| `OPEN_AI_COST($)` | OpenAI estimated USD cost from `estimate_cost_usd` |
| `GRANITE_TOKENS` | Granite `total_tokens` |
| `GRANITE_COST($)` | Granite estimated USD cost (`n/a` only if both rates are `0.0`) |

It also keeps running totals and prints a final `TOTAL` row.

How each `$` cell is made:

1. `get_usage(response)` → prompt + completion tokens  
2. `estimate_cost_usd(...)` → USD number  
3. `format_cost(...)` → `$0.000024` (or `n/a` / `ERROR`)

**Why a separate table?**  
Latency answers “who was faster?”  
Tokens / cost answers “who used more text / money?”

**Input:** each `result` dictionary  
**Output:** one printed tokens/cost row (+ TOTAL at the end)

---

### 12) Script entry point

```python
if __name__ == "__main__":
    print("\nRUNNING MAIN FUNCTION .....")
    main()
    print("\nMAIN FUNCTION COMPLETED .....")
```

**What it does:** Starts the program when you run:

```bash
python LLM_Model_Evaluation.py
```

**Why `if __name__ == "__main__":`?**  
It means: only auto-run when this file is executed directly  
(not when imported by another file).

**Input:** none  
**Output:** runs `main()`, then prints completion

---

### End-to-end example (one mental run)

```text
You run: python LLM_Model_Evaluation.py
   |
   v
Load .env -> print model/url -> create clients
   |
   v
Ask Q1 to OpenAI + Granite
Ask Q2 to OpenAI + Granite
Ask Q3 to OpenAI + Granite
   |
   v
Print ALL answers (both models, all 3 questions)
   |
   v
Print latency table
   |
   v
Print tokens / cost table (+ TOTAL)
   |
   v
MAIN FUNCTION COMPLETED
```

If you remember only one sentence from this README:

> **Same questions, two models — compare answers, latency, tokens, and approximate cost.**

---

## Example terminal output shape

```text
================================================================================
                 ANSWERS FROM BOTH LLMs
================================================================================

QUESTION 1: What is an embedding?
========== OPENAI ==========
An embedding is a numerical vector representation of text...
========== GRANITE ==========
Embeddings map words or documents into a dense vector space...

QUESTION 2: What is RAG?
...

QUESTION 3: What is a vector database?
...

================================================================================
                 LATENCY TABLE
================================================================================
Question                                                 OpenAI      Granite
--------------------------------------------------------------------------------
What is an embedding?                                      4.07s       11.60s
What is RAG?                                               2.54s        8.15s
What is a vector database?                                 3.08s       12.32s
================================================================================

====================================================================================================
                 TOKENS / COST TABLE
====================================================================================================
Question                        OPEN_AI_TOKENS  OPEN_AI_COST($)   GRANITE_TOKENS  GRANITE_COST($)
----------------------------------------------------------------------------------------------------
What is an embedding?                      204       $0.000078              258       $0.000013
What is RAG?                               154       $0.000058              186       $0.000009
What is a vector database?                 291       $0.000112              272       $0.000014
----------------------------------------------------------------------------------------------------
TOTAL                                      649       $0.000248              716       $0.000036
====================================================================================================
Note: costs are approximate estimates from the $/1M rates set in the script.
```

---

### What this evaluates (honest scope)

| Metric | Included? | How |
|--------|-----------|-----|
| Full answers (all 3 questions) | Yes | Printed for both models |
| Latency | Yes | Stopwatch around each API call |
| Token usage | Yes | From `response.usage` |
| Approximate cost | Yes | `(tokens / 1000000) * $/1M rates` in the script |
| Automatic quality score | Not yet | Future upgrade (judge LLM / rubric) |

---

### Possible next upgrades

- Save answers + tables to `results.md`  
- Add a third model (local Ollama)  
- Add a simple scoring rubric or judge-LLM  
- Add a small Gradio UI  

---

## Author

**Souvik Das**  
GitHub: [souvikdas2613](https://github.com/souvikdas2613)  
Repo: [LLM_Model_Evaluation](https://github.com/souvikdas2613/LLM_Model_Evaluation)

---

## License

Apache License 2.0 — see [`LICENSE`](./LICENSE).
