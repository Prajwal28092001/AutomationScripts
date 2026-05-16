from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


def login(driver, username, password):
    username_input = driver.find_element(By.ID, "inputLogin")
    username_input.send_keys(username)
    password_input = driver.find_element(By.ID, "inputPassword")
    password_input.send_keys(password)
    login_button = driver.find_element(By.ID, "loginSubmit")
    login_button.click()