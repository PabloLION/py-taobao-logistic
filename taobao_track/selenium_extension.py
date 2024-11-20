import time

from selenium import webdriver


def scroll_to_bottom(
    driver: webdriver.Chrome, max_attempts: int = 20, pause_time: float = 1
):
    """
    Scroll to the bottom of the page multiple times until no more content is loaded.

    :param driver: Selenium WebDriver instance
    :param max_attempts: Maximum number of scroll attempts
    :param pause_time: Time to wait between scrolls (in seconds)
    """
    last_height: int = driver.execute_script("return document.body.scrollHeight")  # type: ignore

    for _attempt in range(max_attempts):
        # Scroll to the bottom of the page
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")  # type: ignore

        # Wait for the page to load
        time.sleep(pause_time)

        # Check the new height of the page
        new_height: int = driver.execute_script("return document.body.scrollHeight")  # type: ignore

        if new_height == last_height:
            print("Reached the bottom of the page.")
            break  # Stop if the page height hasn't changed

        last_height = new_height  # type: ignore

    else:
        print("Maximum scroll attempts reached. Content may still be loading.")
