
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time
import json
import sys
import os
from pathlib import Path
import datetime
import traceback
from datetime import datetime
import HtmlTestRunner
from urllib.parse import urlparse, parse_qs
from login import login
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from question_handler import QuestionTypeHandler
#from report import lesson_overview, progress, student_overview


# Capture state from command-line
custom_state = None
if len(sys.argv) > 1 and not sys.argv[1].startswith("-"):
    custom_state = sys.argv[1]
    sys.argv = sys.argv[:1]  # Prevent unittest from consuming it

class QuestionTypeHandlerTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Load user data from JSON file
        with open("Backup/Level1/state_user.json") as f:
            all_data = json.load(f)

        # Use the custom_state from the global scope
        global custom_state
        if custom_state:
            cls.state_user_data = [d for d in all_data if d['state'].lower() == custom_state.lower()]
            if not cls.state_user_data:
                raise ValueError(f"No data found for state: {custom_state}")
        else:
            cls.state_user_data = all_data
        
    def setUp(self):
        # self.driver = webdriver.Chrome()
        # self.driver.maximize_window()
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("--headless")  # Run Chrome in headless mode
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        self.driver = webdriver.Chrome(options=self.options)
        self.driver.set_window_size(1280, 1080)
    # reusable screenshot capture function
    def capture_screenshot(self, state, step_name="failure"):
        """Capture screenshot safely with timestamp and URL context."""
        try:
            os.makedirs("Backup/Level1/logs/screenshots", exist_ok=True)
            timestamp = datetime.now().strftime("%Y-%m-%d")
            file_name = f"{state}_{step_name}_{timestamp}.png"
            file_path = os.path.join("Backup/Level1/logs/screenshots", file_name)
            self.driver.save_screenshot(file_path)
            current_url = self.driver.current_url if self.driver else "URL not available"
            print(f" Screenshot captured: {file_path}")
            print(f" URL at failure: {current_url}")
            return file_path
        except Exception as e:
            print(f"️ Failed to capture screenshot: {e}")
            return None

    def test_answer_question_types(self):
        driver = self.driver
        for data in self.state_user_data:
            try:
                state = data['state']
                teacher = data['teacher']
                student = data['student']

                print(f"\n----- Testing for State: {state} -----")
                driver.get("https://backup.lumoslearning.com/llp/login.php")
                wait = WebDriverWait(driver, 10).until
                def teacher_login():
                    login_page_url = driver.current_url
                    # Login to Teacher Portal
                    login(driver, teacher['username'], teacher['password'])
                    assert login_page_url not in driver.current_url, "Login failed, Wrong Credentials"
                    #parent portal= gisewew285@flektel.com password= Lumos@123
                    time.sleep(3)
                    try:
                        select=wait(EC.presence_of_element_located((By.XPATH,"//a[contains(text(), 'Math')]")))
                        select.click()
                    except:
                        pass

                    # # check the report page
                    # lesson_overview(driver, '7', 'ELA','Untitled LessonvKuqRK8bFn','60','Brian Eric')
                    # time.sleep(2)

                    # progress(driver, '7', 'ELA', 'Brian Eric', 'Untitled LessonvKuqRK8bFn')
                    # time.sleep(2)

                    # student_overview(driver, '7', 'ELA','Brian Eric','Untitled LessonvKuqRK8bFn','60')
                    # time.sleep(2)
                    Mylessons = wait(EC.presence_of_element_located ((By.XPATH, "//a[contains(., 'My Lessons')]")))
                    Mylessons.click()
                    assert "subscribed-content.html" in driver.current_url, "Failed to redirection my lesson page"

                    # Assign the lesson //*[@id="lessonTable"]/tbody/tr[2]/td[2]
                    #cat 1 assigned
                    lesson = wait(EC.presence_of_element_located ((By.XPATH, '//*[@id="lessonTable"]/tbody/tr[2]/td[2]')))
                    lesson.click()
                    try:
                        click_student= wait(EC.presence_of_element_located ((By.XPATH,"//*[@class='btn-group bootstrap-select show-tick form-control dropup open']")))
                        click_student.click()
                    except:
                        pass
                    try:
                        assign = wait(EC.presence_of_element_located ((By.XPATH, "//*[@id='assignment-data']//button[contains(normalize-space(.), 'Assign')]")))
                        assign.click()
                        print("Lesson Assigned successfully - Checked.")
                    except:
                        print("Lesson assigned successfully - Not Checked.")

                    assignment_page_URL=driver.current_url
                    print(assignment_page_URL)
                    time.sleep(2)

                    parsed_url = urlparse(assignment_page_URL)

                    # Extract query parameters
                    params = parse_qs(parsed_url.query)

                    # Get lessonid and courseid
                    lessonid = params.get("lessonid", [""])[0]
                    courseid = params.get("courseid", [""])[0]
                    lesson_id=int(lessonid)
                    course_id=int(courseid)

                    print("lessonid:", lessonid)
                    print("courseid:", courseid)
                    
                    time.sleep(5)
                    try:
                        assignment=wait(EC.presence_of_element_located((By.XPATH, '//*[@id="assignments"]/tbody/tr[1]')))
                        driver.execute_script("arguments[0].scrollIntoView();", assignment)
                        # Locate the table row

                        # Extract text from all <td> elements
                        td_elements = assignment.find_elements(By.TAG_NAME, "td")
                        stored_data = {
                        "Lesson": td_elements[2].text.strip(),
                        #"Grade": td_elements[4].text.strip(),
                        #"Subject": td_elements[4].text.strip(),
                        "Teacher": td_elements[3].text.strip(),
                        "Date": td_elements[4].text.strip(),}
                        
                        '''subject=stored_data["Subject"]
                        grade=stored_data["Grade"]'''
                        
                        stored_data['Lesson']=stored_data['Lesson'].replace('\nEdit', '')
                        teacher_name=stored_data["Teacher"]
                        lesson_name=stored_data["Lesson"]
                        dates=stored_data["Date"]
                        
                        print("Teacher details from teacher dashboard",stored_data)
                        print("Lesson assigned successfully appearing in the teacher portal dashboard")
                    except Exception as e:
                        print("No assignments found or unable to locate the assignment element.")
                        raise e


                    """Extracts correct answers from the Teacher Portal preview page"""
                    driver.get(f"https://backup.lumoslearning.com/llwp/schoolup/lessons-preview.html?lessonid={lesson_id}&courseid={course_id}&customlesson=no")  # Replace with actual preview URL
                    time.sleep(2)
                    assert "lessons-preview.html" in driver.current_url, "Failed to redirection lesson preview page"

                    # Store all questions in a list
                    # Find all question containers
                    time.sleep(2)
                    question_containers = driver.find_elements(By.CLASS_NAME, "fullQuestion")
                    time.sleep(2)

                    # Get total number of questions
                    total_questions = len(question_containers)
                    print(f"Total Questions Found: {total_questions}")

                    # Store all questions dynamically
                    question_list = []

                    # Loop through all available questions, starting from 1
                    for index, question_container in enumerate(question_containers, start=1):  
                        # Extract Question Text
                        question_text = question_container.find_element(By.CLASS_NAME, "test_question").text.strip()

                        # Extract Correct Answer
                        try:
                            options = question_container.find_elements(By.CSS_SELECTOR, "div[style='margin: 0 0 20px;']")
                        except:
                            options = question_container.find_elements(By.CSS_SELECTOR,"span[style='margin-right: 5px;']")
                        correct_answer = None

                        for option in options:
                            if "text-success1" in option.get_property("innerHTML"):  # Detect correct answer
                                parts = option.text.split(".", 1)
                                if len(parts) > 1:
                                    correct_answer = parts[1].replace("(Correct Answer)", "").strip()
                                break   
                        question_list.append({
                            "question_num": index,  # Uses normal count dynamically
                            "question": question_text,
                            "correct_answer": correct_answer
                        })

                    if len(question_list) == 0:
                        print("No questions found in the lesson preview.")
                        return []
                    
                    # Print total question count and extracted data
                    print(f"\nExtracted {total_questions} Questions:")
                    # Print extracted data
                    #print(question_list)
                    #print("Teacher name:",teacher_name)
                    logout=wait(EC.presence_of_element_located((By.XPATH,'//*[@id="wrapper"]/nav/div[1]/ul[1]/li[6]/a')))
                    logout.click()
                    assert "schoolup-logout" in driver.current_url or "lumoslearning.com/llp/login.php" in driver.current_url, "Failed to logout from teacher portal"
                    return question_list
                # End of teacher login function

            
                #teacher_login()
                question_list=teacher_login()
                print(question_list)

                # Login to Student Portal
                driver.get("https://backup.lumoslearning.com/llp/login.php")
                login_page_url = driver.current_url
                login(driver, student['username'], student['password'])
                assert login_page_url not in driver.current_url, "Login failed, Wrong Credentials"
                print("Student logged in successfully")
                #login(driver,'sbac_std','a')
                time.sleep(3)
                result_text=None

                try:   
                    wait(EC.element_to_be_clickable((By.XPATH, "(//*[@class='notifications-link'])[1]"))).click()
                    try:
                        wait(EC.element_to_be_clickable((By.XPATH, "(//*[@class='btn btn-labeled btn-success customBtnLabel btn-xs'])[1]"))).click()
                    except:
                        wait(EC.element_to_be_clickable((By.XPATH,"(//*[@class='btn btn-labeled btn-danger customBtnLabel btn-xs'])[1]"))).click()

                    # Start answering questions
                    question_number = 1
                    handler = QuestionTypeHandler(driver, question_list)
                    while True:
                        print(f"Handling question {question_number}")
                        #check if the user is on the assessment page or not
                        assert "llp/start_test.php" in driver.current_url, "Failed to redirect to the assessment page or student terminated the test"
                        # Answer the current question
                        handler.answer_question()
                        is_correct3 = handler.is_element_present((By.XPATH, "//*[@id='nexturl']"))
                        if is_correct3:
                            next_button = wait(EC.element_to_be_clickable((By.XPATH, "//*[@id='nexturl']")))
                            driver.execute_script("arguments[0].click();", next_button)
                            if handler.is_element_present((By.XPATH, "//*[@id='skipQuestionCofirm']")):
                                skip_button = wait(EC.presence_of_element_located((By.XPATH, "//*[@id='skipQuestionCofirm']")))
                                driver.execute_script("arguments[0].click();", skip_button)
                                print(f"Handled 'Skip Question Confirmation' popup for question {question_number}.")
                            try:
                                next_question=wait(EC.presence_of_element_located((By.XPATH,"//*[@id='nextQuestionCofirm']")))
                                next_question.click()
                            except:
                                pass
                            time.sleep(2)
                            question_number += 1
                        last_question=len(question_list)-1
                        #print(compre)
                        if driver.current_url == f"https://backup.lumoslearning.com/llp/start_test.php?qnum={last_question}":
                            break
                    
                    #result button
                    if driver.current_url == f"https://backup.lumoslearning.com/llp/start_test.php?qnum={last_question}":
                        # Click the "Finish" button
                        result_button_selectors = [
                            {"type": "xpath", "value": "//*[@class='nav-buttons reviewUnanswered']"},  # sbac
                            {"type": "xpath", "value": "//*[text()='Result']"},  # acap
                            {"type": "xpath", "value": "//*[text()='Result ']"},  # momap
                            {"type": "xpath", "value": "//*[@class='btn btn-primary reviewUnanswered']"},  # njsla
                            {"type": "css", "value": ".btn-danger.reviewUnanswered"},  # Alternative
                        ]
                        for selector in result_button_selectors:
                            try:
                                if selector["type"] == "xpath":
                                    button = wait(EC.element_to_be_clickable((By.XPATH, selector["value"])))
                                elif selector["type"] == "css":
                                    button = wait(EC.element_to_be_clickable((By.CSS_SELECTOR, selector["value"])))
                                
                                # Try clicking with JavaScript if normal click fails
                                try:
                                    button.click()
                                except:
                                    driver.execute_script("arguments[0].click();", button)
                                #print(f"Clicked using {selector['type']}: {selector['value']}")
                                break
                            except (NoSuchElementException, TimeoutException):
                                continue
                        else:
                            print("Error: No matching 'Result' button found.")

             # Check if the result page is loaded                
                    try:
                        results=['//*[@id="endTestConfirm"]','//*[@id="ResultValue"]']
                        for result in results:
                            result_button2=wait(EC.element_to_be_clickable((By.XPATH,result)))
                            if result_button2.is_displayed():
                                driver.execute_script("arguments[0].click();", result_button2)
                                break
                    except:
                        pass
                    time.sleep(30)
                    # Check if the result page is loaded
                    if "https://backup.lumoslearning.com/llp/selfstudy_guided_practice.php" in driver.current_url:
                        time.sleep(10)
                        assert "llp/selfstudy_guided_practice.php" in driver.current_url, "Failed to redirect to the independent practice page"
                        result_btn=wait(EC.element_to_be_clickable((By.XPATH,'//*[@id="step-2"]/div[2]/div/div[2]')))
                        result_btn.click()
                        time.sleep(5)
                    if "llp/validateans" in driver.current_url or "llp/fullreport" in driver.current_url:
                        time.sleep(10)
                        assert "llp/fullreport" in driver.current_url, "Failed to redirect to the full report page"
                        result=wait(EC.presence_of_element_located((By.XPATH,"//div[contains(@class,'totalScoreBlock')]/div[3]/h5[2]")))
                        result_text=result.text
                        #print(f"Student portal result: {result_text}")
                        print("Test completed successfully: Student Scored: ", result_text)
                except Exception as e:
                    #print(e)
                    raise e
                time.sleep(2)
                logout_btn_student=wait(EC.element_to_be_clickable((By.XPATH,'(//*[@class="profile-coins"])[1]')))
                logout_btn_student.click()
                logout_student=wait(EC.presence_of_element_located((By.XPATH,'(//ul[@class="dropdown-menu"]/li[last()])[2]/a')))
                driver.execute_script("arguments[0].scrollIntoView();", logout_student)
                driver.execute_script("arguments[0].click();", logout_student)
                assert "llp/logout.php" in driver.current_url or "lumoslearning.com/llp/login.php" in driver.current_url, "Failed to logout from student portal"
                print(result_text)
                try:
                    round_str = str(round(float(result_text.split("%")[0])))
                    print(round_str)
                except:
                    pass
            except Exception as e:
                self.capture_screenshot(state, "unexpected_error")
                traceback.print_exc()
                print(f"Test failed for {state} with error: {e}")
    def tearDown(self):
        self.driver.quit()

if __name__ == "__main__":
    unittest.main()
    #unittest.main(testRunner=HtmlTestRunner.HTMLTestRunner(output='Reports', report_name="Main_Test_Report"))
