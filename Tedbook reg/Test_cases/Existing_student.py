from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import os
import json

def load_test_data():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base_dir, "data", "existing_student.json")
    with open(file_path) as f:
        return json.load(f)

class LoginPage:

    def __init__(self, driver):
        self.driver = driver

    # Locators
    CLICK_HERE = (By.LINK_TEXT, "Click here")
    BOOK_CODE = (By.ID, "Book_code")
    BOOK_CODE_CHECK = (By.ID, "bookCodeCheck")
    PAUSE_BTN = (By.XPATH, "//button[@id='pause']")
    EXIT_CONFIRM = (By.XPATH, "//button[@id='exitconfirm']")
    EXISTING_STUDENT_BUTTON = (By.XPATH, "//input[@id='existingstudent']")
    STUDENT_DROPDOWN = (By.ID, "student_id")

    EMAIL = (By.ID, "tedbookparentEmailInput")
    PIN = (By.XPATH, "//input[@id='tedbookLoginpin']")
    SUBMIT = (By.ID, "tedbookParentSubmit")

    # Actions
    def open(self, url):
        self.driver.get(url)

    def click_here(self):
        # Wait up to 15s for page to load and 'Click here' link to appear
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
        time.sleep(3) 
        ActionChains(self.driver).move_to_element(element).click().perform()
        
    def fill_parent_details(self, email, pin):
        email_field = self.driver.find_element(*self.EMAIL)
        for char in email:
            email_field.send_keys(char)
            time.sleep(0.05)
        time.sleep(8)
        self.driver.find_element(*self.PIN).send_keys(pin)
        btn = self.driver.find_element(*self.EXISTING_STUDENT_BUTTON)
        self.driver.execute_script("arguments[0].click();", btn)
        
    def select_student(self, index=0):
        time.sleep(2) 
        dropdown = self.driver.find_element(*self.STUDENT_DROPDOWN)
        Select(dropdown).select_by_index(index)
    
    def submit_form(self):
        element = self.driver.find_element(*self.SUBMIT)
        self.driver.execute_script("arguments[0].click();", element)  

    def refresh(self):
        self.driver.refresh()
