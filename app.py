"""
─────────────────────────────────────────────
LESTER PORTFOLIO — app.py
Flask backend that serves the portfolio and
handles the /api/contact form submissions.
─────────────────────────────────────────────

SETUP:
  pip install flask flask-cors

RUN (development):
  python app.py

RUN (production):
  gunicorn -w 4 -b 0.0.0.0:5000 app:app
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime
import smtplib
import os
import re

# ── APP CONFIG ───────────────────────────────
app = Flask(__name__, static_folder=".")
CORS(app)

# ── EMAIL CONFIG  (set via environment vars) ─
# Export these before running:
#   export MAIL_SENDER="your@gmail.com"
#   export MAIL_PASSWORD="your_app_password"
#   export MAIL_RECEIVER="lester@example.com"
MAIL_SENDER   = os.environ.get("MAIL_SENDER",   "your@gmail.com")
MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD",  "your_app_password")
MAIL_RECEIVER = os.environ.get("MAIL_RECEIVER",  "lester@example.com")
MAIL_SMTP     = os.environ.get("MAIL_SMTP",      "smtp.gmail.com")
MAIL_PORT     = int(os.environ.get("MAIL_PORT",  587))


# ── HELPERS ──────────────────────────────────
def is_valid_email(email: str) -> bool:
    """Basic email format validation."""
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return bool(re.match(pattern, email))


def send_email(name: str, email: str, subject: str, message: str) -> bool:
    """
    Send a contact form email via SMTP.
    Returns True on success, raises on failure.
    """
    body = (
        f"New portfolio contact from {name} <{email}>\n"
        f"{'─' * 40}\n"
        f"Subject : {subject}\n"
        f"Date    : {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}\n\n"
        f"{message}\n"
    )

    raw_message = (
        f"From: {MAIL_SENDER}\r\n"
        f"To: {MAIL_RECEIVER}\r\n"
        f"Reply-To: {email}\r\n"
        f"Subject: [Portfolio] {subject}\r\n"
        f"\r\n"
        f"{body}"
    )

    with smtplib.SMTP(MAIL_SMTP, MAIL_PORT) as server:
        server.ehlo()
        server.starttls()
        server.login(MAIL_SENDER, MAIL_PASSWORD)
        server.sendmail(MAIL_SENDER, MAIL_RECEIVER, raw_message)

    return True


def save_submission(data: dict) -> None:
    """
    Append the contact submission to a local log file
    as a simple fallback / audit trail.
    """
    log_path = os.path.join(os.path.dirname(__file__), "submissions.log")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(
            f"[{datetime.utcnow().isoformat()}] "
            f"FROM={data['email']} "
            f"NAME={data['name']!r} "
            f"SUBJECT={data['subject']!r}\n"
        )


# ── ROUTES ───────────────────────────────────
@app.route("/")
def index():
    """Serve the portfolio index page."""
    return send_from_directory(".", "index.html")


@app.route("/<path:filename>")
def static_files(filename):
    """Serve static assets (CSS, JS, images)."""
    return send_from_directory(".", filename)


@app.route("/api/contact", methods=["POST"])
def contact():
    """
    Handle contact form submission.

    Expected JSON body:
        {
            "name":    "John Doe",
            "email":   "john@example.com",
            "subject": "Project Inquiry",
            "message": "Hello, I'd like to ..."
        }

    Returns:
        200  { "success": true,  "message": "..." }
        400  { "success": false, "message": "..." }
        500  { "success": false, "message": "..." }
    """
    data = request.get_json(silent=True)

    # ── Validate presence ──
    if not data:
        return jsonify({"success": False, "message": "No data received."}), 400

    required_fields = ("name", "email", "subject", "message")
    for field in required_fields:
        if not data.get(field, "").strip():
            return jsonify({
                "success": False,
                "message": f"Field '{field}' is required."
            }), 400

    name    = data["name"].strip()[:100]
    email   = data["email"].strip()[:254]
    subject = data["subject"].strip()[:200]
    message = data["message"].strip()[:5000]

    # ── Validate email format ──
    if not is_valid_email(email):
        return jsonify({"success": False, "message": "Invalid email address."}), 400

    # ── Save to log ──
    try:
        save_submission({"name": name, "email": email, "subject": subject})
    except OSError:
        pass  # Non-fatal; proceed even if logging fails

    # ── Send email (optional; skip if creds not set) ──
    email_sent = False
    if MAIL_SENDER != "your@gmail.com" and MAIL_PASSWORD != "your_app_password":
        try:
            email_sent = send_email(name, email, subject, message)
        except Exception as exc:
            app.logger.warning("Email send failed: %s", exc)

    return jsonify({
        "success": True,
        "message": "Message received! I'll get back to you within 24 hours.",
        "email_sent": email_sent,
    }), 200


@app.route("/api/health", methods=["GET"])
def health():
    """Simple health-check endpoint."""
    return jsonify({
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
    }), 200


# ── ENTRY POINT ──────────────────────────────
if __name__ == "__main__":
    port  = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("DEBUG", "true").lower() == "true"
    print(f"  🚀  Portfolio running at http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=debug)
