from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class LoginPage:

    def __init__(self, driver):
        self.driver = driver

    # Locators
    CLICK_HERE = (By.LINK_TEXT, "Click here")
    BOOK_CODE = (By.ID, "Book_code")
    BOOK_CODE_CHECK = (By.ID, "bookCodeCheck")
    PAUSE_BTN = (By.XPATH, "//button[@id='pause']")
    EXIT_CONFIRM = (By.XPATH, "//button[@id='exitconfirm']")

    EMAIL = (By.ID, "tedbookparentEmailInput")
    FIRST_NAME = (By.ID, "tedbookparentFName")
    LAST_NAME = (By.ID, "tedbookparentLName")
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
        time.sleep(5) 
        ActionChains(self.driver).move_to_element(element).click().perform()
        

    def fill_parent_details(self, email, fname, lname):
        self.driver.find_element(*self.EMAIL).send_keys(email)
        time.sleep(3) 
        self.driver.find_element(*self.FIRST_NAME).send_keys(fname)
        time.sleep(3) 
        self.driver.find_element(*self.LAST_NAME).send_keys(lname)
        time.sleep(3) 

    def submit_form(self):
        element = self.driver.find_element(*self.SUBMIT)
        self.driver.execute_script("arguments[0].click();", element)
       