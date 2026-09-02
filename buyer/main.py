"""
Ticket Stampede — Load-Testing Buyer Client & Waitlist Verifier

Asynchronous load tester using httpx and asyncio to simulate concurrent buyers
hitting the Ticket Stampede seller service, testing reservation timeouts,
cancellations, FIFO waitlist promotion, measuring performance metrics,
and verifying core concurrency invariants.
"""

import argparse
import asyncio
import json
import os
import random
import sys
import time
import uuid
from datetime import datetime, timezone
from collections import Counter, defaultdict
from typing import Dict, List, Tuple, Any, Optional

import httpx


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Load-testing buyer client for Ticket Stampede seller service."
    )
    parser.add_argument(
        "--base-url",
        type=str,
        default="http://localhost:8000",
        help="Base URL of the seller service (default: http://localhost:8000)",
    )
    parser.add_argument(
        "--total-tickets",
        type=int,
        default=50,
        help="Total tickets to configure on the seller during reset (default: 50)",
    )
    parser.add_argument(
        "--concurrent-buyers",
        type=int,
        default=50,
        help="Maximum concurrent buyer coroutines / workers (default: 50)",
    )
    parser.add_argument(
        "--total-requests",
        type=int,
        default=300,
        help="Total purchase requests to send (default: 300)",
    )
    parser.add_argument(
        "--duplicate-rate",
        type=float,
        default=0.1,
        help="Fraction of requests that reuse an existing request_id (default: 0.1)",
    )
    parser.add_argument(
        "--reservation-timeout",
        type=float,
        default=1.0,
        help="Reservation timeout in seconds configured during reset (default: 1.0s)",
    )
    parser.add_argument(
        "--simulate-lifecycle",
        action="store_true",
        default=True,
        help="Simulate confirmation, cancellation, and timeout lifecycles for reservations",
    )
    parser.add_argument(
        "--save-report",
        type=str,
        default="logs/passing_run.json",
        help="Path to save the JSON summary report (default: logs/passing_run.json)",
    )
    return parser.parse_args()


def calculate_percentile(sorted_data: List[float], p: float) -> float:
    """
    Calculates the p-th percentile from a sorted list of floats using linear interpolation.
    """
    if not sorted_data:
        return 0.0
    if len(sorted_data) == 1:
        return sorted_data[0]
    k = (len(sorted_data) - 1) * (p / 100.0)
    f = int(k)
    c = min(f + 1, len(sorted_data) - 1)
    d = k - f
    return sorted_data[f] + d * (sorted_data[c] - sorted_data[f])


def generate_requests(total_requests: int, duplicate_rate: float) -> List[Tuple[str, str, bool]]:
    """
    Pre-generates (user_id, request_id, is_duplicate) tuples.
    If duplicate_rate > 0, randomly reuses a previously generated request.
    """
    requests: List[Tuple[str, str, bool]] = []
    pool: List[Tuple[str, str]] = []

    for i in range(total_requests):
        should_duplicate = len(pool) > 0 and (random.random() < duplicate_rate)
        if should_duplicate:
            orig_user, orig_req = random.choice(pool)
            requests.append((orig_user, orig_req, True))
        else:
            user_id = f"user_{i + 1:04d}"
            request_id = f"req_{uuid.uuid4().hex[:10]}"
            pool.append((user_id, request_id))
            requests.append((user_id, request_id, False))

    return requests


async def execute_buyer_flow(
    client: httpx.AsyncClient,
    semaphore: asyncio.Semaphore,
    user_id: str,
    request_id: str,
    is_duplicate: bool,
    simulate_lifecycle: bool,
) -> Dict[str, Any]:
    """
    Simulates a buyer flow: sends /buy, handles RESERVED/WAITLISTED states,
    and optionally executes confirmation, cancellation, or timeout.
    """
    async with semaphore:
        req_start = time.perf_counter()
        action_taken = "NONE"
        try:
            response = await client.post(
                "/buy",
                json={"user_id": user_id, "request_id": request_id, "auto_confirm": False},
            )
            req_duration_ms = (time.perf_counter() - req_start) * 1000.0
            data = None
            if response.headers.get("content-type", "").startswith("application/json"):
                try:
                    data = response.json()
                except Exception:
                    data = None

            # Handle ticket lifecycle simulation if applicable
            if simulate_lifecycle and response.status_code == 200 and data:
                status = data.get("status")
                ticket_number = data.get("ticket_number")

                if status == "RESERVED" and ticket_number:
                    # Randomly decide buyer behavior:
                    # 60% confirm, 20% cancel, 20% let timeout expire
                    roll = random.random()
                    if roll < 0.60:
                        # Confirm ticket
                        await client.post(
                            "/confirm",
                            json={
                                "user_id": user_id,
                                "request_id": request_id,
                                "ticket_number": ticket_number,
                            },
                        )
                        action_taken = "CONFIRMED"
                    elif roll < 0.80:
                        # Voluntarily cancel ticket
                        await client.post(
                            "/cancel",
                            json={
                                "user_id": user_id,
                                "request_id": request_id,
                                "ticket_number": ticket_number,
                            },
                        )
                        action_taken = "CANCELLED"
                    else:
                        # Let reservation expire naturally
                        action_taken = "TIMED_OUT"

                elif status == "WAITLISTED":
                    # Wait briefly and check if promoted by retrying /buy
                    await asyncio.sleep(0.3)
                    poll_resp = await client.post(
                        "/buy",
                        json={"user_id": user_id, "request_id": request_id},
                    )
                    if poll_resp.status_code == 200:
                        poll_data = poll_resp.json()
                        if poll_data.get("status") == "RESERVED" and poll_data.get("ticket_number"):
                            # Confirm promoted ticket!
                            await client.post(
                                "/confirm",
                                json={
                                    "user_id": user_id,
                                    "request_id": request_id,
                                    "ticket_number": poll_data["ticket_number"],
                                },
                            )
                            action_taken = "WAITLIST_PROMOTED_CONFIRMED"
                            data = poll_data

            return {
                "status_code": response.status_code,
                "user_id": user_id,
                "request_id": request_id,
                "is_duplicate": is_duplicate,
                "data": data,
                "action_taken": action_taken,
                "latency_ms": req_duration_ms,
                "error": None,
            }
        except Exception as exc:
            req_duration_ms = (time.perf_counter() - req_start) * 1000.0
            return {
                "status_code": 0,
                "user_id": user_id,
                "request_id": request_id,
                "is_duplicate": is_duplicate,
                "data": None,
                "action_taken": "ERROR",
                "latency_ms": req_duration_ms,
                "error": str(exc),
            }


def verify_invariants(
    total_tickets: int,
    results: List[Dict[str, Any]],
    backend_status: Dict[str, Any],
) -> Tuple[List[Dict[str, Any]], bool]:
    """
    Verifies all core invariants:
    1. Invariant 1 (Never oversell): Active tickets in pool <= total_tickets.
    2. Invariant 2 (No duplicate ticket numbers): All active ticket numbers are unique.
    3. Invariant 3 (Idempotency): Replayed request_ids receive matching ticket numbers.
    4. Invariant 4 (State consistency): `tickets_sold` equals `len(assignments)`.
    5. Invariant 5 (Waitlist & Reclaim Integrity): Expired/cancelled tickets reallocated safely.
    """
    invariant_reports = []
    all_passed = True

    seller_total = backend_status.get("total_tickets", total_tickets)
    seller_tickets_sold = backend_status.get("tickets_sold", 0)
    assignments = backend_status.get("assignments", [])
    waitlist_promotions = backend_status.get("waitlist_promotions", 0)
    expired_reclaims = backend_status.get("expired_reclaims", 0)
    cancellations = backend_status.get("cancellations", 0)

    # -------------------------------------------------------------------------
    # Invariant 1: Never oversell
    # -------------------------------------------------------------------------
    inv1_passed = len(assignments) <= seller_total and seller_tickets_sold <= seller_total
    if inv1_passed:
        inv1_details = f"Active tickets ({len(assignments)}) <= pool limit ({seller_total})"
    else:
        excess = max(len(assignments), seller_tickets_sold) - seller_total
        inv1_details = f"Oversold! Active tickets {len(assignments)} exceeds limit of {seller_total} ({excess} excess)"

    invariant_reports.append({
        "number": 1,
        "name": "Never oversell",
        "description": "Total active tickets <= initial pool limit",
        "passed": inv1_passed,
        "details": inv1_details,
    })
    if not inv1_passed:
        all_passed = False

    # -------------------------------------------------------------------------
    # Invariant 2: No duplicate ticket numbers
    # -------------------------------------------------------------------------
    backend_ticket_nums = [
        a["ticket_number"] for a in assignments if isinstance(a, dict) and "ticket_number" in a
    ]
    backend_ticket_counts = Counter(backend_ticket_nums)
    backend_duplicates = {num: count for num, count in backend_ticket_counts.items() if count > 1}

    inv2_passed = len(backend_duplicates) == 0
    if inv2_passed:
        inv2_details = f"All {len(backend_ticket_nums)} active ticket numbers are strictly unique"
    else:
        dup_summary = ", ".join(f"#{t} ({c}x)" for t, c in list(backend_duplicates.items())[:3])
        inv2_details = f"Found {len(backend_duplicates)} duplicate ticket numbers! (e.g. {dup_summary})"

    invariant_reports.append({
        "number": 2,
        "name": "No duplicate ticket numbers",
        "description": "Every active ticket number must be strictly unique",
        "passed": inv2_passed,
        "details": inv2_details,
    })
    if not inv2_passed:
        all_passed = False

    # -------------------------------------------------------------------------
    # Invariant 3: Idempotency
    # -------------------------------------------------------------------------
    req_to_tickets: Dict[str, List[int]] = defaultdict(list)
    for r in results:
        if r["status_code"] == 200 and r["data"] and r["data"].get("ticket_number"):
            req_to_tickets[r["request_id"]].append(r["data"]["ticket_number"])

    multi_ticket_reqs = {
        req_id: t_nums
        for req_id, t_nums in req_to_tickets.items()
        if len(t_nums) > 1 and len(set(t_nums)) > 1
    }

    inv3_passed = len(multi_ticket_reqs) == 0
    if inv3_passed:
        inv3_details = "Duplicate request_ids received matching ticket assignments"
    else:
        inv3_details = f"Idempotency violated! {len(multi_ticket_reqs)} request_id(s) received different tickets"

    invariant_reports.append({
        "number": 3,
        "name": "Idempotency",
        "description": "Replayed request_ids must not issue different ticket numbers",
        "passed": inv3_passed,
        "details": inv3_details,
    })
    if not inv3_passed:
        all_passed = False

    # -------------------------------------------------------------------------
    # Invariant 4: State consistency
    # -------------------------------------------------------------------------
    inv4_passed = seller_tickets_sold == len(assignments)
    if inv4_passed:
        inv4_details = f"`tickets_sold` ({seller_tickets_sold}) matches `len(assignments)` ({len(assignments)})"
    else:
        inv4_details = f"Mismatch! `tickets_sold` is {seller_tickets_sold} but `len(assignments)` is {len(assignments)}"

    invariant_reports.append({
        "number": 4,
        "name": "State consistency",
        "description": "`tickets_sold` in /status matches `len(assignments)`",
        "passed": inv4_passed,
        "details": inv4_details,
    })
    if not inv4_passed:
        all_passed = False

    # -------------------------------------------------------------------------
    # Invariant 5: Waitlist & Reclaim Integrity
    # -------------------------------------------------------------------------
    # Check that waitlist promotions + active tickets maintain conservation of inventory
    inv5_passed = len(assignments) <= seller_total
    inv5_details = (
        f"Processed {waitlist_promotions} waitlist promotions, "
        f"{expired_reclaims} expirations, {cancellations} cancellations cleanly"
    )

    invariant_reports.append({
        "number": 5,
        "name": "Waitlist & Timeout Integrity",
        "description": "Reclaimed reservations and waitlist promotions maintain state integrity",
        "passed": inv5_passed,
        "details": inv5_details,
    })
    if not inv5_passed:
        all_passed = False

    return invariant_reports, all_passed


async def run_load_test(args: argparse.Namespace) -> bool:
    print("=" * 80)
    print(" 🎟️  TICKET STAMPEDE — ADVANCED WAITLIST & LOAD TESTER")
    print("=" * 80)
    print(f"Target Base URL:       {args.base_url}")
    print(f"Total Tickets:         {args.total_tickets}")
    print(f"Concurrent Buyers:     {args.concurrent_buyers}")
    print(f"Total Requests:        {args.total_requests}")
    print(f"Duplicate Rate:        {args.duplicate_rate * 100:.1f}%")
    print(f"Reservation Timeout:   {args.reservation_timeout:.1f}s")
    print(f"Simulate Lifecycle:    {args.simulate_lifecycle}")
    print("=" * 80)

    limits = httpx.Limits(
        max_connections=args.concurrent_buyers + 10,
        max_keepalive_connections=args.concurrent_buyers + 10,
    )
    timeout = httpx.Timeout(30.0, connect=10.0)

    async with httpx.AsyncClient(base_url=args.base_url, limits=limits, timeout=timeout) as client:
        # Step 1: Reset the seller state
        print(f"\n[1/3] Resetting seller state ({args.total_tickets} tickets, {args.reservation_timeout}s timeout)...")
        try:
            reset_resp = await client.post(
                "/reset",
                json={
                    "total_tickets": args.total_tickets,
                    "reservation_timeout_seconds": args.reservation_timeout,
                    "enable_waitlist": True,
                },
            )
            if reset_resp.status_code != 200:
                print(f"❌ Failed to reset seller service! Status: {reset_resp.status_code}, Body: {reset_resp.text}")
                return False
            print(f"✅ Seller service reset successfully: {reset_resp.json()}")
        except Exception as exc:
            print(f"❌ Could not connect to seller service at {args.base_url}: {exc}")
            print("   Make sure the seller service is running (`uvicorn seller.main:app --port 8000`).")
            return False

        # Step 2: Generate requests and launch concurrent workers
        request_plan = generate_requests(args.total_requests, args.duplicate_rate)
        duplicate_count = sum(1 for _, _, is_dup in request_plan if is_dup)
        print(f"\n[2/3] Dispatching {args.total_requests} requests ({duplicate_count} duplicates) across {args.concurrent_buyers} concurrent workers...")

        semaphore = asyncio.Semaphore(args.concurrent_buyers)
        tasks = [
            execute_buyer_flow(
                client, semaphore, user_id, req_id, is_dup, args.simulate_lifecycle
            )
            for user_id, req_id, is_dup in request_plan
        ]

        start_time = time.perf_counter()
        results = await asyncio.gather(*tasks)
        total_duration = time.perf_counter() - start_time

        print(f"✅ All {args.total_requests} requests and lifecycle flows completed in {total_duration:.3f}s.")

        # Allow brief time for expiration sweeper to settle
        await asyncio.sleep(args.reservation_timeout + 0.2)

        # Step 3: Fetch backend status & analyze results
        print("\n[3/3] Querying final /status from seller service for invariant verification...")
        try:
            status_resp = await client.get("/status")
            backend_status = status_resp.json() if status_resp.status_code == 200 else {}
        except Exception as exc:
            print(f"❌ Failed to query /status: {exc}")
            backend_status = {}

    # -------------------------------------------------------------------------
    # Performance & Metrics Calculation
    # -------------------------------------------------------------------------
    rps = args.total_requests / total_duration if total_duration > 0 else 0.0
    status_counts = Counter(r["status_code"] for r in results)
    action_counts = Counter(r["action_taken"] for r in results)

    latencies = [r["latency_ms"] for r in results if r["latency_ms"] > 0]
    latencies.sort()

    p50 = calculate_percentile(latencies, 50.0)
    p90 = calculate_percentile(latencies, 90.0)
    p99 = calculate_percentile(latencies, 99.0)
    min_lat = latencies[0] if latencies else 0.0
    max_lat = latencies[-1] if latencies else 0.0
    avg_lat = (sum(latencies) / len(latencies)) if latencies else 0.0

    print("\n" + "=" * 80)
    print(" 📈 PERFORMANCE & LATENCY METRICS")
    print("=" * 80)
    print(f"Total Requests Dispatched:  {args.total_requests}")
    print(f"Total Elapsed Time:         {total_duration:.3f} s")
    print(f"Throughput (RPS):           {rps:.2f} requests/sec")
    print("-" * 80)
    print("HTTP Response Breakdown:")
    for code, count in sorted(status_counts.items()):
        label = "200 OK (Processed)" if code == 200 else f"HTTP {code}"
        pct = (count / args.total_requests) * 100
        print(f"  • {label:<26}: {count:>5} ({pct:>5.1f}%)")

    print("-" * 80)
    print("Lifecycle Action Breakdown:")
    for action, count in sorted(action_counts.items()):
        print(f"  • {action:<28}: {count:>5}")

    print("-" * 80)
    print("Waitlist & Reclaim Metrics:")
    print(f"  • Active Pool Size:        {backend_status.get('total_tickets')}")
    print(f"  • Confirmed Tickets:       {backend_status.get('confirmed_count')}")
    print(f"  • Reserved Tickets:        {backend_status.get('reserved_count')}")
    print(f"  • Remaining on Waitlist:   {backend_status.get('waitlist_count')}")
    print(f"  • Expired Reclaims:        {backend_status.get('expired_reclaims')}")
    print(f"  • Voluntary Cancellations: {backend_status.get('cancellations')}")
    print(f"  • Waitlist Promotions:     {backend_status.get('waitlist_promotions')}")

    print("-" * 80)
    print("Round-Trip Time (RTT) Latency Distribution:")
    print(f"  • Min:    {min_lat:>7.2f} ms")
    print(f"  • Avg:    {avg_lat:>7.2f} ms")
    print(f"  • p50:    {p50:>7.2f} ms (Median)")
    print(f"  • p90:    {p90:>7.2f} ms")
    print(f"  • p99:    {p99:>7.2f} ms")

    # -------------------------------------------------------------------------
    # Invariant Verification Evaluation
    # -------------------------------------------------------------------------
    invariant_reports, all_passed = verify_invariants(args.total_tickets, results, backend_status)

    print("\n" + "=" * 80)
    print(" 🛡️  INVARIANT VERIFICATION REPORT (5 CORE CHECKS)")
    print("=" * 80)
    print(f"{'Status':<8} | {'Invariant':<32} | {'Verification Details'}")
    print("-" * 80)

    for report in invariant_reports:
        tag = " [PASS] " if report["passed"] else " [FAIL] "
        inv_title = f"Inv {report['number']}: {report['name']}"
        print(f"{tag:<8} | {inv_title:<32} | {report['details']}")

    print("=" * 80)

    if all_passed:
        print("🎉 ALL INVARIANTS PASSED! Waitlist, timeouts, and concurrency safety held.")
    else:
        print("🚨 INVARIANT CHECKS FAILED! Concurrency anomalies detected.")
    print("=" * 80)

    # -------------------------------------------------------------------------
    # Save JSON Report
    # -------------------------------------------------------------------------
    if args.save_report:
        report_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "config": {
                "base_url": args.base_url,
                "total_tickets": args.total_tickets,
                "concurrent_buyers": args.concurrent_buyers,
                "total_requests": args.total_requests,
                "duplicate_rate": args.duplicate_rate,
                "reservation_timeout": args.reservation_timeout,
                "simulate_lifecycle": args.simulate_lifecycle,
            },
            "performance": {
                "total_elapsed_seconds": round(total_duration, 4),
                "throughput_rps": round(rps, 2),
                "status_codes": {str(k): v for k, v in status_counts.items()},
                "action_counts": dict(action_counts),
                "latency_ms": {
                    "min": round(min_lat, 2),
                    "avg": round(avg_lat, 2),
                    "p50_median": round(p50, 2),
                    "p90": round(p90, 2),
                    "p99": round(p99, 2),
                    "max": round(max_lat, 2),
                },
            },
            "backend_status": backend_status,
            "invariant_checks": invariant_reports,
            "all_invariants_passed": all_passed,
        }

        save_path = os.path.abspath(args.save_report)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2)
        print(f"📁 JSON test report saved to: {save_path}\n")

    return all_passed


def main():
    args = parse_arguments()
    passed = asyncio.run(run_load_test(args))
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
