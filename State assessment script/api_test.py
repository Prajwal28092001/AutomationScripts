import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import openai
import time
from login import login  # Assuming login() function handles authentication

# Initialize ChatGPT API



def ask_chatgpt(question_text):
    """Fetch the correct answer from ChatGPT for the given text-based question."""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
          {"role": "system", "content": "You are an expert in answering text-based questions accurately and concisely."},
{"role": "user", "content": f"""
Read the question carefully and decide the most suitable answer format.  
- If the question can be answered in one word (e.g., MCQ, True/False, or short fact), then provide only that one word.  
- If a one-word answer is not possible, provide a clear descriptive answer in 2–3 sentences.  

Question: {question_text}
"""}
        ],
        temperature=0.5
    )
    return response["choices"][0]["message"]["content"].strip()

# class QuestionTypeHandlerTest(unittest.TestCase):
#     def setUp(self):
#         self.driver = webdriver.Chrome()
#         self.driver.get("https://backup.lumoslearning.com/llp/login.php")
#         self.driver.implicitly_wait(10)
#         self.driver.maximize_window()

#     def tearDown(self):
#         self.driver.quit()

#     def test_case(self):
#         driver = self.driver
#         wait = WebDriverWait(driver, 10).until

#         # Perform login
#         login(driver, 'mindmap_flash', 'a')

#         # Click on notifications
#         wait(EC.element_to_be_clickable((By.XPATH, "(//*[@class='notifications-link'])[1]"))).click()

#         # Handle green or red button (Start/Continue Test)
#         try:
#             wait(EC.element_to_be_clickable((By.XPATH, "(//*[@class='btn btn-labeled btn-success customBtnLabel btn-xs'])[1]"))).click()
#         except:
#             wait(EC.element_to_be_clickable((By.XPATH, "(//*[@class='btn btn-labeled btn-danger customBtnLabel btn-xs'])[1]"))).click()

#         time.sleep(2)
#         last_question = ""

#         while True:
#             question_element = wait(EC.presence_of_element_located((By.CSS_SELECTOR, ".test_question")))
#             if question_element:
#                 # Extract all text and replace new lines with spaces
#                 question_text = question_element.text.replace("\n", " ").strip()

#                 if question_text== last_question:
#                     print("No new question found. Retrying...")
#                     time.sleep(2)
#                     continue
#                 last_question=question_text
#                 #print(question)
#                 print(f"Question: {question_text}")

#                 # Get the correct answer from ChatGPT
#                 correct_answer = ask_chatgpt(question_text)
#                 print(f"ChatGPT Answer: {correct_answer}")
#                 iframe = driver.find_element(By.XPATH, '//*[@id="cke_1_contents"]/iframe')
#                 driver.switch_to.frame(iframe)

#                 # Now send the answer to the textarea inside the iframe
#                 textarea = driver.find_element(By.TAG_NAME, 'body')  # Usually, the editable area inside CKEditor is the <body>
#                 textarea.send_keys(correct_answer)

#                 # Don't forget to switch back to the default content if needed later
#                 driver.switch_to.default_content()
#                 time.sleep(8)
#                 #next question
#                 next_question = driver.find_element(By.XPATH,"//*[@id='nexturl']")
#                 next_question.click()   
#                 # Submit the answer
#                 print("Answer submitted successfully!")
#             # Check for result button
#             else:
#                 result_button_xpaths = [
#                                         "//*[@class='nav-buttons reviewUnanswered']", #sbac
#                                         "//*[text()='Result']", #acap
#                                         "//*[text()='Result ']", #momap
#                                         "//*[@class='btn btn-primary reviewUnanswered']", #njsla
#                                         "//*[@class='nav-buttons reviewUnanswered']", #nyst 
#                                         "//*[text()='Result']", #gmas
#                                         "//*[@class='glyphicon glyphicon-stop']", #ost
#                                         "//*[@class='btn btn-lg btn-danger pull-right reviewUnanswered']" ]
#                 for xpath in result_button_xpaths:
#                     try:
#                         result_button = driver.find_element(By.XPATH, xpath)
#                         result_button.click()
#                         break
#                     except:
#                         pass

# if __name__ == "__main__":
#     unittest.main()
