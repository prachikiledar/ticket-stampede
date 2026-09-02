"""
Ticket Stampede — Seller Service (ADVANCED WAITLIST & RESERVATION TIMEOUTS)

Features:
1. Concurrency-safe atomic ticket operations via asyncio.Lock.
2. Reservation Lifecycle: Tickets start in RESERVED state with a configurable timeout.
3. Confirmation (/confirm) & Voluntary Cancellation (/cancel).
4. FIFO Waitlist: Saturated sales queue subsequent buyers into a waitlist.
5. Automatic Expiration & Waitlist Promotion: Expired or cancelled reservations are
   atomically reclaimed and promoted to the next waiting user in strict FIFO order.
"""

import asyncio
import time
from typing import Dict, List, Optional, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# In-Memory State & Lock
# ---------------------------------------------------------------------------
state_lock = asyncio.Lock()

state: Dict[str, Any] = {
    "total_tickets": 0,
    "next_ticket_id": 0,
    "reservation_timeout_seconds": 5.0,
    "enable_waitlist": True,
    # Active tickets: ticket_number -> ticket record
    "tickets": {},
    # FIFO Waitlist: list of waitlist entry dicts
    "waitlist": [],
    # Idempotency Cache: request_id -> ticket or waitlist record
    "seen_requests": {},
    # Metrics
    "expired_count": 0,
    "cancelled_count": 0,
    "waitlist_promotions": 0,
}


def _reclaim_expired_tickets_locked(now: Optional[float] = None) -> List[int]:
    """
    Reclaims any expired reservations and awards them to the next user in the waitlist.
    MUST be called while holding `state_lock`.
    """
    if now is None:
        now = time.time()

    reclaimed_ticket_numbers = []
    
    # Find all expired reservations
    for ticket_number, t in list(state["tickets"].items()):
        if t["status"] == "RESERVED" and t["expires_at"] is not None and t["expires_at"] <= now:
            state["expired_count"] += 1
            reclaimed_ticket_numbers.append(ticket_number)
            
            # Invalidate old holder in seen_requests
            old_req_id = t["request_id"]
            if old_req_id in state["seen_requests"]:
                state["seen_requests"][old_req_id] = {
                    **state["seen_requests"][old_req_id],
                    "status": "EXPIRED",
                }

            # If there are users waiting in the FIFO waitlist, award ticket to the head
            if state["waitlist"]:
                next_waiter = state["waitlist"].pop(0)
                timeout = state["reservation_timeout_seconds"]
                new_record = {
                    "ticket_number": ticket_number,
                    "user_id": next_waiter["user_id"],
                    "request_id": next_waiter["request_id"],
                    "status": "RESERVED",
                    "reserved_at": now,
                    "expires_at": now + timeout if timeout > 0 else None,
                    "promoted_from_waitlist": True,
                }
                state["tickets"][ticket_number] = new_record
                state["seen_requests"][next_waiter["request_id"]] = new_record
                state["waitlist_promotions"] += 1
            else:
                # No one on waitlist: ticket returns to free pool
                del state["tickets"][ticket_number]

    return reclaimed_ticket_numbers


async def expiration_sweeper_task():
    """
    Background worker that runs periodically to sweep and promote expired tickets.
    """
    while True:
        try:
            await asyncio.sleep(0.1)
            async with state_lock:
                if state["total_tickets"] > 0:
                    _reclaim_expired_tickets_locked()
        except asyncio.CancelledError:
            break
        except Exception:
            await asyncio.sleep(0.5)


@asynccontextmanager
async def lifespan(app: FastAPI):
    sweeper = asyncio.create_task(expiration_sweeper_task())
    yield
    sweeper.cancel()
    try:
        await sweeper
    except asyncio.CancelledError:
        pass


app = FastAPI(
    title="Ticket Stampede - Advanced Seller Service",
    description="Concurrency-safe ticket seller with FIFO waitlist and reservation timeouts.",
    version="2.0.0",
    lifespan=lifespan,
)


# ---------------------------------------------------------------------------
# Request / Response Schemas
# ---------------------------------------------------------------------------
class ResetRequest(BaseModel):
    total_tickets: int = Field(..., ge=0, description="Total tickets in the initial pool")
    reservation_timeout_seconds: float = Field(
        default=5.0, ge=0.0, description="Seconds before an unconfirmed reservation expires"
    )
    enable_waitlist: bool = Field(default=True, description="Enable FIFO waitlist when sold out")


class BuyRequest(BaseModel):
    user_id: str = Field(..., min_length=1, description="Unique identifier for the buyer")
    request_id: str = Field(..., min_length=1, description="Idempotency key for this request")
    auto_confirm: bool = Field(
        default=False, description="Immediately confirm ticket instead of holding in RESERVED state"
    )


class ConfirmRequest(BaseModel):
    user_id: str
    request_id: str
    ticket_number: int


class CancelRequest(BaseModel):
    user_id: str
    request_id: str
    ticket_number: int


class BuyResponse(BaseModel):
    status: str  # "RESERVED", "CONFIRMED", "WAITLISTED", "EXPIRED"
    ticket_number: Optional[int] = None
    user_id: str
    request_id: str
    waitlist_position: Optional[int] = None
    expires_in_seconds: Optional[float] = None
    message: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.post("/reset")
async def reset_sale(req: ResetRequest):
    """
    Atomically resets all sale state, waitlist, and timers.
    """
    async with state_lock:
        state["total_tickets"] = req.total_tickets
        state["next_ticket_id"] = 0
        state["reservation_timeout_seconds"] = req.reservation_timeout_seconds
        state["enable_waitlist"] = req.enable_waitlist
        state["tickets"] = {}
        state["waitlist"] = []
        state["seen_requests"] = {}
        state["expired_count"] = 0
        state["cancelled_count"] = 0
        state["waitlist_promotions"] = 0

        return {
            "message": "Sale reset successfully.",
            "total_tickets": state["total_tickets"],
            "reservation_timeout_seconds": state["reservation_timeout_seconds"],
            "enable_waitlist": state["enable_waitlist"],
        }


@app.post("/buy", response_model=BuyResponse)
async def buy_ticket(req: BuyRequest):
    """
    Attempts to purchase, reserve, or waitlist a ticket with strict concurrency safety.
    """
    now = time.time()
    async with state_lock:
        # Step 1: Reclaim any currently expired tickets
        _reclaim_expired_tickets_locked(now)

        # Step 2: Idempotency Check
        if req.request_id in state["seen_requests"]:
            cached = state["seen_requests"][req.request_id]
            status = cached.get("status", "RESERVED")
            
            # If user has an active ticket
            if status in ("RESERVED", "CONFIRMED") and cached.get("ticket_number") in state["tickets"]:
                t = state["tickets"][cached["ticket_number"]]
                exp_in = max(t["expires_at"] - now, 0.0) if t.get("expires_at") else None
                return BuyResponse(
                    status=t["status"],
                    ticket_number=t["ticket_number"],
                    user_id=req.user_id,
                    request_id=req.request_id,
                    expires_in_seconds=exp_in,
                    message="Idempotent duplicate request: existing ticket returned",
                )

            # If user's reservation was cancelled or expired
            if status in ("CANCELLED", "EXPIRED"):
                return BuyResponse(
                    status=status,
                    ticket_number=cached.get("ticket_number"),
                    user_id=req.user_id,
                    request_id=req.request_id,
                    message=f"Idempotent response: request was previously {status.lower()}",
                )

            # If user is still in the waitlist
            if status == "WAITLISTED":
                # Find current position in waitlist
                pos = next(
                    (i + 1 for i, w in enumerate(state["waitlist"]) if w["request_id"] == req.request_id),
                    None,
                )
                if pos is not None:
                    return BuyResponse(
                        status="WAITLISTED",
                        ticket_number=None,
                        user_id=req.user_id,
                        request_id=req.request_id,
                        waitlist_position=pos,
                        message=f"You are currently #{pos} on the waitlist",
                    )

        # Step 3: Check Available Inventory
        active_count = len(state["tickets"])
        if active_count < state["total_tickets"]:
            # Allocate ticket
            state["next_ticket_id"] += 1
            ticket_number = state["next_ticket_id"]

            timeout = state["reservation_timeout_seconds"]
            status = "CONFIRMED" if req.auto_confirm else "RESERVED"
            expires_at = None if req.auto_confirm or timeout <= 0 else now + timeout

            record = {
                "ticket_number": ticket_number,
                "user_id": req.user_id,
                "request_id": req.request_id,
                "status": status,
                "reserved_at": now,
                "expires_at": expires_at,
                "promoted_from_waitlist": False,
            }
            state["tickets"][ticket_number] = record
            state["seen_requests"][req.request_id] = record

            exp_in = timeout if status == "RESERVED" and timeout > 0 else None
            return BuyResponse(
                status=status,
                ticket_number=ticket_number,
                user_id=req.user_id,
                request_id=req.request_id,
                expires_in_seconds=exp_in,
                message="Ticket reserved successfully" if status == "RESERVED" else "Ticket purchased and confirmed",
            )

        # Step 4: Saturated inventory -> FIFO Waitlist or 409 Sold Out
        if state["enable_waitlist"]:
            waitlist_entry = {
                "user_id": req.user_id,
                "request_id": req.request_id,
                "joined_at": now,
                "status": "WAITLISTED",
            }
            state["waitlist"].append(waitlist_entry)
            state["seen_requests"][req.request_id] = waitlist_entry
            position = len(state["waitlist"])

            return BuyResponse(
                status="WAITLISTED",
                ticket_number=None,
                user_id=req.user_id,
                request_id=req.request_id,
                waitlist_position=position,
                message=f"Sold out! Added to FIFO waitlist at position #{position}",
            )

        raise HTTPException(
            status_code=409,
            detail=f"Sold out! All {state['total_tickets']} tickets are currently reserved or sold.",
        )


@app.post("/confirm")
async def confirm_ticket(req: ConfirmRequest):
    """
    Confirms a reserved ticket, transitioning it from RESERVED to permanent CONFIRMED.
    """
    now = time.time()
    async with state_lock:
        _reclaim_expired_tickets_locked(now)

        if req.ticket_number not in state["tickets"]:
            raise HTTPException(status_code=404, detail="Ticket not found or already expired.")

        ticket = state["tickets"][req.ticket_number]
        if ticket["request_id"] != req.request_id or ticket["user_id"] != req.user_id:
            raise HTTPException(status_code=403, detail="Ticket does not belong to this request.")

        if ticket["status"] == "CONFIRMED":
            return {"message": "Ticket is already confirmed.", "ticket_number": req.ticket_number}

        ticket["status"] = "CONFIRMED"
        ticket["expires_at"] = None

        return {
            "message": "Ticket confirmed successfully.",
            "ticket_number": req.ticket_number,
            "status": "CONFIRMED",
        }


@app.post("/cancel")
async def cancel_ticket(req: CancelRequest):
    """
    Voluntarily cancels a ticket/reservation and awards it immediately to the FIFO waitlist.
    """
    now = time.time()
    async with state_lock:
        if req.ticket_number not in state["tickets"]:
            raise HTTPException(status_code=404, detail="Ticket not found or already expired.")

        ticket = state["tickets"][req.ticket_number]
        if ticket["request_id"] != req.request_id or ticket["user_id"] != req.user_id:
            raise HTTPException(status_code=403, detail="Ticket does not belong to this request.")

        state["cancelled_count"] += 1
        ticket_number = req.ticket_number

        # Invalidate old record
        if req.request_id in state["seen_requests"]:
            state["seen_requests"][req.request_id] = {
                **state["seen_requests"][req.request_id],
                "status": "CANCELLED",
            }

        # Promote head of waitlist if waiting
        if state["waitlist"]:
            next_waiter = state["waitlist"].pop(0)
            timeout = state["reservation_timeout_seconds"]
            new_record = {
                "ticket_number": ticket_number,
                "user_id": next_waiter["user_id"],
                "request_id": next_waiter["request_id"],
                "status": "RESERVED",
                "reserved_at": now,
                "expires_at": now + timeout if timeout > 0 else None,
                "promoted_from_waitlist": True,
            }
            state["tickets"][ticket_number] = new_record
            state["seen_requests"][next_waiter["request_id"]] = new_record
            state["waitlist_promotions"] += 1
            promoted_to = next_waiter["user_id"]
        else:
            del state["tickets"][ticket_number]
            promoted_to = None

        return {
            "message": "Ticket cancelled successfully.",
            "ticket_number": ticket_number,
            "promoted_to_waitlist_user": promoted_to,
        }


@app.get("/status")
async def get_status():
    """
    Returns an atomic snapshot of current statistics, active tickets, and waitlist queue.
    """
    now = time.time()
    async with state_lock:
        _reclaim_expired_tickets_locked(now)

        active_tickets = list(state["tickets"].values())
        confirmed_count = sum(1 for t in active_tickets if t["status"] == "CONFIRMED")
        reserved_count = sum(1 for t in active_tickets if t["status"] == "RESERVED")

        # Map format compatible with previous tests
        assignments = [
            {
                "ticket_number": t["ticket_number"],
                "user_id": t["user_id"],
                "request_id": t["request_id"],
                "status": t["status"],
            }
            for t in sorted(active_tickets, key=lambda x: x["ticket_number"])
        ]

        return {
            "total_tickets": state["total_tickets"],
            "tickets_sold": len(active_tickets),
            "tickets_remaining": max(state["total_tickets"] - len(active_tickets), 0),
            "confirmed_count": confirmed_count,
            "reserved_count": reserved_count,
            "waitlist_count": len(state["waitlist"]),
            "waitlist": [
                {"position": i + 1, "user_id": w["user_id"], "request_id": w["request_id"]}
                for i, w in enumerate(state["waitlist"])
            ],
            "expired_reclaims": state["expired_count"],
            "cancellations": state["cancelled_count"],
            "waitlist_promotions": state["waitlist_promotions"],
            "assignments": assignments,
        }
