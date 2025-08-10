import asyncio
from celery import Celery
from pyvirtualdisplay import Display
from playwright.async_api import async_playwright
from playwright_stealth import Stealth
from config import general_settings
from scrape import scrape_supercias, scrape_instagram
from databases.postgres import DatabaseSession, FinancialInfo

REDIS_URL = general_settings.REDIS_URL
IN_DOCKER = general_settings.IN_DOCKER


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
    worker_concurrency=10,
    broker_connection_retry_on_startup=True,
    worker_prefetch_multiplier=1,
)


async def _run_scraping(browser, ruc, ig_url, uid):
    return await asyncio.gather(
        scrape_supercias(browser, ruc, uid),
        scrape_instagram(browser, ig_url, uid),
    )


async def get_company_info(ruc, ig_url, uid):
    launch_options = dict(
        headless=False,
        user_data_dir="./scrape/user-data",
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
                    results = await _run_scraping(browser, ruc, ig_url, uid)
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
        financial_info = (
            db.query(FinancialInfo)
            .filter(FinancialInfo.id == financial_info_id)
            .first()
        )
        financial_info.status = "COMPLETED"
        db.commit()
        db.refresh(financial_info)
    return "Task completed"


if __name__ == "__main__":
    args = ["worker", "--loglevel=info"]
    celery_app.worker_main(argv=args)
