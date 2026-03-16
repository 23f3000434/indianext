"""
Trains and saves all ML models on first run.
Uses synthetic but realistic training data for each threat domain.
"""
import os
import numpy as np
import joblib

MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
URL_MODEL_PATH = os.path.join(MODELS_DIR, "url_model.joblib")
EMAIL_MODEL_PATH = os.path.join(MODELS_DIR, "email_model.joblib")
BEHAVIOR_MODEL_PATH = os.path.join(MODELS_DIR, "behavior_model.joblib")


def train_url_model():
    if os.path.exists(URL_MODEL_PATH):
        print("[SaveWaves] URL model already trained.")
        return
    print("[SaveWaves] Training URL model...")
    from sklearn.ensemble import RandomForestClassifier
    from ml.url_model import extract_features

    # Phishing URLs
    phishing_urls = [
        "http://paypal-secure-verify.com/login?user=", "http://192.168.1.1/bank/signin",
        "http://amazon-update.xyz/verify/account", "http://secure-login-apple.tk/update",
        "http://bit.ly/2xAbc1Z", "http://google-security-alert.ml/verify",
        "http://win-prize-now.top/claim?id=", "http://microsoftsupport.ga/renew",
        "http://banking-secure-portal.cf/login/update", "http://ebayaccount-verify.xyz/confirm",
        "http://office365-renew.top/signin?", "http://netflix-billing-update.click/pay",
        "http://secure-paypal-resolution.ml/case", "http://apple-id-locked.ga/unlock",
        "http://amazon-prime-renew.tk/account/billing", "http://gov-tax-refund.xyz/claim",
        "http://fb-account-verify.top/identity", "http://chase-bank-alert.ml/verify",
        "http://irs-refund-2024.ga/apply", "http://dhl-parcel-update.xyz/track",
        "http://wellsfargo-security-alert.ml/account/update",
        "http://royal.bank.secure-login.top/authenticate",
        "http://support-account-google.ml/signin?continue=",
        "http://verify-microsoft-account.xyz/Office365",
        "http://steam-trade-phishing.tk/confirm/item",
    ] * 8

    # Legitimate URLs
    legit_urls = [
        "https://www.google.com/search?q=python", "https://github.com/openai/openai-python",
        "https://stackoverflow.com/questions/12345", "https://docs.python.org/3/library/",
        "https://www.amazon.com/dp/B08N5WRWNW", "https://en.wikipedia.org/wiki/Machine_learning",
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "https://news.ycombinator.com/item?id=39271",
        "https://www.linkedin.com/in/johndoe", "https://medium.com/@author/article-title",
        "https://www.coursera.org/learn/machine-learning", "https://arxiv.org/abs/1706.03762",
        "https://pytorch.org/docs/stable/torch.html", "https://fastapi.tiangolo.com/tutorial/",
        "https://react.dev/learn/thinking-in-react", "https://tailwindcss.com/docs/installation",
        "https://vercel.com/dashboard", "https://render.com/docs/web-services",
        "https://railway.app/project/new", "https://www.notion.so/workspace",
        "https://app.slack.com/client/T123/C456", "https://mail.google.com/mail/u/0/",
        "https://calendar.google.com/calendar/r", "https://drive.google.com/drive/my-drive",
        "https://www.cloudflare.com/dns/", "https://stripe.com/docs/api",
    ] * 8

    urls = phishing_urls + legit_urls
    labels = [1] * len(phishing_urls) + [0] * len(legit_urls)

    X = np.array([extract_features(u) for u in urls])
    y = np.array(labels)

    model = RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42, n_jobs=-1)
    model.fit(X, y)

    os.makedirs(MODELS_DIR, exist_ok=True)
    joblib.dump(model, URL_MODEL_PATH)
    print(f"[SaveWaves] URL model trained and saved. Accuracy: {model.score(X, y):.3f}")


def train_email_model():
    if os.path.exists(EMAIL_MODEL_PATH):
        print("[SaveWaves] Email model already trained.")
        return
    print("[SaveWaves] Training email model...")
    from sklearn.pipeline import Pipeline
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.ensemble import GradientBoostingClassifier

    phishing_emails = [
        "Dear Customer, Your account has been suspended. Please verify your identity immediately by clicking the link below to avoid permanent closure.",
        "URGENT: Unusual sign-in activity detected on your PayPal account. Click here to secure your account now before it is permanently disabled.",
        "Congratulations! You have won a $1000 Amazon gift card. Click here to claim your prize. Limited time offer. Act now!",
        "Security Alert: Your Microsoft account password needs to be updated immediately. Verify your information to restore access.",
        "Important Notice: Your Apple ID has been locked due to suspicious activity. Please verify your account to regain access.",
        "Your bank account has been compromised. Please confirm your details immediately to prevent unauthorized transactions.",
        "Dear User, you have been selected as our weekly winner. Claim your prize of $5000 by clicking here and entering your details.",
        "FINAL WARNING: Your email account will be deactivated within 24 hours. Click here to verify and keep your account active.",
        "Your Netflix subscription could not be renewed. Update your billing information to continue watching your favorite shows.",
        "Tax Refund Notification: The IRS has issued a refund of $2,847.00 to your account. Click here to claim your refund immediately.",
        "Hello, I am Prince Adeyemi from Nigeria. I need your help to transfer $15 million USD. You will receive 30% commission.",
        "ALERT: Your DHL package could not be delivered. Pay the $2.50 customs fee urgently to reschedule delivery.",
        "Your Google account will be suspended. Immediate action required. Click here to verify your email address and password.",
        "HR NOTICE: Please review and update your direct deposit information for this month's payroll by clicking the secure link.",
        "Pharmacy: Buy medication online without prescription. 90% discount on all pills. Click here for special offer today only.",
        "Verify your account now! We noticed you signed in from a new device. Confirm your identity or your account will be locked.",
        "You have an unclaimed package waiting. Please confirm your address and pay the $3 delivery fee to receive it.",
        "WARNING: Your credit card has been charged $499.99 for a subscription you did not authorize. Click here to cancel and refund.",
        "You have been chosen for our customer satisfaction survey. Complete it now and win prizes worth $500.",
        "Dear valued customer, your account security is at risk. Kindly verify your personal details to continue using our services.",
    ] * 10

    legit_emails = [
        "Hi Team, please find attached the meeting agenda for tomorrow's standup. We will discuss Q2 roadmap and sprint velocity.",
        "Thanks for your pull request. I have reviewed the code changes and left some comments. Please address them before we merge.",
        "Our quarterly business review is scheduled for Friday at 2 PM. Please bring your department's performance metrics.",
        "Hi John, I am following up on our discussion about the new feature implementation. The backend changes are ready for review.",
        "Please find attached the invoice for last month's services. Total amount due: $1,200. Payment is due within 30 days.",
        "The deployment to production is scheduled for tonight at 11 PM. All team members should be on standby for rollback if needed.",
        "Good morning, here is your daily briefing. Stock markets opened higher today. Key events: Fed meeting at 2 PM ET.",
        "Your order has been shipped. Tracking number: 1Z999AA10123456784. Estimated delivery: Thursday, March 21.",
        "Thank you for registering for our conference. Your ticket has been confirmed. Please bring this email to the event.",
        "Hi there, I wanted to share this research paper on transformer architectures that I found really insightful.",
        "The project kickoff meeting has been rescheduled to next Monday at 10 AM. Please update your calendars accordingly.",
        "Reminder: Your dentist appointment is on March 20 at 3:30 PM. Please call to reschedule if needed.",
        "Your library books are due for return on March 25. You can renew them online through your library account.",
        "Company All-Hands Meeting: Join us this Friday at 4 PM for updates on our annual performance and future plans.",
        "Hi, could you please review the attached design mockups for the new dashboard and share your feedback by end of day?",
        "The server maintenance window is scheduled for Sunday 2-4 AM. Services may be temporarily unavailable during this time.",
        "Team lunch is confirmed for Thursday at 12:30 PM at the Italian restaurant down the street. RSVP by Wednesday.",
        "Your flight booking is confirmed. Flight AI302 on March 22, departing at 6:45 AM. Check-in opens 24 hours before.",
        "Great job on the presentation today! The client was very impressed with our proposal and wants to move forward.",
        "I wanted to connect with you regarding the open senior engineer position at our company. Your profile looks impressive.",
    ] * 10

    texts = phishing_emails + legit_emails
    labels = [1] * len(phishing_emails) + [0] * len(legit_emails)

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(max_features=3000, ngram_range=(1, 2), stop_words="english", sublinear_tf=True)),
        ("clf", GradientBoostingClassifier(n_estimators=100, max_depth=4, random_state=42)),
    ])
    pipeline.fit(texts, labels)

    os.makedirs(MODELS_DIR, exist_ok=True)
    joblib.dump(pipeline, EMAIL_MODEL_PATH)
    print(f"[SaveWaves] Email model trained and saved. Accuracy: {pipeline.score(texts, labels):.3f}")


def train_behavior_model():
    if os.path.exists(BEHAVIOR_MODEL_PATH):
        print("[SaveWaves] Behavior model already trained.")
        return
    print("[SaveWaves] Training behavior model...")
    from sklearn.ensemble import IsolationForest
    import numpy as np

    rng = np.random.RandomState(42)

    # Normal behavior: login 8-18h, 0-1 failed, no location change, no device change,
    # 0-2 sensitive accesses, 5-30 req/min, 30-120 min session, no off hours
    n_normal = 800
    normal = np.column_stack([
        rng.randint(8, 18, n_normal),          # login_hour
        rng.choice([0, 0, 0, 1], n_normal),    # failed_attempts
        rng.choice([0, 0, 0, 0, 1], n_normal), # location_change
        rng.choice([0, 0, 0, 0, 1], n_normal), # device_change
        rng.randint(0, 3, n_normal),            # sensitive_access_count
        rng.uniform(5, 30, n_normal),           # requests_per_minute
        rng.uniform(20, 120, n_normal),         # session_duration_min
        np.zeros(n_normal),                     # off_hours_activity
    ])

    # Anomalous behavior: weird hours, many failed, new location, high access rate
    n_anomaly = 200
    anomaly = np.column_stack([
        rng.choice([1, 2, 3, 23, 0], n_anomaly),   # login_hour (off hours)
        rng.randint(3, 15, n_anomaly),               # failed_attempts
        rng.choice([1, 1, 0], n_anomaly),            # location_change
        rng.choice([1, 1, 0], n_anomaly),            # device_change
        rng.randint(5, 30, n_anomaly),               # sensitive_access_count
        rng.uniform(80, 300, n_anomaly),             # requests_per_minute
        rng.uniform(1, 10, n_anomaly),               # session_duration_min
        np.ones(n_anomaly),                          # off_hours_activity
    ])

    X_train = np.vstack([normal, anomaly]).astype(float)

    model = IsolationForest(
        n_estimators=100,
        contamination=0.2,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train)

    os.makedirs(MODELS_DIR, exist_ok=True)
    joblib.dump(model, BEHAVIOR_MODEL_PATH)
    print("[SaveWaves] Behavior model trained and saved.")


def train_all_models():
    os.makedirs(MODELS_DIR, exist_ok=True)
    train_url_model()
    train_email_model()
    train_behavior_model()
    print("[SaveWaves] All models ready.")
