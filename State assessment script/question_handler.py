import random
import string
from selenium import webdriver
import unittest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
import time
from api_test import ask_chatgpt  # Assuming this function is in api_test.py
class QuestionTypeHandler:

    def __init__(self, driver, question_list):
        self.driver = driver
        self.driver.implicitly_wait(10)
        self.question_list = question_list

    def is_element_present(self, locator):
        """Check if an element is present on the page."""
        try:
            WebDriverWait(self.driver, 5).until(EC.presence_of_element_located(locator))
            return True
        except:
            return False

    def generate_random_characters(self, length):
        # Choose characters from uppercase, lowercase, digits, and punctuation
        characters = string.ascii_letters + string.digits + string.punctuation
        # Randomly select the specified number of characters
        random_chars = ''.join(random.choice(characters) for _ in range(length))
        return random_chars

    def answer_question(self):
        """Identify and handle different question types dynamically."""
        try:
            # First check if i am in the last question
            if self.is_element_present((By.XPATH, "//*[@class='btn btn-lg btn-danger pull-right reviewUnanswered']")):
                return "LASTQUESTION"
            # Map question types to their handling methods
            question_types = [
                ('//*[@id="cke_1_contents"]/iframe', self.ECR),
                ("//*[@class='editor12']", self.numerical_question),
                ("//*[@class='radio12']", self.MCSA_and_MCMA),
                ("//*[@id='selectoption']", self.handle_type_5),
                ("//*[@class='box ui-droppable']", self.handle_type_4),
                ("//*[@type='checkbox']", self.handle_type_checkbox)
            ]

            # Iterate through the question types and execute the appropriate handler
            handled = False
            for xpath, handler in question_types:
                if self.is_element_present((By.XPATH, xpath)):
                    handler()
                    handled = True
                    break
            if handled:
                return "HANDLED"
            else:
                return "UNHANDLED"
        except Exception as e:
            print(f"An error occurred while answering the question: {str(e)}")
            return "ERROR"

    def numerical_question(self):
        if self.is_element_present((By.XPATH, "//*[@class='editor12']")):
            print("Handling  Numberical question type")
            last_question= ""
            question_element=self.driver.find_element(By.CSS_SELECTOR, ".test_question")
            if question_element:
                # Extract all text and replace new lines with spaces
                question_text = question_element.text.replace("\n", " ").strip()
                if question_text== last_question:
                    print("No new question found. Retrying...")
                    time.sleep(2)
                last_question=question_text
                #print(question)
                print(f"Question: {question_text}")

                # Get the correct answer from ChatGPT
                correct_answer = ask_chatgpt(question_text)
                print(f"ChatGPT Answer: {correct_answer}")
                self.driver.find_element(By.XPATH, "//*[@class='editor12']").send_keys(correct_answer)
        #time.sleep(2)

    def MCSA_and_MCMA(self):
        if self.is_element_present((By.XPATH, "//*[@class='radio12']")):
            radio_buttons = self.driver.find_elements(By.XPATH, "//*[@class='radio12']")
            if len(radio_buttons) > 4:
                print("Handling MCMA ")
                for index in [1, 3, 4, 6, 8]:
                    radio_buttons[index].click()
            elif len(radio_buttons) == 4:
                print("Handling MCQ question Type")
                questiontext=self.driver.find_element(By.CSS_SELECTOR, ".test_question")
                question_text = questiontext.text.replace("\n", " ").strip()
                print(question_text)
                #print(self.question_list)
                correct_answer = None
                found = False
                for q in self.question_list:
                    if q["question"] == question_text:
                        correct_answer = q["correct_answer"]
                        print(correct_answer)
                    else:
                        self.driver.execute_script("arguments[0].click();", radio_buttons[random.randint(0, 3)])

                    options = self.driver.find_elements(By.CSS_SELECTOR, "div.option_text")
                    radio_buttons = self.driver.find_elements(By.XPATH, "//*[@class='radio12']")
                    if correct_answer:
                        found = False
                        for index, option in enumerate(options):
                            if option.text.strip() == correct_answer:
                                #print(f"Correct Answer Found: {correct_answer} at index {index}")

                                if index < len(radio_buttons):
                                    #print(f"Clicking radio button at index {index}")
                                    self.driver.execute_script("arguments[0].click();", radio_buttons[index])
                                    found = True
                                    break
                                else:
                                    print("Index out of range for radio_buttons!")

                        if not correct_answer or not found:
                            print("Correct answer not found, clicking default option.")
                            self.driver.execute_script("arguments[0].click();", radio_buttons[random.randint(0, 3)])
                            if len(radio_buttons) > 2:
                                self.driver.execute_script("arguments[0].click();", radio_buttons[2])
                #print("Hello Aman 2")
            else:
                print("Handling MCQ")
                indexx=random.randint(0,3)
                radio_buttons[indexx].click()
        #time.sleep(2)

    def handle_type_4(self): 
        print("Handling question type 4")
        sources = [
            self.driver.find_element(By.XPATH, "//*[@id='node1']"),
            self.driver.find_element(By.XPATH, "//*[@id='node2']"),
        ]
        targets = [
            self.driver.find_element(By.XPATH, "(//*[@class='box ui-droppable'])[1]"),
            self.driver.find_element(By.XPATH, "(//*[@class='box ui-droppable'])[2]"),
        ]
        actions = ActionChains(self.driver)
        for source, target in zip(sources, targets):
            actions.drag_and_drop(source, target).perform()
        #time.sleep(2)

    def handle_type_5(self):
        print("Handling  dropdown question type")
        dropdown_element = self.driver.find_element(By.XPATH, "//*[@id='selectoption']")
        Select(dropdown_element).select_by_visible_text("=")

    def handle_type_checkbox(self):
        checkboxes = self.driver.find_elements(By.XPATH, "//*[@type='checkbox']")
        if len(checkboxes) > 5:
            print("Handling MCMA ")
            for index in [0, 4, 8, 12]:
                checkboxes[index].click()
        else:
            print("Handling MCMA")
            checkboxes[0].click()
        #time.sleep(2)
    def ECR(self):
        if self.is_element_present((By.XPATH, "//*[@id='cke_1_contents']/iframe")):
            driver=self.driver
            wait = WebDriverWait(driver, 10).until
            print("Handling question type 17")
            last_question= ""
            ECRquestion_element = wait(EC.presence_of_element_located((By.CSS_SELECTOR, ".test_question")))
            if ECRquestion_element:
                # Extract all text and replace new lines with spaces
                Question_text = ECRquestion_element.text.replace("\n", " ").strip()

                if Question_text== last_question:
                    print("No new question found. Retrying...")
                    time.sleep(2)
                last_question=Question_text
                #print(question)
                print(f"Question: {Question_text}")

                # Get the correct answer from ChatGPT
                correct_answer = ask_chatgpt(Question_text)
                print(f"ChatGPT Answer: {correct_answer}")
                time.sleep(2)
                # Wait for the iframe and switch to it
                iframe = wait(EC.presence_of_element_located((By.XPATH, '//*[@id="cke_1_contents"]/iframe')))
                driver.switch_to.frame(iframe)

                # Now send the answer to the textarea inside the iframe
                textarea = wait(EC.presence_of_element_located((By.TAG_NAME, 'body')))  # Replace 'body' with the actual tag(By.TAG_NAME, 'body')  # Usually, the editable area inside CKEditor is the <body>
                textarea.click()  # Click to focus on the textarea
                # Set the HTML content directly
                driver.execute_script("arguments[0].innerHTML = arguments[1];", textarea, correct_answer)

                # Don't forget to switch back to the default content if needed later
                driver.switch_to.default_content()
                time.sleep(8)
