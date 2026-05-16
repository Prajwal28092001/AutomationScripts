from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains


def logout(driver):
    # Click user profile coin/status menu, then click logout.
    coin_btn = driver.find_element(By.XPATH, "//a[@class='dropdown-toggle 2']")
    driver.execute_script("arguments[0].click();", coin_btn)
    logout_btn = driver.find_element(By.ID, "logoutReset")
    driver.execute_script("arguments[0].click();", logout_btn)