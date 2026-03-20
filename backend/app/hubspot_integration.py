"""
HubSpot Integration for Zing Customer Support

Handles ticket creation and escalation via email (SMTP2GO).
When emails are sent to the support inbox, HubSpot automatically creates tickets.
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from email.utils import formataddr
import httpx

from .email_templates import build_html_email, build_plain_text_email


# SMTP2GO Configuration
SMTP2GO_API_URL = "https://api.smtp2go.com/v3/email/send"
SMTP2GO_API_KEY = os.getenv("SMTP2GO_API_KEY", "")  # Required: Get from https://smtp2go.com
SMTP2GO_SENDER = "nathan@zing-work.com"   # Sender address for outgoing emails
SUPPORT_INBOX = "support@zing-work.com"   # Inbox that receives ALL support tickets (including cancellations)


def is_valid_smtp2go_api_key(api_key: str) -> bool:
    """
    Validate SMTP2GO API key format.

    Valid format: api-[A-Za-z0-9]{32} (e.g., api-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX)

    Returns:
        True if the API key appears valid, False otherwise
    """
    if not api_key:
        return False

    # SMTP2GO keys must match: api- followed by exactly 32 alphanumeric characters
    pattern = r"^api-[A-Za-z0-9]{32}$"
    return bool(re.match(pattern, api_key))


class HubSpotTicketManager:
    """Manages creation and tracking of HubSpot support tickets via email."""

    async def create_ticket(
        self,
        customer_email: str,
        subject: str,
        description: str,
        priority: str = "MEDIUM",
        conversation_transcript: Optional[str] = None,
        customer_name: Optional[str] = None,
        # AI Sentiment Assessment scores
        mood_score: str = "NEUTRAL",
        mood_reason: str = "",
        urgency_score: str = "MEDIUM",
        urgency_reason: str = "",
        complexity_score: str = "MODERATE",
        complexity_reason: str = "",
        # Cancellation-specific field (optional)
        cancellation_reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a HubSpot support ticket by sending email to the support inbox.

        When an email arrives at the support inbox, HubSpot Conversations
        automatically creates a ticket. This is simpler and more reliable
        than using the HubSpot API directly.

        Args:
            customer_email: Customer's email address
            subject: Ticket subject line
            description: Detailed description of the issue
            priority: Ticket priority (LOW, MEDIUM, HIGH, URGENT)
            conversation_transcript: Full chat transcript (optional)
            customer_name: Customer's name (optional)
            mood_score: Customer mood (FRUSTRATED/NEUTRAL/SATISFIED)
            mood_reason: Brief explanation for mood assessment
            urgency_score: Issue urgency (LOW/MEDIUM/HIGH/CRITICAL)
            urgency_reason: Brief explanation for urgency assessment
            complexity_score: Issue complexity (SIMPLE/MODERATE/COMPLEX)
            complexity_reason: Brief explanation for complexity assessment

        Returns:
            Dict containing ticket details including ticket_id and ticket_url
        """
        # EMAIL MODE: Send real email to support inbox (HubSpot auto-creates ticket)
        return await self._send_ticket_email(
            customer_email=customer_email,
            subject=subject,
            description=description,
            priority=priority,
            conversation_transcript=conversation_transcript,
            customer_name=customer_name,
            mood_score=mood_score,
            mood_reason=mood_reason,
            urgency_score=urgency_score,
            urgency_reason=urgency_reason,
            complexity_score=complexity_score,
            complexity_reason=complexity_reason,
            cancellation_reason=cancellation_reason,
        )

    async def _send_ticket_email(
        self,
        customer_email: str,
        subject: str,
        description: str,
        priority: str,
        conversation_transcript: Optional[str],
        customer_name: Optional[str],
        # AI Sentiment Assessment scores
        mood_score: str = "NEUTRAL",
        mood_reason: str = "",
        urgency_score: str = "MEDIUM",
        urgency_reason: str = "",
        complexity_score: str = "MODERATE",
        complexity_reason: str = "",
        # Cancellation-specific field (optional)
        cancellation_reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Send a ZING-branded email to the support inbox via SMTP2GO.
        HubSpot Conversations will automatically create a ticket when
        the email arrives in the support inbox.

        Includes AI sentiment assessment for agent prioritization.
        """
        created_at = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')

        # Email subject is just the subject from the AI (already includes priority context)
        email_subject = subject

        # Build HTML and plain text versions with sentiment data
        html_body = build_html_email(
            customer_name=customer_name or "Guest",
            customer_email=customer_email,
            subject=subject,
            description=description,
            priority=priority,
            conversation_transcript=conversation_transcript,
            created_at=created_at,
            mood_score=mood_score,
            mood_reason=mood_reason,
            urgency_score=urgency_score,
            urgency_reason=urgency_reason,
            complexity_score=complexity_score,
            complexity_reason=complexity_reason,
            cancellation_reason=cancellation_reason,
        )

        plain_body = build_plain_text_email(
            customer_name=customer_name or "Guest",
            customer_email=customer_email,
            subject=subject,
            description=description,
            priority=priority,
            conversation_transcript=conversation_transcript,
            created_at=created_at,
            mood_score=mood_score,
            mood_reason=mood_reason,
            urgency_score=urgency_score,
            urgency_reason=urgency_reason,
            complexity_score=complexity_score,
            complexity_reason=complexity_reason,
            cancellation_reason=cancellation_reason,
        )

        # Validate API key before attempting to send
        if not is_valid_smtp2go_api_key(SMTP2GO_API_KEY):
            print("[ERROR] SMTP2GO_API_KEY not configured - set in backend/.env (format: api-XXXXX...)")
            # Fall back to logging mode (ticket still gets recorded locally)
            return self._log_ticket_creation(
                customer_email=customer_email,
                subject=subject,
                description=description,
                priority=priority,
                conversation_transcript=conversation_transcript,
                customer_name=customer_name,
                mood_score=mood_score,
                mood_reason=mood_reason,
                urgency_score=urgency_score,
                urgency_reason=urgency_reason,
                complexity_score=complexity_score,
                complexity_reason=complexity_reason,
                cancellation_reason=cancellation_reason,
            )

        # Send via SMTP2GO API

        try:
            # Build sender with customer identity in display name
            # Format: "Customer Name (customer@email.com)" <nathan@zing-work.com>
            # This allows support agents to see WHO the ticket is from at a glance
            # Using formataddr() ensures proper RFC 5322 escaping of special characters
            if customer_name and customer_name != "Guest":
                display_name = f"{customer_name} ({customer_email})"
            else:
                display_name = customer_email

            # formataddr properly escapes quotes and special chars in display name
            sender_display = formataddr((display_name, SMTP2GO_SENDER))

            payload = {
                "api_key": SMTP2GO_API_KEY,
                "sender": sender_display,
                "to": [SUPPORT_INBOX],
                "subject": email_subject,
                "html_body": html_body,
                "text_body": plain_body,
                "custom_headers": [
                    {"header": "X-Customer-Email", "value": customer_email},
                    {"header": "X-Priority", "value": priority},
                    {"header": "Reply-To", "value": customer_email},
                ]
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    SMTP2GO_API_URL,
                    json=payload,
                    timeout=30.0,
                )
                response.raise_for_status()
                result = response.json()

            print(f"[EMAIL] Ticket sent: {customer_email} - {email_subject}")

            # Also save to local JSON for audit trail
            ticket_data = {
                "created_at": datetime.now(timezone.utc).isoformat(),
                "customer_name": customer_name or "Unknown",
                "customer_email": customer_email,
                "priority": priority,
                "subject": subject,
                "description": description,
                "conversation_transcript": conversation_transcript,
                "email_sent": True,
                "smtp2go_response": result,
                # AI Sentiment Assessment
                "ai_assessment": {
                    "mood": {"score": mood_score, "reason": mood_reason},
                    "urgency": {"score": urgency_score, "reason": urgency_reason},
                    "complexity": {"score": complexity_score, "reason": complexity_reason},
                },
                "cancellation_reason": cancellation_reason,
            }
            self._save_ticket_to_file(ticket_data)

            return {
                "status": "submitted",
                "message": f"Your support request has been submitted to our team. "
                          f"We'll reach out to {customer_email} shortly.",
            }

        except httpx.HTTPStatusError as e:
            print(f"\n[ERROR] SMTP2GO API Error: {e.response.status_code} - {e.response.text}\n")
            # Fall back to logging mode
            return self._log_ticket_creation(
                customer_email=customer_email,
                subject=subject,
                description=description,
                priority=priority,
                conversation_transcript=conversation_transcript,
                customer_name=customer_name,
                mood_score=mood_score,
                mood_reason=mood_reason,
                urgency_score=urgency_score,
                urgency_reason=urgency_reason,
                complexity_score=complexity_score,
                complexity_reason=complexity_reason,
                cancellation_reason=cancellation_reason,
            )
        except Exception as e:
            print(f"\n[ERROR] Email Send Error: {str(e)}\n")
            # Fall back to logging mode
            return self._log_ticket_creation(
                customer_email=customer_email,
                subject=subject,
                description=description,
                priority=priority,
                conversation_transcript=conversation_transcript,
                customer_name=customer_name,
                mood_score=mood_score,
                mood_reason=mood_reason,
                urgency_score=urgency_score,
                urgency_reason=urgency_reason,
                complexity_score=complexity_score,
                complexity_reason=complexity_reason,
                cancellation_reason=cancellation_reason,
            )

    def _log_ticket_creation(
        self,
        customer_email: str,
        subject: str,
        description: str,
        priority: str,
        conversation_transcript: Optional[str],
        customer_name: Optional[str],
        # AI Sentiment Assessment scores
        mood_score: str = "NEUTRAL",
        mood_reason: str = "",
        urgency_score: str = "MEDIUM",
        urgency_reason: str = "",
        complexity_score: str = "MODERATE",
        complexity_reason: str = "",
        # Cancellation-specific field (optional)
        cancellation_reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Fallback: Log what would be sent if email fails."""
        # Build the full ticket content as it would appear in HubSpot
        full_content = description
        if conversation_transcript:
            full_content += f"\n\n--- Conversation Transcript ---\n{conversation_transcript}"

        # Create ticket data structure
        ticket_data = {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "customer_name": customer_name or "Unknown",
            "customer_email": customer_email,
            "priority": priority,
            "subject": subject,
            "description": description,
            "full_content": full_content,
            "conversation_transcript": conversation_transcript,
            "email_sent": False,
            # AI Sentiment Assessment
            "ai_assessment": {
                "mood": {"score": mood_score, "reason": mood_reason},
                "urgency": {"score": urgency_score, "reason": urgency_reason},
                "complexity": {"score": complexity_score, "reason": complexity_reason},
            },
        }

        # Log summary (full details saved to JSON file)
        print(f"[TICKET] Logged locally (email failed): {customer_email} - {subject}")

        # Save to JSON file
        self._save_ticket_to_file(ticket_data)

        return {
            "status": "submitted",
            "message": f"Your support request has been submitted to our team. "
                      f"We'll reach out to {customer_email} shortly.",
        }

    def _save_ticket_to_file(self, ticket_data: Dict[str, Any]) -> None:
        """Save ticket data to JSON file for persistent logging."""
        try:
            # Create logs directory if it doesn't exist
            logs_dir = Path(__file__).parent.parent.parent / "logs"
            logs_dir.mkdir(exist_ok=True)

            # Create tickets file path
            tickets_file = logs_dir / "created_tickets.json"

            # Load existing tickets or create empty list
            tickets = []
            if tickets_file.exists():
                try:
                    with open(tickets_file, "r", encoding="utf-8") as f:
                        content = f.read().strip()
                        if content:  # Only try to parse if file has content
                            tickets = json.loads(content)
                            # Ensure it's a list
                            if not isinstance(tickets, list):
                                print(f"[WARNING] Existing tickets file was not a list, creating new list")
                                tickets = []
                except json.JSONDecodeError as e:
                    print(f"[WARNING] Corrupted tickets file, creating backup: {e}")
                    # Create backup of corrupted file
                    backup_file = logs_dir / f"created_tickets.backup.{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
                    tickets_file.rename(backup_file)
                    tickets = []

            # Add new ticket
            tickets.append(ticket_data)

            # Save back to file (pretty printed)
            with open(tickets_file, "w", encoding="utf-8") as f:
                json.dump(tickets, f, indent=2, ensure_ascii=False)

        except Exception as e:
            print(f"[WARNING] Could not save ticket to file: {e}")
            # Don't fail ticket creation if file saving fails



# Global instance
hubspot_manager = HubSpotTicketManager()
