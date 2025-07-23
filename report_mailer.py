import os
import argparse
from dotenv import load_dotenv
from utils.file_parser import process_file
from utils.email_sender import send_email
from utils.logger import setup_logger
from utils.pdf_generator import generate_pdf_report
from openai import OpenAI

# Load environment variables and logger
load_dotenv()
logger = setup_logger()
client = OpenAI()  # openai>=1.0.0

def summarize_text(text, logger=None):
    try:
        prompt = f"""
Based on the information provided below (from Excel, Word, or PDF), write a formal, readable summary structured into sections such as (but not limited to):

- Leadership or Personnel Updates
- Strategic Initiatives
- Key Operational Highlights
- Financial or Performance Metrics (if available)
- Business Development and Marketing Activities
- External Collaborations or Visits
- Next Steps or Plans

Your output should:
- Be written in full sentences and paragraph form (no bullet points)
- Be suitable for inclusion in a PDF report shared with stakeholders
- Maintain a professional and concise tone
- Avoid generic phrases like "please refer to the document" or "as seen in Sheet1"
- Not mention the data was extracted or parsed

Here is the input data:\n\n{text}
"""
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You write clear and professional business reports."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        summary = response.choices[0].message.content.strip()
        if logger: logger.info("Summary generated successfully using GPT")
        return summary

    except Exception as e:
        error_msg = f"Error generating summary: {e}"
        if logger: logger.error(error_msg)
        return "(Fallback summary) Document processed, but GPT report generation failed."

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="Path to the input file (.docx/.pdf/.xlsx)")
    parser.add_argument("--to", required=True, help="Recipient email address")
    parser.add_argument("--subject", default="Monthly Update", help="Email subject")
    args = parser.parse_args()

    try:
        logger.info(f"Processing file: {args.file}")
        file_text = process_file(args.file)

        logger.info("====== EXTRACTED TEXT ======")
        logger.info(file_text)
        # print(file_text[:3000])  # Optional truncate for terminal
        # print(file_text)  # Optional truncate for terminal
        logger.info("================================")

        confirm_gpt = input("\nDo you want to generate a summary using GPT? (yes/no): ").strip().lower()
        if confirm_gpt != "yes":
            # print("GPT summarization aborted by user.")
            logger.info("GPT summarization aborted by user.")
            exit(0)

        summary = summarize_text(file_text, logger)

        pdf_path = generate_pdf_report(summary)
        logger.info(f"PDF report generated at: {pdf_path}")

        logger.info("\n====== GENERATED SUMMARY ======")
        logger.info(summary)
        logger.info("==================================\n")

        # Ask for confirmation
        confirm = input("Do you want to send this summary via email? (yes/no): ").strip().lower()
        if confirm != "yes":
            # print("Email sending aborted by user.")
            logger.info("Email sending aborted by user.")
            exit(0)

        # Send main summary
        sent = send_email(
            subject=args.subject,
            body="Please find the attached monthly report.",
            to_email=args.to,
            smtp_user=os.getenv("SMTP_USER"),
            smtp_pass=os.getenv("SMTP_PASS"),
            smtp_server=os.getenv("SMTP_SERVER", "smtp.gmail.com"),
            smtp_port=int(os.getenv("SMTP_PORT", 587)),
            attachment_path=pdf_path,
            logger=logger
        )

        # Send status report to self/admin
        report_email = os.getenv("STATUS_REPORT_EMAIL")
        if report_email:
            status = "SUCCESS" if sent else "FAILED"
            report_body = f"""Report Summary Sent:

                File: {args.file}
                Recipient: {args.to}
                Status: {status}
                Summary: {summary}

                """
            send_email(
                subject=f"[STATUS] Report Mailer - {status}",
                body=report_body,
                to_email=report_email,
                smtp_user=os.getenv("SMTP_USER"),
                smtp_pass=os.getenv("SMTP_PASS"),
                smtp_server=os.getenv("SMTP_SERVER", "smtp.gmail.com"),
                smtp_port=int(os.getenv("SMTP_PORT", 587)),
                attachment_path=pdf_path,
                logger=logger
            )

    except Exception as e:
        logger.exception(f"Unexpected failure: {e}")
