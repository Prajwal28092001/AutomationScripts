import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import pytest
from selenium import webdriver
import json

from Pages.logout import logout as logout_fn


@pytest.fixture
def driver():
    driver = webdriver.Chrome()
    driver.maximize_window()
    yield driver
    driver.quit()


def load_json(path: str):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_test_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return load_json(os.path.join(base_dir, "data", "add_student.json"))


class LoginPage:
    def __init__(self, driver):
        self.driver = driver

    # Locators
    CLICK_HERE = (By.LINK_TEXT, "Click here")
    BOOK_CODE = (By.ID, "Book_code")
    BOOK_CODE_CHECK = (By.ID, "bookCodeCheck")
    PAUSE_BTN = (By.XPATH, "//button[@id='pause']")
    EXIT_CONFIRM = (By.XPATH, "//button[@id='exitconfirm']")
    ADD_STUDENT_BUTTON = (By.XPATH, "//input[@id='addstudent']")
    PIN = (By.XPATH, "//input[@id='tedbookLoginpin']")
    EMAIL = (By.ID, "tedbookparentEmailInput")  
    SUBMIT = (By.ID, "tedbookParentSubmit")

    def open(self, url):
        self.driver.get(url)

    def click_here(self):
        element = WebDriverWait(self.driver, 15).until(
            EC.element_to_be_clickable(self.CLICK_HERE)
        )
        self.driver.execute_script("arguments[0].click();", element)

    def enter_book_code(self, code):
        self.driver.find_element(*self.BOOK_CODE).send_keys(code)

    def submit_book_code(self):
        element = self.driver.find_element(*self.BOOK_CODE_CHECK)
        self.driver.execute_script("arguments[0].click();", element)
        time.sleep(5)

    def pause_and_exit(self):
        btn = self.driver.find_element(*self.PAUSE_BTN)
        self.driver.execute_script("arguments[0].click();", btn)
        element = self.driver.find_element(*self.EXIT_CONFIRM)
        time.sleep(2)
        ActionChains(self.driver).move_to_element(element).click().perform()

    def fill_parent_email_pin(self, email, pin):  
        email_field = self.driver.find_element(*self.EMAIL)
        for char in email:
            email_field.send_keys(char)
            time.sleep(0.05)
        time.sleep(8)
        self.driver.find_element(*self.PIN).send_keys(pin)
        element = self.driver.find_element(*self.ADD_STUDENT_BUTTON)
        self.driver.execute_script("arguments[0].click();", element)

    def submit_form(self):
        element = self.driver.find_element(*self.SUBMIT)
        self.driver.execute_script("arguments[0].click();", element)

    def refresh(self):
        self.driver.refresh()
