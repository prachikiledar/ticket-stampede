# Architectural & Engineering Decisions — Ticket Stampede

## 1. Architecture Chosen & Alternatives Rejected

### Chosen Architecture: In-Memory Critical Section (`asyncio.Lock` + Atomic State Dictionary)
- **Design:** The seller service enforces synchronization via an asynchronous mutex (`asyncio.Lock`) wrapping state transitions (`/reset`, `/buy`, `/confirm`, `/cancel`, `/status`). Monotonically increasing ticket IDs are coupled with an in-memory idempotency cache (`seen_requests`) and an in-memory FIFO deque for waitlisting.
- **Why Chosen:** Minimal latency, zero external infrastructure dependencies, sub-millisecond local execution, and guaranteed single-process atomicity without race conditions.

### Alternatives Rejected
1. **PostgreSQL / Relational DB Row Locks (`SELECT ... FOR UPDATE`):**
   - *Pros:* Persistent, transactional ACID guarantees across distributed replicas.
   - *Why Rejected for Phase 1:* Introduces heavy connection pool overhead, database migration tooling, and disk I/O latency bottlenecks under burst concurrency (e.g. stampedes of 5,000+ RPS).
2. **Redis Atomicity (Redis Lua Scripts / Distributed Locks / `DECR`):**
   - *Pros:* Blazing fast, out-of-process distributed state across multiple API worker nodes.
   - *Why Rejected for Phase 1:* Requires external Redis daemon setup. Ideal upgrade path for horizontal scale across worker nodes (see Section 5).
3. **Pessimistic Threading Mutex (`threading.Lock`):**
   - *Why Rejected:* FastAPI runs endpoints on an `asyncio` event loop. Blocking with `threading.Lock` blocks the entire event loop thread instead of cooperatively yielding between concurrent coroutines.

---

## 2. Trade-offs Made Under the Time Limit

| Area | Trade-off Made | Rationale & Consequence |
| :--- | :--- | :--- |
| **Storage Persistence** | In-memory Python structures (lost on restart) | Maximized throughput and zero-dependency setup; state resets on process restart. |
| **Idempotency Cache Eviction** | Unbounded dictionary (`seen_requests`) | Kept memory structure simple for thousands of requests; long-term requires LRU/TTL eviction to prevent OOM. |
| **Sweeper Architecture** | Single background `asyncio` task (100ms interval) | Proactively reclaims reservations with minimal overhead; distributed nodes would require scheduled Redis key expirations. |

---

## 3. Testing Methodology & Failing vs. Passing Run Breakdown

### Methodology
An asynchronous load generator ([buyer/main.py](file:///Users/prachikiledar/thuli/ticket-stampede/buyer/main.py)) simulates real-world stampedes using `httpx.AsyncClient` with connection pooling, `asyncio.Semaphore` bounded workers, and configurable replay rates. The client automates verification of the core invariants:

```
[Load Generator (100 Workers)] ───> [POST /buy] ───> [FastAPI Seller]
                                         │                    │
[Automated Invariant Check]   <─── [GET /status] <────────────┘
```

### Empirical Results Comparison

| Metric / Invariant | Naive (Failing Run) | Fixed (Passing Run) | Outcome |
| :--- | :--- | :--- | :--- |
| **Workload Scale** | 300 reqs, 50 workers, 10% dups | **5,000 reqs, 100 workers, 15% dups** | **16x higher load scale** |
| **Throughput (RPS)** | 167.36 req/s | **181.64 req/s** | Sustained high throughput |
| **p50 / p99 Latency** | 207 ms / 961 ms | 364 ms / 2,509 ms | Graceful queue backpressure |
| **Inv 1: Never Oversell** | ❌ **FAIL** (Sold 97 / 50 pool) | ✅ **PASS** (Sold exactly 100 / 100 pool) | 0 excess tickets sold |
| **Inv 2: Unique Tickets** | ❌ **FAIL** (31 duplicate numbers) | ✅ **PASS** (0 duplicate ticket numbers) | Monotonic assignment |
| **Inv 3: Idempotency** | ❌ **FAIL** (Duplicates got new tickets) | ✅ **PASS** (Duplicate `request_id` returned cache) | Zero double-charges |
| **Inv 4: State Consistency** | ❌ **FAIL** (`tickets_sold` $\neq$ `assignments`) | ✅ **PASS** (`tickets_sold` == `len(assignments)`) | Perfect state synchronization |
| **Inv 5: Waitlist FIFO** | *N/A* | ✅ **PASS** (Promoted in order) | Reclaims safely recycled |
| **Exit Code** | `1` (Failure) | `0` (Success) | CI/CD automated gate |

---

## 4. Where the System Breaks (Limits of Single-Process Architecture)

1. **Multi-Worker Process Isolation (e.g. `uvicorn --workers 4`):**
   - Python memory is isolated per OS process. With multiple Uvicorn worker processes, each worker maintains its own independent lock and state dictionary, resulting in multi-worker overselling.
2. **Horizontal Multi-Node Deployments:**
   - Single-node memory locks cannot coordinate across containers, Kubernetes pods, or load balancers.
3. **Crash Recovery & Fault Tolerance:**
   - If the process terminates, all active reservations, confirmations, and waitlist orders are lost.

---

## 5. What to Do Next with 2 More Weeks

1. **Distributed State via Redis & Lua Scripts:**
   - Migrate the reservation counter, waitlist FIFO queue (`RPUSH` / `LPOP`), and idempotency cache to Redis.
   - Use atomic Lua scripts for compare-and-swap inventory decrement to support arbitrary worker processes.
2. **Persistent Storage with Postgres & Outbox Pattern:**
   - Persist confirmed orders in PostgreSQL. Use transactional outbox with Kafka/RabbitMQ to dispatch asynchronous confirmation emails and payment reconciliation.
3. **Distributed Locks (Redlock) & TTL Keys:**
   - Use Redis Key Space notifications (`expired` events) to automatically trigger reservation timeouts across distributed workers.
4. **Adaptive Rate Limiting & Token Bucket:**
   - Introduce per-IP/per-user token bucket rate limiting to defend against botnet DDoS ticket scalpers before reaching the critical section.
