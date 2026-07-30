from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from random import uniform
from time import sleep

temp = "https://www.allrecipes.com/"

BASE_URL = "https://www.allrecipes.com/recipes-a-z-6735880"

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/141.0.0.0 Safari/537.36"
)

all_links_list = set()

def write_recipe_links_to_files(all_links_list):
    try:
        print("Writing to files...", len(all_links_list))

        with open("data/dish_links.txt", "w", encoding="utf-8") as file:
            for link in all_links_list:
                file.write(str(link) + "\n")

    except Exception as e:
        print(f"Error while writing files! {e}")    


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    try:
        main_context = browser.new_context(
            locale="en-US",
            user_agent = USER_AGENT,
            extra_http_headers={"Accept-Language": "en-US,en;q=0.9"},
        )
        main_page = main_context.new_page()
        main_page.goto(BASE_URL, wait_until="networkidle", timeout=60000)
        page_content = BeautifulSoup(main_page.content(), "html.parser")
        print("Working main")
        all_link_groups = page_content.find_all("div", {"class" : "mntl-alphabetical-list__group"})
        for link_group in all_link_groups:
            all_links = link_group.find_all("a")
            for link in all_links:
                href = link.get("href", None)
                if href is None:
                    continue
                if href not in all_links_list:
                    all_links_list.add(href)
                    context = browser.new_context(
                        locale="en-US",
                        user_agent=USER_AGENT,
                        extra_http_headers={
                            "Accept-Language": "en-US,en;q=0.9",
                        },
                    )
                    page = context.new_page()
                    try:
                        period = uniform(0.3, 0.5)
                        sleep(period)
                        inner_response = page.goto(href, wait_until="domcontentloaded", timeout=60000)
                        print("URL:", href, "Status:", inner_response.status if inner_response else "No response")
                        inner_content = BeautifulSoup(page.content(), "html.parser")
                        print("Working inner:", href)
                        inner_links_div = inner_content.find("ul", {
                            "id": "mntl-taxonomy-nodes__list_1-0",
                            "class": "mntl-taxonomy-nodes__list"
                        })
                        if inner_links_div is None:
                            continue
                        inner_links_list = inner_links_div.find_all("a")
                        for inner_link in inner_links_list:
                            inner_href = inner_link.get("href")
                            all_links_list.add(inner_href)

                        write_recipe_links_to_files(all_links_list)
                        
                    finally:
                        context.close()
    finally:
        main_context.close()
        browser.close()