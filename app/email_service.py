import logging
import smtplib
from email.message import EmailMessage
from typing import Dict, Sequence

from .config import settings

logger = logging.getLogger("ziadsupplies.email")


def build_order_confirmation_email(order_summary: Dict[str, object]) -> EmailMessage:
    customer_name = str(order_summary.get("customerName", "Customer"))
    recipient_email = str(order_summary.get("email", ""))
    order_id = order_summary.get("id")

    subject = "Ziad's Supplies – Order received"

    items: Sequence[Dict[str, object]] = order_summary.get("items", [])  # type: ignore[assignment]
    lines = [
        "Hello {name},".format(name=customer_name),
        "",
        "Thanks for placing an order with Ziad's Supplies. We've queued it for dispatch and will reach out to confirm delivery details shortly.",
        "",
        f"Order ID: {order_id}",
        "Payment method: Cash on Delivery",
    ]

    if items:
        lines.append("")
        lines.append("Items:")
        for item in items:
            qty = item.get("quantity", 0)
            name = item.get("name", "Item")
            line_total = item.get("lineTotal", 0)
            lines.append(f"• {qty} × {name} – ${line_total:.2f}")

    total = order_summary.get("total")
    if total is not None:
        lines.append("")
        lines.append(f"Total (COD): ${total:.2f}")

    lines.extend(
        [
            "",
            "We'll be in touch to finalise dispatch details. If any adjustments are needed, simply reply to this email.",
            "",
            "Best regards,",
            "Ziad's Supplies Team",
        ]
    )

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = settings.email_from or "Ziad's Supplies <no-reply@ziads-supplies.local>"
    if recipient_email:
        message["To"] = recipient_email
    message.set_content("\n".join(lines))
    return message


def send_order_confirmation_email(order_summary: Dict[str, object]) -> bool:
    message = build_order_confirmation_email(order_summary)
    order_id = order_summary.get("id", "unknown")
    recipient_email = message.get("To")

    if not settings.smtp_host or not settings.email_from or not recipient_email:
        logger.info(
            "SMTP not configured. Confirmation email for order %s would target %s.",
            order_id,
            recipient_email or "<missing recipient>",
        )
        return False

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15) as smtp:
            if settings.email_use_tls:
                smtp.starttls()
            if settings.smtp_username and settings.smtp_password:
                smtp.login(settings.smtp_username, settings.smtp_password)
            smtp.send_message(message)
        logger.info("Sent order confirmation email for order %s to %s", order_id, recipient_email)
        return True
    except Exception as exc:  # pragma: no cover
        logger.error("Failed to send order confirmation email: %s", exc)
        return False
