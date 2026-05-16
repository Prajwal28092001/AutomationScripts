from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException


def Lumos_Assistent(driver):
    """Close the Lumos assistant popup if it appears. Silently skips if not present."""
    try:
        coin_btn = driver.find_element(By.XPATH, "//span[@class='glyphicon glyphicon-remove']")
        driver.execute_script("arguments[0].click();", coin_btn)
        print("  -> Closed Lumos Assistant popup.")
    except NoSuchElementException:
        pass  # Popup not present on this page load, continue normally
