import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from backend.core.config import get_settings
from backend.providers.mock.provider import MockProvider
from backend.scheduler.jobs import evaluate_user

logger = logging.getLogger(__name__)


async def run_scheduled_evaluations() -> None:
    provider = MockProvider()
    for user_key in provider.list_users():
        try:
            result = await evaluate_user(user_key, mock=True)
            logger.info(
                "Scheduled evaluation for %s: %d suggestions",
                user_key,
                len(result["suggestions"]),
            )
        except Exception:
            logger.exception("Failed evaluation for %s", user_key)


def create_scheduler() -> AsyncIOScheduler:
    settings = get_settings()
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        run_scheduled_evaluations,
        "interval",
        minutes=settings.scheduler_interval_minutes,
        id="per_user_evaluation",
        replace_existing=True,
    )
    return scheduler


def main() -> None:
    logging.basicConfig(level=get_settings().log_level)
    scheduler = create_scheduler()
    scheduler.start()
    logger.info("Kairos scheduler worker started")
    try:
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()


if __name__ == "__main__":
    main()
