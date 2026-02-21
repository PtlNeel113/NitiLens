"""
Scheduler: periodic compliance scan using APScheduler.
The scheduler runs a scan every 24 hours and can be triggered manually.
"""
import logging
from datetime import datetime, timezone

logger = logging.getLogger("nitilens.scheduler")

_scheduler = None
_last_run: dict = {"timestamp": None, "violations_found": 0}


def start_scheduler():
    """Start the APScheduler background scheduler."""
    global _scheduler
    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        _scheduler = BackgroundScheduler()
        _scheduler.add_job(
            _run_scheduled_scan,
            trigger="interval",
            hours=24,
            id="daily_aml_scan",
            replace_existing=True,
        )
        _scheduler.start()
        logger.info("APScheduler started — daily AML scan scheduled.")
    except ImportError:
        logger.warning("APScheduler not installed. Periodic scanning disabled.")
    except Exception as e:
        logger.warning(f"Failed to start scheduler: {e}")


def stop_scheduler():
    """Stop the scheduler on shutdown."""
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("APScheduler stopped.")


def _run_scheduled_scan():
    """Callback executed by the scheduler."""
    global _last_run
    try:
        from app.core.violation_engine import run_scan
        violations = run_scan()
        _last_run = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "violations_found": len(violations),
        }
        logger.info(f"Scheduled scan complete — {len(violations)} violations found.")
    except Exception as e:
        logger.error(f"Scheduled scan failed: {e}")


def get_scheduler_status() -> dict:
    """Return scheduler status and last run info."""
    return {
        "running": _scheduler.running if _scheduler else False,
        "next_run": (
            str(_scheduler.get_job("daily_aml_scan").next_run_time)
            if _scheduler and _scheduler.get_job("daily_aml_scan")
            else None
        ),
        "last_run": _last_run,
    }
