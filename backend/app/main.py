from __future__ import annotations

# Load environment variables from .env file FIRST (before any other imports use them)
from dotenv import load_dotenv
load_dotenv()

import base64
import os
import sys
import traceback
import uuid
from typing import Any, AsyncIterator
from datetime import datetime, timedelta

from agents import Runner
from chatkit.agents import AgentContext, Message, ThreadItemConverter, stream_agent_response
from chatkit.server import ChatKitServer, StreamingResult
from chatkit.store import AttachmentStore
from chatkit.types import (
    Attachment,
    AttachmentCreateParams,
    ClientToolCallItem,
    FileAttachment,
    ImageAttachment,
    ThreadMetadata,
    ThreadStreamEvent,
    UserMessageItem,
)
from fastapi import Depends, FastAPI, Query, Request, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, StreamingResponse
from openai.types.responses import ResponseInputContentParam, ResponseInputTextParam, ResponseInputImageParam
from pydantic import BaseModel, Field
from starlette.responses import JSONResponse
from typing import Optional, Literal

from .zing_state import ZingStateManager, CustomerContext, state_manager
from .memory_store import MemoryStore
from .zing_support_agent import build_zing_support_agent, is_valid_email
from .hubspot_integration import hubspot_manager
from .title_agent import generate_thread_title

# =============================================================================
# VERSION & LOGGING - Use this to verify deployment
# =============================================================================
BACKEND_VERSION = "2.0.0-chatkit-widgets"
DEPLOY_TIMESTAMP = "2025-11-29T09:00:00Z"

# =============================================================================
# In-Memory Attachment Store
# =============================================================================
# Simple dict to store uploaded attachment data URLs by ID.
# When ChatKit sends a message with attachments, it may not include the full
# data URL - only the attachment ID. This store allows us to look up the
# original data URL when converting attachments to message content.
#
# Cleanup: Attachments older than 24 hours are automatically removed.
# =============================================================================
attachment_data_store: dict[str, tuple[str, datetime]] = {}  # attachment_id -> (data_url, created_at)
attachment_metadata_store: dict[str, Attachment] = {}  # attachment_id -> Attachment object (legacy, may be removed)

# Cleanup configuration
ATTACHMENT_TTL_HOURS = 24
_last_attachment_cleanup: datetime = datetime.utcnow()

DEFAULT_THREAD_ID = "demo_default_thread"


def cleanup_old_attachments() -> None:
    """Remove attachments older than TTL to prevent memory leaks."""
    global _last_attachment_cleanup
    now = datetime.utcnow()

    # Only run cleanup every 5 minutes
    if (now - _last_attachment_cleanup).total_seconds() < 300:
        return

    _last_attachment_cleanup = now
    cutoff = now - timedelta(hours=ATTACHMENT_TTL_HOURS)

    # Clean up data store
    to_remove = [
        att_id for att_id, (_, created_at) in attachment_data_store.items()
        if created_at < cutoff
    ]
    for att_id in to_remove:
        del attachment_data_store[att_id]
        if att_id in attachment_metadata_store:
            del attachment_metadata_store[att_id]

    if to_remove:
        log("CLEANUP", f"Removed {len(to_remove)} expired attachments from data store")


class ZingAttachmentStore(AttachmentStore[dict[str, Any]]):
    """
    In-memory attachment store for ChatKit file uploads.

    This implements the AttachmentStore interface required by ChatKitServer
    to enable file upload functionality. Without this, the attachment button
    in the ChatKit UI will be disabled or non-functional.

    For direct uploads, the client POSTs to /support/upload, which stores
    the file data and returns an Attachment object. This store then provides
    lookup/delete capabilities for those attachments.
    """

    def generate_attachment_id(self, mime_type: str, context: dict[str, Any]) -> str:
        """Generate a unique ID for a new attachment."""
        return f"att_{uuid.uuid4().hex[:16]}"

    async def create_attachment(
        self, input: AttachmentCreateParams, context: dict[str, Any]
    ) -> Attachment:
        """
        Create an attachment record. This is called during two-phase upload.
        For direct upload (which we use), this may not be called since the
        upload endpoint handles everything.
        """
        log("ATTACHMENT_STORE", f"create_attachment called - input type: {type(input)}")

        attachment_id = self.generate_attachment_id(input.mime_type, context)
        timestamp = datetime.utcnow().isoformat() + "Z"

        # Determine if it's an image based on MIME type
        is_image = input.mime_type.startswith("image/")

        if is_image:
            attachment = ImageAttachment(
                id=attachment_id,
                type="image",
                name=input.name or "image",
                mime_type=input.mime_type,
                created_at=timestamp,
                preview_url=None,  # Will be set after upload
            )
        else:
            attachment = FileAttachment(
                id=attachment_id,
                type="file",
                name=input.name or "file",
                mime_type=input.mime_type,
                size=0,  # Will be set after upload
                created_at=timestamp,
            )

        # Store the metadata
        attachment_metadata_store[attachment_id] = attachment
        log("ATTACHMENT_STORE", f"Created attachment: id={attachment_id}, type={'image' if is_image else 'file'}")

        return attachment

    async def delete_attachment(self, attachment_id: str, context: dict[str, Any]) -> None:
        """Delete an attachment from the store."""
        log("ATTACHMENT_STORE", f"delete_attachment called - id={attachment_id}")

        # Remove from both stores
        if attachment_id in attachment_data_store:
            del attachment_data_store[attachment_id]
        if attachment_id in attachment_metadata_store:
            del attachment_metadata_store[attachment_id]

        log("ATTACHMENT_STORE", f"Deleted attachment: id={attachment_id}")


# Create a global attachment store instance
zing_attachment_store = ZingAttachmentStore()


def log(category: str, message: str, level: str = "INFO") -> None:
    """Centralized logging with timestamp and category."""
    timestamp = datetime.utcnow().isoformat() + "Z"
    print(f"[{timestamp}] [{level}] [{category}] {message}", flush=True)


def log_error(category: str, message: str, exc: Exception | None = None) -> None:
    """Log error with optional exception details."""
    timestamp = datetime.utcnow().isoformat() + "Z"
    error_msg = f"[{timestamp}] [ERROR] [{category}] {message}"
    if exc:
        error_msg += f"\n  Exception: {type(exc).__name__}: {str(exc)}"
        error_msg += f"\n  Traceback:\n{traceback.format_exc()}"
    print(error_msg, flush=True)


def validate_environment() -> None:
    """Validate required environment variables at startup."""
    missing = []
    warnings = []

    # Required for core functionality
    if not os.getenv("OPENAI_API_KEY"):
        missing.append("OPENAI_API_KEY")

    # Required for ticket escalation (email)
    smtp_key = os.getenv("SMTP2GO_API_KEY", "")
    if not smtp_key:
        warnings.append("SMTP2GO_API_KEY not set - ticket escalation will use fallback logging mode")
    elif not smtp_key.startswith("api-"):
        warnings.append("SMTP2GO_API_KEY may be invalid (expected 'api-' prefix)")

    # Report issues
    if missing:
        raise RuntimeError(
            f"Missing required environment variables: {', '.join(missing)}. "
            "See backend/.env.example for required configuration."
        )

    for warning in warnings:
        print(f"[WARNING] {warning}")


def _user_message_text(item: UserMessageItem) -> str:
    parts: list[str] = []
    for part in item.content:
        text = getattr(part, "text", None)
        if text:
            parts.append(text)
    return " ".join(parts).strip()


def _format_customer_context(context: CustomerContext) -> str:
    """Format customer context for the AI agent."""
    interactions = context.interactions[:5]  # Most recent 5
    recent_activity = "\n".join(
        f"  * [{interaction.action_type}] {interaction.description}"
        for interaction in interactions
    )

    return (
        "=== Customer Support Session Context ===\n"
        f"Session ID: {context.session_id}\n"
        f"Customer: {context.customer_name}\n"
        f"Email: {context.customer_email or 'Not provided'}\n"
        f"Phone: {context.customer_phone or 'Not provided'}\n"
        f"Company: {context.customer_company or 'Not provided'}\n"
        f"\n"
        f"Session Stats:\n"
        f"  - Questions asked: {context.questions_asked}\n"
        f"  - KB articles viewed: {context.kb_articles_viewed}\n"
        f"  - Tickets created: {context.tickets_created}\n"
        f"\n"
        f"Recent Activity:\n"
        f"{recent_activity or '  * No activity yet'}\n"
        "========================================"
    )


def _is_tool_completion_item(item: Any) -> bool:
    return isinstance(item, ClientToolCallItem)


class ZingAttachmentConverter(ThreadItemConverter):
    """
    Custom ThreadItemConverter that handles image attachments.

    Override to_agent_input to handle the entire conversion process ourselves,
    avoiding any issues with the base class's attachment handling.
    """

    async def to_agent_input(self, item: Any) -> list[Message] | None:
        """
        Override to_agent_input to safely handle attachments.

        For now, convert image attachments to text descriptions to ensure
        the chat doesn't break. Vision support can be added later once
        the basic flow is working.
        """
        log("CONVERTER", f"to_agent_input called - item type: {type(item).__name__}")

        try:
            # Check if this is a user message with attachments
            if hasattr(item, 'content') and hasattr(item, 'attachments'):
                attachments = getattr(item, 'attachments', None) or []
                log("CONVERTER", f"UserMessageItem with {len(attachments)} attachment(s)")

                # Build content parts
                content_parts: list[ResponseInputContentParam] = []

                # Add text content
                for part in item.content:
                    text = getattr(part, 'text', None)
                    if text:
                        content_parts.append(ResponseInputTextParam(
                            type="input_text",
                            text=text
                        ))

                # Add attachment descriptions as text (safe fallback)
                for att in attachments:
                    att_type = getattr(att, 'type', 'unknown')
                    att_name = getattr(att, 'name', 'file')
                    att_id = getattr(att, 'id', None)
                    att_preview = getattr(att, 'preview_url', None)
                    log("CONVERTER", f"Processing attachment: type={att_type}, name={att_name}, id={att_id}")
                    log("CONVERTER", f"  preview_url present: {att_preview is not None}, length: {len(str(att_preview)) if att_preview else 0}")
                    log("CONVERTER", f"  attachment_data_store keys: {list(attachment_data_store.keys())}")
                    log("CONVERTER", f"  attachment object attrs: {[a for a in dir(att) if not a.startswith('_')]}")

                    if att_type == "image":
                        # For images, try to include the actual image data
                        # First try preview_url from attachment, then fallback to store lookup
                        preview_url = getattr(att, 'preview_url', None)
                        log("CONVERTER", f"Initial preview_url from attachment: {preview_url is not None}, len={len(str(preview_url)) if preview_url else 0}")

                        if not preview_url:
                            # ChatKit may not include preview_url - look up by ID from store
                            if att_id and att_id in attachment_data_store:
                                preview_url = attachment_data_store[att_id][0]  # Tuple: (data_url, created_at)
                                log("CONVERTER", f"Retrieved image from store by ID: {att_id}, len={len(str(preview_url))}")
                            else:
                                log("CONVERTER", f"Store lookup failed: att_id={att_id}, in_store={att_id in attachment_data_store if att_id else False}")

                        if preview_url:
                            try:
                                image_url = str(preview_url)
                                log("CONVERTER", f"Adding image to content, url length: {len(image_url)}, starts_with: {image_url[:50]}...")
                                # Use ResponseInputImageParam as per GitHub issue #85 working example
                                # MUST include detail parameter - using "auto" for best quality/cost balance
                                content_parts.append(ResponseInputImageParam(
                                    type="input_image",
                                    image_url=image_url,
                                    detail="auto",
                                ))
                                log("CONVERTER", "Successfully added ResponseInputImageParam to content_parts")
                            except Exception as img_err:
                                log_error("CONVERTER", f"Failed to create ResponseInputImageParam", exc=img_err)
                                content_parts.append(ResponseInputTextParam(
                                    type="input_text",
                                    text=f"[User attached an image: {att_name}]"
                                ))
                        else:
                            log("CONVERTER", f"No preview_url found for image, using text fallback")
                            content_parts.append(ResponseInputTextParam(
                                type="input_text",
                                text=f"[User attached an image: {att_name}]"
                            ))
                    else:
                        content_parts.append(ResponseInputTextParam(
                            type="input_text",
                            text=f"[User attached a file: {att_name}]"
                        ))

                if content_parts:
                    log("CONVERTER", f"Created message with {len(content_parts)} content parts")
                    return [Message(
                        type="message",
                        role="user",
                        content=content_parts
                    )]

                log("CONVERTER", "No content parts generated")
                return None

            # For other item types, use the default conversion
            log("CONVERTER", "Using default conversion")
            return await super().to_agent_input(item)

        except Exception as e:
            log_error("CONVERTER", f"Exception in to_agent_input, returning text fallback", exc=e)
            # Return a safe text-only message
            text = "[Message could not be fully processed]"
            if hasattr(item, 'content'):
                for part in item.content:
                    t = getattr(part, 'text', None)
                    if t:
                        text = t
                        break
            return [Message(
                type="message",
                role="user",
                content=[ResponseInputTextParam(type="input_text", text=text)]
            )]

    async def attachment_to_message_content(
        self, attachment: Attachment
    ) -> ResponseInputContentParam:
        """
        Convert a ChatKit attachment to OpenAI message content.
        This is called by the parent class if we don't fully override to_agent_input.
        """
        log("ATTACHMENT", f"attachment_to_message_content called - type={attachment.type}")

        try:
            if attachment.type == "image":
                # First try preview_url from attachment
                preview_url = getattr(attachment, 'preview_url', None)
                if not preview_url:
                    # ChatKit may not include preview_url - look up by ID from store
                    att_id = getattr(attachment, 'id', None)
                    if att_id and att_id in attachment_data_store:
                        preview_url = attachment_data_store[att_id][0]  # Tuple: (data_url, created_at)
                        log("ATTACHMENT", f"Retrieved image from store by ID: {att_id}")

                if preview_url:
                    # Use ResponseInputImageParam as per GitHub issue #85 working example
                    return ResponseInputImageParam(
                        type="input_image",
                        image_url=str(preview_url),
                        detail="auto",
                    )

            return ResponseInputTextParam(
                type="input_text",
                text=f"[Attachment: {getattr(attachment, 'name', 'file')}]"
            )
        except Exception as e:
            log_error("ATTACHMENT", f"Exception in attachment_to_message_content", exc=e)
            return ResponseInputTextParam(
                type="input_text",
                text=f"[Attachment could not be processed]"
            )


# Create a global converter instance
log("INIT", f"Creating ZingAttachmentConverter instance (version={BACKEND_VERSION})")
attachment_converter = ZingAttachmentConverter()


class ZingSupportServer(ChatKitServer[dict[str, Any]]):
    """Zing customer support ChatKit server."""

    def __init__(
        self,
        state_manager: ZingStateManager,
        attachment_store: AttachmentStore[dict[str, Any]] | None = None,
    ) -> None:
        store = MemoryStore()
        # CRITICAL: Pass attachment_store to enable file uploads in ChatKit UI
        # Without this parameter, the attachment button will be disabled/non-functional
        super().__init__(store, attachment_store)
        self.store = store
        self.state_manager = state_manager
        self.agent = build_zing_support_agent(state_manager)
        log("SERVER", f"ZingSupportServer initialized with attachment_store: {attachment_store is not None}")

    def _resolve_thread_id(self, thread: ThreadMetadata | None) -> str:
        return thread.id if thread and thread.id else DEFAULT_THREAD_ID

    async def respond(
        self,
        thread: ThreadMetadata,
        item: UserMessageItem | None,
        context: dict[str, Any],
    ) -> AsyncIterator[ThreadStreamEvent]:
        log("RESPOND", f"respond() called - thread_id={thread.id if thread else 'None'}")

        if item is None:
            log("RESPOND", "Item is None, returning early")
            return

        if _is_tool_completion_item(item):
            log("RESPOND", "Item is tool completion, returning early")
            return

        # Check for attachments in the item
        has_attachments = hasattr(item, 'attachments') and item.attachments
        attachment_count = len(item.attachments) if has_attachments else 0
        log("RESPOND", f"Item has {attachment_count} attachment(s)")

        if has_attachments:
            for idx, att in enumerate(item.attachments):
                att_type = getattr(att, 'type', 'unknown')
                att_name = getattr(att, 'name', 'unknown')
                log("RESPOND", f"  Attachment[{idx}]: type={att_type}, name={att_name}")

        message_text = _user_message_text(item)
        if not message_text and not has_attachments:
            log("RESPOND", "No message text and no attachments, returning early")
            return
        log("RESPOND", f"Message text: {message_text[:100]}..." if len(message_text) > 100 else f"Message text: {message_text}")

        # Get customer context
        thread_key = self._resolve_thread_id(thread)
        customer_context = self.state_manager.get_context(thread_key)
        context_prompt = _format_customer_context(customer_context)

        # Increment question counter
        customer_context.increment_stat("questions")

        # System context for the agent (customer info, session stats)
        system_context = context_prompt

        # Create agent context
        agent_context = AgentContext(
            thread=thread,
            store=self.store,
            request_context=context,
        )

        # Load full conversation history from thread
        log("RESPOND", f"Loading thread items for thread_id={thread.id}")
        thread_items_page = await self.store.load_thread_items(
            thread_id=thread.id,
            after=None,
            limit=100,  # Load last 100 messages
            order="asc",  # Chronological order
            context=context
        )
        log("RESPOND", f"Loaded {len(thread_items_page.data)} thread items")

        # Generate thread title for new conversations
        # Only generate if: thread has no title AND this is the first message
        # Note: By the time respond() is called, the user message is already in the thread,
        # so we check for exactly 1 item (the current user message)
        thread_title = getattr(thread, 'title', None)
        is_first_message = len(thread_items_page.data) == 1
        if is_first_message and not thread_title and message_text:
            try:
                log("RESPOND", "Generating thread title for new conversation...")
                new_title = await generate_thread_title(message_text)
                log("RESPOND", f"Generated title: {new_title}")
                # Update thread metadata with the new title
                thread.title = new_title
                await self.store.save_thread(thread, context)
                log("RESPOND", "Thread title saved successfully")
            except Exception as e:
                log_error("RESPOND", "Failed to generate thread title", exc=e)
                # Non-critical error - continue without title

        # Build message list for agent
        messages: list[Message] = []

        # Add system context as first message
        messages.append(Message(
            type="message",
            role="system",
            content=[ResponseInputTextParam(
                type="input_text",
                text=system_context
            )]
        ))
        log("RESPOND", "Added system context message")

        # Convert existing thread items (previous conversation) to messages
        # Use custom converter that handles image attachments
        converted_count = 0
        skipped_count = 0
        for thread_item in thread_items_page.data:
            try:
                agent_input = await attachment_converter.to_agent_input(thread_item)
                if agent_input:
                    messages.extend(agent_input)
                    converted_count += 1
            except Exception as e:
                # Skip items that can't be converted (e.g., widgets, tasks)
                log("RESPOND", f"Skipping thread item conversion: {type(e).__name__}: {str(e)}")
                skipped_count += 1
                continue
        log("RESPOND", f"Converted {converted_count} thread items, skipped {skipped_count}")

        # Add the current user message (not yet in store)
        # Use custom converter that handles image attachments
        if item:
            log("RESPOND", f"Converting current item with {attachment_count} attachment(s)")
            try:
                current_input = await attachment_converter.to_agent_input(item)
                if current_input:
                    messages.extend(current_input)
                    log("RESPOND", f"Successfully converted current item, added {len(current_input)} message(s)")
                else:
                    # Fallback if to_agent_input returns empty
                    log("RESPOND", "to_agent_input returned empty, using fallback")
                    fallback_text = message_text if message_text else "[User sent an image]"
                    messages.append(Message(
                        type="message",
                        role="user",
                        content=[ResponseInputTextParam(
                            type="input_text",
                            text=fallback_text
                        )]
                    ))
            except Exception as e:
                # Fallback: create simple user message if conversion fails
                log_error("RESPOND", f"Failed to convert current item, using fallback", exc=e)
                fallback_text = message_text if message_text else "[User sent a message with an attachment that could not be processed]"
                messages.append(Message(
                    type="message",
                    role="user",
                    content=[ResponseInputTextParam(
                        type="input_text",
                        text=fallback_text
                    )]
                ))

        log("RESPOND", f"Total messages for agent: {len(messages)}")

        # Run the agent with full conversation history
        # Note: Don't pass temperature - Responses API doesn't support it
        log("RESPOND", "Starting agent run_streamed")
        try:
            result = Runner.run_streamed(
                self.agent,
                messages,
                context=agent_context,
            )

            # Stream the response
            event_count = 0
            async for event in stream_agent_response(agent_context, result):
                event_count += 1
                yield event

            log("RESPOND", f"Streamed {event_count} events successfully")
        except Exception as e:
            log_error("RESPOND", "Exception during agent streaming", exc=e)
            raise


# Initialize server with attachment store to enable file uploads
log("INIT", "Creating ZingSupportServer with attachment store")
support_server = ZingSupportServer(
    state_manager=state_manager,
    attachment_store=zing_attachment_store,
)

# Create FastAPI app
app = FastAPI(
    title="Zing Customer Support API",
    description="AI-powered customer support agent for Zing Business Management Software",
    version="1.0.0",
)

# CORS Configuration - Use environment variable for production security
# Default allows localhost for development; set ALLOWED_ORIGINS env var for production
# IMPORTANT: Always include OpenAI's CDN domain since ChatKit widget runs in an iframe from there
ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost:5171,http://localhost:5172,http://localhost:5173,http://localhost:5174,http://localhost:5175,http://localhost:5176,http://localhost:3000").split(",")
] + [
    "https://cdn.platform.openai.com",  # ChatKit iframe origin - REQUIRED
    "https://zing-customer-support-agent.vercel.app",  # Production frontend (Vercel)
    "https://zing.work",  # ZING main domain
    "https://www.zing.work",  # ZING www subdomain
    "https://website.zing.work",  # ZING website subdomain
    "https://zing-work.com",  # ZING alternate domain
    "https://www.zing-work.com",  # ZING alternate www
    "https://website.zing-work.com",  # ZING alternate website subdomain
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],  # Allow all headers - ChatKit may send custom headers
    allow_credentials=True,
    max_age=600,  # Cache preflight requests for 10 minutes
)


@app.on_event("startup")
async def startup_event() -> None:
    """Validate environment variables and initialize services on startup."""
    log("STARTUP", "=" * 60)
    log("STARTUP", f"ZING CUSTOMER SUPPORT API - VERSION {BACKEND_VERSION}")
    log("STARTUP", f"Deploy timestamp: {DEPLOY_TIMESTAMP}")
    log("STARTUP", f"Python version: {sys.version}")
    log("STARTUP", "=" * 60)

    validate_environment()
    log("STARTUP", "Environment validated successfully")
    log("STARTUP", f"CORS allowed origins: {ALLOWED_ORIGINS}")
    log("STARTUP", "Server ready to accept requests")


def get_server() -> ZingSupportServer:
    return support_server


@app.post("/support/chatkit")
async def chatkit_endpoint(
    request: Request, server: ZingSupportServer = Depends(get_server)
) -> Response:
    """ChatKit webhook endpoint for handling customer conversations."""
    request_id = datetime.utcnow().strftime("%H%M%S%f")[:10]
    log("CHATKIT", f"[{request_id}] Received request from origin={request.headers.get('origin', 'unknown')}")

    try:
        payload = await request.body()
        payload_preview = payload[:200].decode('utf-8', errors='replace') if payload else "empty"
        log("CHATKIT", f"[{request_id}] Payload preview: {payload_preview}...")

        result = await server.process(payload, {"request": request})
        log("CHATKIT", f"[{request_id}] Processing complete, result type: {type(result).__name__}")

        if isinstance(result, StreamingResult):
            log("CHATKIT", f"[{request_id}] Returning StreamingResponse")
            return StreamingResponse(result, media_type="text/event-stream")
        if hasattr(result, "json"):
            log("CHATKIT", f"[{request_id}] Returning JSON response")
            return Response(content=result.json, media_type="application/json")
        log("CHATKIT", f"[{request_id}] Returning JSONResponse")
        return JSONResponse(result)
    except Exception as e:
        log_error("CHATKIT", f"[{request_id}] Exception in chatkit_endpoint", exc=e)
        return JSONResponse(
            {"error": str(e), "type": type(e).__name__},
            status_code=500,
            headers={
                "Access-Control-Allow-Origin": request.headers.get("origin", "*"),
                "Access-Control-Allow-Credentials": "true",
            }
        )


def _thread_param(thread_id: str | None) -> str:
    return thread_id or DEFAULT_THREAD_ID


@app.get("/support/customer")
async def customer_snapshot(
    thread_id: str | None = Query(None, description="ChatKit thread identifier"),
    server: ZingSupportServer = Depends(get_server),
) -> dict[str, Any]:
    """Get current customer context for a support session."""
    key = _thread_param(thread_id)
    data = server.state_manager.to_dict(key)
    return {"customer": data}


@app.get("/health")
@app.get("/support/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint for deployment platforms (Railway, Render, etc.)."""
    return {"status": "healthy", "service": "Zing Customer Support API", "version": BACKEND_VERSION}


@app.get("/version")
@app.get("/support/version")
async def version_info() -> dict[str, str]:
    """Version endpoint to verify which code is deployed."""
    return {
        "version": BACKEND_VERSION,
        "deploy_timestamp": DEPLOY_TIMESTAMP,
        "python_version": sys.version,
        "attachment_converter": "ZingAttachmentConverter",
    }


@app.get("/support/debug/attachments")
async def debug_attachments() -> dict[str, Any]:
    """Debug endpoint to check attachment store state."""
    return {
        "data_store_count": len(attachment_data_store),
        "data_store_keys": list(attachment_data_store.keys()),
        "data_store_sizes": {k: len(v[0]) for k, v in attachment_data_store.items()},  # v is (data_url, created_at)
        "data_store_ages_minutes": {
            k: int((datetime.utcnow() - v[1]).total_seconds() / 60)
            for k, v in attachment_data_store.items()
        },
        "metadata_store_count": len(attachment_metadata_store),
        "metadata_store_keys": list(attachment_metadata_store.keys()),
        "ttl_hours": ATTACHMENT_TTL_HOURS,
    }


# ============================================================================
# Direct Ticket Creation API
# ============================================================================

class CreateTicketRequest(BaseModel):
    """Request model for creating a support ticket directly (bypassing AI agent)."""
    customer_name: Optional[str] = Field(None, description="Customer's name")
    customer_email: str = Field(..., description="Customer's email address (required)")
    subject: str = Field(..., description="Ticket subject line")
    description: str = Field(..., description="Detailed description of the issue")
    priority: Literal["LOW", "MEDIUM", "HIGH", "URGENT"] = Field(
        default="MEDIUM",
        description="Ticket priority level"
    )
    conversation_transcript: Optional[str] = Field(
        None,
        description="Optional chat transcript to include"
    )


class CreateTicketResponse(BaseModel):
    """Response model for ticket creation."""
    success: bool
    status: str
    message: str


@app.post("/support/ticket", response_model=CreateTicketResponse)
async def create_ticket_direct(request: CreateTicketRequest) -> CreateTicketResponse:
    """
    Create a support ticket directly without going through the AI agent.

    This endpoint allows the frontend to create tickets via a form UI,
    collecting the same information the AI agent would gather through conversation.

    The ticket is sent via email to the support inbox, where HubSpot
    automatically creates a ticket from it.
    """
    # Validate email
    if not is_valid_email(request.customer_email):
        return CreateTicketResponse(
            success=False,
            status="invalid_email",
            message="Please provide a valid email address (e.g., name@company.com)"
        )

    try:
        # Create ticket using the same flow as the AI agent
        result = await hubspot_manager.create_ticket(
            customer_email=request.customer_email,
            subject=request.subject,
            description=request.description,
            priority=request.priority,
            conversation_transcript=request.conversation_transcript,
            customer_name=request.customer_name,
        )

        return CreateTicketResponse(
            success=True,
            status=result.get("status", "submitted"),
            message=result.get("message", "Your support request has been submitted.")
        )

    except Exception as e:
        print(f"[ERROR] Direct ticket creation failed: {e}")
        return CreateTicketResponse(
            success=False,
            status="error",
            message="Failed to create ticket. Please try again or contact support directly."
        )


# ============================================================================
# File Upload API (for ChatKit image attachments)
# ============================================================================


@app.post("/support/upload")
async def upload_file(file: UploadFile = File(...)) -> dict:
    """
    Handle file uploads for ChatKit attachments.

    ChatKit sends files via multipart/form-data with a "file" field.
    We convert the file to a base64 data URL and return an ImageAttachment.
    """
    log("UPLOAD", f"Upload request received - filename={file.filename}, content_type={file.content_type}")

    try:
        # Read file content
        content = await file.read()
        log("UPLOAD", f"Read {len(content)} bytes")

        # Get MIME type
        mime_type = file.content_type or "application/octet-stream"

        # Generate unique ID
        attachment_id = f"att_{uuid.uuid4().hex[:16]}"

        # Convert to base64 data URL
        base64_content = base64.b64encode(content).decode("utf-8")
        data_url = f"data:{mime_type};base64,{base64_content}"
        log("UPLOAD", f"Created data URL, length={len(data_url)}")

        # Run cleanup periodically to prevent memory leaks
        cleanup_old_attachments()

        # Store in attachment_data_store for later retrieval by ID
        # This is needed because ChatKit may only send the attachment ID when
        # the user sends a message, not the full data URL we return here.
        attachment_data_store[attachment_id] = (data_url, datetime.utcnow())
        log("UPLOAD", f"Stored attachment in memory store, total stored: {len(attachment_data_store)}")

        # Check if it's an image
        is_image = mime_type.startswith("image/")
        timestamp = datetime.utcnow().isoformat() + "Z"

        if is_image:
            log("UPLOAD", f"Returning ImageAttachment - id={attachment_id}, type=image")
            # Create and store ImageAttachment
            attachment = ImageAttachment(
                id=attachment_id,
                type="image",
                name=file.filename or "image",
                mime_type=mime_type,
                preview_url=data_url,
                created_at=timestamp,
            )
            attachment_metadata_store[attachment_id] = attachment
            # CRITICAL: Also save to the ChatKit store so load_attachment() works
            await support_server.store.save_attachment(attachment, {})
            log("UPLOAD", f"Saved attachment to ChatKit store")
            # Return as dict for JSON response
            return {
                "id": attachment_id,
                "type": "image",
                "name": file.filename or "image",
                "mime_type": mime_type,
                "preview_url": data_url,
                "created_at": timestamp,
            }
        else:
            log("UPLOAD", f"Returning FileAttachment - id={attachment_id}, type=file")
            # Create and store FileAttachment
            attachment = FileAttachment(
                id=attachment_id,
                type="file",
                name=file.filename or "file",
                mime_type=mime_type,
                size=len(content),
                created_at=timestamp,
            )
            attachment_metadata_store[attachment_id] = attachment
            # CRITICAL: Also save to the ChatKit store so load_attachment() works
            await support_server.store.save_attachment(attachment, {})
            log("UPLOAD", f"Saved attachment to ChatKit store")
            # Return as dict for JSON response
            return {
                "id": attachment_id,
                "type": "file",
                "name": file.filename or "file",
                "mime_type": mime_type,
                "size": len(content),
                "created_at": timestamp,
            }

    except Exception as e:
        log_error("UPLOAD", "File upload failed", exc=e)
        return JSONResponse(
            {"error": str(e), "type": type(e).__name__},
            status_code=500
        )


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint with service information."""
    return {
        "service": "Zing Customer Support API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }
