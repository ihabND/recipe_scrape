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

all_links_list = []
side_links_list = []

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
                    all_links_list.append(href)
                    context = browser.new_context(
                        locale="en-US",
                        user_agent=USER_AGENT,
                        extra_http_headers={
                            "Accept-Language": "en-US,en;q=0.9",
                        },
                    )
                    page = context.new_page()
                    try:
                        period = uniform(0.5, 1.5)
                        sleep(period)
                        page.goto(href, wait_until="domcontentloaded", timeout=60000)
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
                            side_links_list.append(inner_link["href"])
                    finally:
                        context.close()
    finally:
        main_context.close()
        browser.close()

try:
    for link in all_links_list:
        print(link)
    print(len(all_links_list))

    with open("data/dish_links.txt", "w", encoding="utf-8") as file:
        for link in all_links_list:
            file.write(str(link) + "\n")

    with open("data/inner_links.txt", "w", encoding="utf-8") as file:
        for link in side_links_list:
            file.write(str(link) + "\n")
except Exception as e:
    print(f"Error while writing files! {e}")
