import pytest
import time
import os
import csv
import json
import smtplib
from email.message import EmailMessage

try:
    from fpdf import FPDF
    HAS_FPDF = True
except ImportError:
    HAS_FPDF = False

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Global list — one dict per completed state
test_results = []
session_start_time = None


# ---------------------------------------------------------------------------
# PDF builder
# ---------------------------------------------------------------------------

def create_master_pdf(results, report_path):
    if not HAS_FPDF:
        return None

    class PDF(FPDF):
        def header(self):
            self.set_font("Arial", "B", 14)
            self.cell(0, 10, "Automation Master Report - Used Credentials", ln=1, align="C")
            self.set_font("Arial", "", 9)
            self.cell(0, 6, f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}", ln=1, align="C")
            self.ln(4)

        def footer(self):
            self.set_y(-15)
            self.set_font("Arial", "I", 8)
            self.cell(0, 10, f"Page {self.page_no()}", align="C")

    pdf = PDF(orientation="L")          # Landscape → 297mm wide
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # ------ Column definitions (header label, width) ------
    # Landscape A4 usable width ≈ 277mm (297 - 2×10 margins)
    cols = [
        ("State",    26),
        ("Grade",    16),
        ("Subject",  24),
        ("Code S1",  32),
        ("Code S2",  32),
        ("Code S3",  32),
        ("Email",    68),
        ("PIN",      20),
        ("Status",   27),
    ]

    row_h = 8

    # Header row
    pdf.set_fill_color(0, 123, 255)   # blue
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 7)
    for label, w in cols:
        pdf.cell(w, row_h, label, border=1, align="C", fill=True)
    pdf.ln()

    # Data rows
    pdf.set_font("Arial", "", 7)
    for res in results:
        status = res.get("status", "N/A")
        pdf.set_text_color(0, 0, 0)
        values = [
            res.get("state_name",  res.get("state", "N/A")),
            res.get("grade",       "N/A"),
            res.get("subject",     "N/A"),
            res.get("code_step1",  "N/A"),
            res.get("code_step2",  "N/A"),
            res.get("code_step3",  "N/A"),
            res.get("email",       "N/A"),
            res.get("pin",         "N/A"),
            status,
        ]
        for i, (_, w) in enumerate(cols):
            val = values[i]
            if i == len(cols) - 1:          # Status column — colour it
                if status == "PASS":
                    pdf.set_text_color(40, 167, 69)
                else:
                    pdf.set_text_color(220, 53, 69)
            else:
                pdf.set_text_color(0, 0, 0)
            pdf.cell(w, row_h, str(val), border=1, align="C")
        pdf.ln()

    pdf.output(report_path)
    return report_path


def append_run_log(results):
    """Write / append all run results to data/run_log.csv."""
    log_path = os.path.join(BASE_DIR, "data", "run_log.csv")
    fieldnames = [
        "state_name", "grade", "subject",
        "code_step1", "code_step2", "code_step3",
        "email", "pin", "status", "timestamp"
    ]
    file_exists = os.path.exists(log_path)
    with open(log_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        if not file_exists:
            writer.writeheader()
        for r in results:
            r.setdefault("timestamp", time.strftime("%Y-%m-%d %H:%M:%S"))
            writer.writerow(r)
    return log_path


# ---------------------------------------------------------------------------
# Pytest hooks
# ---------------------------------------------------------------------------

def pytest_sessionstart(session):
    global session_start_time
    session_start_time = time.time()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()

    if rep.when == "call" or (rep.when == "setup" and rep.failed):
        # Derive state name from parametrize id
        callspec   = getattr(item, "callspec", None)
        state_name = callspec.id if callspec else item.name
        status     = "PASS" if rep.passed else "FAIL"
        timestamp  = time.strftime("%H:%M:%S")

        # Pull everything that test attached to user_properties
        props = {k: v for k, v in rep.user_properties}

        test_results.append({
            "state_name":  props.get("state_name",  state_name),
            "grade":       props.get("grade",        "N/A"),
            "subject":     props.get("subject",      "N/A"),
            "code_step1":  props.get("code_step1",   "N/A"),
            "code_step2":  props.get("code_step2",   "N/A"),
            "code_step3":  props.get("code_step3",   "N/A"),
            "email":       props.get("used_email",   "N/A"),
            "pin":         props.get("used_pin",     "N/A"),
            "status":      status,
            "timestamp":   timestamp,
            # backward-compat key for HTML report
            "state":       props.get("state_name",  state_name),
            "script":      "Automation_assessment.main_test_for_cron",
            "end_time":    timestamp,
        })


def pytest_sessionfinish(session, exitstatus):
    total_secs = time.time() - session_start_time
    passed = sum(1 for r in test_results if r["status"] == "PASS")
    failed = sum(1 for r in test_results if r["status"] == "FAIL")

    h, rem  = divmod(total_secs, 3600)
    m, s    = divmod(rem, 60)
    duration = f"{int(h):02d}:{int(m):02d}:{int(s):02d}"

    # ---- Append to run_log.csv -----------------------------------------------
    log_path = append_run_log(test_results)
    print(f"\nRun log appended: {log_path}")

    # ---- Build HTML summary rows ---------------------------------------------
    rows_html = ""
    for tr in test_results:
        color = "#28a745" if tr["status"] == "PASS" else "#dc3545"
        rows_html += f"""
        <tr>
          <td>{tr.get('state_name','')}</td>
          <td>{tr.get('grade','')}</td>
          <td>{tr.get('subject','')}</td>
          <td>{tr.get('code_step1','')}</td>
          <td>{tr.get('code_step2','')}</td>
          <td>{tr.get('code_step3','')}</td>
          <td>{tr.get('email','')}</td>
          <td>{tr.get('pin','')}</td>
          <td style="font-weight:bold;color:{color};">{tr.get('status','')}</td>
          <td>{tr.get('end_time','')}</td>
        </tr>"""

    html_content = f"""
    <html><head><style>
      body {{font-family:sans-serif;}}
      table {{border-collapse:collapse;width:100%;font-size:12px;}}
      th {{background:#007bff;color:#fff;padding:8px;border:1px solid #ddd;}}
      td {{padding:7px;border:1px solid #ddd;}}
    </style></head><body>
    <h2>Automation Report: Type A Batch</h2>
    <p><b>Passed:</b> {passed} &nbsp; <b>Failed:</b> {failed} &nbsp; <b>Duration:</b> {duration}</p>
    <table>
      <thead><tr>
        <th>State</th><th>Grade</th><th>Subject</th>
        <th>Code S1</th><th>Code S2</th><th>Code S3</th>
        <th>Email Used</th><th>PIN</th><th>Status</th><th>Time</th>
      </tr></thead>
      <tbody>{rows_html}</tbody>
    </table>
    <br><p>Regards,<br>Automation System</p>
    </body></html>"""

    # ---- Save HTML locally ---------------------------------------------------
    html_path = os.path.join(BASE_DIR, "report.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    # ---- Generate PDF --------------------------------------------------------
    pdf_path = os.path.join(BASE_DIR, "credentials_report.pdf")
    generated_pdf = create_master_pdf(test_results, pdf_path)
    if generated_pdf:
        print(f"PDF report saved: {generated_pdf}")
    else:
        print("fpdf2 not installed — PDF skipped. Run: pip install fpdf2")

    # ---- Send Email ----------------------------------------------------------
    config_path = os.path.join(BASE_DIR, "email_config.json")
    if not os.path.exists(config_path):
        print("[NOTE] email_config.json not found — skipping email.")
        return

    with open(config_path) as f:
        config = json.load(f)

    sender    = config.get("sender_email", "")
    pwd       = config.get("sender_password", "")
    recipient = config.get("recipient_email", "")

    # Support both single string and list of recipients
    if isinstance(recipient, list):
        recipients = [r.strip() for r in recipient if r.strip()]
    else:
        recipients = [r.strip() for r in recipient.split(",") if r.strip()]

    if not sender or "YOUR_" in sender or not pwd or not recipients:
        print("[NOTE] Skipped email — fill in email_config.json with real credentials.")
        return

    print(f"\nSending report to {', '.join(recipients)} ...")
    try:
        msg = EmailMessage()
        msg["Subject"] = "Automation Report: Type A Batch"
        msg["From"]    = sender
        msg["To"]      = ", ".join(recipients)
        msg.set_content("Enable HTML to view this report.")
        msg.add_alternative(html_content, subtype="html")

        # Attach PDF
        if generated_pdf and os.path.exists(generated_pdf):
            with open(generated_pdf, "rb") as pdf_f:
                msg.add_attachment(
                    pdf_f.read(),
                    maintype="application",
                    subtype="pdf",
                    filename="Credentials_Report.pdf"
                )

        # Attach run log CSV
        if os.path.exists(log_path):
            with open(log_path, "rb") as csv_f:
                msg.add_attachment(
                    csv_f.read(),
                    maintype="text",
                    subtype="csv",
                    filename="run_log.csv"
                )

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, pwd)
            server.send_message(msg)
        print("Email sent successfully! (HTML + PDF + CSV attached)")
    except Exception as e:
        print(f"Failed to send email: {e}")
        print("Hint: Make sure you are using a Gmail App Password, not your regular password.")
        print("Get one at: myaccount.google.com → Security → App Passwords")
