from utils.file_parser import process_file
from utils.email_sender import send_email
from utils.logger import setup_logger
import os
import argparse
from dotenv import load_dotenv
import openai

load_dotenv()
logger = setup_logger()
openai.api_key = os.getenv("OPENAI_API_KEY")

def summarize_text(text):
    prompt = f"""
    Summarize the following text into a professional email body:

    {text[:3000]}
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        summary = response['choices'][0]['message']['content'].strip()
        logger.info("Successfully generated summary")
        logger.debug(f"Summary: {summary}")
        return summary
    except Exception as e:
        logger.error(f"Error generating summary: {e}")
        return "(Fallback summary) Document processed, but summarization failed."

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="Input file (.docx/.pdf/.xlsx)")
    parser.add_argument("--to", required=True)
    parser.add_argument("--subject", default="Monthly Chair Update")
    args = parser.parse_args()

    try:
        logger.info(f"Processing file: {args.file}")
        file_text = process_file(args.file)
        summary = summarize_text(file_text)

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

        # Send status report
        report_email = os.getenv("STATUS_REPORT_EMAIL")
        if report_email:
            status_msg = "SUCCESS" if sent else "FAILED"
            report_body = f"""Report Summary Sent:
            
File: {args.file}
Recipient: {args.to}
Status: {status_msg}

See logs/app.log for details."""
            send_email(
                subject=f"[STATUS] Report Mailer - {status_msg}",
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