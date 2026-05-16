# import json
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from datetime import datetime
# import urllib.parse
# import requests
# import time

# # -------------------- CONFIG --------------------

# urls_to_test = {
#     "Login Page": "https://www.lumoslearning.com/llp/login.php",
#     "Dashboard": "https://www.lumoslearning.com/llwp/librarian.html",
#     "Subscribe Program": "https://www.lumoslearning.com/llwp/librarian/my-programs.html",
#     "Trynow Page": "https://www.lumoslearning.com/llp/reports_main.php?CourseID=15775",
#     "Usagae by Programs": "https://www.lumoslearning.com/llwp/librarian/program-report.html",
#     "Popular By lessons": "https://www.lumoslearning.com/llwp/librarian/lesson-by-session.html",
#     "Lessons by Grade": "https://www.lumoslearning.com/llwp/librarian/lesson-insights.html",
#     "Media Kit": "https://www.lumoslearning.com/llwp/librarian/media-kit.html",
#     "Lib FAQ Page": "https://www.lumoslearning.com/llwp/stepup-parent-faq.html?type=librarian",
#     "Lib Profile Page": "https://www.lumoslearning.com/llwp/schoolup/schoolup-registration.html?userid=50969874",
# }

# USERNAME = "demo_library_njsla"
# PASSWORD = "17932486"

# # ------------------------------------------------

# skip_ticket_pages = {
#     "Trynow Page",
#     "Media Kit",
#     "Lib FAQ Page",
#     "Lib Profile Page"
# }

# created_tickets = set()

# # ------------------------------------------------

# def collect_metrics(driver, page_url):

#     # Clear previous logs
#     driver.get_log("performance")

#     driver.get(page_url)

#     WebDriverWait(driver, 15).until(
#         EC.presence_of_element_located((By.CSS_SELECTOR, "body"))
#     )
#     time.sleep(2)

#     # Stable load time calculation
#     load_time = driver.execute_script("""
#         var timing = window.performance.timing;
#         return (timing.loadEventEnd - timing.navigationStart) / 1000;
#     """)

#     if load_time <= 0:
#         load_time = driver.execute_script("return performance.now()/1000")

#     logs = driver.get_log("performance")

#     events = [json.loads(log["message"])["message"] for log in logs if "message" in log]

#     slow_requests = []

#     for event in events:

#         if event["method"] == "Network.loadingFinished":

#             req_id = event["params"]["requestId"]
#             finish = event["params"]["timestamp"]

#             sent_event = next(
#                 (e for e in events if e["method"] == "Network.requestWillBeSent"
#                  and e["params"]["requestId"] == req_id),
#                 None
#             )

#             if sent_event:

#                 url = sent_event["params"]["request"]["url"]
#                 start = sent_event["params"]["timestamp"]

#                 duration = (finish - start) * 1000

#                 resource_type = sent_event["params"].get("type", "")

#                 if duration > 500 and (
#                     resource_type in ["XHR", "Fetch"] or
#                     ".php" in url or
#                     ".json" in url or
#                     "ajax" in url
#                 ):
#                     slow_requests.append((url, duration))

#     try:
#         fcp = driver.execute_script("""
#             const paints = performance.getEntriesByType('paint');
#             return paints.find(p => p.name === 'first-contentful-paint')?.startTime || null;
#         """)
#     except:
#         fcp = None

#     try:
#         tti = driver.execute_script("""
#             const entries = performance.getEntriesByType('longtask');
#             if (entries.length === 0) return null;
#             let lastTask = entries[entries.length - 1];
#             return lastTask.startTime + lastTask.duration;
#         """)
#     except:
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

# options.add_argument(
# "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
# "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
# )

# driver = webdriver.Chrome(options=options)
# driver.execute_cdp_cmd("Network.enable", {})


# # ---------- LOGIN (UNCHANGED) ----------

# driver.get(urls_to_test["Login Page"])

# WebDriverWait(driver, 10).until(
# EC.presence_of_element_located((By.ID, "inputLogin"))
# )

# driver.find_element(By.ID, "inputLogin").send_keys(USERNAME)
# driver.find_element(By.ID, "inputPassword").send_keys(PASSWORD)
# driver.find_element(By.ID, "loginSubmit").click()

# WebDriverWait(driver, 10).until(
# EC.presence_of_element_located((By.CSS_SELECTOR, "body"))
# )


# # ---------- Login Metrics ----------

# nav_start = driver.execute_script(
# "return window.performance.timing.navigationStart"
# )

# load_end = driver.execute_script(
# "return window.performance.timing.loadEventEnd"
# ) or driver.execute_script("return Date.now()")

# login_metrics = {
# "url": urls_to_test["Login Page"],
# "load_time": (load_end - nav_start) / 1000,
# "fcp": None,
# "tti": None,
# "slow_requests": []
# }


# # ---------- Ticket Function ----------

# def create_ticket(metrics):

#     try:

#         payload = {
#             "name": "Skandesh P B",
#             "email": "Skandesh.lumos@gmail.com",
#             "desc": f"Performance report for {metrics['url']} - Load Time: {metrics['load_time']:.2f} seconds",
#             "studentid": "Testing Team",
#             "page": metrics['url'],
#             "pageurl": metrics['url'],
#             "courseid": "Performance testing",
#             "lessonid": "Performance testing",
#             "questionid": "Performance testing",
#             "browser": "Server",
#             "browserversion": "server",
#             "sentryeventid": "Performance Testing"
#         }

#         query_string = urllib.parse.urlencode(payload)

#         url = f"https://dev.lumoslearning.com/llp/report_an_error.php?{query_string}"

#         headers = {
#             "User-Agent": "Mozilla/5.0"
#         }

#         response = requests.get(url, headers=headers)

#         if response.status_code in [200, 201]:

#             data = response.json()

#             ticket_no = data.get("error", {}).get("ticketno")

#             if ticket_no:
#                 return {
#                     "status": "Ticket created",
#                     "ticket_no": ticket_no
#                 }
#             else:
#                 return {
#                     "status": "Ticket created but ticket number missing",
#                     "ticket_no": None
#                 }

#         else:
#             return {
#                 "status": f"Failed: {response.status_code}",
#                 "ticket_no": None
#             }

#     except Exception as e:

#         return {
#             "status": f"Error: {e}",
#             "ticket_no": None
#         }


# # ---------- Run Metrics ----------

# results = {"Login Page": login_metrics}

# for name, url in urls_to_test.items():

#     if name == "Login Page":
#         continue

#     print(f"\n⏳ Testing: {name}")

#     metrics = collect_metrics(driver, url)
#     metrics["ticket_no"] = None

#     print(f"Load Time: {metrics['load_time']:.2f} sec")

#     metrics["ticket_status"] = "No Ticket"

#     if metrics["load_time"] > 3:

#         if name in skip_ticket_pages:

#             metrics["ticket_status"] = "Ticket already exist"
#             print(f"⚠️ {name} → Ticket already exist")

#         elif name in created_tickets:

#             metrics["ticket_status"] = "Duplicate prevented"
#             print(f"⚠️ {name} → Duplicate prevented")

#         else:

#             ticket_status = create_ticket(metrics)

#             print(f"🎫 Ticket for {name}: {ticket_status['status']}")

#             metrics["ticket_status"] = "Ticket created"

#             if ticket_status.get("ticket_no"):

#                 print(f"✅ Ticket Number: {ticket_status['ticket_no']}")
#                 metrics["ticket_no"] = ticket_status["ticket_no"]

#             if "created" in ticket_status["status"].lower():
#                 created_tickets.add(name)

#     # ✅ ALWAYS SAVE RESULT
#     results[name] = metrics

# driver.quit()


# # ---------- HTML REPORT ----------

# timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# filename = f"Lib_portal_perf_report_{timestamp}.html"


# def make_table(metrics):

#     return ''.join(
#         f"<tr><td>{url}</td><td>{duration:.0f}</td></tr>"
#         for url, duration in metrics
#     ) or "<tr><td colspan='2'>None</td></tr>"


# def format_value(value):

#     return f"{value:.2f}" if isinstance(value, (int, float)) else "N/A"

# def get_status_color(status):

#     if status == "Ticket created":
#         return "#ff4d4d"   # red

#     elif status == "Ticket already exist":
#         return "#ffcc00"   # yellow

#     elif status == "Duplicate prevented":
#         return "#ffcc00"   # yellow

#     else:
#         return "#66cc66"   # green
# def block_html(title, data):
#     ticket_display = data.get("ticket_no") or data.get("ticket_status", "No Ticket")
#     status = data.get("ticket_status", "No Ticket")
#     color = get_status_color(status)
#     return f"""
#     <h2>{title}</h2>
#     <p><strong>URL:</strong> {data['url']}</p>
#     <p><strong>Page Load Time:</strong> {data['load_time']:.2f} sec</p>
#     <p><strong>Ticket Status:</strong>
#     <span style="background:{color};padding:4px 10px;border-radius:5px;">
#     {ticket_display}
#     </span>
#     </p>
#     <p><strong>FCP:</strong> {format_value(data.get('fcp'))} ms</p>
#     <p><strong>TTI:</strong> {format_value(data.get('tti'))} ms</p>

#     <table>
#     <tr>
#     <th>Slow XHR Request</th>
#     <th>Duration (ms)</th>
#     </tr>

#     {make_table(data['slow_requests'])}

#     </table>
#     """


# with open(filename, "w", encoding="utf-8") as f:

#     f.write(f"""
#     <!DOCTYPE html>
#     <html>

#     <head>
#     <title>Lumos Performance Report</title>

#     <style>

#     body {{font-family:Arial;padding:20px;}}

#     table {{border-collapse:collapse;width:100%;}}

#     th,td {{border:1px solid #ccc;padding:8px;}}

#     th {{background:#f4f4f4;}}

#     </style>

#     </head>

#     <body>

#     <h1>Teacher Portal Performance Report</h1>

#     <p><strong>Test Run:</strong> {timestamp}</p>

#     {''.join(block_html(title,data) for title,data in results.items())}

#     </body>

#     </html>
#     """)

# print(f"\n✅ HTML performance report generated: {filename}")
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import time
import os

print("RUNNING CLEAN VERSION - NO TICKETS AT ALL")

# -------------------- CONFIG --------------------

urls_to_test = {
    "Login Page": "https://www.lumoslearning.com/llp/login.php",
    "Dashboard": "https://www.lumoslearning.com/llwp/librarian.html",
    "Subscribe Program": "https://www.lumoslearning.com/llwp/librarian/my-programs.html",
    "Trynow Page": "https://www.lumoslearning.com/llp/reports_main.php?CourseID=15775",
    "Usagae by Programs": "https://www.lumoslearning.com/llwp/librarian/program-report.html",
    "Popular By lessons": "https://www.lumoslearning.com/llwp/librarian/lesson-by-session.html",
    "Lessons by Grade": "https://www.lumoslearning.com/llwp/librarian/lesson-insights.html",
    "Media Kit": "https://www.lumoslearning.com/llwp/librarian/media-kit.html",
    "Lib FAQ Page": "https://www.lumoslearning.com/llwp/stepup-parent-faq.html?type=librarian",
    "Lib Profile Page": "https://www.lumoslearning.com/llwp/schoolup/schoolup-registration.html?userid=50969874",
}

USERNAME = "demo_library_njsla"
PASSWORD = "17932486"

# ------------------------------------------------

def collect_metrics(driver, page_url):

    driver.get_log("performance")
    driver.get(page_url)

    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "body"))
    )
    time.sleep(2)

    load_time = driver.execute_script("""
        var timing = window.performance.timing;
        return (timing.loadEventEnd - timing.navigationStart) / 1000;
    """)

    if load_time <= 0:
        load_time = driver.execute_script("return performance.now()/1000")

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
                resource_type = sent_event["params"].get("type", "")

                if duration > 500 and (
                    resource_type in ["XHR", "Fetch"] or
                    ".php" in url or
                    ".json" in url or
                    "ajax" in url
                ):
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
            if (entries.length === 0) return null;
            let lastTask = entries[entries.length - 1];
            return lastTask.startTime + lastTask.duration;
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
"user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
"(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
)

driver = webdriver.Chrome(options=options)
driver.execute_cdp_cmd("Network.enable", {})


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


# ---------- Login Metrics ----------

nav_start = driver.execute_script(
    "return window.performance.timing.navigationStart"
)

load_end = driver.execute_script(
    "return window.performance.timing.loadEventEnd"
) or driver.execute_script("return Date.now()")

login_metrics = {
    "url": urls_to_test["Login Page"],
    "load_time": (load_end - nav_start) / 1000,
    "fcp": None,
    "tti": None,
    "slow_requests": []
}


# ---------- Run Metrics ----------

results = {"Login Page": login_metrics}

for name, url in urls_to_test.items():

    if name == "Login Page":
        continue

    print(f"\n⏳ Testing: {name}")

    metrics = collect_metrics(driver, url)

    print(f"Load Time: {metrics['load_time']:.2f} sec")

    if metrics["load_time"] > 3:
        print(f"⚠️ {name} is slow (>3 sec)")

    results[name] = metrics

driver.quit()


# ---------- HTML REPORT ----------

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
filename = f"Lib_portal_perf_report_{timestamp}.html"


def make_table(metrics):
    return ''.join(
        f"<tr><td>{url}</td><td>{duration:.0f}</td></tr>"
        for url, duration in metrics
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
    <tr>
    <th>Slow XHR Request</th>
    <th>Duration (ms)</th>
    </tr>

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
    body {{font-family:Arial;padding:20px;}}
    table {{border-collapse:collapse;width:100%;}}
    th,td {{border:1px solid #ccc;padding:8px;}}
    th {{background:#f4f4f4;}}
    </style>

    </head>

    <body>

    <h1>Teacher Portal Performance Report</h1>
    <p><strong>Test Run:</strong> {timestamp}</p>

    {''.join(block_html(title,data) for title,data in results.items())}

    </body>

    </html>
    """)

print(f"\n✅ HTML performance report generated: {filename}")


# ---------- EMAIL REPORT (ADDED ONLY) ----------

import smtplib
from email.message import EmailMessage
import os

def send_email_report(file_path): 
    sender_email = "automationtesting.lumos@gmail.com"
    sender_password = "ajxvmfxqvubczddj"  
    receiver_email = "prajwal.lumos@gmail.com"

    msg = EmailMessage()
    msg["Subject"] = "Lumos Performance Report"
    msg["From"] = "automationtesting.lumos@gmail.com"
    msg["To"] = "prajwal.lumos@gmail.com"

    msg.set_content("Please find the attached performance report.")

    with open(file_path, "rb") as f:
        file_data = f.read()
        file_name = os.path.basename(file_path)

    msg.add_attachment(file_data, maintype="text", subtype="html", filename=file_name)

    try:
        # ✅ Correct SMTP config
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(sender_email, sender_password)
            smtp.send_message(msg)

        print("📧 Email sent successfully!")

    except Exception as e:
        print(f"❌ Failed to send email: {e}")


# Call function
send_email_report(filename)