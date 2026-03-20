"""
ZING-Branded Email Templates for Support Tickets

Professional, branded emails with AI sentiment assessment.
Colors and styling match the ZING brand identity.
"""

import html
import re
from typing import Optional


# =============================================================================
# ZING BRAND COLORS
# =============================================================================
ZING_INDIGO = "#6366F1"      # Primary brand color
ZING_INDIGO_DARK = "#4F46E5"  # Darker for text on light backgrounds
ZING_INDIGO_LIGHT = "#818CF8"  # Lighter accent


def escape_html(text: str) -> str:
    """Escape HTML special characters to prevent XSS attacks."""
    if text is None:
        return ""
    return html.escape(str(text))


def strip_markdown(text: str) -> str:
    """Strip markdown formatting from text for plain display."""
    if text is None:
        return ""
    # Remove bold **text** and __text__
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'__(.+?)__', r'\1', text)
    # Remove italic *text* and _text_
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    text = re.sub(r'_(.+?)_', r'\1', text)
    # Remove inline code `text`
    text = re.sub(r'`(.+?)`', r'\1', text)
    # Remove markdown links [text](url) -> text
    text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text)
    # Remove markdown bullet points at start of lines
    text = re.sub(r'^[\-\*]\s+', '• ', text, flags=re.MULTILINE)
    return text


def get_priority_color(priority: str) -> str:
    """Get color for priority level."""
    colors = {
        "URGENT": "#DC2626",  # Red
        "HIGH": "#EA580C",    # Orange
        "MEDIUM": "#2563EB",  # Blue
        "LOW": "#16A34A",     # Green
    }
    return colors.get(priority.upper(), colors["MEDIUM"])


# =============================================================================
# SENTIMENT SCORE STYLING
# =============================================================================

# Unified sentiment styles configuration
SENTIMENT_STYLES = {
    "mood": {
        "default": "NEUTRAL",
        "values": {
            "FRUSTRATED": {"emoji": "😤", "color": "#DC2626", "bg": "#FEE2E2", "label": "Frustrated"},
            "NEUTRAL": {"emoji": "😐", "color": "#D97706", "bg": "#FEF3C7", "label": "Neutral"},
            "SATISFIED": {"emoji": "😊", "color": "#16A34A", "bg": "#DCFCE7", "label": "Satisfied"},
        },
    },
    "urgency": {
        "default": "MEDIUM",
        "values": {
            "LOW": {"emoji": "🟢", "color": "#16A34A", "bg": "#DCFCE7", "label": "Low"},
            "MEDIUM": {"emoji": "🟡", "color": "#D97706", "bg": "#FEF3C7", "label": "Medium"},
            "HIGH": {"emoji": "🟠", "color": "#EA580C", "bg": "#FFEDD5", "label": "High"},
            "CRITICAL": {"emoji": "🔴", "color": "#DC2626", "bg": "#FEE2E2", "label": "Critical"},
        },
    },
    "complexity": {
        "default": "MODERATE",
        "values": {
            "SIMPLE": {"emoji": "✓", "color": "#16A34A", "bg": "#DCFCE7", "label": "Simple"},
            "MODERATE": {"emoji": "◐", "color": "#D97706", "bg": "#FEF3C7", "label": "Moderate"},
            "COMPLEX": {"emoji": "🧩", "color": "#DC2626", "bg": "#FEE2E2", "label": "Complex"},
        },
    },
}


def get_sentiment_style(category: str, value: str) -> dict:
    """
    Get emoji, color, background, and label for a sentiment score.

    Args:
        category: One of "mood", "urgency", or "complexity"
        value: The score value (e.g., "FRUSTRATED", "HIGH", "COMPLEX")

    Returns:
        Dict with emoji, color, bg, and label keys
    """
    category_config = SENTIMENT_STYLES.get(category)
    if not category_config:
        # Fallback to neutral mood style if category unknown
        return {"emoji": "😐", "color": "#D97706", "bg": "#FEF3C7", "label": "Unknown"}

    value = value.upper() if value else category_config["default"]
    values = category_config["values"]
    return values.get(value, values[category_config["default"]])


def build_sentiment_badge_html(emoji: str, label: str, color: str, bg: str, reason: str) -> str:
    """Build a single sentiment badge with reason."""
    safe_reason = escape_html(reason) if reason else ""
    return f'''
    <div style="display: flex; align-items: flex-start; margin-bottom: 12px;">
        <div style="background-color: {bg}; color: {color}; padding: 6px 12px; border-radius: 20px; font-weight: 600; font-size: 13px; white-space: nowrap; margin-right: 12px;">
            {emoji} {label}
        </div>
        <div style="color: #4B5563; font-size: 13px; padding-top: 6px; line-height: 1.4;">
            {safe_reason if safe_reason else '<span style="color: #9CA3AF; font-style: italic;">No details provided</span>'}
        </div>
    </div>
    '''


# =============================================================================
# HTML EMAIL TEMPLATE
# =============================================================================

def build_html_email(
    customer_name: str,
    customer_email: str,
    subject: str,
    description: str,
    priority: str,
    conversation_transcript: Optional[str],
    created_at: str,
    # Sentiment scores (optional, with defaults)
    mood_score: str = "NEUTRAL",
    mood_reason: str = "",
    urgency_score: str = "MEDIUM",
    urgency_reason: str = "",
    complexity_score: str = "MODERATE",
    complexity_reason: str = "",
    # Cancellation-specific field (optional)
    cancellation_reason: Optional[str] = None,
) -> str:
    """
    Build a ZING-branded HTML email for support ticket escalation.

    Features:
    - ZING indigo branding in header
    - AI Assessment section with sentiment scores
    - Clean, professional layout
    - Conversation transcript
    """
    priority_color = get_priority_color(priority)

    # Get sentiment styles
    mood = get_sentiment_style("mood", mood_score)
    urgency = get_sentiment_style("urgency", urgency_score)
    complexity = get_sentiment_style("complexity", complexity_score)

    # Build sentiment badges
    mood_badge = build_sentiment_badge_html(
        mood["emoji"], mood["label"], mood["color"], mood["bg"], mood_reason
    )
    urgency_badge = build_sentiment_badge_html(
        urgency["emoji"], urgency["label"], urgency["color"], urgency["bg"], urgency_reason
    )
    complexity_badge = build_sentiment_badge_html(
        complexity["emoji"], complexity["label"], complexity["color"], complexity["bg"], complexity_reason
    )

    # Format transcript by parsing messages (not individual lines)
    # This groups multi-line responses into single message blocks
    transcript_html = ""
    if conversation_transcript:
        clean_transcript = strip_markdown(conversation_transcript)

        # Parse transcript into messages by speaker prefix
        # Format: "Speaker: message content" where content may span multiple lines
        # Split on speaker prefixes while keeping the delimiter
        message_pattern = r'(?=(?:Customer|AI Assistant|AI|Unknown):)'
        messages = re.split(message_pattern, clean_transcript.strip())

        for message in messages:
            message = message.strip()
            if not message:
                continue

            # Determine speaker and extract content
            if message.startswith("Customer:") or message.startswith("Unknown:"):
                speaker = "Customer"
                content = message.split(":", 1)[1].strip() if ":" in message else message
                # Customer messages: Indigo/purple theme (highlighted as the requester)
                transcript_html += f'''<div style="background-color: #EEF2FF; padding: 12px 16px; border-radius: 8px; margin-bottom: 8px; border-left: 4px solid {ZING_INDIGO};">
                    <strong style="color: {ZING_INDIGO_DARK}; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px;">Customer</strong>
                    <div style="color: #1F2937; margin-top: 6px; line-height: 1.5; white-space: pre-wrap;">{escape_html(content)}</div>
                </div>'''
            elif message.startswith("AI Assistant:") or message.startswith("AI:"):
                speaker = "AI Assistant"
                content = message.split(":", 1)[1].strip() if ":" in message else message
                # AI messages: Green theme (distinct from customer purple)
                transcript_html += f'''<div style="background-color: #F0FDF4; padding: 12px 16px; border-radius: 8px; margin-bottom: 8px; border-left: 4px solid #22C55E;">
                    <strong style="color: #166534; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px;">AI Assistant</strong>
                    <div style="color: #1F2937; margin-top: 6px; line-height: 1.5; white-space: pre-wrap;">{escape_html(content)}</div>
                </div>'''
            elif message:
                # Fallback for unrecognized format
                transcript_html += f'''<div style="background-color: #F9FAFB; padding: 12px 16px; border-radius: 8px; margin-bottom: 8px; border-left: 4px solid #D1D5DB;">
                    <div style="color: #1F2937; line-height: 1.5; white-space: pre-wrap;">{escape_html(message)}</div>
                </div>'''
    else:
        transcript_html = '<p style="color: #9CA3AF; font-style: italic;">No transcript available</p>'

    # Build cancellation reason section (only if cancellation_reason is provided)
    cancellation_html = ""
    if cancellation_reason:
        cancellation_html = f'''
                    <!-- CANCELLATION REASON - Prominent Section -->
                    <tr>
                        <td style="padding: 0 24px 20px 24px;">
                            <div style="background: linear-gradient(135deg, #FEF2F2 0%, #FEE2E2 100%); border: 2px solid #F87171; border-radius: 10px; padding: 18px;">
                                <div style="display: flex; align-items: center; margin-bottom: 12px;">
                                    <span style="font-size: 20px; margin-right: 10px;">🚫</span>
                                    <span style="font-size: 14px; font-weight: 700; color: #DC2626; text-transform: uppercase; letter-spacing: 0.5px;">
                                        Cancellation Request
                                    </span>
                                </div>
                                <div style="background-color: #FFFFFF; border-radius: 8px; padding: 16px; border-left: 4px solid #DC2626;">
                                    <div style="font-size: 11px; color: #991B1B; font-weight: 600; text-transform: uppercase; margin-bottom: 8px;">
                                        Reason for Cancellation
                                    </div>
                                    <div style="color: #1F2937; font-size: 15px; line-height: 1.6; font-weight: 500;">
                                        {escape_html(cancellation_reason)}
                                    </div>
                                </div>
                            </div>
                        </td>
                    </tr>
        '''

    return f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #F9FAFB;">
    <table role="presentation" style="width: 100%; border-collapse: collapse;">
        <tr>
            <td style="padding: 20px;">
                <table role="presentation" style="max-width: 640px; margin: 0 auto; background-color: #FFFFFF; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.07);">

                    <!-- ZING Branded Header -->
                    <tr>
                        <td style="background: linear-gradient(135deg, {ZING_INDIGO} 0%, {ZING_INDIGO_DARK} 100%); padding: 20px 24px;">
                            <table role="presentation" style="width: 100%;">
                                <tr>
                                    <td>
                                        <div style="display: flex; align-items: center; gap: 12px;">
                                            <div style="width: 36px; height: 36px; background-color: rgba(255,255,255,0.2); border-radius: 8px; display: inline-flex; align-items: center; justify-content: center;">
                                                <span style="color: #FFFFFF; font-weight: bold; font-size: 18px;">Z</span>
                                            </div>
                                            <div>
                                                <div style="color: #FFFFFF; font-size: 18px; font-weight: 700;">
                                                    Support Ticket
                                                </div>
                                                <div style="color: rgba(255,255,255,0.8); font-size: 12px;">
                                                    ZING AI Assistant Escalation
                                                </div>
                                            </div>
                                        </div>
                                    </td>
                                    <td style="text-align: right; vertical-align: middle;">
                                        <span style="background-color: {priority_color}; color: #FFFFFF; padding: 6px 14px; border-radius: 20px; font-size: 12px; font-weight: 600; text-transform: uppercase;">
                                            {escape_html(priority)}
                                        </span>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>

                    <!-- Subject Line -->
                    <tr>
                        <td style="padding: 20px 24px 0 24px;">
                            <h1 style="margin: 0 0 16px 0; color: #111827; font-size: 20px; font-weight: 600; line-height: 1.3;">
                                {escape_html(subject)}
                            </h1>
                        </td>
                    </tr>

                    <!-- Customer Info -->
                    <tr>
                        <td style="padding: 0 24px 20px 24px;">
                            <table role="presentation" style="width: 100%; background-color: #F9FAFB; border-radius: 8px; padding: 14px;">
                                <tr>
                                    <td style="padding: 14px;">
                                        <table role="presentation" style="width: 100%;">
                                            <tr>
                                                <td style="color: #6B7280; font-size: 13px; padding-bottom: 6px; width: 80px;">From:</td>
                                                <td style="font-size: 13px; padding-bottom: 6px;">
                                                    <strong style="color: #111827;">{escape_html(customer_name)}</strong>
                                                    &lt;<a href="mailto:{escape_html(customer_email)}" style="color: {ZING_INDIGO}; text-decoration: none;">{escape_html(customer_email)}</a>&gt;
                                                </td>
                                            </tr>
                                            <tr>
                                                <td style="color: #6B7280; font-size: 13px;">Created:</td>
                                                <td style="font-size: 13px; color: #6B7280;">{escape_html(created_at)}</td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>

                    {cancellation_html}

                    <!-- AI Assessment Section -->
                    <tr>
                        <td style="padding: 0 24px 20px 24px;">
                            <div style="background: linear-gradient(135deg, #EEF2FF 0%, #F5F3FF 100%); border: 1px solid #C7D2FE; border-radius: 10px; padding: 18px;">
                                <div style="display: flex; align-items: center; margin-bottom: 14px;">
                                    <span style="font-size: 16px; margin-right: 8px;">🤖</span>
                                    <span style="font-size: 13px; font-weight: 700; color: {ZING_INDIGO_DARK}; text-transform: uppercase; letter-spacing: 0.5px;">
                                        AI Assessment
                                    </span>
                                </div>

                                <table role="presentation" style="width: 100%;">
                                    <tr>
                                        <td style="padding-bottom: 8px;">
                                            <div style="color: #6B7280; font-size: 11px; font-weight: 600; text-transform: uppercase; margin-bottom: 4px;">Customer Mood</div>
                                            {mood_badge}
                                        </td>
                                    </tr>
                                    <tr>
                                        <td style="padding-bottom: 8px;">
                                            <div style="color: #6B7280; font-size: 11px; font-weight: 600; text-transform: uppercase; margin-bottom: 4px;">Urgency</div>
                                            {urgency_badge}
                                        </td>
                                    </tr>
                                    <tr>
                                        <td>
                                            <div style="color: #6B7280; font-size: 11px; font-weight: 600; text-transform: uppercase; margin-bottom: 4px;">Complexity</div>
                                            {complexity_badge}
                                        </td>
                                    </tr>
                                </table>
                            </div>
                        </td>
                    </tr>

                    <!-- Issue Description -->
                    <tr>
                        <td style="padding: 0 24px 20px 24px;">
                            <div style="background-color: #FFFBEB; border: 1px solid #FCD34D; border-radius: 8px; padding: 16px;">
                                <div style="font-size: 11px; color: #92400E; font-weight: 700; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.5px;">
                                    📋 Issue Summary
                                </div>
                                <div style="color: #1F2937; font-size: 14px; line-height: 1.6;">
                                    {escape_html(description)}
                                </div>
                            </div>
                        </td>
                    </tr>

                    <!-- Conversation Transcript -->
                    <tr>
                        <td style="padding: 0 24px 20px 24px;">
                            <div style="font-size: 11px; color: #6B7280; font-weight: 700; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 0.5px;">
                                💬 Conversation Transcript
                            </div>
                            <div style="max-height: 400px; overflow-y: auto;">
                                {transcript_html}
                            </div>
                        </td>
                    </tr>

                    <!-- Action Button -->
                    <tr>
                        <td style="padding: 0 24px 24px 24px;">
                            <a href="mailto:{escape_html(customer_email)}?subject=Re: {escape_html(subject)}"
                               style="display: inline-block; background-color: {ZING_INDIGO}; color: #FFFFFF; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-size: 14px; font-weight: 600;">
                                Reply to {escape_html(customer_name)} →
                            </a>
                        </td>
                    </tr>

                    <!-- Footer -->
                    <tr>
                        <td style="background-color: #F9FAFB; padding: 16px 24px; border-top: 1px solid #E5E7EB;">
                            <table role="presentation" style="width: 100%;">
                                <tr>
                                    <td style="color: #9CA3AF; font-size: 11px;">
                                        Auto-generated by ZING AI Support Assistant
                                    </td>
                                    <td style="text-align: right;">
                                        <span style="color: #9CA3AF; font-size: 11px;">
                                            zing.work
                                        </span>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>

                </table>
            </td>
        </tr>
    </table>
</body>
</html>'''


# =============================================================================
# PLAIN TEXT EMAIL TEMPLATE
# =============================================================================

def build_plain_text_email(
    customer_name: str,
    customer_email: str,
    subject: str,
    description: str,
    priority: str,
    conversation_transcript: Optional[str],
    created_at: str,
    # Sentiment scores (optional, with defaults)
    mood_score: str = "NEUTRAL",
    mood_reason: str = "",
    urgency_score: str = "MEDIUM",
    urgency_reason: str = "",
    complexity_score: str = "MODERATE",
    complexity_reason: str = "",
    # Cancellation-specific field (optional)
    cancellation_reason: Optional[str] = None,
) -> str:
    """
    Build plain text fallback email with sentiment assessment.
    """
    # Strip markdown from transcript
    clean_transcript = strip_markdown(conversation_transcript) if conversation_transcript else '[No transcript available]'

    # Get labels for sentiment scores
    mood = get_sentiment_style("mood", mood_score)
    urgency = get_sentiment_style("urgency", urgency_score)
    complexity = get_sentiment_style("complexity", complexity_score)

    # Build cancellation section for plain text (only if cancellation_reason provided)
    cancellation_section = ""
    if cancellation_reason:
        cancellation_section = f"""
🚫 CANCELLATION REQUEST
================================================================
REASON: {cancellation_reason}
----------------------------------------------------------------
"""

    return f"""ZING SUPPORT TICKET
================================================================

{subject}

FROM: {customer_name} <{customer_email}>
PRIORITY: {priority}
CREATED: {created_at}
{cancellation_section}
AI ASSESSMENT
----------------------------------------------------------------
{mood["emoji"]} Mood: {mood["label"]}
   {mood_reason if mood_reason else "(No details)"}

{urgency["emoji"]} Urgency: {urgency["label"]}
   {urgency_reason if urgency_reason else "(No details)"}

{complexity["emoji"]} Complexity: {complexity["label"]}
   {complexity_reason if complexity_reason else "(No details)"}

ISSUE SUMMARY
----------------------------------------------------------------
{description}

CONVERSATION TRANSCRIPT
----------------------------------------------------------------
{clean_transcript}

================================================================
Reply to customer: {customer_email}
Auto-generated by ZING AI Support | zing.work
"""
