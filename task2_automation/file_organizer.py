# ============================================================
# TASK 2: File Organizer Automation Script
# Automatically sorts files in a folder by their file type
# Features: config file, dry-run, scheduling, email notifications
# Author:  Toheeb Olanrewaju Olagoke   Intern ID: RDXINTTOHEWH86E
# ============================================================

import os
import json
import shutil
import smtplib
import logging
import argparse
import time
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

try:
    import schedule  # External library — install with: pip install schedule
except ImportError:
    schedule = None  # Allow the script to run even if schedule isn't installed


# ─────────────────────────────────────────
# CONFIG LOADING
# All categories and settings live in config.json
# so users can customise without editing this script.
# ─────────────────────────────────────────
DEFAULT_CONFIG = {
    "file_categories": {
        "Images":    [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp"],
        "Videos":    [".mp4", ".mov", ".avi", ".mkv", ".wmv", ".flv"],
        "Audio":     [".mp3", ".wav", ".aac", ".flac", ".ogg"],
        "Documents": [".pdf", ".doc", ".docx", ".txt", ".xlsx", ".xls", ".pptx", ".csv"],
        "Code":      [".py", ".js", ".html", ".css", ".json", ".ts", ".java", ".cpp", ".c"],
        "Archives":  [".zip", ".tar", ".gz", ".rar", ".7z"]
    },
    "default_folder": "./test_files",
    "log_directory": "./logs",
    "email": {"enabled": False}
}


def load_config(config_path="config.json"):
    """Load config from JSON file. Falls back to defaults if missing or malformed."""
    if not os.path.exists(config_path):
        print(f"⚠️  Config file '{config_path}' not found — using built-in defaults.")
        return DEFAULT_CONFIG

    try:
        with open(config_path, "r") as f:
            config = json.load(f)
        for key, value in DEFAULT_CONFIG.items():
            config.setdefault(key, value)
        return config
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing {config_path}: {e}. Using defaults.")
        return DEFAULT_CONFIG


# ─────────────────────────────────────────
# LOGGING SETUP
# ─────────────────────────────────────────
def setup_logging(log_dir):
    """Configure logging to write to both a file and the console."""
    os.makedirs(log_dir, exist_ok=True)
    log_filename = os.path.join(
        log_dir,
        f"organizer_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    )
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)s  %(message)s",
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler()
        ],
        force=True
    )
    return logging.getLogger(__name__), log_filename


# ─────────────────────────────────────────
# CATEGORY LOOKUP
# ─────────────────────────────────────────
def get_category(extension, categories):
    """Figure out which folder a file belongs in based on its extension."""
    ext = extension.lower()
    for category, extensions in categories.items():
        if ext in extensions:
            return category
    return "Others"


# ─────────────────────────────────────────
# MAIN ORGANIZER LOGIC
# ─────────────────────────────────────────
def organize_folder(target_folder, config, logger, dry_run=False):
    """
    Scans the target folder and moves each file into a subfolder named after its category.
    Returns a dict with stats so the caller can use them (e.g. for an email notification).
    """
    if not os.path.exists(target_folder):
        logger.error(f"Folder not found: {target_folder}")
        return {"moved": 0, "skipped": 0, "errors": 1, "status": "folder_missing"}

    categories = config["file_categories"]

    logger.info(f"{'[DRY RUN] ' if dry_run else ''}Starting organizer on: {target_folder}")

    moved = 0
    skipped = 0
    errors = 0

    for filename in os.listdir(target_folder):
        filepath = os.path.join(target_folder, filename)

        if os.path.isdir(filepath):
            logger.info(f"  Skipping directory: {filename}")
            skipped += 1
            continue

        if filename.startswith("organizer_log"):
            skipped += 1
            continue

        _, ext = os.path.splitext(filename)
        category = get_category(ext, categories)

        destination_folder = os.path.join(target_folder, category)
        destination_path = os.path.join(destination_folder, filename)

        try:
            if dry_run:
                logger.info(f"  [WOULD MOVE] {filename}  →  {category}/")
                moved += 1
            else:
                os.makedirs(destination_folder, exist_ok=True)

                if os.path.exists(destination_path):
                    base, extension = os.path.splitext(filename)
                    counter = 1
                    while os.path.exists(destination_path):
                        destination_path = os.path.join(
                            destination_folder, f"{base}_{counter}{extension}"
                        )
                        counter += 1

                shutil.move(filepath, destination_path)
                logger.info(f"  MOVED: {filename}  →  {category}/")
                moved += 1

        except Exception as e:
            logger.error(f"  ERROR moving {filename}: {e}")
            errors += 1

    logger.info("─" * 50)
    logger.info(f"✅ Done! Moved: {moved} | Skipped: {skipped} | Errors: {errors}")

    return {"moved": moved, "skipped": skipped, "errors": errors, "status": "ok"}


# ─────────────────────────────────────────
# EMAIL NOTIFICATION
# Sends a summary email after the run.
# Supports a preview mode that prints the email to the console
# instead of actually sending it (useful for demos without SMTP setup).
# ─────────────────────────────────────────
def build_email_body(stats, target_folder, log_filename, dry_run):
    """Compose the email body from the run statistics."""
    mode = "DRY RUN" if dry_run else "LIVE RUN"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return f"""File Organizer — Run Summary
{'=' * 50}

Mode:        {mode}
Timestamp:   {timestamp}
Folder:      {target_folder}

Results
-------
Files moved:   {stats['moved']}
Skipped:       {stats['skipped']}
Errors:        {stats['errors']}
Status:        {stats['status']}

Log file: {log_filename}

This is an automated message from the File Organizer.
"""


def send_email_notification(stats, config, target_folder, log_filename, logger,
                             dry_run=False, preview=False):
    """
    Send an email summary of the organizer run.

    If preview=True, the email is printed to the console instead of being sent.
    Otherwise it's sent via SMTP using credentials from config.json.
    """
    email_cfg = config.get("email", {})
    subject = f"📁 File Organizer Report — {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    body = build_email_body(stats, target_folder, log_filename, dry_run)

    # PREVIEW MODE — for demos and screenshots without real SMTP credentials
    if preview:
        logger.info("📧 [EMAIL PREVIEW MODE] — message would be sent with the following content:")
        logger.info("─" * 50)
        logger.info(f"To:      {email_cfg.get('recipient_email', '<not configured>')}")
        logger.info(f"From:    {email_cfg.get('sender_email', '<not configured>')}")
        logger.info(f"Subject: {subject}")
        logger.info("─" * 50)
        for line in body.splitlines():
            logger.info(line)
        logger.info("─" * 50)
        logger.info("📧 [Preview only — no email actually sent.]")
        return True

    # LIVE MODE — actually send the email through SMTP
    required = ["sender_email", "sender_password", "recipient_email", "smtp_server", "smtp_port"]
    # Only check .startswith() on string values (smtp_port is an int)
    missing = [
        k for k in required
        if not email_cfg.get(k)
        or (isinstance(email_cfg.get(k), str) and email_cfg.get(k).startswith("your"))
    ]
    if missing:
        logger.error(f"Email config incomplete: missing/unset {missing}. Skipping send.")
        return False

    try:
        msg = MIMEMultipart()
        msg["From"] = email_cfg["sender_email"]
        msg["To"] = email_cfg["recipient_email"]
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        logger.info(f"📧 Connecting to {email_cfg['smtp_server']}:{email_cfg['smtp_port']}...")
        with smtplib.SMTP(email_cfg["smtp_server"], email_cfg["smtp_port"]) as server:
            server.starttls()
            server.login(email_cfg["sender_email"], email_cfg["sender_password"])
            server.send_message(msg)

        logger.info(f"📧 Email sent to {email_cfg['recipient_email']} ✅")
        return True

    except Exception as e:
        logger.error(f"📧 Failed to send email: {e}")
        return False


# ─────────────────────────────────────────
# SCHEDULED RUN MODE
# ─────────────────────────────────────────
def run_scheduled(interval_minutes, target_folder, config, logger, dry_run=False,
                   notify_email=False, preview_email=False, log_filename=None):
    """Run organize_folder() every N minutes until the user presses Ctrl+C."""
    if schedule is None:
        logger.error("The 'schedule' library is not installed. Run: pip install schedule")
        return

    logger.info(f"⏰ Scheduler started: running every {interval_minutes} minute(s). Press Ctrl+C to stop.")

    def job():
        stats = organize_folder(target_folder, config, logger, dry_run=dry_run)
        if notify_email or preview_email:
            send_email_notification(stats, config, target_folder, log_filename, logger,
                                    dry_run=dry_run, preview=preview_email)

    # Run once immediately
    job()

    # Then schedule periodic runs
    schedule.every(interval_minutes).minutes.do(job)

    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("🛑 Scheduler stopped by user.")


# ─────────────────────────────────────────
# COMMAND LINE ARGUMENTS
# ─────────────────────────────────────────
def parse_args():
    parser = argparse.ArgumentParser(
        description="📁 File Organizer — automatically sorts files into folders by type."
    )
    parser.add_argument(
        "folder",
        nargs="?",
        default=None,
        help="Path to the folder you want to organize (overrides config default)."
    )
    parser.add_argument(
        "--config",
        default="config.json",
        help="Path to the config file (default: config.json)."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview what would happen without actually moving any files."
    )
    parser.add_argument(
        "--schedule",
        type=int,
        metavar="MINUTES",
        help="Run the organizer every N minutes (e.g. --schedule 60). Press Ctrl+C to stop."
    )
    parser.add_argument(
        "--notify-email",
        action="store_true",
        help="Send an email notification with the run summary (requires email config)."
    )
    parser.add_argument(
        "--preview-email",
        action="store_true",
        help="Print the email to the console instead of sending it (useful for demos)."
    )
    return parser.parse_args()


# ─────────────────────────────────────────
# DEMO: Create test files
# ─────────────────────────────────────────
def create_test_files(folder):
    """Creates some fake files so you can test the organizer easily."""
    os.makedirs(folder, exist_ok=True)
    test_files = [
        "photo1.jpg", "photo2.png", "video.mp4", "song.mp3",
        "report.pdf", "notes.txt", "script.py", "archive.zip",
        "spreadsheet.xlsx", "index.html", "unknown.xyz"
    ]
    for f in test_files:
        open(os.path.join(folder, f), "w").close()
    print(f"✅ Created {len(test_files)} test files in '{folder}' — run the organizer now!")


# ─────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────
if __name__ == "__main__":
    args = parse_args()

    config = load_config(args.config)
    target_folder = args.folder or config["default_folder"]

    logger, log_filename = setup_logging(config["log_directory"])
    logger.info(f"Loaded config from: {args.config}")

    if not os.path.exists(target_folder):
        logger.info(f"Folder '{target_folder}' not found. Creating test files for demo...")
        create_test_files(target_folder)

    # Scheduled mode vs one-shot run
    if args.schedule:
        run_scheduled(
            args.schedule, target_folder, config, logger,
            dry_run=args.dry_run,
            notify_email=args.notify_email,
            preview_email=args.preview_email,
            log_filename=log_filename
        )
    else:
        stats = organize_folder(target_folder, config, logger, dry_run=args.dry_run)

        # Send email if requested
        if args.notify_email or args.preview_email:
            send_email_notification(
                stats, config, target_folder, log_filename, logger,
                dry_run=args.dry_run,
                preview=args.preview_email
            )

        logger.info(f"📄 Log saved to: {log_filename}")
