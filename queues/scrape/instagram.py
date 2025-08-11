import json
import os
import asyncio
from playwright.async_api import Page, ElementHandle
from datetime import datetime
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from config import general_settings

API_KEY = general_settings.API_KEY
IG_USERNAME = general_settings.IG_USERNAME
IG_PASSWORD = general_settings.IG_PASSWORD

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)


llm = ChatOpenAI(
    model="gpt-4.1",
    openai_api_key=API_KEY,
    temperature=0.2,
)


def get_likes_from_text(llm, content):
    message = HumanMessage(
        content=[
            {
                "type": "text",
                "text": "Eres un analizador de números escritos con palabras. "
                + "Dame el número de likes que tiene la publicación."
                + "A veces dice 'Le gusta a <PERSONA> y <NÚMERO> más',"
                + "en ese caso, suma el número de likes más el número que dice."
                + "Si no hay número, devuelve 0. No explicas por qué, solo"
                + "devuelve el número",
            },
            {
                "type": "text",
                "text": f"El texto es: '{content}'",
            },
        ]
    )

    response = llm.invoke([message])
    return response.content


def get_number_from_text(llm, content):
    message = HumanMessage(
        content=[
            {
                "type": "text",
                "text": "Eres un analizador de números escritos con palabras, "
                + "dame cada número identificado separados por comas sin "
                + "espacio entre ellos. Si no hay números, devuelve ninguno.",
            },
            {
                "type": "text",
                "text": f"El texto es: '{content}'",
            },
        ]
    )

    response = llm.invoke([message])
    return response.content


def get_days_from_date(llm, post_date):
    curr_date = datetime.now().strftime("%Y-%m-%d")
    message = HumanMessage(
        content=[
            {
                "type": "text",
                "text": "Eres un analizador de fechas. Dame la fecha en "
                + "formato YYYY-MM-DD. Si no hay fecha, devuelve ninguno. "
                + "Ten en cuenta el curr_date y si la fecha es relativa, "
                + "calcula la fecha absoluta.",
            },
            {
                "type": "text",
                "text": f"La fecha actual es: {curr_date}",
            },
            {
                "type": "text",
                "text": f"La fecha de la publicación es: {post_date}",
            },
        ]
    )

    response = llm.invoke([message])
    post_date = datetime.now().date()
    try:
        post_date = datetime.strptime(response.content, "%Y-%m-%d").date()
    except ValueError:
        return None

    diff = datetime.now().date() - post_date
    return diff.days


async def load_comments(page: Page, times: int):
    for _ in range(times):
        try:
            load_button = await page.wait_for_selector(
                "ul._a9z6._a9za > div button._abl-", timeout=1000
            )
            await load_button.click()
            await page.wait_for_selector(
                "div[role='progressbar']", state="detached", timeout=1000
            )
        except Exception:
            return


async def get_post_info(page: Page, post: ElementHandle):
    await post.click()
    await asyncio.sleep(0.2)

    dummy_content = {
        "description": "",
        "comments": [],
    }
    try:
        await page.wait_for_selector("ul._a9z6._a9za > div", timeout=3000)
        sections = await page.query_selector_all("ul._a9z6._a9za > div")
        description = await sections[0].query_selector("div._a9zr > div")
        description_text = await description.inner_text()
        parsed_description = description_text.strip().replace("\n", " ")
        dummy_content["description"] = parsed_description
        comments_section = await sections[-1].query_selector("> div > div")
        await load_comments(page, 3)
        all_comments = await comments_section.query_selector_all("> div")
        comments_info = []
        for comment in all_comments:
            comment_container = await comment.query_selector("div._a9zr")
            comment_text = await comment_container.query_selector(
                "div.xt0psk2 > span"
            )
            likes = await comment_container.query_selector_all("> div")
            likes_element = await likes[-1].query_selector("button")
            likes_text = await likes_element.text_content()
            num_likes = 0
            try:
                if "Responder" not in likes_text:
                    num_likes = int(likes_text.split(" ")[0])
            except Exception:
                num_likes = get_number_from_text(llm, likes_text)

            comments_info.append(
                {
                    "comment": await comment_text.text_content(),
                    "likes": num_likes if num_likes != "ninguno" else 0,
                }
            )
        dummy_content["comments"] = comments_info
    except Exception:
        pass

    likes_section = await page.query_selector(
        ".html-div.xexx8yu.xyri2b.x18d9i69.x1c1uobl.x9f619.xjbqb8w.x78zum5"
        + ".x15mokao.x1ga7v0g.x16uus16.xbiv7yw.xr1yuqi"
    )
    likes_text = await likes_section.inner_text()
    num_likes_post = get_likes_from_text(llm, likes_text)

    last_day = await page.query_selector("div.x1yztbdb.x1h3rv7z.xf7dkkf time")
    last_day_text = await last_day.text_content()
    num_days = get_days_from_date(llm, last_day_text)

    close_button = await page.wait_for_selector(
        ".xo2ifbc.x10l6tqk.x1eu8d0j.x1vjfegm > div > div"
    )
    await close_button.click()

    return {
        "description": dummy_content["description"],
        "likes": num_likes_post,
        "last_day": num_days,
        "comments": dummy_content["comments"],
    }


async def get_rows(page: Page, min_rows: int = 5, retries: int = 3):
    try:
        post_container = await page.query_selector(".xg7h5cd.x1n2onr6")
        prev_rows = await post_container.query_selector_all(
            "._ac7v.x1ty9z65.xzboxd6"
        )
    except Exception:
        return [], False
    while (len(prev_rows) < min_rows) and (retries > 0):
        await page.evaluate(
            """
            window.scrollTo(0, document.body.scrollHeight);
            """
        )
        try:
            await page.wait_for_selector(
                ".html-div.x14z9mp.xat24cr.x1lziwak.xexx8yu.xyri2b.x18d9i69"
                + ".x1c1uobl.x9f619.x16ye13r",
                state="detached",
                timeout=3000,
            )
        except Exception:
            pass
        rows = await post_container.query_selector_all(
            "._ac7v.x1ty9z65.xzboxd6"
        )
        if len(prev_rows) == len(rows):
            retries -= 1
        prev_rows = rows

    return prev_rows, True


async def attemp_to_login(page: Page):
    try:
        await page.wait_for_selector("input[name='username']", timeout=2000)

        await page.type(
            "input[name='username']",
            IG_USERNAME,
            delay=100,
        )
        await asyncio.sleep(0.2)
        await page.type("input[name='password']", IG_PASSWORD, delay=150)
        await asyncio.sleep(1)
        await page.click("button[type='submit']", delay=100)
    except Exception:
        print("Ya logeado")


async def scrape_instagram(browser, url, uid):
    folder_path = os.path.join(parent_dir, "generated")
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    page = await browser.new_page()
    await page.goto("https://www.instagram.com")

    await attemp_to_login(page)

    # print("Inicio de sesión exitoso")
    await asyncio.sleep(3)

    await page.goto(url)
    name_container = await page.query_selector("h2.x1lliihq")
    if not name_container:
        await page.close()
        early_json = {
            "profile": {},
            "posts": [],
        }
        with open(f"{folder_path}/{uid}.json", "w", encoding="utf-8") as f:
            json.dump(early_json, f, indent=4, ensure_ascii=False)
        return early_json

    name = await name_container.inner_text()
    # print("name", name)

    profile_follows = await page.query_selector_all(
        ".xc3tme8.x1xdureb.x18wylqe.x13vxnyz.xvxrpd7 > ul > li"
    )
    # print("len(profile_follows)", len(profile_follows))
    profile_texts = []
    for follow in profile_follows:
        text = await follow.inner_text()
        profile_texts.append(text)

    profile_follows_text = "\n".join(profile_texts)
    # print("profile_follows_text", profile_follows_text)
    post_num, follower_num, following_num = get_number_from_text(
        llm, profile_follows_text
    ).split(",")
    # print(post_num, follower_num, following_num)

    description = await page.query_selector(".x7a106z")
    description_text = await description.inner_text()
    parsed_description = description_text.strip().replace("\n", " ")

    verified = await page.query_selector(
        ".x78zum5.x193iq5w.x6ikm8r.x10wlt62 title"
    )
    is_verified = False
    if verified:
        is_verified = "Verificado" in await verified.text_content()
    # print(is_verified)

    rows, is_public = await get_rows(page, min_rows=3)

    # print(len(rows))
    all_posts = []
    all_posts_handles = []
    for row in rows:
        curr_posts = await row.query_selector_all("a")
        all_posts_handles += curr_posts
        for post in curr_posts:
            href = await post.get_attribute("href")
            final_href = f"https://www.instagram.com{href}"
            all_posts.append(final_href)

    # print(len(all_posts))

    posts_info = []
    for post in all_posts_handles:
        results = await get_post_info(page, post)
        posts_info.append(results)
        await asyncio.sleep(0.5)

    final_json = {
        "profile": {
            "name": name,
            "description": parsed_description,
            "is_verified": is_verified,
            "post_num": post_num,
            "follower_num": follower_num,
            "following_num": following_num,
            "is_public": is_public,
        },
        "posts": posts_info,
    }

    with open(f"{folder_path}/{uid}.json", "w", encoding="utf-8") as f:
        json.dump(final_json, f, indent=2, ensure_ascii=False)

    print(f"Scraping results saved in {folder_path}/{uid}.json")

    await page.close()

    return final_json


async def scrape_instagram_wrapper(browser, ig_url, uid):
    try:
        return await scrape_instagram(browser, ig_url, uid)
    except Exception as e:
        print(e)
        return {
            "profile": {},
            "posts": [],
        }
