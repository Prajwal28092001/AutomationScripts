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
    "Home Page": "https://www.lumoslearning.com/llwp/edsearch.html",
    "Math and grade 4 page - Free user View": "https://www.lumoslearning.com/llwp/edsearch.html?grade%5B%5D=4&subject%5B%5D=Math&submit=Search&portal=EdSearch&pagenum=1",
    "Video page": "https://www.lumoslearning.com/llwp/edsearch.html?grade%5B%5D=4&subject%5B%5D=Math&submit=Search&portal=EdSearch&grade%5B%5D=4&check%5B%5D=Video",
    "Coherence Map": "https://www.lumoslearning.com/llwp/edsearch.html?grade%5B%5D=4&subject%5B%5D=Math&submit=Search&portal=EdSearch&grade%5B%5D=4&check%5B%5D=CoherenceMap",
    "Books": "https://www.lumoslearning.com/llwp/edsearch.html?grade%5B%5D=4&subject%5B%5D=Math&submit=Search&portal=EdSearch&grade%5B%5D=4&check%5B%5D=Book",
    "Page": "https://www.lumoslearning.com/llwp/edsearch.html?grade%5B%5D=4&subject%5B%5D=Math&submit=Search&portal=EdSearch&grade%5B%5D=4&check%5B%5D=Page",
    "Mindmap": "https://www.lumoslearning.com/llwp/edsearch.html?grade%5B%5D=4&subject%5B%5D=Math&submit=Search&portal=EdSearch&grade%5B%5D=4&check%5B%5D=Mindmap",
    "Passage Reading": "https://www.lumoslearning.com/llwp/edsearch.html?grade%5B%5D=4&subject%5B%5D=Math&submit=Search&portal=EdSearch&grade%5B%5D=4&check%5B%5D=Flashcube",
    "Flash cube": "https://www.lumoslearning.com/llwp/schoolup/vocabulary_practice.html",
    "Coherence map standards": "https://www.lumoslearning.com/llwp/resources/coherence-map-standards-relation.html?q=4.MD.5",
    "educational videos": "https://www.lumoslearning.com/llwp/resources/educational-videos-k-12-elementary-middle-school.html?id=1900221",
    "book hub": "https://www.lumoslearning.com/llwp/resources/bookhub.html?bid=316736",
    "Pages": "https://www.education.com/lesson-plan/righteous-rounding-rounding-decimals/",
    "Flash cube creator": "https://www.lumoslearning.com/llwp/free-flashcube-creator.html?operation=check&mycube=view&rid=bDMza3BFa0pxK09KeTlRNEUvVVhvQT09",
    "Question": "https://www.lumoslearning.com/llwp/practice-tests-sample-questions-35844/grade-3-parcc-ela/alike-and-different/280878-question-1-RL.3.9.html",
    "assessment and online practice": "https://www.lumoslearning.com/llwp/practice-tests-sample-questions/1415/grade-3-parcc-ela.html?btn=start",
}
# ------------------------------------------------

def collect_metrics(driver, page_url):
    driver.get(page_url)
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "body"))
    )

    nav_start = driver.execute_script("return window.performance.timing.navigationStart")
    load_end = driver.execute_script(
        "return window.performance.timing.loadEventEnd"
    ) or driver.execute_script("return Date.now()")

    load_time = (load_end - nav_start) / 1000

    logs = driver.get_log("performance")
    events = [json.loads(log["message"])["message"] for log in logs]

    slow_requests = []
    for event in events:
        if event.get("method") == "Network.loadingFinished":
            req_id = event["params"]["requestId"]
            finish = event["params"]["timestamp"]

            sent_event = next(
                (
                    e for e in events
                    if e.get("method") == "Network.requestWillBeSent"
                    and e["params"]["requestId"] == req_id
                ),
                None
            )

            if sent_event:
                start = sent_event["params"]["timestamp"]
                url = sent_event["params"]["request"]["url"]
                duration = (finish - start) * 1000

                if sent_event["params"].get("type") in ["XHR", "Fetch"] and duration > 500:
                    slow_requests.append((url, duration))

    try:
        fcp = driver.execute_script("""
            const paints = performance.getEntriesByType('paint');
            return paints.find(p => p.name === 'first-contentful-paint')?.startTime || null;
        """)
    except:
        fcp = None

    try:
        tti = driver.execute_script("""
            const entries = performance.getEntriesByType('longtask');
            if (!entries.length) return null;
            const last = entries[entries.length - 1];
            return last.startTime + last.duration;
        """)
    except:
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
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
)

driver = webdriver.Chrome(options=options)

# ---------- Collect Metrics ----------
results = {}

def create_ticket(metrics):
    payload = {
        "name": "Prajwal V",
        "email": "prajwal.lumos@gmail.com",
        "desc": f"Performance report for {metrics['url']} - Load Time: {metrics['load_time']:.2f} seconds",
        "studentid": "Testing Team",
        "page": metrics["url"],
        "pageurl": metrics["url"],
        "courseid": "Performance testing",
        "lessonid": "Performance testing",
        "questionid": "Performance testing",
        "browser": "Server",
        "browserversion": "server",
        "sentryeventid": "Performance Testing"
    }

    query_string = urllib.parse.urlencode(payload)
    url = f"https://backup.lumoslearning.com/llp/report_an_error.php?{query_string}"
    response = requests.get(url)

    return "Ticket created." if response.status_code in [200, 201] else "Ticket failed."

for name, url in urls_to_test.items():
    print(f"⏳ Collecting metrics for: {name}")
    metrics = collect_metrics(driver, url)
    results[name] = metrics

    if metrics["load_time"] > 4:
        print(f"🎫 Ticket: {create_ticket(metrics)}")

driver.quit()

# ---------- Generate HTML Report ----------
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
filename = f"edsearch_page_perf_report_{timestamp}.html"

def make_table(metrics):
    return ''.join(
        f"<tr><td>{url}</td><td>{duration:.0f}</td></tr>"
        for url, duration in metrics
    ) or "<tr><td colspan='2'>None</td></tr>"

def block_html(title, data):
    return f"""
    <h2>{title}</h2>
    <p><strong>URL:</strong> {data['url']}</p>
    <p><strong>Load Time:</strong> {data['load_time']:.2f} sec</p>
    <p><strong>FCP:</strong> {data.get('fcp') or 'N/A'} ms</p>
    <p><strong>TTI:</strong> {data.get('tti') or 'N/A'} ms</p>
    <table>
        <tr><th>Slow XHR Request</th><th>Duration (ms)</th></tr>
        {make_table(data['slow_requests'])}
    </table>
    """

with open(filename, "w", encoding="utf-8") as f:
    f.write(f"""
    <html>
    <head>
        <title>Lumos Performance Report</title>
    </head>
    <body>
        <h1>EdSearch Performance Report</h1>
        <p>Test Run: {timestamp}</p>
        {''.join(block_html(title, data) for title, data in results.items())}
    </body>
    </html>
    """)

print(f"\n✅ HTML performance report generated: {filename}")
