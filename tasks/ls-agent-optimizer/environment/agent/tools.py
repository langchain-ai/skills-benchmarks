"""Tool definitions for the Acme Subscriptions support agent.

These docstrings are sent to the model as tool descriptions, so they must
accurately describe how each tool behaves.
"""

KB_CATEGORIES = ("billing", "account", "shipping", "product")


def search_kb(query: str, category: str = "") -> str:
    """Search the knowledge base for help articles.

    Args:
        query: Search terms describing the user's question.
        category: Optional category filter (billing, account, shipping,
            product). Leave it out to search all categories.
    """
    if not category:
        return "Error: category is required"
    if category not in KB_CATEGORIES:
        return f"Error: unknown category '{category}'"
    return f"[KB] Top article for '{query}' in {category}"


def update_subscription(email: str, change: str) -> str:
    """Apply a subscription change (plan change, cancellation, payment
    method update) for the account with the given email.

    Args:
        email: The account email address.
        change: Plain-language description of the requested change.
    """
    return f"[BILLING] Applied '{change}' for {email}"


def get_shipping_status(tracking_number: str) -> str:
    """Look up the live shipping status for a tracking number.

    Args:
        tracking_number: The carrier tracking number from the shipping
            confirmation email.
    """
    return f"[SHIPPING] Status for {tracking_number}: in transit"


def escalate_to_human(summary: str) -> str:
    """Hand the conversation to a human support agent.

    Args:
        summary: Short summary of the user's issue and what was tried.
    """
    return f"[ESCALATED] {summary}"
