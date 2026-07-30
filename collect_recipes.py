from playwright.sync_api import sync_playwright
import json
from random import uniform
from pprint import pprint
from time import sleep

def extract_single_recipe(response):
    data = dict()

    recipe = response[0]
    data["dish_name"] = recipe.get("name", None)
    data["date_published"] = recipe.get("datePublished", None)
    data["description"] = recipe.get("description", None)
    data["cook_time"] = recipe.get("cookTime", None)
    data["prep_time"] = recipe.get("prepTime", None)
    data["total_time"] = recipe.get("totalTime", None)

    nutrition = recipe.get("nutrition", {})
    data["nutrition"] = {
        k: v for k, v in nutrition.items() if not k.startswith("@")
    }

    data["categories"] = recipe.get("recipeCategory", None)
    data["cuisine"] = recipe.get("recipeCuisine", None)
    data["ingredients"] = recipe.get("recipeIngredient", None)
    data["yield"] = recipe.get("recipeYield", [None])[0] if recipe.get("recipeYield") else None

    instructions_list = recipe.get("recipeInstructions", None)
    if instructions_list is not None:
        instructions = []
        for instruction in instructions_list:
            instructions.append(instruction.get("text", None))

        data["instructions"] = instructions
    else:
        data["instructions"] = ["No instructions provided"]

    return data

with open("data/individual_recipe_link.txt") as file:
    individual_recipe_links = file.readlines()

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/141.0.0.0 Safari/537.36"
)

def dump_recipes(recipes, counter):
    with open(f"data/recipe_db{counter}.json", "w", encoding="utf-8") as file:
        json.dump(recipes, file, indent=4, ensure_ascii=False)

counter = 0
recipes = []
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    for one_recipe_link in individual_recipe_links:
        context = None
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
            page.goto(
                one_recipe_link,
                wait_until="domcontentloaded",
                timeout=60000
            )
            sleep(period)
            raw = page.locator(
                'script[type="application/ld+json"]'
            ).first.text_content()
            if not raw:
                print("NO RAW JSON-LD, SKIPPING:", one_recipe_link)
                continue
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                print("INVALID JSON, SKIPPING:", one_recipe_link)
                continue
            if not data:
                print("EMPTY DATA, SKIPPING:", one_recipe_link)
                continue
            recipes.append(extract_single_recipe(data))
        except Exception as e:
            print("FAILED:", one_recipe_link, "|", e)
        finally:
            counter += 1
            print("RUNNING...", counter)
            if context:
                context.close()
            if counter % 5 == 0:
                print("SAVING RECIPES...", counter)
                dump_recipes(recipes, counter)

dump_recipes(recipes, counter)
print("SAVING RECIPES...", counter)