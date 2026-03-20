"""
Thread Title Agent

Generates concise, descriptive titles for support conversations
based on the first user message. Uses a lightweight model call
for fast, cost-effective title generation.
"""

from __future__ import annotations

import os
from openai import AsyncOpenAI

# Initialize OpenAI client for title generation
_client: AsyncOpenAI | None = None


def _get_client() -> AsyncOpenAI:
    """Get or create the OpenAI client."""
    global _client
    if _client is None:
        _client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    return _client


async def generate_thread_title(user_message: str) -> str:
    """
    Generate a short, descriptive title for a support thread.

    Uses GPT-4.1-nano (fastest/cheapest model) to generate a 3-6 word
    title that captures the essence of the user's question or issue.

    Args:
        user_message: The first message from the user in the thread

    Returns:
        A short title string (3-6 words, no punctuation at end)
    """
    if not user_message or not user_message.strip():
        return "New Support Conversation"

    # Truncate very long messages to save tokens
    truncated_message = user_message[:500] if len(user_message) > 500 else user_message

    try:
        client = _get_client()

        response = await client.chat.completions.create(
            model="gpt-4o",  # Quality titles with fast response
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Generate a short, descriptive title (3-6 words) for a customer support conversation. "
                        "The title should capture the main topic or issue. "
                        "Do NOT include punctuation at the end. "
                        "Do NOT use quotes around the title. "
                        "Examples:\n"
                        "- Website Not Loading\n"
                        "- Pricing Question\n"
                        "- Cancel My Subscription\n"
                        "- Update Contact Information\n"
                        "- ZING Local Setup Help"
                    ),
                },
                {
                    "role": "user",
                    "content": f"Generate a title for this support message:\n\n{truncated_message}",
                },
            ],
            max_tokens=20,  # Titles are short
            temperature=0.3,  # Lower temp for consistent results
        )

        title = response.choices[0].message.content
        if title:
            # Clean up the title - remove quotes, trailing punctuation
            title = title.strip().strip('"\'').rstrip('.!?:')
            # Ensure reasonable length
            if len(title) > 50:
                title = title[:47] + "..."
            return title

        return "Support Conversation"

    except Exception as e:
        print(f"[TITLE_AGENT] Error generating title: {e}")
        # Fallback: Use first few words of message
        words = user_message.split()[:5]
        fallback = " ".join(words)
        if len(fallback) > 40:
            fallback = fallback[:37] + "..."
        return fallback or "Support Conversation"
