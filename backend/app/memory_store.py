from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

from chatkit.store import NotFoundError, Store
from chatkit.types import Attachment, Page, Thread, ThreadItem, ThreadMetadata

# Session TTL configuration
SESSION_TTL_HOURS = 24  # Sessions expire after 24 hours
CLEANUP_INTERVAL_SECONDS = 300  # Run cleanup at most every 5 minutes


@dataclass
class _ThreadState:
    thread: ThreadMetadata
    items: List[ThreadItem]


@dataclass
class _AttachmentState:
    attachment: Attachment
    created_at: datetime


class MemoryStore(Store[dict[str, Any]]):
    """Simple in-memory store compatible with the ChatKit server interface."""

    def __init__(self) -> None:
        self._threads: Dict[str, _ThreadState] = {}
        self._attachments: Dict[str, _AttachmentState] = {}  # Store attachments with timestamps
        self._last_cleanup: datetime = datetime.now(timezone.utc)

    def _cleanup_old_sessions(self) -> None:
        """Remove sessions and attachments older than TTL to prevent memory leaks."""
        now = datetime.now(timezone.utc)

        # Only run cleanup periodically to avoid overhead on every request
        if (now - self._last_cleanup).total_seconds() < CLEANUP_INTERVAL_SECONDS:
            return

        self._last_cleanup = now
        cutoff = now - timedelta(hours=SESSION_TTL_HOURS)

        # Clean up old threads
        threads_to_remove = []
        for thread_id, state in self._threads.items():
            created_at = state.thread.created_at
            if created_at:
                # Handle both timezone-aware and naive datetimes
                if created_at.tzinfo is None:
                    created_at = created_at.replace(tzinfo=timezone.utc)
                if created_at < cutoff:
                    threads_to_remove.append(thread_id)

        for thread_id in threads_to_remove:
            del self._threads[thread_id]

        if threads_to_remove:
            print(f"[CLEANUP] Cleaned up {len(threads_to_remove)} expired sessions")

        # Clean up old attachments
        attachments_to_remove = []
        for attachment_id, state in self._attachments.items():
            created_at = state.created_at
            if created_at.tzinfo is None:
                created_at = created_at.replace(tzinfo=timezone.utc)
            if created_at < cutoff:
                attachments_to_remove.append(attachment_id)

        for attachment_id in attachments_to_remove:
            del self._attachments[attachment_id]

        if attachments_to_remove:
            print(f"[CLEANUP] Cleaned up {len(attachments_to_remove)} expired attachments")

    @staticmethod
    def _coerce_thread_metadata(thread: ThreadMetadata | Thread) -> ThreadMetadata:
        """Return thread metadata without any embedded items (openai-chatkit>=1.0)."""
        has_items = isinstance(thread, Thread) or "items" in getattr(
            thread, "model_fields_set", set()
        )
        if not has_items:
            return thread.model_copy(deep=True)

        data = thread.model_dump()
        data.pop("items", None)
        return ThreadMetadata(**data).model_copy(deep=True)

    # -- Thread metadata -------------------------------------------------
    async def load_thread(self, thread_id: str, context: dict[str, Any]) -> ThreadMetadata:
        state = self._threads.get(thread_id)
        if not state:
            raise NotFoundError(f"Thread {thread_id} not found")
        return self._coerce_thread_metadata(state.thread)

    async def save_thread(self, thread: ThreadMetadata, context: dict[str, Any]) -> None:
        # Run cleanup periodically to prevent memory leaks
        self._cleanup_old_sessions()

        metadata = self._coerce_thread_metadata(thread)
        state = self._threads.get(thread.id)
        if state:
            state.thread = metadata
        else:
            self._threads[thread.id] = _ThreadState(
                thread=metadata,
                items=[],
            )

    async def load_threads(
        self,
        limit: int,
        after: str | None,
        order: str,
        context: dict[str, Any],
    ) -> Page[ThreadMetadata]:
        threads = sorted(
            (self._coerce_thread_metadata(state.thread) for state in self._threads.values()),
            key=lambda t: t.created_at or datetime.min,
            reverse=(order == "desc"),
        )

        if after:
            index_map = {thread.id: idx for idx, thread in enumerate(threads)}
            start = index_map.get(after, -1) + 1
        else:
            start = 0

        slice_threads = threads[start : start + limit + 1]
        has_more = len(slice_threads) > limit
        slice_threads = slice_threads[:limit]
        next_after = slice_threads[-1].id if has_more and slice_threads else None
        return Page(
            data=slice_threads,
            has_more=has_more,
            after=next_after,
        )

    async def delete_thread(self, thread_id: str, context: dict[str, Any]) -> None:
        self._threads.pop(thread_id, None)

    # -- Thread items ----------------------------------------------------
    def _items(self, thread_id: str) -> List[ThreadItem]:
        state = self._threads.get(thread_id)
        if state is None:
            state = _ThreadState(
                thread=ThreadMetadata(id=thread_id, created_at=datetime.utcnow()),
                items=[],
            )
            self._threads[thread_id] = state
        return state.items

    async def load_thread_items(
        self,
        thread_id: str,
        after: str | None,
        limit: int,
        order: str,
        context: dict[str, Any],
    ) -> Page[ThreadItem]:
        items = [item.model_copy(deep=True) for item in self._items(thread_id)]
        items.sort(
            key=lambda item: getattr(item, "created_at", datetime.utcnow()),
            reverse=(order == "desc"),
        )

        if after:
            index_map = {item.id: idx for idx, item in enumerate(items)}
            start = index_map.get(after, -1) + 1
        else:
            start = 0

        slice_items = items[start : start + limit + 1]
        has_more = len(slice_items) > limit
        slice_items = slice_items[:limit]
        next_after = slice_items[-1].id if has_more and slice_items else None
        return Page(data=slice_items, has_more=has_more, after=next_after)

    async def add_thread_item(
        self, thread_id: str, item: ThreadItem, context: dict[str, Any]
    ) -> None:
        self._items(thread_id).append(item.model_copy(deep=True))

    async def save_item(self, thread_id: str, item: ThreadItem, context: dict[str, Any]) -> None:
        items = self._items(thread_id)
        for idx, existing in enumerate(items):
            if existing.id == item.id:
                items[idx] = item.model_copy(deep=True)
                return
        items.append(item.model_copy(deep=True))

    async def load_item(self, thread_id: str, item_id: str, context: dict[str, Any]) -> ThreadItem:
        for item in self._items(thread_id):
            if item.id == item_id:
                return item.model_copy(deep=True)
        raise NotFoundError(f"Item {item_id} not found")

    async def delete_thread_item(
        self, thread_id: str, item_id: str, context: dict[str, Any]
    ) -> None:
        items = self._items(thread_id)
        self._threads[thread_id].items = [item for item in items if item.id != item_id]

    # -- Files -----------------------------------------------------------
    # In-memory attachment storage for ChatKit file uploads.
    # Note: This is suitable for development/demo but for production use
    # a persistent store with proper auth would be recommended.

    async def save_attachment(
        self,
        attachment: Attachment,
        context: dict[str, Any],
    ) -> None:
        """Store an attachment in memory with timestamp for cleanup."""
        self._attachments[attachment.id] = _AttachmentState(
            attachment=attachment,
            created_at=datetime.now(timezone.utc),
        )

    async def load_attachment(
        self,
        attachment_id: str,
        context: dict[str, Any],
    ) -> Attachment:
        """Load an attachment from memory by ID."""
        state = self._attachments.get(attachment_id)
        if state is None:
            raise NotFoundError(f"Attachment {attachment_id} not found")
        return state.attachment

    async def delete_attachment(self, attachment_id: str, context: dict[str, Any]) -> None:
        """Delete an attachment from memory."""
        if attachment_id in self._attachments:
            del self._attachments[attachment_id]
