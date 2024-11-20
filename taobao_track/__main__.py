## Configurations
# old HISTORY_URL = r"https://buyertrade.taobao.com/trade/itemlist/list_bought_items.htm?spm=a21bo.jianhua/a.bought.1.5af92a89JTa1X3"
HOMEPAGE_URL = r"https://www.taobao.com/"
TRACK_URL = r"https://buyertrade.taobao.com/trade/itemlist/list_bought_items.htm?spm=tbpc.mytb_index.bought.1.6db2782dNjKsZF"
HOMEPAGE_LOAD_TIME = 1
TRACK_PAGE_LOAD_TIME = 3
HOVER_DROPDOWN_DISAPPEAR_TIME = 0.5
HOVER_DROPDOWN_LOAD_TIME = 2

_DEV_VERBOSE = False
_DEV_MAX_TRACK_NUM = 16
## Constants
TRACK_ENTRY_WRAPPER_SELECTOR = "div.index-mod__order-container___1ur4-"
TRACK_HEADER_SELECTOR = "td.bought-wrapper-mod__head-info-cell___29cDO"
ORDER_ID_FROM_TRACK_HEADER_SELECTOR = ":scope > span > span:nth-child(3)"
TRACK_HOVER_TRIGGER_SELECTOR = "a#viewLogistic"
TRACK_DROPDOWN_SELECTOR = ".tm-tooltip"
TRACK_DROPDOWN_LOGISTIC_SELECTOR = "div.logistics-info-mod__header___1z4Ea"

import pickle
import time
from pathlib import Path
from typing import TYPE_CHECKING

from selenium.webdriver.remote.webelement import WebElement

if TYPE_CHECKING:
    from _typeshed import SupportsWrite

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By

COOKIE_FILE = Path(__file__).parent.parent / "taobao-track-temp" / "cookies.pkl"


class Track: ...


def dev_print(
    *values: object,
    sep: str | None = " ",
    end: str | None = "\n",
    file: "SupportsWrite[str] | None" = None,
) -> None:
    if _DEV_VERBOSE:
        print(*values, sep=sep, end=end, file=file, flush=False)


def login_or_load_cookie(driver: webdriver.Chrome, cookie_file: Path):
    if not cookie_file.exists():
        driver.get(TRACK_URL)  # 替换为目标网站

        print("请手动完成登录，完成后按回车键继续...")
        input("按回车键继续")
        # for english version:
        # print("Please log in manually.")
        # input("Press Enter after logging in...")

        # Save cookies to a file
        with open(cookie_file, "wb") as file:
            pickle.dump(driver.get_cookies(), file)  # type: ignore
            # ignore/selenium get_cookies(): returns List[Dict[str, Any]]
        print("Cookies saved.")

    else:  # Load cookies into the browser and reuse session
        driver.get(HOMEPAGE_URL)
        time.sleep(HOMEPAGE_LOAD_TIME)

        with open(cookie_file, "rb") as file:
            cookies = pickle.load(file)

            for cookie in cookies:
                """debug loading cookie
                print(f"Adding cookie: {cookie}")
                current_domain = driver.current_url.split("/")[2]
                cookie_domain = cookie.get("domain", "")

                # Check if the cookie's domain matches the current domain
                if not current_domain.endswith(cookie_domain.strip(".")):  # type: ignore
                    # ignore/selenium WebDriver.current_url: returns str
                    print(
                        f"Invalid cookie: {cookie['name']} with domain {cookie_domain}"
                    )
                    continue  # Skip this cookie

                try:
                    driver.add_cookie(cookie)  # type: ignore
                    # ignore/selenium get_cookies(): returns List[Dict[str, Any]]
                    # print(f"Added cookie: {cookie['name']}")
                except Exception as e:
                    print(f"Failed to add cookie {cookie['name']}: {e}")
                """

                if cookie["domain"] == "buyertrade.taobao.com":
                    continue
                driver.add_cookie(cookie)  # type: ignore
                # ignore/selenium get_cookies(): returns List[Dict[str, Any]]
            # Refresh to apply cookies
            driver.refresh()
            print("Logged in using saved session.")
            driver.get(TRACK_URL)  # 替换为目标网站
            for cookie in cookies:
                if cookie["domain"] == "buyertrade.taobao.com":
                    driver.add_cookie(cookie)  # type: ignore
                    # ignore/selenium get_cookies(): returns List[Dict[str, Any]]
            driver.refresh()

        time.sleep(TRACK_PAGE_LOAD_TIME)


# def scrape_whole_page


def scrape_current_page(
    driver: webdriver.Chrome,
):
    page_scrape_result = list[tuple[str, str]]()
    body = driver.find_element(By.TAG_NAME, "body")  # to move to topleft corner

    track_entries = driver.find_elements(By.CSS_SELECTOR, TRACK_ENTRY_WRAPPER_SELECTOR)
    actions = ActionChains(driver)
    last_hover_dropdowns = list[WebElement]()

    for _cnt, entry_wrapper in enumerate(iterable=track_entries, start=1):
        if _cnt > _DEV_MAX_TRACK_NUM:
            break

        track_header = entry_wrapper.find_element(  # type: ignore
            # ignore/selenium WebElement.find_element(): returns WebElement
            By.CSS_SELECTOR,
            TRACK_HEADER_SELECTOR,
        )
        order_id = track_header.find_element(  # type: ignore
            # ignore/selenium WebElement.find_element(): returns WebElement
            By.CSS_SELECTOR,
            ORDER_ID_FROM_TRACK_HEADER_SELECTOR,
        ).text
        dev_print("订单号:", order_id)

        # mark the element
        driver.execute_script(  # type: ignore
            # ignore/selenium WebDriver.execute_script(): returns Any
            """
            arguments[0].style.border = '2px solid red';
            arguments[0].style.backgroundColor = 'yellow';
            """,
            entry_wrapper,
        )

        dropdown_trigger_elements = entry_wrapper.find_elements(  # type: ignore
            # ignore/selenium WebElement.find_elements(): returns List[WebElement]
            By.CSS_SELECTOR,
            TRACK_HOVER_TRIGGER_SELECTOR,
        )
        if len(dropdown_trigger_elements) != 1:
            print(
                f"Invalid number of hover elements {len(dropdown_trigger_elements)} for track {order_id}"
            )
            page_scrape_result.append((order_id, "N/A: No dropdown trigger element"))
            continue
        trigger_element = dropdown_trigger_elements[0]

        actions.move_to_element_with_offset(body, 0, 0).perform()

        actions.move_by_offset(-200, 0).perform()  # move to the corner
        time.sleep(HOVER_DROPDOWN_DISAPPEAR_TIME)
        actions.move_to_element(trigger_element).perform()
        time.sleep(HOVER_DROPDOWN_LOAD_TIME)
        # Perform actions after hovering
        # The dropdown should now be visible, but they are not in the entry_wrapper
        # use the driver to find all the dropdowns and get the last one
        hover_dropdowns = driver.find_elements(  # type: ignore
            # ignore/selenium WebElement.find_element(): returns WebElement
            By.CSS_SELECTOR,
            TRACK_DROPDOWN_LOGISTIC_SELECTOR,
        )
        if len(hover_dropdowns) - len(last_hover_dropdowns) != 1:
            print(
                f"Invalid number of last hover dropdowns: {len(last_hover_dropdowns)=}, {len(hover_dropdowns)=} for track {order_id}"
            )
            dev_print(page_scrape_result)
            page_scrape_result.append((order_id, "N/A: No new dropdown element"))
            continue
        last_hover_dropdowns = hover_dropdowns

        # time.sleep(HOVER_DROPDOWN_LOAD_TIME)
        hover_dropdown = hover_dropdowns[-1]  # always the last one
        logistic_info = hover_dropdown.text
        dev_print("Hover content:", logistic_info)

        page_scrape_result.append((order_id, logistic_info))
        print(f"Scrapped {order_id=}, {logistic_info=}")

    return page_scrape_result


if __name__ == "__main__":
    total_scrape_result = list[tuple[str, str]]()
    driver = webdriver.Chrome()

    login_or_load_cookie(driver, COOKIE_FILE)

    user_wants_to_scrape = True
    while user_wants_to_scrape:
        page_scrape_result = scrape_current_page(driver)
        total_scrape_result.extend(page_scrape_result)
        user_answer = input("Page scraped. 'q' to quit, otherwise continue: ")
        user_wants_to_scrape = user_answer.lower() != "q"

    print(f"Scrap result {total_scrape_result=}")
    driver.quit()
