# import json

# import urllib.parse
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from datetime import datetime
# import requests

# # -------------------- CONFIG --------------------
# urls_to_test = {
#     "Login Page": "https://www.lumoslearning.com/llp/login.php",
#     "Billing Page - Subscriptions View": "https://www.lumoslearning.com/llwp/schoolup/schoolup-billing.html?view=mysubscriptions&user=free",
#     "Parent Dashboard": "https://www.lumoslearning.com/llwp/schoolup-parent.html",
#     "Parent Progress Summary": "https://www.lumoslearning.com/llwp/schoolup/schoolup-parent-progress-summary.html",
#     "Parent Lesson Insights": "https://www.lumoslearning.com/llwp/schoolup/schoolup-parent-lesson-insights.html",
#     "Parent Student Insights": "https://www.lumoslearning.com/llwp/schoolup/schoolup-parent-student-insights.html",
#     "Grading Questions": "https://www.lumoslearning.com/llwp/schoolup/grading-questions.html",
#     "Passage Reading": "https://www.lumoslearning.com/llwp/schoolup/passage-reading.html",
#     "Vocabulary Practice": "https://www.lumoslearning.com/llwp/schoolup/vocabulary_practice.html",
#     "Ed Blogs": "https://www.lumoslearning.com/llwp/schoolup/ed-blogs.html",
#     "Mindmaps": "https://www.lumoslearning.com/llwp/schoolup/my-mindmaps.html",
#     "New Registration Page": "https://www.lumoslearning.com/llwp/schoolup/new-schoolup-registration.html",
#     "Student Progress": "https://www.lumoslearning.com/llwp/schoolup/student-progress.html",
#     "Student Study Plan": "https://www.lumoslearning.com/llwp/student-studyplan.html",
#     "Parent FAQ": "https://www.lumoslearning.com/llwp/stepup-parent-faq.html",
#     "Messages": "https://www.lumoslearning.com/llwp/lumos-messages.html",
#     "Parent My Students": "https://www.lumoslearning.com/llwp/schoolup/schoolup-parent-mystudents.html",
#     "Billing Page": "https://www.lumoslearning.com/llwp/schoolup/schoolup-billing.html",
#     "Worksheets Page": "https://www.lumoslearning.com/llwp/schoolup/schoolup-worksheets.html"
# }


# USERNAME = "ashmccomb@gmail.com"
# PASSWORD = "a"
# # ------------------------------------------------

# def collect_metrics(driver, page_url):
#     driver.get(page_url)
#     WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "body")))

#     nav_start = driver.execute_script("return window.performance.timing.navigationStart")
#     load_end = driver.execute_script("return window.performance.timing.loadEventEnd") or driver.execute_script("return Date.now()")
#     load_time = (load_end - nav_start) / 1000

#     logs = driver.get_log("performance")
#     events = [json.loads(log["message"])["message"] for log in logs if "message" in log]

#     slow_requests = []
#     for event in events:
#         if event["method"] == "Network.loadingFinished":
#             req_id = event["params"]["requestId"]
#             finish = event["params"]["timestamp"]
#             sent_event = next((e for e in events if e["method"] == "Network.requestWillBeSent" and e["params"]["requestId"] == req_id), None)
#             if sent_event:
#                 url = sent_event["params"]["request"]["url"]
#                 start = sent_event["params"]["timestamp"]
#                 duration = (finish - start) * 1000
#                 if sent_event["params"].get("type") in ["XHR", "Fetch"] and duration > 500:
#                     slow_requests.append((url, duration))

#     try:
#         fcp = driver.execute_script("""
#             const paints = performance.getEntriesByType('paint');
#             return paints.find(p => p.name === 'first-contentful-paint')?.startTime || null;
#         """)
#     except Exception:
#         fcp = None

#     try:
#         tti = driver.execute_script("""
#             const entries = performance.getEntriesByType('longtask');
#             if (entries.length === 0) return null;
#             let lastTask = entries[entries.length - 1];
#             return lastTask.startTime + lastTask.duration;
#         """)
#     except Exception:
#         tti = None

#     return {
#         "url": page_url,
#         "load_time": load_time,
#         "fcp": fcp,
#         "tti": tti,
#         "slow_requests": slow_requests
#     }

# # ---------- WebDriver Setup ----------
# options = Options()
# options.add_argument("--headless=new")
# options.add_argument("--window-size=1920,1080")
# options.add_argument("--disable-gpu")
# options.add_argument("--no-sandbox")
# options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
# options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

# driver = webdriver.Chrome(options=options)

# # ---------- LOGIN ----------
# driver.get(urls_to_test["Login Page"])
# WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "inputLogin")))
# driver.find_element(By.ID, "inputLogin").send_keys(USERNAME)
# driver.find_element(By.ID, "inputPassword").send_keys(PASSWORD)
# driver.find_element(By.ID, "loginSubmit").click()
# WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "body")))

# # Manually track login time
# nav_start = driver.execute_script("return window.performance.timing.navigationStart")
# load_end = driver.execute_script("return window.performance.timing.loadEventEnd") or driver.execute_script("return Date.now()")
# login_metrics = {
#     "url": urls_to_test["Login Page"],
#     "load_time": (load_end - nav_start) / 1000,
#     "fcp": None,
#     "tti": None,
#     "slow_requests": []
# }
# def create_ticket(metrics):
#     try:
#         payload = {
#                 "name": "Prajwal V",
#                 "email": "prajwal.lumos@gmail.com",
#                 "desc": f"Performance report for {metrics['url']} - Load Time: {metrics['load_time']:.2f} secands",
#                 "studentid": "Testing Team",
#                 "page": metrics['url'],
#                 "pageurl": metrics['url'],
#                 "courseid": "Performance testing",
#                 "lessonid": "Performance testing",
#                 "questionid": "Performance testing",
#                 "browser": "Server",
#                 "browserversion": "server",
#                 "sentryeventid": "Performance Testing"
#             }

#             # URL encode the parameters properly
#         query_string = urllib.parse.urlencode(payload)
#         print(f"Query String: {query_string}")  # Debugging line to check the query string
#         url = f"https://backup.lumoslearning.com/llp/report_an_error.php?{query_string}"
#         headers = {
#                 "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
#             }

#             # Make a GET request since the endpoint expects query parameters
#         response = requests.get(url, headers=headers)

#         if response.status_code in [200, 201]:
#             return "Ticket created."
#         else:
#             return f"Failed to create ticket. Status code: {response.status_code}"

#     except Exception as e:
#             return f"Error while raising ticket: {e}"

# # ---------- Collect Metrics for Remaining Pages ----------
# results = {"Login Page": login_metrics}
# for name, url in urls_to_test.items():
#     if name == "Login Page":
#         continue
#     print(f"⏳ Collecting metrics for: {name}")
#     results[name] = collect_metrics(driver, url)

#     # Automatically raise ticket if load time exceeds 4 seconds
#     metrics = collect_metrics(driver, url)
#     results[name] = metrics

#     # Automatically raise ticket if load time exceeds 4 seconds
#     if metrics["load_time"] > 4:
#         ticket_status = create_ticket(metrics)
#         print(f"🎫 Ticket for '{name}': {ticket_status}")

# driver.quit()

# # ---------- Generate HTML Report ----------
# timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
# filename = f"Parent_page_perf_report_{timestamp}.html"

# def make_table(metrics):
#     return ''.join(f"<tr><td>{url}</td><td>{duration:.0f}</td></tr>" for url, duration in metrics or []) or "<tr><td colspan='2'>None</td></tr>"

# def format_value(value):
#     return f"{value:.2f}" if isinstance(value, (int, float)) else "N/A"

# def block_html(title, data):
#     return f"""
#         <h2>{title}</h2>
#         <p><strong>URL:</strong> {data['url']}</p>
#         <p><strong>Page Load Time:</strong> {data['load_time']:.2f} sec</p>
#         <p><strong>FCP:</strong> {format_value(data.get('fcp'))} ms</p>
#         <p><strong>TTI:</strong> {format_value(data.get('tti'))} ms</p>
#         <table><tr><th>Slow XHR Request</th><th>Duration (ms)</th></tr>
#         {make_table(data['slow_requests'])}</table>
#     """

# with open(filename, "w", encoding="utf-8") as f:
#     f.write(f"""
#     <!DOCTYPE html>
#     <html>
#     <head>
#         <title>Lumos Performance Report</title>
#         <style>
#             body {{ font-family: Arial, sans-serif; padding: 20px; }}
#             table {{ border-collapse: collapse; width: 100%; margin: 10px 0; }}
#             th, td {{ border: 1px solid #ccc; padding: 8px; text-align: left; }}
#             th {{ background-color: #f4f4f4; }}
#             h2 {{ color: #2c3e50; }}
#         </style>
#     </head>
#     <body>
#         <h1>Parent Portal Performance Report</h1>
#         <p><strong>Test Run:</strong> {timestamp}</p>
#         {''.join(block_html(title, data) for title, data in results.items())}
#     </body>
#     </html>
#     """)

# print(f"\n✅ HTML performance report generated: {filename}")
import json
import urllib.parse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import requests

# -------------------- CONFIG --------------------
urls_to_test = {
    "Login Page": "https://www.lumoslearning.com/llp/login.php",
    "Billing Page - Subscriptions View": "https://www.lumoslearning.com/llwp/schoolup/schoolup-billing.html?view=mysubscriptions&user=free",
    "Parent Dashboard": "https://www.lumoslearning.com/llwp/schoolup-parent.html",
    "Parent Progress Summary": "https://www.lumoslearning.com/llwp/schoolup/schoolup-parent-progress-summary.html",
    "Parent Lesson Insights": "https://www.lumoslearning.com/llwp/schoolup/schoolup-parent-lesson-insights.html",
    "Parent Student Insights": "https://www.lumoslearning.com/llwp/schoolup/schoolup-parent-student-insights.html",
    "Grading Questions": "https://www.lumoslearning.com/llwp/schoolup/grading-questions.html",
    "Passage Reading": "https://www.lumoslearning.com/llwp/schoolup/passage-reading.html",
    "Vocabulary Practice": "https://www.lumoslearning.com/llwp/schoolup/vocabulary_practice.html",
    "Ed Blogs": "https://www.lumoslearning.com/llwp/schoolup/ed-blogs.html",
    "Mindmaps": "https://www.lumoslearning.com/llwp/schoolup/my-mindmaps.html",
    "New Registration Page": "https://www.lumoslearning.com/llwp/schoolup/new-schoolup-registration.html",
    "Student Progress": "https://www.lumoslearning.com/llwp/schoolup/student-progress.html",
    "Student Study Plan": "https://www.lumoslearning.com/llwp/student-studyplan.html",
    "Parent FAQ": "https://www.lumoslearning.com/llwp/stepup-parent-faq.html",
    "Messages": "https://www.lumoslearning.com/llwp/lumos-messages.html",
    "Parent My Students": "https://www.lumoslearning.com/llwp/schoolup/schoolup-parent-mystudents.html",
    "Billing Page": "https://www.lumoslearning.com/llwp/schoolup/schoolup-billing.html",
    "Worksheets Page": "https://www.lumoslearning.com/llwp/schoolup/schoolup-worksheets.html"
}

USERNAME = "ashmccomb@gmail.com"
PASSWORD = "a"
# ------------------------------------------------


def collect_metrics(driver, page_url):
    driver.get(page_url)
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "body"))
    )

    nav_start = driver.execute_script("return window.performance.timing.navigationStart")
    load_end = driver.execute_script("return window.performance.timing.loadEventEnd") or driver.execute_script("return Date.now()")
    load_time = (load_end - nav_start) / 1000

    logs = driver.get_log("performance")
    events = [json.loads(log["message"])["message"] for log in logs if "message" in log]

    slow_requests = []
    for event in events:
        if event["method"] == "Network.loadingFinished":
            req_id = event["params"]["requestId"]
            finish = event["params"]["timestamp"]
            sent_event = next(
                (e for e in events if e["method"] == "Network.requestWillBeSent"
                 and e["params"]["requestId"] == req_id),
                None
            )
            if sent_event:
                url = sent_event["params"]["request"]["url"]
                start = sent_event["params"]["timestamp"]
                duration = (finish - start) * 1000
                if sent_event["params"].get("type") in ["XHR", "Fetch"] and duration > 500:
                    slow_requests.append((url, duration))

    try:
        fcp = driver.execute_script("""
            const paints = performance.getEntriesByType('paint');
            return paints.find(p => p.name === 'first-contentful-paint')?.startTime || null;
        """)
    except Exception:
        fcp = None

    try:
        tti = driver.execute_script("""
            const entries = performance.getEntriesByType('longtask');
            if (entries.length === 0) return null;
            let lastTask = entries[entries.length - 1];
            return lastTask.startTime + lastTask.duration;
        """)
    except Exception:
        tti = None

    return {
        "url": page_url,
        "load_time": load_time,
        "fcp": fcp,
        "tti": tti,
        "slow_requests": slow_requests
    }


# ---------- WebDriver Setup ----------
options = Options()
options.add_argument("--headless=new")
options.add_argument("--window-size=1920,1080")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
)

driver = webdriver.Chrome(options=options)

# ---------- LOGIN ----------
driver.get(urls_to_test["Login Page"])
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "inputLogin"))
)
driver.find_element(By.ID, "inputLogin").send_keys(USERNAME)
driver.find_element(By.ID, "inputPassword").send_keys(PASSWORD)
driver.find_element(By.ID, "loginSubmit").click()

WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "body"))
)

nav_start = driver.execute_script("return window.performance.timing.navigationStart")
load_end = driver.execute_script("return window.performance.timing.loadEventEnd") or driver.execute_script("return Date.now()")

login_metrics = {
    "url": urls_to_test["Login Page"],
    "load_time": (load_end - nav_start) / 1000,
    "fcp": None,
    "tti": None,
    "slow_requests": []
}

# ---------- Collect Metrics ----------
results = {"Login Page": login_metrics}

for name, url in urls_to_test.items():
    if name == "Login Page":
        continue

    print(f"⏳ Collecting metrics for: {name}")
    metrics = collect_metrics(driver, url)
    results[name] = metrics

driver.quit()

# ---------- Generate HTML Report ----------
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
filename = f"Parent_page_perf_report_{timestamp}.html"


def make_table(metrics):
    return ''.join(
        f"<tr><td>{url}</td><td>{duration:.0f}</td></tr>"
        for url, duration in metrics or []
    ) or "<tr><td colspan='2'>None</td></tr>"


def format_value(value):
    return f"{value:.2f}" if isinstance(value, (int, float)) else "N/A"


def block_html(title, data):
    return f"""
        <h2>{title}</h2>
        <p><strong>URL:</strong> {data['url']}</p>
        <p><strong>Page Load Time:</strong> {data['load_time']:.2f} sec</p>
        <p><strong>FCP:</strong> {format_value(data.get('fcp'))} ms</p>
        <p><strong>TTI:</strong> {format_value(data.get('tti'))} ms</p>
        <table>
            <tr><th>Slow XHR Request</th><th>Duration (ms)</th></tr>
            {make_table(data['slow_requests'])}
        </table>
    """


with open(filename, "w", encoding="utf-8") as f:
    f.write(f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Lumos Performance Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; padding: 20px; }}
            table {{ border-collapse: collapse; width: 100%; margin: 10px 0; }}
            th, td {{ border: 1px solid #ccc; padding: 8px; text-align: left; }}
            th {{ background-color: #f4f4f4; }}
            h2 {{ color: #2c3e50; }}
        </style>
    </head>
    <body>
        <h1>Parent Portal Performance Report</h1>
        <p><strong>Test Run:</strong> {timestamp}</p>
        {''.join(block_html(title, data) for title, data in results.items())}
    </body>
    </html>
    """)

print(f"\n✅ HTML performance report generated: {filename}")


