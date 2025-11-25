import os
from api_client import APIClient
from excel_writer import create_excel
from emailer import send_email_with_attachments
from error_handler import log_exception, log_info, get_log_path
from utils import now_utc_iso

def main():
    try:
        log_info("Starting parent report process")

        # ENV / Secrets (set in GitHub Secrets)
        SMTP_HOST = os.getenv("SMTP_HOST")
        SMTP_PORT = os.getenv("SMTP_PORT", "587")
        SMTP_USER = os.getenv("SMTP_USER")
        SMTP_PASS = os.getenv("SMTP_PASS")
        TO_EMAIL = os.getenv("TO_EMAIL")

        API1 = os.getenv("API1_URL", "https://internal.company.com/api/v1/transactions/summary")
        API2 = os.getenv("API2_URL", "https://internal.company.com/api/v1/scorecard/monthly")
        API3 = os.getenv("API3_URL", "https://internal.company.com/api/v1/reports/daily")
        API_KEY = os.getenv("API_KEY")
        headers = {"Authorization": f"Bearer {API_KEY}"} if API_KEY else {}

        client = APIClient(headers=headers)

        # Fetch APIs (with retry in child)
        transaction_summary = client.fetch(API1)
        scorecard = client.fetch(API2)
        daily_report = client.fetch(API3)

        # Create Excel
        excel_file = create_excel(transaction_summary, scorecard, daily_report, filename="daily_report.xlsx")

        # Prepare body
        body = (
            f"Hello,\n\n"
            f"Automated report generated.\n\n"
            f"TransactionSummary rows: {len(transaction_summary)}\n"
            f"Scorecard rows: {len(scorecard)}\n"
            f"DailyReport rows: {len(daily_report)}\n\n"
            f"Generated at: {now_utc_iso()}\n\n-- Automation Bot"
        )

        # Attach logs if any
        attachments = [excel_file]
        logpath = get_log_path()
        if os.path.exists(logpath) and os.path.getsize(logpath) > 0:
            attachments.append(logpath)
            body = "⚠ Some errors occurred during processing. See attached log.\n\n" + body

        # Send email
        send_email_with_attachments(SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, TO_EMAIL, "Daily Multi-API Report", body, attachments)

        log_info("Parent process finished successfully")
    except Exception as e:
        log_exception("PARENT PROCESS FAILED", e)
        # In case of fatal failure, try to email admins with log (best-effort, do not crash)
        try:
            admin_email = os.getenv("ADMIN_EMAIL")
            if admin_email:
                send_email_with_attachments(os.getenv("SMTP_HOST"), os.getenv("SMTP_PORT"), os.getenv("SMTP_USER"), os.getenv("SMTP_PASS"), admin_email, "Report Parent Fatal Failure", f"PARENT failed: {str(e)}", [get_log_path()])
        except Exception as ee:
            log_exception("Failed to notify admin", ee)

if __name__ == "__main__":
    main()
