# AI Session Transcript — Building Naive Ticket Service

- **Session Goal:** Build naive FastAPI ticket-selling service with demonstrable race condition and corresponding load-testing client.
- **Conversation ID:** `a9f06c47-6b63-4bcd-8aec-688f348c7249`
- **Raw JSONL Log:** [building_naive_ticket_service_transcript.jsonl](./building_naive_ticket_service_transcript.jsonl)

---

### 👤 USER (2026-09-02T16:31:17Z)

```text
<USER_REQUEST>
📌 Sentry Memory Context
──────────────────────
[IMPORTANT INSTRUCTION]: This is a saved context block from a previous session. Do NOT begin solving, generating, or proposing the next steps yet. Output a brief, one-sentence acknowledgment confirming you have absorbed this background context, and explicitly state that you are ready for the user to provide their next input.
──────────────────────
The following is the saved context from a previous AI conversation. Use this as your complete background reference and continue naturally from where we left off — no need to re-explain anything already established.

Goal: Build both a buggy naive FastAPI ticket-selling service and its corresponding load-testing client to demonstrate concurrency race conditions before implementing a thread-safe Redis/Postgres backend.
Background: The user is working on Problem 1 (Ticket Stampede) from a take-home assessment for Thuli Studio, executing the workflow step-by-step in separate AI chat sessions.
Constraints:
- Python FastAPI backend
- Must support /reset, /buy, and /status endpoints
- Must verify 4 invariants: no overselling, no duplicate ticket numbers, idempotent request IDs, and accurate status counts
- Include a README and session logs
- Deliver prompts in incremental pieces
Key Decisions:
- Choosing to build the naive, intentionally flawed in-memory version first to demonstrate race conditions
- Structuring the project with dedicated /seller, /buyer, and /logs folders
- Delivering prompts incrementally rather than all at once
Where we left off: Supplying the first granular prompt to build the naive FastAPI seller in seller/main.py with an intentional race condition and no locking mechanisms.
Continue from: Instruct the user to run Prompt 1 in their secondary chat, wait for the naive FastAPI code generation, and then request the load-testing client prompt.
──────────────────────


this is the content of claude chat
</USER_REQUEST>
<ADDITIONAL_METADATA>
The current local time is: 2026-09-02T22:01:17+05:30.

The user's current state is as follows:
Active Document: /Users/prachikiledar/thuli/ticket-stampede/main.py (LANGUAGE_PYTHON)
Cursor is on line: 1
Other open documents:
- /Users/prachikiledar/thuli/ticket-stampede/main.py (LANGUAGE_PYTHON)
</ADDITIONAL_METADATA>
<USER_SETTINGS_CHANGE>
The user changed setting `Model Selection` from None to Gemini 3.7 Flash (Medium). No need to comment on this change if the user doesn't ask about it. If reporting what model you are, please use a human readable name instead of the exact string.
</USER_SETTINGS_CHANGE>
```

---

### 🤖 AI ASSISTANT (2026-09-02T16:31:17Z)

I have absorbed the background context regarding the Ticket Stampede service and the incremental workflow, and I am ready for your next input.

---

### 👤 USER (2026-09-02T16:33:07Z)

```text
<USER_REQUEST>
Create a Python FastAPI project for a ticket-selling service called "Ticket Stampede".

Project structure:
- /seller — the FastAPI service
- /buyer — will hold the load-testing client (empty for now)
- /logs — will hold AI session logs (empty for now)
- README.md
- requirements.txt

Build a NAIVE (intentionally flawed) version of the seller service first. I want this version to have a real, demonstrable race condition — this is intentional, I will fix it in a later step.

Requirements for the seller service (seller/main.py):

1. POST /reset
   - Takes a ticket count (e.g. {"total_tickets": 100})
   - Wipes all existing state and starts a fresh sale

2. POST /buy
   - Takes a user_id and a request_id in the body
   - If tickets remain, assign the next ticket number to this user and return it
   - If sold out, return a clear "sold out" response (e.g. 409 status with a message)
   - For this naive version, do NOT worry about race conditions or duplicate request_id handling yet — implement it in the most straightforward, naive way (e.g. read current count, check if less than total, then increment) so that under concurrent load it CAN oversell or skip idempotency. Add a code comment explaining exactly why this is unsafe under concurrency.

3. GET /status
   - Returns the number of tickets sold and a full list of which user_id holds which ticket number

Use in-memory Python data structures (a plain dict/list, no locks, no database) for this naive version — this is meant to break under load.

Also write a minimal README.md explaining how to install dependencies and run the service with uvicorn.

After generating the code, briefly explain in plain language exactly where and why this implementation is unsafe under concurrent requests.
</USER_REQUEST>
<ADDITIONAL_METADATA>
The current local time is: 2026-09-02T22:03:07+05:30.

The user's current state is as follows:
Active Document: /Users/prachikiledar/thuli/ticket-stampede/main.py (LANGUAGE_PYTHON)
Cursor is on line: 1
Other open documents:
- /Users/prachikiledar/thuli/ticket-stampede/main.py (LANGUAGE_PYTHON)
</ADDITIONAL_METADATA>
```

---

### 👤 USER (2026-09-02T16:33:37Z)

```text
<USER_REQUEST>
Create a Python FastAPI project for a ticket-selling service called "Ticket Stampede".

Project structure:
- /seller — the FastAPI service
- /buyer — will hold the load-testing client (empty for now)
- /logs — will hold AI session logs (empty for now)
- README.md
- requirements.txt

Build a NAIVE (intentionally flawed) version of the seller service first. I want this version to have a real, demonstrable race condition — this is intentional, I will fix it in a later step.

Requirements for the seller service (seller/main.py):

1. POST /reset
   - Takes a ticket count (e.g. {"total_tickets": 100})
   - Wipes all existing state and starts a fresh sale

2. POST /buy
   - Takes a user_id and a request_id in the body
   - If tickets remain, assign the next ticket number to this user and return it
   - If sold out, return a clear "sold out" response (e.g. 409 status with a message)
   - For this naive version, do NOT worry about race conditions or duplicate request_id handling yet — implement it in the most straightforward, naive way (e.g. read current count, check if less than total, then increment) so that under concurrent load it CAN oversell or skip idempotency. Add a code comment explaining exactly why this is unsafe under concurrency.

3. GET /status
   - Returns the number of tickets sold and a full list of which user_id holds which ticket number

Use in-memory Python data structures (a plain dict/list, no locks, no database) for this naive version — this is meant to break under load.

Also write a minimal README.md explaining how to install dependencies and run the service with uvicorn.

After generating the code, briefly explain in plain language exactly where and why this implementation is unsafe under concurrent requests.
</USER_REQUEST>
<ADDITIONAL_METADATA>
The current local time is: 2026-09-02T22:03:37+05:30.

The user's current state is as follows:
Active Document: /Users/prachikiledar/thuli/ticket-stampede/main.py (LANGUAGE_PYTHON)
Cursor is on line: 1
Other open documents:
- /Users/prachikiledar/thuli/ticket-stampede/main.py (LANGUAGE_PYTHON)
</ADDITIONAL_METADATA>
<USER_SETTINGS_CHANGE>
The user changed setting `Model Selection` from None to Gemini 3.7 Flash (Medium). No need to comment on this change if the user doesn't ask about it. If reporting what model you are, please use a human readable name instead of the exact string.
</USER_SETTINGS_CHANGE>
```

---

### 🤖 AI ASSISTANT (2026-09-02T16:35:37Z)

The Python FastAPI project for **Ticket Stampede** is created.

### Project Structure

```text
ticket-stampede/
├── seller/
│   ├── __init__.py
│   └── [main.py](file:///Users/prachikiledar/thuli/ticket-stampede/seller/main.py)       # Naive FastAPI seller service
├── buyer/
│   └── [.gitkeep](file:///Users/prachikiledar/thuli/ticket-stampede/buyer/.gitkeep)      # Placeholder for load-testing client
├── logs/
│   └── [.gitkeep](file:///Users/prachikiledar/thuli/ticket-stampede/logs/.gitkeep)       # Placeholder for AI session logs
├── [README.md](file:///Users/prachikiledar/thuli/ticket-stampede/README.md)             # Setup & usage instructions
└── [requirements.txt](file:///Users/prachikiledar/thuli/ticket-stampede/requirements.txt) # Project dependencies
```

---

### How to Run

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
2. **Start the service**:
   ```bash
   uvicorn seller.main:app --reload --host 0.0.0.0 --port 8000
   ```
3. **Interactive Swagger Docs**:
   Visit `http://localhost:8000/docs` in your browser.

---

### Why and Where This Implementation is Unsafe Under Concurrent Requests

The concurrency vulnerability is located in [seller/main.py](file:///Users/prachikiledar/thuli/ticket-stampede/seller/main.py#L70-L140) inside the `POST /buy` endpoint:

```python
# 1. READ current count
current_sold = state["tickets_sold"]
total = state["total_tickets"]

# 2. CHECK if tickets remain
if current_sold >= total:
    raise HTTPException(status_code=409, detail="Sold out!...")

# Simulated I/O latency / Event Loop Yield
await asyncio.sleep(0)

# 3. WRITE: increment and assign
ticket_number = current_sold + 1
state["tickets_sold"] = current_sold + 1
state["assignments"].append(...)
```

#### 1. Check-Then-Act Race Condition (Time-of-Check to Time-of-Use / TOCTOU)
- **The Gap**: The logic splits the transaction into three non-atomic steps: *Read*, *Check*, and *Write*.
- **The Interleaving**: Suppose only **1 ticket remains** (`tickets_sold = 99`, `total_tickets = 100`) and two concurrent requests ($A$ and $B$) arrive at nearly the same instant:
  1. Request $A$ reads `current_sold = 99`.
  2. Request $B$ also reads `current_sold = 99`.
  3. Both check `99 < 100` $\rightarrow$ both pass the validation check.
  4. Both proceed to assign `ticket_number = 99 + 1 = 100` and increment the counter.
- **Outcome**: Ticket #100 is assigned twice, or `tickets_sold` climbs to `101`, causing the service to **oversell beyond the inventory limit**.

#### 2. Event Loop Context Switching
In an asynchronous server, any I/O operation (database query, network call, or `await asyncio.sleep(0)`) yields control back to the event loop. Without a mutex lock (`asyncio.Lock`) or an atomic database transaction/compare-and-swap, another request will run during this window and operate on stale state.

#### 3. Lack of Idempotency Protection
While `request_id` is recorded, it is never validated before attempting to purchase. If a buyer's network glitches and their client retries with the same `request_id`, the naive service will charge/assign them multiple tickets instead of returning the already-created ticket.

---

### 👤 USER (2026-09-02T16:40:16Z)

```text
<USER_REQUEST>
Now, let's start Part B: The Buyer.

Create a simple asynchronous load-testing script in `buyer/main.py` using `httpx` (or `aiohttp`) and `asyncio`.

Requirements:
1. It should accept command-line arguments:
   - `--base-url` (default: `http://localhost:8000`)
   - `--total-tickets` (default: 100)
   - `--concurrent-buyers` (default: 50)
   - `--total-requests` (default: 500)
   - `--duplicate-rate` (default: 0.1, i.e., 10% requests will reuse an already sent request_id to test idempotency)

2. Flow:
   - First, call `POST /reset` with `total_tickets`.
   - Then, fire `total_requests` concurrently across `concurrent-buyers` workers hitting `POST /buy`.
   - Each request sends a `user_id` and a `request_id`.
   - Collect and print the total HTTP status codes returned (how many 200 OK, 409 Conflict, errors).

3. Update `requirements.txt` with `httpx` and any other required libraries.

</USER_REQUEST>
<ADDITIONAL_METADATA>
The current local time is: 2026-09-02T22:10:16+05:30.

The user's current state is as follows:
Active Document: /Users/prachikiledar/thuli/ticket-stampede/buyer/.gitkeep (LANGUAGE_UNSPECIFIED)
Cursor is on line: 1
Other open documents:
- /Users/prachikiledar/thuli/ticket-stampede/buyer/.gitkeep (LANGUAGE_UNSPECIFIED)
- /Users/prachikiledar/thuli/ticket-stampede/requirements.txt (LANGUAGE_UNSPECIFIED)
- /Users/prachikiledar/thuli/ticket-stampede/README.md (LANGUAGE_MARKDOWN)
- /Users/prachikiledar/thuli/ticket-stampede/seller/main.py (LANGUAGE_PYTHON)
- /Users/prachikiledar/thuli/ticket-stampede/seller/__init__.py (LANGUAGE_PYTHON)
</ADDITIONAL_METADATA>
```

---

### 🤖 AI ASSISTANT (2026-09-02T16:41:54Z)

### Part B: Buyer Load-Testing Client Completed

We have created the asynchronous load-testing client in [buyer/main.py](file:///Users/prachikiledar/thuli/ticket-stampede/buyer/main.py) and updated [requirements.txt](file:///Users/prachikiledar/thuli/ticket-stampede/requirements.txt) & [README.md](file:///Users/prachikiledar/thuli/ticket-stampede/README.md).

---

### Key Features of `buyer/main.py`

1. **CLI Arguments via `argparse`**:
   - `--base-url` (default: `http://localhost:8000`)
   - `--total-tickets` (default: `100`)
   - `--concurrent-buyers` (default: `50`)
   - `--total-requests` (default: `500`)
   - `--duplicate-rate` (default: `0.1`, i.e., 10% reuses existing `(user_id, request_id)` pairs to test idempotency)

2. **Load-Testing Execution Flow**:
   - Sends `POST /reset` with `total_tickets` to prepare a clean state.
   - Generates the request pool with configured duplicate rates.
   - Dispatches requests concurrently bounded by `asyncio.Semaphore(concurrent_buyers)` using `httpx.AsyncClient`.
   - Aggregates HTTP status codes (`200 OK`, `409 Conflict`, errors) and measures execution time and throughput.
   - Queries `GET /status` post-run and highlights detected concurrency anomalies (overselling, duplicate ticket numbers).

---

### How to Run

1. **Start the Seller service** in terminal 1:
   ```bash
   uvicorn seller.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Run the Buyer load tester** in terminal 2:
   ```bash
   python3 -m buyer.main --total-tickets 50 --concurrent-buyers 50 --total-requests 300 --duplicate-rate 0.1
   ```

---

### Sample Output Under Load (Demonstrating Race Condition)

```text
======================================================================
 🎟️  TICKET STAMPEDE — LOAD TESTER
======================================================================
Target Base URL:     http://localhost:8000
Total Tickets:       50
Concurrent Buyers:   50
Total Requests:      300
Duplicate Rate:      10.0%
======================================================================

[1/3] Resetting seller state with 50 tickets...
✅ Seller service reset successfully. Response: {'message': 'Sale reset successfully.', 'total_tickets': 50, 'tickets_sold': 0}

[2/3] Firing 300 requests (29 intentional duplicates) across 50 concurrent workers...
✅ All 300 requests completed in 2.159s (138.9 req/s).

[3/3] Fetching final status from seller service...

======================================================================
 📊 LOAD TEST RESULTS SUMMARY
======================================================================
Total Requests Sent:       300
Elapsed Time:              2.159 seconds
Throughput:                138.93 req/s
----------------------------------------------------------------------
HTTP Status Code Breakdown:
  • 200 OK (Purchased)          :    84 ( 28.0%)
  • 409 Conflict (Sold Out)     :   216 ( 72.0%)
----------------------------------------------------------------------
Backend Status & Concurrency Anomaly Detection:
  • Configured Inventory:    50
  • Client Successful (200): 84
  • Backend `tickets_sold`:  50
  • Backend Assignments:     84

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
 CONCURRENCY RACE CONDITION MANIFESTED:
  🚨 DUPLICATE TICKET NUMBERS ISSUED! 25 ticket number(s) assigned to multiple users.
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
======================================================================
```

---

### 👤 USER (2026-09-02T16:41:26Z)

```text
<USER_REQUEST>
Now, update `buyer/main.py` to add comprehensive performance metrics and the 4 Invariant Verification checks required by the PDF.

### Requirements:

1. **Latency & Throughput Tracking:**
   - Measure individual request round-trip times (RTT in milliseconds).
   - Calculate and display:
     - Total duration and Requests Per Second (RPS / Throughput)
     - Response status code counts (200 OK, 409 Conflict, errors)
     - Latency percentiles: **Median (p50)**, **p90**, and **99th percentile (p99)**

2. **Automated 4 Invariant Verification:**
   After the load test completes, query `GET /status` and evaluate all 4 required invariants:
   - **Invariant 1 (Never oversell):** Total tickets issued must NOT exceed the initial pool (`len(tickets) <= total_tickets`).
   - **Invariant 2 (No duplicate ticket numbers):** Every ticket number issued must be strictly unique.
   - **Invariant 3 (Idempotency):** Replayed `request_id`s must NOT issue new/duplicate ticket numbers for the same request.
   - **Invariant 4 (State consistency):** `tickets_sold` reported by `/status` must exactly match `len(assignments)`.

3. **Output Reporting:**
   - Print a clean summary table in the terminal showing `[PASS]` or `[FAIL]` for each invariant with details (e.g., how many tickets were oversold or duplicates found).
   - Return an exit code (0 if all pass, 1 if any invariant fails).

</USER_REQUEST>
<ADDITIONAL_METADATA>
The current local time is: 2026-09-02T22:11:26+05:30.

The user's current state is as follows:
Active Document: /Users/prachikiledar/thuli/ticket-stampede/buyer/.gitkeep (LANGUAGE_UNSPECIFIED)
Cursor is on line: 1
Other open documents:
- /Users/prachikiledar/thuli/ticket-stampede/README.md (LANGUAGE_MARKDOWN)
- /Users/prachikiledar/thuli/ticket-stampede/seller/main.py (LANGUAGE_PYTHON)
- /Users/prachikiledar/thuli/ticket-stampede/seller/__init__.py (LANGUAGE_PYTHON)
- /Users/prachikiledar/thuli/ticket-stampede/logs/.gitkeep (LANGUAGE_UNSPECIFIED)
- /Users/prachikiledar/thuli/ticket-stampede/buyer/.gitkeep (LANGUAGE_UNSPECIFIED)
</ADDITIONAL_METADATA>
```

---

### 🤖 AI ASSISTANT (2026-09-02T16:43:25Z)

### Performance Metrics & 4 Invariant Verification Added

We have updated [buyer/main.py](file:///Users/prachikiledar/thuli/ticket-stampede/buyer/main.py) and [README.md](file:///Users/prachikiledar/thuli/ticket-stampede/README.md) to implement latency tracking, throughput measurements, and automated evaluation of all 4 invariants.

---

### What Was Implemented

1. **Individual RTT Latency Tracking & Percentiles**:
   - Measures round-trip time (RTT in ms) per request.
   - Calculates **Throughput (Requests Per Second)**.
   - Computes **Median (p50)**, **p90**, and **99th percentile (p99)** latency metrics.

2. **Automated 4 Invariant Verification**:
   - **Invariant 1 (Never oversell):** Verifies `len(assignments) <= total_tickets` and total 200 OK responses $\le$ initial pool.
   - **Invariant 2 (No duplicate ticket numbers):** Verifies all assigned ticket numbers across backend and client responses are strictly unique.
   - **Invariant 3 (Idempotency):** Detects if replayed `request_id`s caused duplicate ticket allocations or distinct ticket numbers.
   - **Invariant 4 (State consistency):** Verifies `tickets_sold` reported by `GET /status` matches `len(assignments)`.

3. **Output Reporting & Exit Code Handling**:
   - Formats a clean ASCII summary table with `[PASS]` or `[FAIL]` status for each invariant and diagnostic details.
   - Returns exit code `0` if all invariants pass, and `1` if any fail.

---

### Sample Test Output Against the Naive Seller

Running:
```bash
python3 -m buyer.main --total-tickets 50 --concurrent-buyers 50 --total-requests 300 --duplicate-rate 0.1
```

Produces:
```text
================================================================================
 🎟️  TICKET STAMPEDE — ASYNCHRONOUS LOAD TESTER
================================================================================
Target Base URL:       http://localhost:8000
Total Tickets:         50
Concurrent Buyers:     50
Total Requests:        300
Duplicate Rate:        10.0%
================================================================================

[1/3] Resetting seller state with 50 tickets...
✅ Seller service reset successfully: {'message': 'Sale reset successfully.', 'total_tickets': 50, 'tickets_sold': 0}

[2/3] Firing 300 requests (37 intentional duplicates) across 50 concurrent workers...
✅ All 300 requests completed in 1.738s.

[3/3] Querying final /status from seller service for invariant verification...

================================================================================
 📈 PERFORMANCE & LATENCY METRICS
================================================================================
Total Requests Dispatched:  300
Total Elapsed Time:         1.738 s
Throughput (RPS):           172.59 requests/sec
--------------------------------------------------------------------------------
HTTP Response Breakdown:
  • 200 OK (Purchased)        :    89 ( 29.7%)
  • 409 Conflict (Sold Out)   :   211 ( 70.3%)
--------------------------------------------------------------------------------
Round-Trip Time (RTT) Latency Distribution:
  • Min:      39.57 ms
  • Avg:     266.32 ms
  • p50:     177.80 ms (Median)
  • p90:     555.92 ms
  • p99:    1109.41 ms

================================================================================
 🛡️  INVARIANT VERIFICATION REPORT (4 CORE CHECKS)
================================================================================
Status   | Invariant                        | Verification Details
--------------------------------------------------------------------------------
 [FAIL]  | Inv 1: Never oversell            | Oversold! Issued 89 tickets for pool of 50 (39 excess tickets sold)
 [FAIL]  | Inv 2: No duplicate ticket numbers | Found 31 duplicate ticket numbers! (e.g. #1 (issued 2x), #2 (issued 4x), #3 (issued 2x))
 [FAIL]  | Inv 3: Idempotency               | Idempotency violated! 10 replayed request_id(s) received multiple tickets
 [FAIL]  | Inv 4: State consistency         | State mismatch! `tickets_sold` is 50 but `len(assignments)` is 89
================================================================================
🚨 INVARIANT CHECKS FAILED! Concurrency race conditions were detected.
================================================================================
(Exit Code: 1)
```

---

### 👤 USER (2026-09-02T16:46:01Z)

```text
<USER_REQUEST>
Now, let's build the load testing client for Part B: The Buyer.

Create an asynchronous load-testing script in `buyer/main.py` using `httpx` and `asyncio`.

Requirements:
1. Accept CLI arguments (using argparse):
   - `--base-url` (default: `http://localhost:8000`)
   - `--total-tickets` (default: 100)
   - `--concurrent-buyers` (default: 50)
   - `--total-requests` (default: 500)
   - `--duplicate-rate` (default: 0.1, i.e., 10% replayed request_ids for idempotency probing)

2. Execution Flow:
   - Call `POST /reset` with `total_tickets`.
   - Concurrently send `total_requests` using `concurrent-buyers` workers to `POST /buy`.
   - Send `user_id` and `request_id` in the body.
   - Aggregate and display HTTP status code counts (200 OK, 409 Conflict, errors).

3. Update `requirements.txt` to include `httpx`.

</USER_REQUEST>
<ADDITIONAL_METADATA>
The current local time is: 2026-09-02T22:16:01+05:30.

The user's current state is as follows:
Active Document: /Users/prachikiledar/thuli/ticket-stampede/buyer/.gitkeep (LANGUAGE_UNSPECIFIED)
Cursor is on line: 1
Other open documents:
- /Users/prachikiledar/thuli/ticket-stampede/buyer/.gitkeep (LANGUAGE_UNSPECIFIED)
- /Users/prachikiledar/thuli/ticket-stampede/requirements.txt (LANGUAGE_UNSPECIFIED)
- /Users/prachikiledar/thuli/ticket-stampede/README.md (LANGUAGE_MARKDOWN)
- /Users/prachikiledar/thuli/ticket-stampede/seller/main.py (LANGUAGE_PYTHON)
- /Users/prachikiledar/thuli/ticket-stampede/seller/__init__.py (LANGUAGE_PYTHON)
</ADDITIONAL_METADATA>
```

---

### 🤖 AI ASSISTANT (2026-09-02T16:46:07Z)

### Part B: The Buyer Load-Testing Client

The asynchronous load-testing client is implemented in [buyer/main.py](file:///Users/prachikiledar/thuli/ticket-stampede/buyer/main.py) with dependencies recorded in [requirements.txt](file:///Users/prachikiledar/thuli/ticket-stampede/requirements.txt).

---

### Key Capabilities & Options

1. **CLI Arguments via `argparse`**:
   - `--base-url` (default: `http://localhost:8000`)
   - `--total-tickets` (default: `100`)
   - `--concurrent-buyers` (default: `50`)
   - `--total-requests` (default: `500`)
   - `--duplicate-rate` (default: `0.1`, i.e., 10% simulated duplicate `request_id`s for idempotency verification)

2. **Execution Flow**:
   - Resets backend state with `POST /reset` and `{"total_tickets": ...}`.
   - Generates and dispatches `total_requests` concurrently across `concurrent-buyers` workers hitting `POST /buy`.
   - Sends payload: `{"user_id": "...", "request_id": "..."}`.
   - Aggregates HTTP status codes (`200 OK`, `409 Conflict`, errors) and computes throughput and RTT latency percentiles (`p50`, `p90`, `p99`).
   - Verifies the **4 Concurrency Invariants** from `GET /status` (Never oversell, No duplicate ticket numbers, Idempotency, State consistency) and exits with code `0` on pass or `1` on failure.

---

### How to Run

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the Seller service**:
   ```bash
   uvicorn seller.main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Run the Buyer load test**:
   ```bash
   # Default parameters (100 tickets, 50 workers, 500 requests, 10% duplicate rate)
   python3 -m buyer.main

   # Custom load test
   python3 -m buyer.main --total-tickets 50 --concurrent-buyers 50 --total-requests 300 --duplicate-rate 0.1
   ```

---

### 👤 USER (2026-09-02T16:46:42Z)

```text
<USER_REQUEST>
Update `buyer/main.py` to add latency metrics and the 4 automated Invariant checks.

Requirements:
1. Performance Metrics:
   - Track request duration in milliseconds.
   - Calculate and display: Total time, Requests Per Second (RPS), Median (p50), p90, and 99th percentile (p99) latency.

2. Invariant Verification:
   After all requests finish, query `GET /status` and verify the 4 invariants:
   - Invariant 1 (No Overselling): `tickets_sold <= total_tickets`
   - Invariant 2 (No Duplicate Tickets): All assigned ticket numbers are unique.
   - Invariant 3 (Idempotency): Replayed request_ids did NOT receive multiple distinct ticket numbers.
   - Invariant 4 (State Consistency): `tickets_sold` equals the count of ticket assignments in `/status`.

3. Display a clear `[PASS]` / `[FAIL]` table for each invariant with failure details.

</USER_REQUEST>
<ADDITIONAL_METADATA>
The current local time is: 2026-09-02T22:16:42+05:30.

The user's current state is as follows:
Active Document: /Users/prachikiledar/thuli/ticket-stampede/buyer/.gitkeep (LANGUAGE_UNSPECIFIED)
Cursor is on line: 1
Other open documents:
- /Users/prachikiledar/thuli/ticket-stampede/buyer/.gitkeep (LANGUAGE_UNSPECIFIED)
- /Users/prachikiledar/thuli/ticket-stampede/requirements.txt (LANGUAGE_UNSPECIFIED)
- /Users/prachikiledar/thuli/ticket-stampede/README.md (LANGUAGE_MARKDOWN)
- /Users/prachikiledar/thuli/ticket-stampede/seller/main.py (LANGUAGE_PYTHON)
- /Users/prachikiledar/thuli/ticket-stampede/seller/__init__.py (LANGUAGE_PYTHON)
</ADDITIONAL_METADATA>
```

---

### 🤖 AI ASSISTANT (2026-09-02T16:46:48Z)

The asynchronous load-testing and invariant-verification client in [buyer/main.py](file:///Users/prachikiledar/thuli/ticket-stampede/buyer/main.py) is complete with latency tracking and the 4 invariant checks.

---

### Implementation Breakdown

#### 1. Performance & Latency Metrics
- Tracks RTT per request (`latency_ms`) using `time.perf_counter()`.
- Computes:
  - **Total Elapsed Time** and **Throughput (RPS)**
  - **HTTP Status Code Breakdown** (`200 OK`, `409 Conflict`, Network errors)
  - **Latency Percentiles:** **p50 (Median)**, **p90**, **p99**, plus Min, Max, and Average.

#### 2. Automated 4 Invariant Verification
After the test finishes, `GET /status` is queried to verify:
- **Invariant 1 (No Overselling):** `tickets_sold <= total_tickets` and total tickets issued $\le$ initial pool.
- **Invariant 2 (No Duplicate Tickets):** Every ticket number issued is strictly unique across all assignments and responses.
- **Invariant 3 (Idempotency):** Replayed `request_id`s do not receive multiple distinct ticket numbers or duplicate entries.
- **Invariant 4 (State Consistency):** `tickets_sold` reported by `/status` matches `len(assignments)`.

#### 3. Summary Reporting & Exit Code
- Renders a clean `[PASS]` / `[FAIL]` table in the terminal.
- Exits with return code `0` if all invariants pass, and `1` if any invariant fails.

---

### How to Run

```bash
# Start Seller in Terminal 1
uvicorn seller.main:app --reload --host 0.0.0.0 --port 8000

# Run Load Tester in Terminal 2
python3 -m buyer.main --total-tickets 50 --concurrent-buyers 50 --total-requests 300 --duplicate-rate 0.1
```

---

### Example Terminal Output

```text
================================================================================
 🎟️  TICKET STAMPEDE — ASYNCHRONOUS LOAD TESTER
================================================================================
Target Base URL:       http://localhost:8000
Total Tickets:         50
Concurrent Buyers:     50
Total Requests:        300
Duplicate Rate:        10.0%
================================================================================

[1/3] Resetting seller state with 50 tickets...
✅ Seller service reset successfully: {'message': 'Sale reset successfully.', 'total_tickets': 50, 'tickets_sold': 0}

[2/3] Firing 300 requests (37 intentional duplicates) across 50 concurrent workers...
✅ All 300 requests completed in 1.738s.

[3/3] Querying final /status from seller service for invariant verification...

================================================================================
 📈 PERFORMANCE & LATENCY METRICS
================================================================================
Total Requests Dispatched:  300
Total Elapsed Time:         1.738 s
Throughput (RPS):           172.59 requests/sec
--------------------------------------------------------------------------------
HTTP Response Breakdown:
  • 200 OK (Purchased)        :    89 ( 29.7%)
  • 409 Conflict (Sold Out)   :   211 ( 70.3%)
--------------------------------------------------------------------------------
Round-Trip Time (RTT) Latency Distribution:
  • Min:      39.57 ms
  • Avg:     266.32 ms
  • p50:     177.80 ms (Median)
  • p90:     555.92 ms
  • p99:    1109.41 ms

================================================================================
 🛡️  INVARIANT VERIFICATION REPORT (4 CORE CHECKS)
================================================================================
Status   | Invariant                        | Verification Details
--------------------------------------------------------------------------------
 [FAIL]  | Inv 1: Never oversell            | Oversold! Issued 89 tickets for pool of 50 (39 excess tickets sold)
 [FAIL]  | Inv 2: No duplicate ticket numbers | Found 31 duplicate ticket numbers! (e.g. #1 (issued 2x), #2 (issued 4x), #3 (issued 2x))
 [FAIL]  | Inv 3: Idempotency               | Idempotency violated! 10 replayed request_id(s) received multiple tickets
 [FAIL]  | Inv 4: State consistency         | State mismatch! `tickets_sold` is 50 but `len(assignments)` is 89
================================================================================
🚨 INVARIANT CHECKS FAILED! Concurrency race conditions were detected.
================================================================================
```

---

### 👤 USER (2026-09-02T16:47:09Z)

```text
<USER_REQUEST>
Let's run the load test against the naive seller to prove it fails under concurrency.

Requirements:
1. Add an option `--save-report` (default: `logs/failing_run.json`) to `buyer/main.py` that dumps:
   - Test configuration parameters
   - RPS, p50, p90, p99 latencies
   - Status code counts
   - Invariant check results and exact failure details (e.g. oversold count, duplicate ticket IDs)
2. Provide the exact shell commands to run the naive seller with uvicorn and execute the buyer client against it.

</USER_REQUEST>
<ADDITIONAL_METADATA>
The current local time is: 2026-09-02T22:17:09+05:30.

The user's current state is as follows:
Active Document: /Users/prachikiledar/thuli/ticket-stampede/buyer/.gitkeep (LANGUAGE_UNSPECIFIED)
Cursor is on line: 1
Other open documents:
- /Users/prachikiledar/thuli/ticket-stampede/buyer/.gitkeep (LANGUAGE_UNSPECIFIED)
- /Users/prachikiledar/thuli/ticket-stampede/requirements.txt (LANGUAGE_UNSPECIFIED)
- /Users/prachikiledar/thuli/ticket-stampede/README.md (LANGUAGE_MARKDOWN)
- /Users/prachikiledar/thuli/ticket-stampede/seller/main.py (LANGUAGE_PYTHON)
- /Users/prachikiledar/thuli/ticket-stampede/seller/__init__.py (LANGUAGE_PYTHON)
</ADDITIONAL_METADATA>
```

---

### 🤖 AI ASSISTANT (2026-09-02T16:47:49Z)

The `--save-report` option is added to [buyer/main.py](file:///Users/prachikiledar/thuli/ticket-stampede/buyer/main.py) (defaulting to [logs/failing_run.json](file:///Users/prachikiledar/thuli/ticket-stampede/logs/failing_run.json)), and the failure run has been recorded.

---

### Exact Shell Commands to Run the Test

#### Terminal 1: Start the Naive Seller
```bash
uvicorn seller.main:app --reload --host 0.0.0.0 --port 8000
```

#### Terminal 2: Run the Buyer Load Tester
```bash
python3 -m buyer.main \
  --base-url http://localhost:8000 \
  --total-tickets 50 \
  --concurrent-buyers 50 \
  --total-requests 300 \
  --duplicate-rate 0.1 \
  --save-report logs/failing_run.json
```

---

### Test Execution Results

```text
================================================================================
 🎟️  TICKET STAMPEDE — ASYNCHRONOUS LOAD TESTER
================================================================================
Target Base URL:       http://localhost:8000
Total Tickets:         50
Concurrent Buyers:     50
Total Requests:        300
Duplicate Rate:        10.0%
================================================================================

[1/3] Resetting seller state with 50 tickets...
✅ Seller service reset successfully: {'message': 'Sale reset successfully.', 'total_tickets': 50, 'tickets_sold': 0}

[2/3] Firing 300 requests (31 intentional duplicates) across 50 concurrent workers...
✅ All 300 requests completed in 1.793s.

[3/3] Querying final /status from seller service for invariant verification...

================================================================================
 📈 PERFORMANCE & LATENCY METRICS
================================================================================
Total Requests Dispatched:  300
Total Elapsed Time:         1.793 s
Throughput (RPS):           167.36 requests/sec
--------------------------------------------------------------------------------
HTTP Response Breakdown:
  • 200 OK (Purchased)        :    97 ( 32.3%)
  • 409 Conflict (Sold Out)   :   203 ( 67.7%)
--------------------------------------------------------------------------------
Round-Trip Time (RTT) Latency Distribution:
  • Min:      35.58 ms
  • Avg:     273.66 ms
  • p50:     207.45 ms (Median)
  • p90:     634.06 ms
  • p99:     961.86 ms

================================================================================
 🛡️  INVARIANT VERIFICATION REPORT (4 CORE CHECKS)
================================================================================
Status   | Invariant                        | Verification Details
--------------------------------------------------------------------------------
 [FAIL]  | Inv 1: Never oversell            | Oversold! Issued 97 tickets for pool of 50 (47 excess tickets sold)
 [FAIL]  | Inv 2: No duplicate ticket numbers | Found 31 duplicate ticket numbers! (e.g. #2 (issued 5x), #3 (issued 4x), #4 (issued 2x))
 [FAIL]  | Inv 3: Idempotency               | Idempotency violated! 6 replayed request_id(s) received multiple tickets
 [FAIL]  | Inv 4: State consistency         | State mismatch! `tickets_sold` is 50 but `len(assignments)` is 97
================================================================================
🚨 INVARIANT CHECKS FAILED! Concurrency race conditions were detected.
================================================================================
📁 JSON test report saved to: /Users/prachikiledar/thuli/ticket-stampede/logs/failing_run.json
```

---

### Saved Report File

The detailed failure metrics and diagnostic dump have been saved to [logs/failing_run.json](file:///Users/prachikiledar/thuli/ticket-stampede/logs/failing_run.json).

---

### 👤 USER (2026-09-02T16:48:15Z)

```text
<USER_REQUEST>
Now, let's fix the seller service in `seller/main.py` so it is thread-safe, async-safe, and holds all 4 invariants under heavy concurrency.

Requirements:
1. Concurrency Control:
   - Use proper synchronization (`asyncio.Lock` or an atomic state manager) to eliminate the check-then-act race condition.
   - Ensure ticket numbers are assigned strictly monotonically without duplicates or overselling.

2. Idempotency Handling:
   - Maintain an idempotency cache of `request_id` -> existing ticket response.
   - If a duplicate `request_id` is received, return the previously assigned ticket without consuming a new one.

3. Accuracy:
   - Ensure `POST /reset`, `POST /buy`, and `GET /status` remain consistent at all times.

</USER_REQUEST>
<ADDITIONAL_METADATA>
The current local time is: 2026-09-02T22:18:15+05:30.

The user's current state is as follows:
Active Document: /Users/prachikiledar/thuli/ticket-stampede/buyer/.gitkeep (LANGUAGE_UNSPECIFIED)
Cursor is on line: 1
Other open documents:
- /Users/prachikiledar/thuli/ticket-stampede/logs/.gitkeep (LANGUAGE_UNSPECIFIED)
- /Users/prachikiledar/thuli/ticket-stampede/buyer/.gitkeep (LANGUAGE_UNSPECIFIED)
- /Users/prachikiledar/thuli/ticket-stampede/requirements.txt (LANGUAGE_UNSPECIFIED)
- /Users/prachikiledar/thuli/ticket-stampede/README.md (LANGUAGE_MARKDOWN)
- /Users/prachikiledar/thuli/ticket-stampede/seller/main.py (LANGUAGE_PYTHON)
</ADDITIONAL_METADATA>
```

---

### 🤖 AI ASSISTANT (2026-09-02T16:49:36Z)

### Concurrency-Safe Seller Service Implemented

We have updated [seller/main.py](file:///Users/prachikiledar/thuli/ticket-stampede/seller/main.py) to make the seller service thread-safe, async-safe, and idempotent, ensuring all 4 core invariants hold under heavy concurrency.

---

### Key Improvements in `seller/main.py`

1. **Atomic Concurrency Control (`asyncio.Lock`)**:
   - Eliminated the check-then-act race condition across `/reset`, `/buy`, and `/status`.
   - Guaranteed sequential, monotonic ticket assignment without overselling or duplicate ticket numbers.

2. **Idempotency Handling**:
   - Added an in-memory idempotency cache (`seen_requests`) mapping `request_id` to its assigned ticket record.
   - If a duplicate `request_id` arrives (e.g. from network retries), the service returns the existing ticket without deducting from inventory or incrementing `tickets_sold`.

3. **State Consistency**:
   - `tickets_sold` is strictly synchronized with `len(assignments)` inside atomic critical sections.

---

### Load Test Verification

Running the load tester against the updated seller:

```bash
python3 -m buyer.main \
  --base-url http://localhost:8000 \
  --total-tickets 50 \
  --concurrent-buyers 50 \
  --total-requests 300 \
  --duplicate-rate 0.1 \
  --save-report logs/passing_run.json
```

#### Output:

```text
================================================================================
 🎟️  TICKET STAMPEDE — ASYNCHRONOUS LOAD TESTER
================================================================================
Target Base URL:       http://localhost:8000
Total Tickets:         50
Concurrent Buyers:     50
Total Requests:        300
Duplicate Rate:        10.0%
================================================================================

[1/3] Resetting seller state with 50 tickets...
✅ Seller service reset successfully: {'message': 'Sale reset successfully.', 'total_tickets': 50, 'tickets_sold': 0}

[2/3] Firing 300 requests (35 intentional duplicates) across 50 concurrent workers...
✅ All 300 requests completed in 1.455s.

[3/3] Querying final /status from seller service for invariant verification...

================================================================================
 📈 PERFORMANCE & LATENCY METRICS
================================================================================
Total Requests Dispatched:  300
Total Elapsed Time:         1.455 s
Throughput (RPS):           206.22 requests/sec
--------------------------------------------------------------------------------
HTTP Response Breakdown:
  • 200 OK (Purchased)        :    66 ( 22.0%)
  • 409 Conflict (Sold Out)   :   234 ( 78.0%)
--------------------------------------------------------------------------------
Round-Trip Time (RTT) Latency Distribution:
  • Min:      26.03 ms
  • Avg:     221.47 ms
  • p50:     160.90 ms (Median)
  • p90:     444.00 ms
  • p99:    1000.49 ms

================================================================================
 🛡️  INVARIANT VERIFICATION REPORT (4 CORE CHECKS)
================================================================================
Status   | Invariant                        | Verification Details
--------------------------------------------------------------------------------
 [PASS]  | Inv 1: Never oversell            | Total issued (50) <= pool limit (50)
 [PASS]  | Inv 2: No duplicate ticket numbers | All 50 issued ticket numbers are unique
 [PASS]  | Inv 3: Idempotency               | No duplicate tickets issued for replayed request_ids
 [PASS]  | Inv 4: State consistency         | `tickets_sold` (50) matches `len(assignments)` (50)
================================================================================
🎉 ALL 4 INVARIANTS PASSED! Service maintained complete concurrency safety.
================================================================================
📁 JSON test report saved to: /Users/prachikiledar/thuli/ticket-stampede/logs/passing_run.json
```

---

### 👤 USER (2026-09-02T16:49:22Z)

```text
<USER_REQUEST>
Run the buyer load test against the fixed seller to verify that all 4 invariants now pass under heavy concurrency.

Requirements:
1. Run with high concurrency (e.g., `--total-requests 5000 --concurrent-buyers 100 --duplicate-rate 0.15`).
2. Save the passing run results to `logs/passing_run.json`.
3. Display comparative metrics between the naive (failing) run and the fixed (passing) run.

</USER_REQUEST>
<ADDITIONAL_METADATA>
The current local time is: 2026-09-02T22:19:22+05:30.

The user's current state is as follows:
Active Document: /Users/prachikiledar/thuli/ticket-stampede/buyer/.gitkeep (LANGUAGE_UNSPECIFIED)
Cursor is on line: 1
Other open documents:
- /Users/prachikiledar/thuli/ticket-stampede/buyer/.gitkeep (LANGUAGE_UNSPECIFIED)
- /Users/prachikiledar/thuli/ticket-stampede/requirements.txt (LANGUAGE_UNSPECIFIED)
- /Users/prachikiledar/thuli/ticket-stampede/README.md (LANGUAGE_MARKDOWN)
- /Users/prachikiledar/thuli/ticket-stampede/seller/main.py (LANGUAGE_PYTHON)
- /Users/prachikiledar/thuli/ticket-stampede/seller/__init__.py (LANGUAGE_PYTHON)
</ADDITIONAL_METADATA>
```

---

### 🤖 AI ASSISTANT (2026-09-02T16:50:03Z)

I have launched the heavy load test (5,000 requests, 100 concurrent buyers, 15% duplicate rate) against the fixed seller service in the background and will analyze and compare the results as soon as it completes.

---

### 🤖 AI ASSISTANT (2026-09-02T16:50:09Z)

Waiting for the 5,000-request load test to complete.

---

### 🤖 AI ASSISTANT (2026-09-02T16:50:29Z)

### High-Concurrency Verification & Comparative Analysis

The high-concurrency load test (**5,000 requests, 100 concurrent workers, 15% duplicate rate**) has completed against the fixed seller service. All 4 core concurrency invariants passed, and the results are saved to [logs/passing_run.json](file:///Users/prachikiledar/thuli/ticket-stampede/logs/passing_run.json).

---

### Invariant Verification Results (Fixed Seller)

```text
================================================================================
 🛡️  INVARIANT VERIFICATION REPORT (4 CORE CHECKS)
================================================================================
Status   | Invariant                        | Verification Details
--------------------------------------------------------------------------------
 [PASS]  | Inv 1: Never oversell            | Total issued (100) <= pool limit (100)
 [PASS]  | Inv 2: No duplicate ticket numbers | All 100 issued ticket numbers are unique
 [PASS]  | Inv 3: Idempotency               | No duplicate tickets issued for replayed request_ids
 [PASS]  | Inv 4: State consistency         | `tickets_sold` (100) matches `len(assignments)` (100)
================================================================================
🎉 ALL 4 INVARIANTS PASSED! Service maintained complete concurrency safety.
================================================================================
```

---

### Comparative Metrics: Naive Run vs. Fixed Run

| Metric / Check | Naive (Failing Run) | Fixed (Passing Run) | Impact / Resolution |
| :--- | :--- | :--- | :--- |
| **Total Requests Dispatched** | 300 requests | **5,000 requests** | Scaled load by >16x |
| **Concurrent Workers** | 50 workers | **100 workers** | 2x concurrency |
| **Duplicate Request Rate** | 10.0% | **15.0%** (739 duplicates) | Tested idempotency under heavy load |
| **Throughput (RPS)** | 167.36 req/s | **181.64 req/s** | Maintained high throughput with lock |
| **p50 Latency (Median)** | 207.45 ms | **364.79 ms** | Predictable scaling under 100 workers |
| **p90 Latency** | 634.06 ms | **1216.90 ms** | Smooth queuing under saturated load |
| **p99 Latency** | 961.86 ms | **2509.36 ms** | Tail latency accounted for under burst |
| **Invariant 1: No Overselling** | ❌ **FAIL** (Sold 97 / 50 pool) | ✅ **PASS** (Sold exactly 100 / 100 pool) | `asyncio.Lock` prevented inventory leaks |
| **Invariant 2: Unique Tickets** | ❌ **FAIL** (31 duplicate tickets) | ✅ **PASS** (0 duplicates across all tickets) | Monotonic counter inside critical section |
| **Invariant 3: Idempotency** | ❌ **FAIL** (Replays got new tickets) | ✅ **PASS** (Replays returned cached ticket) | In-memory `seen_requests` cache |
| **Invariant 4: State Consistency** | ❌ **FAIL** (`tickets_sold` $\neq$ `len(assignments)`) | ✅ **PASS** (`tickets_sold` == `len(assignments)` == 100) | Atomic state updates |
| **Exit Code** | `1` (Failure) | `0` (Success) | Fully automated CI/CD-compatible test |

---

### Artifacts Saved

- **Failing Run Report**: [logs/failing_run.json](file:///Users/prachikiledar/thuli/ticket-stampede/logs/failing_run.json)
- **Passing Run Report**: [logs/passing_run.json](file:///Users/prachikiledar/thuli/ticket-stampede/logs/passing_run.json)

---

### 👤 USER (2026-09-02T16:50:02Z)

```text
<USER_REQUEST>
Let's implement one of the advanced "Take It Further" requirements: A Waitlist Queue with reservation timeouts.

Requirements:
1. When all tickets are sold out, subsequent buyers enter a FIFO waitlist queue.
2. If a reserved ticket is cancelled or times out (e.g., after 30s), it returns to the pool and is atomically allocated to the next user in the waitlist queue.
3. Update the buyer script to test and verify the waitlist mechanics under concurrency.

</USER_REQUEST>
<ADDITIONAL_METADATA>
The current local time is: 2026-09-02T22:20:02+05:30.

The user's current state is as follows:
Active Document: /Users/prachikiledar/thuli/ticket-stampede/buyer/.gitkeep (LANGUAGE_UNSPECIFIED)
Cursor is on line: 1
Other open documents:
- /Users/prachikiledar/thuli/ticket-stampede/buyer/.gitkeep (LANGUAGE_UNSPECIFIED)
- /Users/prachikiledar/thuli/ticket-stampede/requirements.txt (LANGUAGE_UNSPECIFIED)
- /Users/prachikiledar/thuli/ticket-stampede/README.md (LANGUAGE_MARKDOWN)
- /Users/prachikiledar/thuli/ticket-stampede/seller/main.py (LANGUAGE_PYTHON)
- /Users/prachikiledar/thuli/ticket-stampede/seller/__init__.py (LANGUAGE_PYTHON)
</ADDITIONAL_METADATA>
```

---

### 🤖 AI ASSISTANT (2026-09-02T16:52:13Z)

### Advanced FIFO Waitlist & Reservation Timeout Mechanics Implemented

We have implemented the complete **FIFO Waitlist & Reservation Timeout Lifecycle** in [seller/main.py](file:///Users/prachikiledar/thuli/ticket-stampede/seller/main.py) and updated [buyer/main.py](file:///Users/prachikiledar/thuli/ticket-stampede/buyer/main.py) and [README.md](file:///Users/prachikiledar/thuli/ticket-stampede/README.md).

---

### Key Architectural Components

1. **Reservation Lifecycle & State Transitions**:
   - Tickets start in `RESERVED` status with a configurable `reservation_timeout_seconds` countdown.
   - `POST /confirm`: Buyers confirm their ticket, transitioning it to permanent `CONFIRMED` status.
   - `POST /cancel`: Buyers can voluntarily surrender a reservation.
   - An asynchronous background sweeper (`expiration_sweeper_task`) proactively reclaims expired reservations every 100ms.

2. **FIFO Waitlist Queue**:
   - When all tickets are reserved or sold, subsequent buyers receive `200 OK` with `status: "WAITLISTED"` and their queue position.
   - When a ticket is cancelled or times out, it is **atomically transferred to the head of the FIFO waitlist** (`waitlist.pop(0)`) with a fresh reservation timer.

3. **Buyer Simulation & Invariant Verification**:
   - The buyer simulates real-world behavior (confirmations, voluntary cancellations, timeout expirations, and waitlist promotion claims).
   - Verifies **5 Core Concurrency Invariants** under high load:
     1. **Never Oversell** (`active_tickets <= total_tickets`)
     2. **No Duplicate Ticket Numbers** (all active tickets strictly unique)
     3. **Idempotency** (replayed requests receive consistent status)
     4. **State Consistency** (`tickets_sold` == `len(assignments)`)
     5. **Waitlist & Timeout Integrity** (reclaims and promotions conserve total inventory)

---

### Load Test Results with Waitlist & Timeouts

Running:
```bash
python3 -m buyer.main \
  --base-url http://localhost:8000 \
  --total-tickets 30 \
  --concurrent-buyers 40 \
  --total-requests 200 \
  --reservation-timeout 1.0 \
  --save-report logs/waitlist_run.json
```

Produces:
```text
================================================================================
 🎟️  TICKET STAMPEDE — ADVANCED WAITLIST & LOAD TESTER
================================================================================
Target Base URL:       http://localhost:8000
Total Tickets:         30
Concurrent Buyers:     40
Total Requests:        200
Duplicate Rate:        10.0%
Reservation Timeout:   1.0s
Simulate Lifecycle:    True
================================================================================

[1/3] Resetting seller state (30 tickets, 1.0s timeout)...
✅ Seller service reset successfully: {'message': 'Sale reset successfully.', 'total_tickets': 30, 'reservation_timeout_seconds': 1.0, 'enable_waitlist': True}

[2/3] Dispatching 200 requests (32 duplicates) across 40 concurrent workers...
✅ All 200 requests and lifecycle flows completed in 1.840s.

[3/3] Querying final /status from seller service for invariant verification...

================================================================================
 📈 PERFORMANCE & LATENCY METRICS
================================================================================
Total Requests Dispatched:  200
Total Elapsed Time:         1.840 s
Throughput (RPS):           108.68 requests/sec
--------------------------------------------------------------------------------
HTTP Response Breakdown:
  • 200 OK (Processed)        :   200 (100.0%)
--------------------------------------------------------------------------------
Lifecycle Action Breakdown:
  • CANCELLED                   :     6
  • CONFIRMED                   :    30
  • NONE                        :   154
  • TIMED_OUT                   :     7
  • WAITLIST_PROMOTED_CONFIRMED :     3
--------------------------------------------------------------------------------
Waitlist & Reclaim Metrics:
  • Active Pool Size:        30
  • Confirmed Tickets:       27
  • Reserved Tickets:        3
  • Remaining on Waitlist:   126
  • Expired Reclaims:        7
  • Voluntary Cancellations: 5
  • Waitlist Promotions:     10
--------------------------------------------------------------------------------
Round-Trip Time (RTT) Latency Distribution:
  • Min:       3.30 ms
  • Avg:      56.23 ms
  • p50:      22.05 ms (Median)
  • p90:     175.37 ms
  • p99:     296.79 ms

================================================================================
 🛡️  INVARIANT VERIFICATION REPORT (5 CORE CHECKS)
================================================================================
Status   | Invariant                        | Verification Details
--------------------------------------------------------------------------------
 [PASS]  | Inv 1: Never oversell            | Active tickets (30) <= pool limit (30)
 [PASS]  | Inv 2: No duplicate ticket numbers | All 30 active ticket numbers are strictly unique
 [PASS]  | Inv 3: Idempotency               | Duplicate request_ids received matching ticket assignments
 [PASS]  | Inv 4: State consistency         | `tickets_sold` (30) matches `len(assignments)` (30)
 [PASS]  | Inv 5: Waitlist & Timeout Integrity | Processed 10 waitlist promotions, 7 expirations, 5 cancellations cleanly
================================================================================
🎉 ALL INVARIANTS PASSED! Waitlist, timeouts, and concurrency safety held.
================================================================================
📁 JSON test report saved to: logs/waitlist_run.json
```

---

### 👤 USER (2026-09-02T16:51:17Z)

```text
<USER_REQUEST>
Create the required `DECISIONS.md` (under 2 pages) and update `README.md`.

Requirements for `DECISIONS.md`:
1. Architecture chosen and alternatives rejected (e.g. In-memory locking vs Redis vs Postgres row-locks).
2. Trade-offs made under the time limit.
3. Testing methodology and breakdown of Failing Run vs Passing Run results.
4. Where the system breaks (limits of single-process event-loop concurrency vs distributed multi-node).
5. What to do next with 2 more weeks.

Requirements for `README.md`:
- How to set up and run the seller and buyer in under 5 minutes on a clean machine.

</USER_REQUEST>
<ADDITIONAL_METADATA>
The current local time is: 2026-09-02T22:21:17+05:30.

The user's current state is as follows:
Active Document: /Users/prachikiledar/thuli/ticket-stampede/buyer/.gitkeep (LANGUAGE_UNSPECIFIED)
Cursor is on line: 1
Other open documents:
- /Users/prachikiledar/thuli/ticket-stampede/requirements.txt (LANGUAGE_UNSPECIFIED)
- /Users/prachikiledar/thuli/ticket-stampede/README.md (LANGUAGE_MARKDOWN)
- /Users/prachikiledar/thuli/ticket-stampede/seller/main.py (LANGUAGE_PYTHON)
- /Users/prachikiledar/thuli/ticket-stampede/seller/__init__.py (LANGUAGE_PYTHON)
- /Users/prachikiledar/thuli/ticket-stampede/logs/.gitkeep (LANGUAGE_UNSPECIFIED)
</ADDITIONAL_METADATA>
```

---

### 🤖 AI ASSISTANT (2026-09-02T16:52:44Z)

### Architectural Decisions Document & 5-Minute Quickstart

We have created [DECISIONS.md](file:///Users/prachikiledar/thuli/ticket-stampede/DECISIONS.md) (under 2 pages, highly structured and technical) and updated [README.md](file:///Users/prachikiledar/thuli/ticket-stampede/README.md) with a streamlined 5-minute setup guide.

---

### Summary of `DECISIONS.md`

1. **Architecture Chosen vs. Alternatives Rejected**:
   - **Chosen:** In-memory critical sections via `asyncio.Lock` with an atomic state dictionary and FIFO deque.
   - **Rejected:** PostgreSQL row-locks (I/O & connection pool overhead under burst stampedes) and Redis (unnecessary infrastructure dependency for single-node Phase 1).

2. **Trade-offs Made Under the Time Limit**:
   - In-memory data structures (sub-millisecond speed vs. loss of state on restart).
   - Unbounded idempotency dictionary (simplicity vs. long-term memory management).
   - Single-task background sweeper for timeouts.

3. **Testing Methodology & Empirical Run Breakdown**:
   - Automated testing with `httpx.AsyncClient` under burst concurrency.
   - Direct comparison showing 100% pass rate on all 5 invariants on the fixed seller versus catastrophic overselling (97 sold / 50 limit) on the naive seller.

4. **Where the System Breaks (Failure Modes)**:
   - Multi-process isolation (`uvicorn --workers N`).
   - Horizontal multi-node / multi-container scaling.
   - Process crash recovery.

5. **2-Week Production Roadmap**:
   - Redis + Lua script atomic compare-and-swap state store.
   - PostgreSQL persistence with Transactional Outbox pattern & message queues.
   - Redis Key Space expiry events for distributed reservation timeouts.
   - Token bucket / Leaky bucket rate limiting against bot traffic.

---

### ⚡ 5-Minute Quickstart (from `README.md`)

```bash
# 1. Setup Virtual Environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Terminal 1: Start Seller Service
uvicorn seller.main:app --reload --host 0.0.0.0 --port 8000

# 3. Terminal 2: Run Automated Buyer Suite & Invariant Verifier
python3 -m buyer.main --total-tickets 50 --concurrent-buyers 50 --total-requests 300
```

---
