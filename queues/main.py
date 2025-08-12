import os
import asyncio
from celery import Celery
from pyvirtualdisplay import Display
from playwright.async_api import async_playwright
from playwright_stealth import Stealth
from config import general_settings
from scrape import scrape_supercias_wrapper, scrape_instagram_wrapper
from databases.postgres import DatabaseSession, FinancialInfo
from filelock import FileLock, Timeout
from ai_agent import analyze_company, SCORING_WEIGHTS

REDIS_URL = general_settings.REDIS_URL
IN_DOCKER = general_settings.IN_DOCKER

current_dir = os.path.dirname(os.path.abspath(__file__))
folder_path = os.path.join(current_dir, "profiles_pool")

NUM_PROFILES = 5
LOCK_TIMEOUT = 5


celery_app = Celery(
    "worker",
    broker=f"{REDIS_URL}/0",
    backend=f"{REDIS_URL}/1",
)

celery_app.conf.update(
    result_expires=3600,
    task_serializer="json",
    accept_content=["json"],
    result_backend=f"{REDIS_URL}/1",
    worker_pool="threads",
    worker_concurrency=5,
    broker_connection_retry_on_startup=True,
    worker_prefetch_multiplier=1,
)


def acquire_profile():
    for i in range(1, NUM_PROFILES + 1):
        profile_path = os.path.join(folder_path, f"profile_{i}")
        lock_path = profile_path + ".lock"
        os.makedirs(profile_path, exist_ok=True)
        lock = FileLock(lock_path)
        try:
            lock.acquire(timeout=LOCK_TIMEOUT)
            print(f"Acquired profile {i} by {os.getpid()}")
            return profile_path, lock
        except Timeout:
            continue
    raise Exception(
        f"No profile available after {LOCK_TIMEOUT} seconds. "
        + "Please, try again later."
    )


def release_profile(lock):
    lock.release()
    print(f"Released profile by {os.getpid()}")


async def _run_scraping(browser, ruc, ig_url, uid):
    return await asyncio.gather(
        scrape_supercias_wrapper(browser, ruc, uid),
        scrape_instagram_wrapper(browser, ig_url, uid),
    )


async def get_company_info(ruc, ig_url, uid):
    profile_path, lock = acquire_profile()
    try:
        launch_options = dict(
            headless=False,
            user_data_dir=profile_path,
            color_scheme="dark",
            locale="es-EC",
            no_viewport=True,
            slow_mo=2000,
            timezone_id="America/Guayaquil",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit"
            + "/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 "
            + "Edg/139.0.0.0",
            args=["--disable-blink-features=AutomationControlled"],
        )

        if IN_DOCKER:
            with Display(visible=0, size=(800, 600)):
                async with Stealth().use_async(async_playwright()) as p:
                    browser = await p.chromium.launch_persistent_context(
                        **launch_options
                    )
                    try:
                        results = await _run_scraping(
                            browser, ruc, ig_url, uid
                        )
                    finally:
                        await browser.close()
                    return results
        else:
            async with Stealth().use_async(async_playwright()) as p:
                browser = await p.chromium.launch_persistent_context(
                    **launch_options
                )
                try:
                    results = await _run_scraping(browser, ruc, ig_url, uid)
                finally:
                    await browser.close()
                return results
    finally:
        release_profile(lock)


def sync_wrapper(ruc, ig_url, uid):
    return asyncio.run(get_company_info(ruc, ig_url, uid))


@celery_app.task(name="scrape_task")
def scrape_task(financial_info_id, ruc, ig_url):
    uid = financial_info_id
    print("Task started", financial_info_id, ruc, ig_url, uid)
    with DatabaseSession() as db:
        financial_info = (
            db.query(FinancialInfo)
            .filter(FinancialInfo.id == financial_info_id)
            .first()
        )
        if not financial_info:
            raise Exception("Financial info not found")
        financial_info.status = "IN_PROGRESS"
        db.commit()
        db.refresh(financial_info)
    sync_wrapper(ruc, ig_url, uid)
    with DatabaseSession() as db:
        analysis = analyze_company(uid)
        financial_info = (
            db.query(FinancialInfo)
            .filter(FinancialInfo.id == financial_info_id)
            .first()
        )
        financial_info.status = "COMPLETED"
        for key in SCORING_WEIGHTS.keys():
            financial_info.setattr(key, analysis.get(key, 0))
        db.commit()
        db.refresh(financial_info)
    return "Task completed"


if __name__ == "__main__":
    args = ["worker", "--loglevel=info"]
    celery_app.worker_main(argv=args)
