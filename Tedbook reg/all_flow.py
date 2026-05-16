import os
import sys
import csv
import json
import time
import logging
import pytest
import random
import string
from selenium import webdriver

from Pages.logout import logout as logout_fn
from Test_cases import New_user
from Test_cases import Add_student
from Test_cases import Existing_student

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_global_config():
    with open(os.path.join(BASE_DIR, "config.json"), encoding="utf-8") as f:
        return json.load(f)

def load_states_config():
    path = os.path.join(BASE_DIR, "data", "states.json")
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def load_codes_for_state(state_name):
    path = os.path.join(BASE_DIR, "data", "book_codes.csv")
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not any(row.values()):
                continue
            if row["state_name"].strip().upper() == state_name.strip().upper():
                rows.append(row)

    if len(rows) < 3:
        raise ValueError(
            f"State '{state_name}' has only {len(rows)} code(s) in book_codes.csv. "
            "Need at least 3 unique codes (one per step)."
        )
    # Return first 3 unique codes
    seen = []
    unique = []
    for r in rows:
        if r["code"] not in seen:
            seen.append(r["code"])
            unique.append(r)
        if len(unique) == 3:
            break
    return unique  

def save_json(filename, data):
    """Overwrite a JSON file in data/."""
    with open(os.path.join(BASE_DIR, "data", filename), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def append_run_log(row_dict):
    """Append one row to data/run_log.csv (creates the file if needed)."""
    log_path = os.path.join(BASE_DIR, "data", "run_log.csv")
    fieldnames = [
        "state", "grade", "subject",
        "code_step1", "code_step2", "code_step3",
        "email", "pin", "status", "timestamp"
    ]
    file_exists = os.path.exists(log_path)
    with open(log_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row_dict)

def take_screenshot(driver, name):
    screenshots_dir = os.path.join(BASE_DIR, "screenshots")
    if not os.path.exists(screenshots_dir):
        os.makedirs(screenshots_dir)
    driver.save_screenshot(os.path.join(screenshots_dir, f"{name}.png"))


# ---------------------------------------------------------------------------
# Driver Fixture
# ---------------------------------------------------------------------------

def get_chrome_options():
    """Return Chrome options configured for headless cron execution."""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    # Anti-detection: prevent site from blocking headless Chrome
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    )
    return options

@pytest.fixture(scope="function")
def driver():
    drv = webdriver.Chrome(options=get_chrome_options())
    drv.maximize_window()
    drv.implicitly_wait(10)
    yield drv
    try:
        drv.quit()
    except Exception:
        pass  # driver was already quit mid-test (after new user registration)


# ---------------------------------------------------------------------------
# Master Test - one iteration per state
# ---------------------------------------------------------------------------

GLOBAL_URL = load_global_config()["url"]

@pytest.mark.parametrize(
    "state_data",
    load_states_config(),
    ids=lambda x: x["state_name"]
)
def test_state_workflow(driver, request, state_data):
    """
    Full 3-step workflow per state:
      Step 1 - New User Registration   (code_step1)
      Step 2 - Add Student             (code_step2)
      Step 3 - Existing Student        (code_step3)
    """
    from utils.guerrilla_mail import GuerrillaMailClient

    state_name = state_data["state_name"]
    url        = GLOBAL_URL

    print(f"\n{'='*55}")
    print(f"  STARTING WORKFLOW FOR STATE: {state_name}")
    print(f"{'='*55}")

    # ---- Load 3 distinct book codes from CSV --------------------------------
    try:
        codes = load_codes_for_state(state_name)
    except ValueError as e:
        pytest.fail(str(e))

    step1_row = codes[0]
    step2_row = codes[1]
    step3_row = codes[2]

    print(f"  Codes -> Step1: {step1_row['code']} | Step2: {step2_row['code']} | Step3: {step3_row['code']}")
    print(f"  Grade: {step1_row['grade']}  |  Subject: {step1_row['subject']}")

    # ---- Step 0: Generate temp email ----------------------------------------
    mail_client   = GuerrillaMailClient()
    email_address = mail_client.get_email_address()

    first_name = "Test" + ''.join(random.choices(string.ascii_lowercase, k=4)).capitalize()
    last_name  = "User" + ''.join(random.choices(string.ascii_lowercase, k=4)).capitalize()

    # =========================================================================
    # STEP 1 — NEW USER REGISTRATION
    # =========================================================================
    print(f"\n--- [1] New User Registration -> code: {step1_row['code']} | email: {email_address} ---")
    page_new = New_user.LoginPage(driver)
    page_new.open(url)
    page_new.click_here()
    page_new.enter_book_code(step1_row["code"])
    page_new.submit_book_code()
    page_new.pause_and_exit()
    page_new.fill_parent_details(email_address, first_name, last_name)
    page_new.submit_form()
    time.sleep(5)
    take_screenshot(driver, f"{state_name}_1_new_user_success")
    print("--- [1] Completed New User Registration ---")

    # Close the browser completely and reopen a fresh window
    print("  -> Closing browser after New User Registration...")
    driver.quit()
    time.sleep(2)
    print("  -> Reopening fresh browser window (headless)...")
    driver = webdriver.Chrome(options=get_chrome_options())
    driver.maximize_window()
    driver.implicitly_wait(10)
    time.sleep(2)
    print("  -> Fresh browser ready. Continuing with Add Student flow...")

    # ---- Fetch PIN from inbox ------------------------------------------------
    try:
        pin = mail_client.wait_for_pin_email(timeout_seconds=90)
    except Exception as e:
        pytest.fail(f"Could not retrieve PIN for state {state_name}. Error: {e}")

    print(f"  PIN received: {pin}")

    # ---- Attach email/pin to test node (for conftest PDF) --------------------
    request.node.user_properties.append(("state_name",  state_name))
    request.node.user_properties.append(("used_email",  email_address))
    request.node.user_properties.append(("used_pin",    pin))
    request.node.user_properties.append(("grade",       step1_row["grade"]))
    request.node.user_properties.append(("subject",     step1_row["subject"]))
    request.node.user_properties.append(("code_step1",  step1_row["code"]))
    request.node.user_properties.append(("code_step2",  step2_row["code"]))
    request.node.user_properties.append(("code_step3",  step3_row["code"]))

    # ---- Persist credentials to all JSON data files -------------------------
    new_user_payload = {
        "url":       url,
        "book_code": step1_row["code"],
        "email":     email_address,
        "pin":       pin
    }
    add_payload = {**new_user_payload, "book_code": step2_row["code"]}
    ext_payload = {**new_user_payload, "book_code": step3_row["code"]}

    save_json("new_user_data.json",      new_user_payload)
    save_json("add_student.json",        add_payload)
    save_json("existing_student.json",   ext_payload)
    print("  -> Saved credentials to new_user_data.json, add_student.json, existing_student.json")

    # =========================================================================
    # STEP 2 — ADD STUDENT
    # =========================================================================
    print(f"\n--- [2] Add Student -> code: {step2_row['code']} | PIN: {pin} ---")
    page_add = Add_student.LoginPage(driver)
    page_add.open(url)
    page_add.click_here()
    page_add.enter_book_code(step2_row["code"])
    page_add.submit_book_code()
    page_add.pause_and_exit()
    time.sleep(2)
    # page_add.refresh()
    time.sleep(2)
    page_add.fill_parent_email_pin(email_address, pin)
    time.sleep(1)
    page_add.submit_form()
    take_screenshot(driver, f"{state_name}_2_add_student_success")
    logout_fn(driver)
    time.sleep(3)
    print("--- [2] Completed Add Student Flow ---")

    # =========================================================================
    # STEP 3 — EXISTING STUDENT
    # =========================================================================
    print(f"\n--- [3] Existing Student -> code: {step3_row['code']} ---")
    page_ext = Existing_student.LoginPage(driver)
    page_ext.open(url)
    page_ext.click_here()
    page_ext.enter_book_code(step3_row["code"])
    page_ext.submit_book_code()
    page_ext.pause_and_exit()
    time.sleep(2)
    # page_ext.refresh()
    time.sleep(2)
    page_ext.fill_parent_details(email_address, pin)
    time.sleep(1)
    page_ext.select_student(0)
    time.sleep(2)
    page_ext.submit_form()
    time.sleep(3)
    take_screenshot(driver, f"{state_name}_3_existing_student_success")
    logout_fn(driver)

    print("--- [3] Completed Existing Student Flow ---")

    # Clean up the new browser instance (created after Step 1)
    driver.quit()


# ---------------------------------------------------------------------------
# Cron-Job / Standalone Entry Point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # """
    # Run as:  python all_flow.py
    # Cron:    0 6 * * * cd /path/to/Tedbook\ reg && python all_flow.py >> data/cron_run.log 2>&1
    # Windows Task Scheduler:
    #     Program: python
    #     Arguments: all_flow.py
    #     Start in: C:\Users\Cyber Monkey\Desktop\Tedbook reg
    # """
    
    # Force UTF-8 output encoding (prevents cp1252 crashes on Windows)
    os.environ["PYTHONIOENCODING"] = "utf-8"

    # ---- Setup logging (file + console) ------------------------------------
    log_dir = os.path.join(BASE_DIR, "data")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "cron_run.log")

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )
    logger = logging.getLogger("all_flow")

    # ---- Run ---------------------------------------------------------------
    start_ts = time.strftime("%Y-%m-%d %H:%M:%S")
    start_time = time.time()
    logger.info("=" * 60)
    logger.info("CRON RUN STARTED at %s", start_ts)
    logger.info("=" * 60)

    try:
        # Invoke pytest programmatically on this file.
        # -v : verbose output
        # -s : disable stdout capture (so print() works)
        # --tb=short : shorter tracebacks for log readability
        exit_code = pytest.main([
            __file__,
            "-v",
            "-s",
            "--tb=short",
        ])
    except Exception:
        logger.exception("Unexpected error during pytest execution")
        exit_code = 1

    # ---- Wrap up -----------------------------------------------------------
    elapsed = time.time() - start_time
    h, rem = divmod(elapsed, 3600)
    m, s = divmod(rem, 60)
    duration = f"{int(h):02d}:{int(m):02d}:{int(s):02d}"

    end_ts = time.strftime("%Y-%m-%d %H:%M:%S")
    status = "SUCCESS" if exit_code == 0 else f"FAILED (exit code {exit_code})"
    logger.info("-" * 60)
    logger.info("CRON RUN FINISHED at %s  |  Duration: %s  |  %s", end_ts, duration, status)
    logger.info("-" * 60)

    sys.exit(exit_code)
