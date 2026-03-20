"""
Zing Customer State Management

Tracks customer information and conversation context for support sessions.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

# Session TTL configuration
SESSION_TTL_HOURS = 24  # Sessions expire after 24 hours
CLEANUP_INTERVAL_SECONDS = 300  # Run cleanup at most every 5 minutes


def _now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


@dataclass(slots=True)
class SupportInteraction:
    """Single support interaction or action taken."""

    timestamp: str
    action_type: str  # "question_answered", "ticket_created", "contact_provided"
    description: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class CustomerContext:
    """Customer information and support session context."""

    session_id: str
    customer_name: str = "Guest"
    customer_email: str = ""
    customer_phone: str = ""
    customer_company: str = ""

    # Support history
    interactions: List[SupportInteraction] = field(default_factory=list)

    # Session metadata
    session_started: str = field(default_factory=_now_iso)
    questions_asked: int = 0
    kb_articles_viewed: int = 0
    tickets_created: int = 0

    def log_interaction(
        self,
        action_type: str,
        description: str,
        metadata: Dict[str, Any] | None = None,
    ) -> None:
        """Log a support interaction."""
        interaction = SupportInteraction(
            timestamp=_now_iso(),
            action_type=action_type,
            description=description,
            metadata=metadata or {},
        )
        self.interactions.insert(0, interaction)  # Most recent first

    def update_customer_info(
        self,
        name: str | None = None,
        email: str | None = None,
        phone: str | None = None,
        company: str | None = None,
    ) -> None:
        """Update customer contact information."""
        if name:
            self.customer_name = name
        if email:
            self.customer_email = email
        if phone:
            self.customer_phone = phone
        if company:
            self.customer_company = company

    def increment_stat(self, stat_name: str) -> None:
        """Increment a session statistic."""
        if stat_name == "questions":
            self.questions_asked += 1
        elif stat_name == "kb_articles":
            self.kb_articles_viewed += 1
        elif stat_name == "tickets":
            self.tickets_created += 1

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = {
            "session_id": self.session_id,
            "customer_name": self.customer_name,
            "customer_email": self.customer_email,
            "customer_phone": self.customer_phone,
            "customer_company": self.customer_company,
            "session_started": self.session_started,
            "questions_asked": self.questions_asked,
            "kb_articles_viewed": self.kb_articles_viewed,
            "tickets_created": self.tickets_created,
            "interactions": [interaction.to_dict() for interaction in self.interactions],
        }
        return data


class ZingStateManager:
    """Manages per-session customer support state."""

    def __init__(self) -> None:
        self._sessions: Dict[str, CustomerContext] = {}
        self._last_cleanup: datetime = datetime.now(timezone.utc)

    def _cleanup_old_sessions(self) -> None:
        """Remove sessions older than TTL to prevent memory leaks."""
        now = datetime.now(timezone.utc)

        # Only run cleanup periodically to avoid overhead
        if (now - self._last_cleanup).total_seconds() < CLEANUP_INTERVAL_SECONDS:
            return

        self._last_cleanup = now
        cutoff = now - timedelta(hours=SESSION_TTL_HOURS)

        sessions_to_remove = []
        for session_id, context in self._sessions.items():
            try:
                session_started = datetime.fromisoformat(context.session_started)
                if session_started.tzinfo is None:
                    session_started = session_started.replace(tzinfo=timezone.utc)
                if session_started < cutoff:
                    sessions_to_remove.append(session_id)
            except (ValueError, AttributeError):
                # If we can't parse the timestamp, leave the session alone
                pass

        for session_id in sessions_to_remove:
            del self._sessions[session_id]

        if sessions_to_remove:
            print(f"[CLEANUP] Cleaned up {len(sessions_to_remove)} expired customer sessions")

    def _create_default_context(self, session_id: str) -> CustomerContext:
        """Create a new customer context for a session."""
        context = CustomerContext(
            session_id=session_id,
            customer_name="Guest",
            customer_email="",
            customer_phone="",
            customer_company="",
        )
        context.log_interaction(
            action_type="session_started",
            description="New support session initiated",
            metadata={"session_id": session_id},
        )
        return context

    def get_context(self, session_id: str) -> CustomerContext:
        """Get or create customer context for a session."""
        # Run cleanup periodically to prevent memory leaks
        self._cleanup_old_sessions()

        if session_id not in self._sessions:
            self._sessions[session_id] = self._create_default_context(session_id)
        return self._sessions[session_id]

    def log_kb_search(
        self,
        session_id: str,
        query: str,
        results_count: int,
    ) -> None:
        """Log a knowledge base search."""
        context = self.get_context(session_id)
        context.log_interaction(
            action_type="kb_search",
            description=f"Searched knowledge base for: {query}",
            metadata={"query": query, "results_count": results_count},
        )
        context.increment_stat("kb_articles")

    def log_ticket_creation(
        self,
        session_id: str,
        ticket_id: str,
        subject: str,
        priority: str,
    ) -> None:
        """Log a support ticket creation."""
        context = self.get_context(session_id)
        context.log_interaction(
            action_type="ticket_created",
            description=f"Created support ticket: {subject}",
            metadata={
                "ticket_id": ticket_id,
                "subject": subject,
                "priority": priority,
            },
        )
        context.increment_stat("tickets")

    def update_customer_info(
        self,
        session_id: str,
        name: str | None = None,
        email: str | None = None,
        phone: str | None = None,
        company: str | None = None,
    ) -> None:
        """Update customer information."""
        context = self.get_context(session_id)
        context.update_customer_info(
            name=name,
            email=email,
            phone=phone,
            company=company,
        )

    def to_dict(self, session_id: str) -> Dict[str, Any]:
        """Get session data as dictionary."""
        return self.get_context(session_id).to_dict()


# Global state manager instance
state_manager = ZingStateManager()
