import asyncio
import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from config import general_settings


API_KEY = general_settings.API_KEY

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)


llm = ChatOpenAI(
    model="gpt-4.1",
    openai_api_key=API_KEY,
    temperature=0.2,
)

base_url = (
    "https://appscvsgen.supercias.gob.ec/consultaCompanias/"
    + "societario/busquedaCompanias.jsf"
)
pdf_doc = {}


async def download_pdf(page, url_pdf, output_path):
    response = await page.request.get(url_pdf)
    if response.ok:
        content = await response.body()
        with open(output_path, "wb") as f:
            f.write(content)
        print(f"PDF descargado en {output_path}")
    else:
        print(f"Error al descargar PDF: {response.status}")


async def supercias_ocr(llm, image_jshandle):
    img_b64 = await image_jshandle.evaluate(
        """
            img => {
            const canvas = document.createElement('canvas');
            canvas.width = img.naturalWidth;
            canvas.height = img.naturalHeight;
            const ctx = canvas.getContext('2d');
            ctx.drawImage(img, 0, 0);
            return canvas.toDataURL().split(',')[1];
            }
        """
    )
    message = HumanMessage(
        content=[
            {
                "type": "text",
                "text": "Eres un OCR, dame el texto que veas en la imagen, "
                + "solo el texto, no hay que dar explicaciones",
            },
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{img_b64}"},
            },
        ]
    )

    response = llm.invoke([message])
    return response.content


async def process_loading(page):
    await asyncio.sleep(0.2)
    try:
        await page.wait_for_selector("#j_idt1210", state="hidden")
    except Exception:
        pass

    await asyncio.sleep(0.2)
    try:
        input_text = await page.wait_for_selector(
            "div#dlgCaptcha input#frmCaptcha\\:captcha", timeout=1500
        )
        image_captcha = await page.wait_for_selector(
            "div#dlgCaptcha img#frmCaptcha\\:captchaImage", timeout=1500
        )
        captcha_text = await supercias_ocr(llm, image_captcha)
        await input_text.type(captcha_text, delay=100)
        await page.keyboard.press("Enter")
    except Exception:
        pass

    await asyncio.sleep(0.2)
    try:
        await page.wait_for_selector("#j_idt1210", state="hidden")
    except Exception:
        pass


async def scrape_supercias(browser, ruc, uid):
    folder_path = os.path.join(parent_dir, "generated")
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    page = await browser.new_page()

    def handle_request(request):
        url = request.url

        if "documento" in url:
            pdf_doc[uid] = url

    page.on("request", handle_request)

    await page.goto(base_url)

    radio_blanks = await page.query_selector_all(
        ".ui-radiobutton-icon.ui-icon.ui-c.ui-icon-blank"
    )
    await radio_blanks[0].click()
    # print("Clickeando RUC")

    await asyncio.sleep(0.2)

    text_input = await page.query_selector("input[type='text']")
    await text_input.type(ruc, delay=100)
    # print("Escribiendo RUC")

    await asyncio.sleep(0.2)

    first_li_result = await page.query_selector("ul li")
    await first_li_result.click()
    # print("Seleccionando 1er resultado del autocomplete")

    await asyncio.sleep(0.2)

    all_images = await page.query_selector_all("table img")
    ocr_img = all_images[-1]

    ocr_text = await supercias_ocr(llm, ocr_img)
    tbody_handle = await ocr_img.evaluate_handle(
        """
        async (el) => {
            let parent = el.parentElement;
            while (parent && parent.tagName.toLowerCase() !== 'tbody') {
            parent = parent.parentElement;
            }
            return parent;
        }
        """
    )
    ocr_input = await tbody_handle.query_selector("input[type='text']")
    await ocr_input.type(ocr_text, delay=50)
    # print("Escribiendo el texto ocr")

    button_span = await page.query_selector(".ui-button-text.ui-c")
    parent_span = await button_span.evaluate_handle("el => el.parentElement")
    await parent_span.click()
    # print("Clickeando boton verificar")

    await asyncio.sleep(0.2)

    online_docs = await page.wait_for_selector("#frmMenu\\:menuDocumentacion")
    await online_docs.click()
    # print("Clickeando Documentos onlines")

    await process_loading(page)

    economic_docs = await page.wait_for_selector(
        "#frmInformacionCompanias\\:tabViewDocumentacion\\:j_idt964"
    )
    await economic_docs.click()
    # print("Clickeando Documentos economicos")

    await process_loading(page)

    search_input = await page.query_selector(
        "input#frmInformacionCompanias\\:tabViewDocumentacion\\:"
        + "tblDocumentosEconomicos\\:j_idt969\\:filter"
    )
    await search_input.type("BALANCE", delay=100)

    await process_loading(page)

    await page.wait_for_selector(
        "#frmInformacionCompanias\\:tabViewDocumentacion\\:"
        + "tblDocumentosEconomicos_paginator_bottom > a",
        timeout=4000,
    )
    nav_bar = await page.query_selector_all(
        "#frmInformacionCompanias\\:tabViewDocumentacion\\:"
        + "tblDocumentosEconomicos_paginator_bottom > a"
    )
    last_page = nav_bar[-1]
    classes = await last_page.get_attribute("class")
    if classes and "ui-state-disabled" not in classes:
        await last_page.click()

    await process_loading(page)

    rows = []
    try:
        await page.wait_for_selector(
            "tbody#frmInformacionCompanias\\:tabViewDocumentacion\\:"
            + "tblDocumentosEconomicos_data > tr",
            timeout=8000,
        )
        rows = await page.query_selector_all(
            "tbody#frmInformacionCompanias\\:tabViewDocumentacion\\:"
            + "tblDocumentosEconomicos_data > tr",
        )
        print(len(rows))
        last_balance = rows[-1]
        pdf_link = await last_balance.query_selector("a")
        await pdf_link.click()
    except Exception:
        print("No tiene balance")
        no_doc_json = {
            "name": None,
        }
        return no_doc_json

    await process_loading(page)

    await asyncio.sleep(2)

    if pdf_doc[uid]:
        await download_pdf(page, pdf_doc[uid], f"{folder_path}/{uid}.pdf")

    return {
        "name": f"{uid}.pdf",
    }
