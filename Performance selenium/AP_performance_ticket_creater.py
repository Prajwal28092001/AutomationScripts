import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import urllib.parse
import requests
from selenium.common.exceptions import TimeoutException

# -------------------- CONFIG --------------------
urls_to_test = {
    "Login Page": "https://www.lumoslearning.com/llp/login.php",
    "Dashboard": "https://www.lumoslearning.com/llwp/admin.html",
    "My Teachers": "https://www.lumoslearning.com/llwp/admin/my-teachers.html",
    "My Students": "https://www.lumoslearning.com/llwp/admin/my-students.html",
    "My Lessons": "https://www.lumoslearning.com/llwp/admin/my-program.html",
    "Assignment Page": "https://www.lumoslearning.com/llwp/schoolup/assignments.html?schoolid=332113&courseid=16012&lessonid=935146",
    "Preview Page": "https://www.lumoslearning.com/llwp/schoolup/lessons-preview.html?lessonid=935148&courseid=16012&customlesson=no",
    "Quotes": "https://www.lumoslearning.com/llwp/admin-quote.html?quoteList=Y",
    "Account Setup": "https://www.lumoslearning.com/llwp/admin-account-creation.html",
    "Live Reports": "https://www.lumoslearning.com/llwp/live-progress-summary.html",
    "Lesson Details": "https://www.lumoslearning.com/llwp/schoolup/lesson-analysis-report.html",
    "Grade Mastery": "https://www.lumoslearning.com/llwp/admin/proficiency-report.html",
    "Standards Proficiency": "https://www.lumoslearning.com/llwp/admin/standards-proficiency-report.html",
    "Benchmark Report": "https://www.lumoslearning.com/llwp/schoolup/benchmark-report.html",
    "Teacher Activity": "https://www.lumoslearning.com/llwp/admin/teacher-activity.html",
    "Domain Mastery": "http://lumoslearning.com/llwp/schoolup/domain-standards-mastery.html",
    "Lumos Knowledge Assistant": "https://www.lumoslearning.com/llwp/stepup-knowledge-assistant.html",
    "Video Search": "https://www.lumoslearning.com/llwp/schoolup/video-search.html?q",
    "Mindmaps Page": "https://www.lumoslearning.com/llwp/admin/my-mindmaps.html?1750758908",
    "Flashcubes Page": "https://www.lumoslearning.com/llwp/admin/my-flashcubes.html?1750758926",
    "Reading Passages": "https://www.lumoslearning.com/llwp/schoolup/passage-reading.html?grade%5B%5D=3:4&category%5B%5D=Lumos%20Passages",
    "Vocabulary Practice": "https://www.lumoslearning.com/llwp/schoolup/vocabulary_practice.html",
    "Ed Blogs": "https://www.lumoslearning.com/llwp/schoolup/ed-blogs.html",
    "Help / FAQ Page": "https://www.lumoslearning.com/llwp/admin-faq-lumos-learning.html",
    "Profile Page": "https://www.lumoslearning.com/llwp/schoolup/schoolup-registration.html?userid=55238032",
    "Custom Lesson Creation": "https://www.lumoslearning.com/llwp/schoolup/subscribed-content/custom-lessons.html?lessonid=3041071&cid=11470&editmode=Y"
}

USERNAME = "lumos_admin_alak"
PASSWORD = "Julia@2025"
# ------------------------------------------------

def collect_metrics(driver, page_url):
    try:
        driver.get(page_url)
    except TimeoutException:
        print(f"⚠️ Timeout loading: {page_url}")
        return {
            "url": page_url,
            "load_time": None,
            "fcp": None,
            "tti": None,
            "slow_requests": []
        }

    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "body")))

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
            sent_event = next((e for e in events if e["method"] == "Network.requestWillBeSent" and e["params"]["requestId"] == req_id), None)
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
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

driver = webdriver.Chrome(options=options)
driver.set_page_load_timeout(60)

# ---------- LOGIN ----------
driver.get(urls_to_test["Login Page"])
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "inputLogin")))
driver.find_element(By.ID, "inputLogin").send_keys(USERNAME)
driver.find_element(By.ID, "inputPassword").send_keys(PASSWORD)
driver.find_element(By.ID, "loginSubmit").click()
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "body")))

# ---------- LOGIN METRICS ----------
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
filename = f"Admin_page_perf_report_{timestamp}.html"

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
        <p><strong>Page Load Time:</strong> {format_value(data['load_time'])} sec</p>
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
        <h1>Admin Portal Performance Report</h1>
        <p><strong>Test Run:</strong> {timestamp}</p>
        {''.join(block_html(title, data) for title, data in results.items())}
    </body>
    </html>
    """)

print(f"\n✅ HTML performance report generated: {filename}")