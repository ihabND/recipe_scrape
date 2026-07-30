from playwright.sync_api import sync_playwright
import json
from random import uniform
from pprint import pprint
from time import sleep

with open("data/dish_links.txt", "r", encoding="utf-8") as file:
    category_links = file.readlines()
category_links = [link.strip() for link in category_links]

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/141.0.0.0 Safari/537.36"
)

separate_recipe_links = set()

with open("data/individual_recipe_link.txt", "a", encoding="utf-8") as file:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        for category_link in category_links:
            try:
                context = browser.new_context(
                    locale="en-US",
                    user_agent=USER_AGENT,
                    extra_http_headers={
                        "Accept-Language": "en-US,en;q=0.9",
                    },
                )
                page = context.new_page()
                period = uniform(0.3, 0.5)
                recipe_page = page.goto(category_link, wait_until="domcontentloaded", timeout=60000)
                sleep(period)

                raw = page.locator('script[type="application/ld+json"]').first.text_content()
                data = json.loads(raw)

                all_recipes_links = data[0]["itemListElement"]
                for recipe_link in all_recipes_links:
                    separate_recipe_links.add(recipe_link["url"])                    
                    file.write(recipe_link["url"] + "\n")
                print(f"Written {len(separate_recipe_links)} links to file.")
                    
            finally:
                print("RUNNING...")
                if context:
                    context.close()

with open("recipes_FINAL.txt", "w", encoding="utf-8") as file:
    for link in separate_recipe_links:
        file.write(link + "\n")
