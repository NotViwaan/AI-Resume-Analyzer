import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings
from app.services.groq_service import generate_screening_email

logger = logging.getLogger(__name__)


async def send_screening_outcome_email(
    candidate_email: str,
    candidate_name: str,
    job_title: str,
    recommendation: str,
) -> bool:
    """
    Generate a personalized email via Groq and send via SMTP.
    Returns True if sent successfully.
    """
    if not settings.SMTP_HOST:
        logger.warning("SMTP not configured — email skipped")
        return False

    body = await generate_screening_email(candidate_name, job_title, recommendation)

    subject_map = {
        "hire": f"Next Steps: {job_title} Application",
        "maybe": f"Follow-up: Your {job_title} Application",
        "reject": f"Update on Your {job_title} Application",
    }

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject_map.get(recommendation, f"Update on Your {job_title} Application")
    msg["From"] = settings.EMAIL_FROM
    msg["To"] = candidate_email

    html_body = f"""
    <html><body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
      <p>{body.replace(chr(10), "<br>")}</p>
      <hr style="border: none; border-top: 1px solid #eee; margin: 24px 0;">
      <p style="color: #999; font-size: 12px;">
        This email was sent by the AI Resume Analyzer platform.
      </p>
    </body></html>
    """

    msg.attach(MIMEText(body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.EMAIL_FROM, candidate_email, msg.as_string())
        logger.info(f"Sent {recommendation} email to {candidate_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {candidate_email}: {e}")
        return False
