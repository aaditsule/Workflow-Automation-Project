import os
import argparse
from dotenv import load_dotenv
from utils.file_parser import process_file
from utils.email_sender import send_email
from utils.logger import setup_logger
from openai import OpenAI

# Load environment variables and logger
load_dotenv()
logger = setup_logger()
client = OpenAI()  # openai>=1.0.0

def summarize_text(text, logger=None):
    try:
        prompt = f"""
You are an assistant tasked with summarizing data from a document. The data is extracted as text below.

Your goal is to:
- Identify key themes or metrics 
- Summarize findings in 4–6 bullet points or a professional paragraph
- Be specific, avoid saying "see Sheet1" or referring to the document itself

Here is the extracted data:\n\n{text[:3000]}
"""
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful summarizer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        summary = response.choices[0].message.content.strip()
        if logger: logger.info("Summary generated successfully using GPT-3.5")
        return summary

    except Exception as e:
        error_msg = f"Error generating summary: {e}"
        if logger: logger.error(error_msg)
        return "(Fallback summary) Document processed, but GPT-3.5 summary generation failed."

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="Path to the input file (.docx/.pdf/.xlsx)")
    parser.add_argument("--to", required=True, help="Recipient email address")
    parser.add_argument("--subject", default="Monthly Chair Update", help="Email subject")
    args = parser.parse_args()

    try:
        logger.info(f"Processing file: {args.file}")
        file_text = process_file(args.file)

        logger.info("Extracted Text:\n" + file_text)
        print("\n====== EXTRACTED TEXT ======")
        print(file_text[:3000])  # Optional truncate for terminal
        print("================================")

        confirm_gpt = input("\nDo you want to generate a summary using GPT? (yes/no): ").strip().lower()
        if confirm_gpt != "yes":
            print("GPT summarization aborted by user.")
            logger.info("GPT summarization aborted by user.")
            exit(0)

        summary = summarize_text(file_text, logger)

        print("\n====== GENERATED SUMMARY ======")
        print(summary)
        print("==================================\n")

        # Ask for confirmation
        confirm = input("Do you want to send this summary via email? (yes/no): ").strip().lower()
        if confirm != "yes":
            print("Email sending aborted by user.")
            logger.info("Email sending aborted by user.")
            exit(0)

        # Send main summary
        sent = send_email(
            subject=args.subject,
            body=summary,
            to_email=args.to,
            smtp_user=os.getenv("SMTP_USER"),
            smtp_pass=os.getenv("SMTP_PASS"),
            smtp_server=os.getenv("SMTP_SERVER", "smtp.gmail.com"),
            smtp_port=int(os.getenv("SMTP_PORT", 587)),
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

See logs/app.log for details.
"""
            send_email(
                subject=f"[STATUS] Report Mailer - {status}",
                body=report_body,
                to_email=report_email,
                smtp_user=os.getenv("SMTP_USER"),
                smtp_pass=os.getenv("SMTP_PASS"),
                smtp_server=os.getenv("SMTP_SERVER", "smtp.gmail.com"),
                smtp_port=int(os.getenv("SMTP_PORT", 587)),
                logger=logger
            )

    except Exception as e:
        logger.exception(f"Unexpected failure: {e}")
