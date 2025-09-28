import os
import argparse
from dotenv import load_dotenv
from utils.file_parser import process_file
from utils.email_sender import send_email
from utils.logger import setup_logger
from utils.pdf_generator import generate_pdf_report
from openai import OpenAI
from datetime import datetime

# Load environment variables and logger
load_dotenv()
logger = setup_logger()
client = OpenAI()  # openai>=1.0.0
logger.info(client.models.list())

def summarize_text(text, logger=None):
    try:
        prompt = f"""
Based on the information provided below, Summarize this uploaded Annual report.
Return the output in *strict JSON-like format*:
{{
  "title": "<short professional title capturing the essence of the update>",
  "subtitle": "<descriptive and engaging subtitle providing context>",
  "summary": "<multi-paragraph narrative written in the tone of a press release or board communication, highlighting key outcomes, trends, and implications>"
}}

Do not add explanations outside this format.

Guidelines for the summary:
- Focus on storytelling and framing—assume the reader has **not seen the data** and requires context and interpretation.
- Give more emphasis on "Sheet 1" data than "Sheet 2" data
- Use a professional and formal tone, suitable for business communication
- Focus on the Management discussion and Analysis section first and then the financials
- No need to mention about the company information, field of company, history, etc.
- Are the sales, operating profit (USE EBITDA and Not EBIT), and PAT increasing
- Are the Operating profit margins (EBITDA) and net profit margins increasing? Show a breakdown of how they are growing and why they are increasing
- Do not mention aything like "Data is not provided" or "As per the data" or "limited data is provided"
- Do not mention anything about the metrics for which data is not provided
- Is the balance sheet of the company healthy? Are there any signs of stress?
- Keep the financial upto 2 paragraphs only
- Identify the red flags in the company

Formatting - 
- Easy to read language
- Use bullet points

Here is the input data:\n\n{text}
"""
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are equity analyst and you write clear and professional business reports and summaries."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        summary = response.choices[0].message.content.strip()
        if logger: logger.info("Summary generated successfully using GPT")
        # print( summary)
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

        pdf_path = generate_pdf_report(
            content=summary,
            output_path="monthly_summary.pdf",
            header_image="header.jpg"
        )

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
