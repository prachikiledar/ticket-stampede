# Ticket Stampede

A high-concurrency ticket-selling service and asynchronous load tester built with Python, FastAPI, and `httpx`, featuring reservation timeouts, FIFO waitlist mechanics, and automated invariant verification.

## Project Structure

```
ticket-stampede/
├── seller/             # FastAPI ticket-selling service
│   ├── __init__.py
│   └── main.py
├── buyer/              # Asynchronous load-testing & invariant verification client
│   ├── __init__.py
│   └── main.py
├── logs/               # Run reports & AI session logs
├── requirements.txt    # Project dependencies
└── README.md
```

## Features

- **Concurrency-Safe Atomic Transactions**: Powered by `asyncio.Lock` to guarantee strict monotonic ticket assignment with zero overselling or duplicate numbers.
- **Idempotency Protection**: In-memory cache ensures duplicate `request_id`s safely return existing assignments without consuming additional tickets.
- **Reservation Timeouts & Sweeper**: Tickets start in `RESERVED` state with a configurable expiration timeout. An asynchronous background worker continuously reclaims expired reservations.
- **FIFO Waitlist Queue**: When inventory is saturated, incoming buyers enter a FIFO waitlist. Reclaimed or cancelled tickets are atomically promoted to the next waiting user.
- **Automated Invariant Verification**: The buyer suite evaluates 5 core invariants across high-concurrency load tests.

---

## ⚡ 5-Minute Quickstart (Clean Machine Setup)

Follow these steps to clone, set up, and run both services in under 5 minutes:

### 1. Prerequisites & Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Start Seller Service (Terminal 1)
```bash
uvicorn seller.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Run Load Tester & Invariant Suite (Terminal 2)
```bash
# Run 300 concurrent requests with waitlist, lifecycle simulation, and invariant verification
python3 -m buyer.main --total-tickets 30 --concurrent-buyers 40 --total-requests 200

# Or run heavy burst test (5,000 requests)
python3 -m buyer.main --total-tickets 100 --concurrent-buyers 100 --total-requests 5000 --duplicate-rate 0.15
```

---

## Running the Buyer Load Tester & Invariant Verifier

In a separate terminal, launch the load tester against the running seller service:

```bash
python3 -m buyer.main
```

### Command-Line Options

| Option | Default | Description |
| :--- | :--- | :--- |
| `--base-url` | `http://localhost:8000` | Target URL of the seller service |
| `--total-tickets` | `50` | Number of tickets available in the pool |
| `--concurrent-buyers` | `50` | Maximum concurrent buyer workers |
| `--total-requests` | `300` | Total purchase requests to dispatch |
| `--duplicate-rate` | `0.1` | Fraction of requests that reuse an existing `request_id` |
| `--reservation-timeout` | `1.0` | Seconds before an unconfirmed reservation times out |
| `--simulate-lifecycle` | `True` | Simulates confirmations (60%), cancellations (20%), and timeouts (20%) |
| `--save-report` | `logs/passing_run.json` | Destination path for the detailed JSON execution report |

**Example with custom parameters**:

```bash
python3 -m buyer.main \
  --total-tickets 30 \
  --concurrent-buyers 40 \
  --total-requests 200 \
  --reservation-timeout 1.0 \
  --save-report logs/waitlist_run.json
```

---

## Core Invariants Verified

After each test run, `buyer/main.py` queries `GET /status` and automatically evaluates:
1. **Invariant 1 (Never oversell):** Active tickets in pool $\le$ initial ticket pool limit.
2. **Invariant 2 (No duplicate ticket numbers):** Every active ticket number issued is strictly unique.
3. **Invariant 3 (Idempotency):** Replayed `request_id`s receive matching ticket assignments.
4. **Invariant 4 (State consistency):** `tickets_sold` reported by `/status` matches `len(assignments)`.
5. **Invariant 5 (Waitlist & Timeout Integrity):** Reclaimed reservations and waitlist promotions maintain state integrity.

The test returns exit code `0` on success and `1` on failure.

---

## Endpoints

### 1. `POST /reset`
Wipes all state, initializes ticket pool, and configures timeout settings.

```bash
curl -X POST http://localhost:8000/reset \
  -H "Content-Type: application/json" \
  -d '{"total_tickets": 50, "reservation_timeout_seconds": 5.0, "enable_waitlist": true}'
```

### 2. `POST /buy`
Attempts to reserve, confirm, or waitlist a ticket.

```bash
curl -X POST http://localhost:8000/buy \
  -H "Content-Type: application/json" \
  -d '{"user_id": "alice", "request_id": "req-001", "auto_confirm": false}'
```

### 3. `POST /confirm`
Confirms a reserved ticket before expiration.

```bash
curl -X POST http://localhost:8000/confirm \
  -H "Content-Type: application/json" \
  -d '{"user_id": "alice", "request_id": "req-001", "ticket_number": 1}'
```

### 4. `POST /cancel`
Voluntarily cancels a ticket and transfers it immediately to the head of the waitlist.

```bash
curl -X POST http://localhost:8000/cancel \
  -H "Content-Type: application/json" \
  -d '{"user_id": "alice", "request_id": "req-001", "ticket_number": 1}'
```

### 5. `GET /status`
Returns atomic snapshot of inventory, confirmed/reserved tickets, waitlist queue, and promotion metrics.

```bash
curl http://localhost:8000/status
```
