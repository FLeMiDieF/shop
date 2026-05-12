import logging
from celery_worker import celery

logger = logging.getLogger(__name__)


@celery.task(name="tasks.send_order_confirmation")
def send_order_confirmation(order_id: int, user_email: str, total: float):
    """Async task: simulate sending order confirmation email."""
    logger.info(
        "[EMAIL] Order #%d confirmed → %s, total %.2f ₽",
        order_id, user_email, total,
    )
    # Production: integrate with SendGrid / Amazon SES / etc.
    return {"status": "sent", "order_id": order_id}
