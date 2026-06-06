"""
Herramienta de diagnóstico (NO forma parte del MVP).

El DDS-003 asumió selectores como input[name="usuario"], pero el SUV real
no los expone con esos nombres. Este script abre el SUV y vuelca los
selectores reales de inputs, botones e imagen de captcha para poder
ajustar SuvAuthenticator con datos verificados en lugar de supuestos.

Uso:
    python3 scripts/inspect_suv_login.py
"""

import asyncio

from playwright.async_api import async_playwright

SUV_URL = "https://suv2.unitru.edu.pe/"

_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)


async def main() -> None:
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-blink-features=AutomationControlled"],
        )
        context = await browser.new_context(user_agent=_USER_AGENT)
        page = await context.new_page()

        await page.goto(SUV_URL, wait_until="networkidle", timeout=60_000)

        # El template usa animsition; la pantalla puede tardar en estabilizarse
        await page.wait_for_timeout(2000)

        inputs = await page.evaluate(
            """() => Array.from(document.querySelectorAll('input, select, textarea')).map(el => ({
                tag: el.tagName.toLowerCase(),
                type: el.getAttribute('type'),
                name: el.getAttribute('name'),
                id: el.getAttribute('id'),
                placeholder: el.getAttribute('placeholder'),
                className: el.getAttribute('class')
            }))"""
        )

        buttons = await page.evaluate(
            """() => Array.from(document.querySelectorAll('button, input[type=submit], a.login100-form-btn')).map(el => ({
                tag: el.tagName.toLowerCase(),
                type: el.getAttribute('type'),
                id: el.getAttribute('id'),
                name: el.getAttribute('name'),
                text: (el.innerText || el.value || '').trim(),
                className: el.getAttribute('class')
            }))"""
        )

        images = await page.evaluate(
            """() => Array.from(document.querySelectorAll('img')).map(el => ({
                id: el.getAttribute('id'),
                src: el.getAttribute('src'),
                alt: el.getAttribute('alt'),
                className: el.getAttribute('class')
            }))"""
        )

        forms = await page.evaluate(
            """() => Array.from(document.querySelectorAll('form')).map(el => ({
                id: el.getAttribute('id'),
                name: el.getAttribute('name'),
                action: el.getAttribute('action'),
                method: el.getAttribute('method')
            }))"""
        )

        print("URL final:", page.url)
        print("\n=== FORMS ===")
        for f in forms:
            print(f)
        print("\n=== INPUTS / SELECTS ===")
        for el in inputs:
            print(el)
        print("\n=== BOTONES ===")
        for b in buttons:
            print(b)
        print("\n=== IMAGENES ===")
        for img in images:
            print(img)

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
