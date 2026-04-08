"""
Email Dataset for the Email Triage Environment.

Contains realistic email examples with ground-truth labels for:
- Priority classification (low, medium, high, urgent)
- Category classification (support, sales, billing, technical, spam)
- Routing department (customer_support, sales, billing, engineering, spam_filter)
- Expected response keywords for rubric-based grading
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Email:
    """A single email with ground-truth labels."""

    email_id: str
    sender: str
    subject: str
    body: str
    ground_truth_priority: str  # low, medium, high, urgent
    ground_truth_category: str  # support, sales, billing, technical, spam
    ground_truth_department: str  # customer_support, sales, billing, engineering, spam_filter
    ground_truth_triage_action: str = ""  # accept, reject
    expected_response_keywords: List[str] = field(default_factory=list)
    sender_name: str = ""

    def __post_init__(self):
        if not self.sender_name:
            # Extract name from email
            self.sender_name = self.sender.split("@")[0].replace(".", " ").title()


# ─────────────────────────────────────────────────────────────────────────────
# EMAIL DATASET — 15 realistic emails across all categories and priorities
# ─────────────────────────────────────────────────────────────────────────────

EMAILS: List[Email] = [
    # ── EASY: Clear classification signals ───────────────────────────────────
    Email(
        email_id="email_001",
        sender="john.smith@acmecorp.com",
        sender_name="John Smith",
        subject="Cannot login to my account",
        body=(
            "Hi Support Team,\n\n"
            "I've been trying to log into my account for the past 30 minutes "
            "but keep getting an 'Invalid credentials' error. I've tried resetting "
            "my password twice but the reset email never arrives.\n\n"
            "My username is john.smith@acmecorp.com. Can you please help me "
            "regain access to my account?\n\n"
            "Thanks,\nJohn Smith"
        ),
        ground_truth_priority="high",
        ground_truth_category="support",
        ground_truth_department="customer_support",
        expected_response_keywords=[
            "account", "password", "reset", "login", "help", "access",
            "sorry", "assist", "investigate"
        ],
    ),
    Email(
        email_id="email_002",
        sender="sarah.jones@megastore.io",
        sender_name="Sarah Jones",
        subject="Interested in Enterprise Plan pricing",
        body=(
            "Hello,\n\n"
            "I'm the VP of Operations at MegaStore and we're evaluating your "
            "platform for our team of 500+ employees. Could you send me "
            "information about your Enterprise Plan pricing and volume discounts?\n\n"
            "We're particularly interested in:\n"
            "- SSO integration\n"
            "- Custom SLA options\n"
            "- Data residency in EU\n\n"
            "Looking forward to hearing from you.\n\n"
            "Best regards,\nSarah Jones\nVP Operations, MegaStore"
        ),
        ground_truth_priority="medium",
        ground_truth_category="sales",
        ground_truth_department="sales",
        expected_response_keywords=[
            "enterprise", "pricing", "plan", "team", "demo",
            "contact", "information", "thank"
        ],
    ),
    Email(
        email_id="email_003",
        sender="mike.chen@startup.dev",
        sender_name="Mike Chen",
        subject="Invoice #4521 - Duplicate charge on credit card",
        body=(
            "Hi Billing,\n\n"
            "I noticed that I was charged twice for Invoice #4521 dated March 15. "
            "The amount of $299.99 was deducted from my Visa ending in 4242 on both "
            "March 15 and March 16.\n\n"
            "Can you please refund the duplicate charge? I've attached my bank "
            "statement showing both transactions.\n\n"
            "Regards,\nMike Chen"
        ),
        ground_truth_priority="high",
        ground_truth_category="billing",
        ground_truth_department="billing",
        expected_response_keywords=[
            "invoice", "charge", "refund", "duplicate", "payment",
            "apologize", "sorry", "review", "investigate"
        ],
    ),
    Email(
        email_id="email_004",
        sender="winner@prize-lottery-intl.xyz",
        sender_name="Prize Department",
        subject="🎉 CONGRATULATIONS! You've WON $5,000,000!!!",
        body=(
            "DEAR LUCKY WINNER,\n\n"
            "You have been selected as the GRAND PRIZE WINNER of our international "
            "lottery! You have won FIVE MILLION US DOLLARS ($5,000,000).\n\n"
            "To claim your prize, please send us:\n"
            "1. Your full name and address\n"
            "2. Bank account number for wire transfer\n"
            "3. Copy of your passport or ID\n"
            "4. Processing fee of $500 via Western Union\n\n"
            "ACT NOW! This offer expires in 24 hours!\n\n"
            "Congratulations,\nPrize Department\nInternational Lottery Commission"
        ),
        ground_truth_priority="low",
        ground_truth_category="spam",
        ground_truth_department="spam_filter",
        expected_response_keywords=[
            "spam", "suspicious", "ignore", "phishing", "scam",
            "do not", "never", "personal information"
        ],
    ),
    Email(
        email_id="email_005",
        sender="dev.lead@techfirm.co",
        sender_name="Alex Rivera",
        subject="API returning 500 errors on /v2/users endpoint",
        body=(
            "Hi Technical Team,\n\n"
            "Since the latest deployment (v2.4.1) yesterday at 3pm UTC, our "
            "production integration with your API has been failing. Specifically, "
            "GET requests to /v2/users are returning 500 Internal Server Error "
            "approximately 40% of the time.\n\n"
            "Here's a sample error response:\n"
            '{"error": "internal_error", "message": "connection pool exhausted", '
            '"request_id": "req_8f3d2a"}\n\n'
            "This is blocking our release. We have 10,000 users affected.\n\n"
            "Can you investigate urgently?\n\n"
            "Alex Rivera\nLead Developer, TechFirm"
        ),
        ground_truth_priority="urgent",
        ground_truth_category="technical",
        ground_truth_department="engineering",
        expected_response_keywords=[
            "api", "error", "investigate", "urgently", "team",
            "fix", "deploy", "incident", "priority", "sorry"
        ],
    ),
    # ── MEDIUM: Moderate ambiguity ───────────────────────────────────────────
    Email(
        email_id="email_006",
        sender="lisa.wang@retailco.com",
        sender_name="Lisa Wang",
        subject="Feature request: Bulk export to CSV",
        body=(
            "Hello,\n\n"
            "Our analytics team frequently needs to export large datasets from your "
            "platform. Currently, we can only export 1,000 rows at a time, which is "
            "very tedious for our nightly reports.\n\n"
            "Could you add a bulk export feature that allows exporting up to 100K "
            "rows as a CSV file? This would save us several hours per week.\n\n"
            "We're on the Business plan and have been customers for 3 years.\n\n"
            "Thanks,\nLisa Wang\nData Analyst, RetailCo"
        ),
        ground_truth_priority="medium",
        ground_truth_category="support",
        ground_truth_department="customer_support",
        expected_response_keywords=[
            "feature", "request", "export", "feedback", "team",
            "thank", "roadmap", "consider"
        ],
    ),
    Email(
        email_id="email_007",
        sender="raj.patel@consulting.in",
        sender_name="Raj Patel",
        subject="Downgrade from Pro to Basic plan",
        body=(
            "Hi,\n\n"
            "I'd like to downgrade my subscription from the Pro plan ($49/month) "
            "to the Basic plan ($19/month), effective from the next billing cycle "
            "on April 1.\n\n"
            "I no longer need the advanced analytics features. Please confirm "
            "the change and let me know if there will be any data loss.\n\n"
            "Account ID: ACC-78234\n\n"
            "Thanks,\nRaj Patel"
        ),
        ground_truth_priority="medium",
        ground_truth_category="billing",
        ground_truth_department="billing",
        expected_response_keywords=[
            "downgrade", "plan", "subscription", "billing", "change",
            "confirm", "data", "cycle"
        ],
    ),
    Email(
        email_id="email_008",
        sender="emily.taylor@nonprofit.org",
        sender_name="Emily Taylor",
        subject="Partnership opportunity for education sector",
        body=(
            "Dear Team,\n\n"
            "I'm reaching out from EduReach, a nonprofit serving 200+ schools in "
            "underserved communities. We've been using your free tier and would love "
            "to discuss a partnership that provides discounted access for our schools.\n\n"
            "We can offer:\n"
            "- Case studies and testimonials from our schools\n"
            "- Co-marketing opportunities in the education sector\n"
            "- Feedback from teachers as beta testers\n\n"
            "Would someone from your partnerships team be available for a call "
            "next week?\n\n"
            "Warm regards,\nEmily Taylor\nDirector of Technology, EduReach"
        ),
        ground_truth_priority="medium",
        ground_truth_category="sales",
        ground_truth_department="sales",
        expected_response_keywords=[
            "partnership", "opportunity", "education", "discuss",
            "schedule", "call", "thank", "team"
        ],
    ),
    Email(
        email_id="email_009",
        sender="ops@cloudhost.net",
        sender_name="CloudHost Operations",
        subject="Scheduled maintenance window - April 10, 2-4 AM UTC",
        body=(
            "Dear Customer,\n\n"
            "This is to inform you about a scheduled maintenance window for our "
            "infrastructure on April 10, 2026, from 2:00 AM to 4:00 AM UTC.\n\n"
            "During this window:\n"
            "- Brief service interruptions may occur (typically < 5 minutes)\n"
            "- API latency may be elevated\n"
            "- All data will be preserved\n\n"
            "No action is required on your part. If you have questions, please "
            "contact our support team.\n\n"
            "Best regards,\nCloudHost Operations Team"
        ),
        ground_truth_priority="low",
        ground_truth_category="support",
        ground_truth_department="customer_support",
        expected_response_keywords=[
            "maintenance", "noted", "thank", "schedule", "information",
            "acknowledge"
        ],
    ),
    Email(
        email_id="email_010",
        sender="security@your-bank-verify.com",
        sender_name="Security Team",
        subject="URGENT: Verify your bank account immediately",
        body=(
            "Dear Valued Customer,\n\n"
            "We have detected unusual activity on your account. Your account will be "
            "SUSPENDED within 24 hours unless you verify your identity.\n\n"
            "Click here to verify: http://your-bank-verify.com/verify?token=abc123\n\n"
            "You must provide:\n"
            "- Your account number\n"
            "- Social security number\n"
            "- Mother's maiden name\n\n"
            "Failure to act immediately will result in permanent account closure.\n\n"
            "Security Department\nYour Bank"
        ),
        ground_truth_priority="low",
        ground_truth_category="spam",
        ground_truth_department="spam_filter",
        expected_response_keywords=[
            "phishing", "spam", "suspicious", "scam", "ignore",
            "do not click", "report"
        ],
    ),
    # ── HARD: Complex, multi-faceted ─────────────────────────────────────────
    Email(
        email_id="email_011",
        sender="cto@fintech.com",
        sender_name="David Kim",
        subject="Critical: Data sync failures + billing discrepancy + need API docs",
        body=(
            "Hi,\n\n"
            "Multiple issues to report:\n\n"
            "1. CRITICAL: Our data sync pipeline has been failing since Monday. "
            "Webhook events for user.created and user.updated are not being "
            "delivered to our endpoint https://hooks.fintech.com/webhook.\n\n"
            "2. Our last invoice shows charges for 15,000 API calls but our logs "
            "show only 8,200. Please audit this.\n\n"
            "3. We also need updated API docs for the v3 batch endpoints — the "
            "current docs reference deprecated fields.\n\n"
            "This is affecting our production system. We need a response ASAP.\n\n"
            "David Kim\nCTO, FinTech Inc."
        ),
        ground_truth_priority="urgent",
        ground_truth_category="technical",
        ground_truth_department="engineering",
        expected_response_keywords=[
            "webhook", "sync", "investigate", "billing", "audit",
            "api", "documentation", "urgent", "priority", "sorry", "team"
        ],
    ),
    Email(
        email_id="email_012",
        sender="maria.garcia@healthcare.org",
        sender_name="Maria Garcia",
        subject="HIPAA compliance question + renewal quote",
        body=(
            "Hello,\n\n"
            "We're a healthcare organization preparing for our annual compliance "
            "audit. I have two requests:\n\n"
            "1. Can you provide documentation confirming your platform's HIPAA "
            "compliance status? We need a BAA (Business Associate Agreement) "
            "and SOC 2 Type II report.\n\n"
            "2. Our annual subscription renewal is coming up next month. Our "
            "current plan is Enterprise at $999/month. Are there any loyalty "
            "discounts for a 3-year commitment?\n\n"
            "Please route these to the appropriate teams.\n\n"
            "Maria Garcia, IT Director\nHealthCare Systems Inc."
        ),
        ground_truth_priority="high",
        ground_truth_category="sales",
        ground_truth_department="sales",
        expected_response_keywords=[
            "compliance", "hipaa", "renewal", "enterprise", "discount",
            "documentation", "team", "assist"
        ],
    ),
    Email(
        email_id="email_013",
        sender="intern@smallbiz.com",
        sender_name="Jamie Lee",
        subject="How do I add users to my workspace?",
        body=(
            "Hi there,\n\n"
            "I just started using your platform and I can't figure out how to "
            "add team members to my workspace. I went to Settings but don't see "
            "an option for team management.\n\n"
            "I'm on the free plan. Is this a paid feature?\n\n"
            "Thanks!\nJamie"
        ),
        ground_truth_priority="low",
        ground_truth_category="support",
        ground_truth_department="customer_support",
        expected_response_keywords=[
            "workspace", "team", "add", "users", "settings", "plan",
            "upgrade", "help", "steps"
        ],
    ),
    Email(
        email_id="email_014",
        sender="sysadmin@enterprise.co",
        sender_name="Tom Wilson",
        subject="SSL certificate expiring on custom domain",
        body=(
            "Urgent,\n\n"
            "The SSL certificate for our custom domain (app.enterprise.co) hosted "
            "on your platform expires in 3 days. Auto-renewal seems to have failed.\n\n"
            "Error from our monitoring:\n"
            "Certificate CN=app.enterprise.co expires on 2026-04-11T00:00:00Z\n"
            "Auto-renewal last attempted: 2026-04-05T03:00:00Z — FAILED\n"
            "Error: DNS validation record not found\n\n"
            "This will cause our entire customer portal to go down. Please fix "
            "this before expiry.\n\n"
            "Tom Wilson\nSenior Systems Administrator"
        ),
        ground_truth_priority="urgent",
        ground_truth_category="technical",
        ground_truth_department="engineering",
        expected_response_keywords=[
            "ssl", "certificate", "domain", "renewal", "dns",
            "urgent", "investigate", "fix", "team", "priority"
        ],
    ),
    Email(
        email_id="email_015",
        sender="happy.customer@email.com",
        sender_name="Rachel Adams",
        subject="Loving the new dashboard update!",
        body=(
            "Hey team!\n\n"
            "Just wanted to drop a note to say the new dashboard redesign is "
            "AMAZING! The analytics widgets are so much more intuitive now, and "
            "the export feature works like a dream.\n\n"
            "Our team has been raving about it. Keep up the great work!\n\n"
            "Cheers,\nRachel Adams"
        ),
        ground_truth_priority="low",
        ground_truth_category="support",
        ground_truth_department="customer_support",
        expected_response_keywords=[
            "thank", "feedback", "glad", "appreciate", "team",
            "happy", "great"
        ],
    ),
    # ── MOOD-BASED TRIAGE (Marketplace / Opportunities) ──────────────────────
    Email(
        email_id="email_016",
        sender="alerts@unstop.com",
        sender_name="Unstop Announcements",
        subject="New Coding Challenge - Win Goodies!",
        body=(
            "Hi there,\n\n"
            "Participate in the upcoming Weekend Hackathon on Unstop. "
            "Top 10 winners get exclusive company swag and certificates.\n\n"
            "Note: This is just a competition, not an active hiring or internship drive. "
            "Register now and challenge your peers!\n\n"
            "Best,\nUnstop Team"
        ),
        ground_truth_priority="low",
        ground_truth_category="spam",
        ground_truth_department="spam_filter",
        ground_truth_triage_action="reject",
    ),
    Email(
        email_id="email_017",
        sender="internships@internshala.com",
        sender_name="Internshala",
        subject="Software Engineering Internship at TechCorp",
        body=(
            "Hello Junior Developer,\n\n"
            "We have a matched internship opportunity for you! TechCorp is hiring "
            "3rd-year students for a 6-month Software Engineering Internship.\n\n"
            "Stipend: Rs. 30,000 / month\n"
            "Requirements: Python, React, APIs\n\n"
            "Apply via your Internshala dashboard today.\n\n"
            "Regards,\nInternshala"
        ),
        ground_truth_priority="high",
        ground_truth_category="sales",
        ground_truth_department="sales",
        ground_truth_triage_action="accept",
    ),
    Email(
        email_id="email_018",
        sender="bot@telegram.org",
        sender_name="Telegram Notifications",
        subject="You have 5 new messages in 'Crypto Job Alerts'",
        body=(
            "Hi,\n\n"
            "You have unread messages in the group 'Crypto Job Alerts'.\n"
            "Airdrop announced! Send 0.1 ETH to receive 1000 SHIB tokens. "
            "Click the link below to connect your wallet.\n\n"
            "Unsubscribe if you don't want these emails.\n"
            "Telegram Automations"
        ),
        ground_truth_priority="low",
        ground_truth_category="spam",
        ground_truth_department="spam_filter",
        ground_truth_triage_action="reject",
    ),
    Email(
        email_id="email_019",
        sender="jobs@tophire.co",
        sender_name="TopHire Recruiters",
        subject="Interview Request: Summer SDE Intern",
        body=(
            "Hello,\n\n"
            "Based on your resume, a hiring manager at Innovate.ai wants to "
            "interview you for the Summer SDE Intern position. This perfectly "
            "aligns with your goal as a 3rd-year university student looking for "
            "practical industry exposure.\n\n"
            "Please click 'Accept' to schedule the first round.\n\n"
            "Best,\nTopHire"
        ),
        ground_truth_priority="high",
        ground_truth_category="support",
        ground_truth_department="customer_support",
        ground_truth_triage_action="accept",
    ),
    Email(
        email_id="email_020",
        sender="newsletter@campus-digest.com",
        sender_name="Campus Digest",
        subject="10 Ways to Ace Your Exams",
        body=(
            "Read our latest blog post!\n\n"
            "As a 3rd year student, exams can be stressful. We've compiled "
            "a list of the best study techniques and productivity hacks.\n\n"
            "No jobs or internships here, just pure academic advice.\n\n"
            "Happy Reading,\nCampus Digest Team"
        ),
        ground_truth_priority="low",
        ground_truth_category="support",
        ground_truth_department="customer_support",
        ground_truth_triage_action="reject",
    ),
]


# ─────────────────────────────────────────────────────────────────────────────
# TASK CONFIGURATIONS
# ─────────────────────────────────────────────────────────────────────────────

# Emails assigned to each task type
TASK_EMAIL_IDS: Dict[str, List[str]] = {
    "classify_email": [
        "email_001", "email_002", "email_003", "email_004", "email_005",
    ],
    "draft_response": [
        "email_006", "email_007", "email_008", "email_009", "email_013",
    ],
    "full_triage": [
        "email_005", "email_011", "email_012", "email_014", "email_015",
    ],
    "mood_based_triage": [
        "email_016", "email_017", "email_018", "email_019", "email_020",
    ],
}

# Valid values for each field
VALID_PRIORITIES = {"low", "medium", "high", "urgent"}
VALID_CATEGORIES = {"support", "sales", "billing", "technical", "spam"}
VALID_DEPARTMENTS = {
    "customer_support", "sales", "billing", "engineering", "spam_filter"
}
VALID_TRIAGE_ACTIONS = {"accept", "reject"}


def get_email_by_id(email_id: str) -> Optional[Email]:
    """Look up an email by its ID."""
    for email in EMAILS:
        if email.email_id == email_id:
            return email
    return None


def get_task_emails(task_type: str) -> List[Email]:
    """Get the list of emails for a given task type."""
    email_ids = TASK_EMAIL_IDS.get(task_type, [])
    return [e for e in EMAILS if e.email_id in email_ids]


def get_available_tasks() -> List[str]:
    """Return list of available task names."""
    return list(TASK_EMAIL_IDS.keys())
