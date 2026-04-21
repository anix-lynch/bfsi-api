"""Synthetic BFSI dataset generator.

Generates deterministic Faker data across five domains — retail banking,
commercial lending, wealth management, insurance claims, and compliance —
into a single SQLite file plus a docs/ folder of long-form text blobs.

All PII-shaped fields use a `__synthetic__` prefix to make it explicit
that no real data is used. Run:

    python data/generate.py
"""
from __future__ import annotations

import json
import random
import sqlite3
from datetime import date, datetime, timedelta
from pathlib import Path

from faker import Faker

SEED = 42
fake = Faker()
Faker.seed(SEED)
random.seed(SEED)

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "bfsi.db"
DOCS_DIR = ROOT / "docs"
DOCS_DIR.mkdir(exist_ok=True)

SCHEMA = """
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS tickets;
DROP TABLE IF EXISTS loans;
DROP TABLE IF EXISTS credit_memos;
DROP TABLE IF EXISTS covenants;
DROP TABLE IF EXISTS advisors;
DROP TABLE IF EXISTS wealth_clients;
DROP TABLE IF EXISTS advisor_notes;
DROP TABLE IF EXISTS kyc_flags;
DROP TABLE IF EXISTS claims;
DROP TABLE IF EXISTS claim_narratives;
DROP TABLE IF EXISTS fraud_indicators;
DROP TABLE IF EXISTS reg_docs;
DROP TABLE IF EXISTS policies;

CREATE TABLE customers (
    id INTEGER PRIMARY KEY,
    __synthetic__name TEXT,
    __synthetic__ssn_like TEXT,
    __synthetic__dob TEXT,
    __synthetic__address TEXT,
    __synthetic__email TEXT,
    segment TEXT,
    tenure_years INTEGER
);

CREATE TABLE transactions (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER,
    txn_date TEXT,
    merchant TEXT,
    amount REAL,
    category TEXT,
    flag TEXT,
    FOREIGN KEY(customer_id) REFERENCES customers(id)
);

CREATE TABLE tickets (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER,
    created_at TEXT,
    channel TEXT,
    subject TEXT,
    body TEXT,
    status TEXT,
    FOREIGN KEY(customer_id) REFERENCES customers(id)
);

CREATE TABLE loans (
    id INTEGER PRIMARY KEY,
    borrower TEXT,
    industry TEXT,
    amount_requested REAL,
    status TEXT,
    submitted_at TEXT,
    application_text TEXT
);

CREATE TABLE credit_memos (
    id INTEGER PRIMARY KEY,
    loan_id INTEGER,
    analyst TEXT,
    memo_text TEXT,
    recommendation TEXT,
    FOREIGN KEY(loan_id) REFERENCES loans(id)
);

CREATE TABLE covenants (
    id INTEGER PRIMARY KEY,
    loan_id INTEGER,
    covenant_type TEXT,
    threshold REAL,
    current_value REAL,
    status TEXT,
    notes TEXT,
    FOREIGN KEY(loan_id) REFERENCES loans(id)
);

CREATE TABLE wealth_clients (
    id INTEGER PRIMARY KEY,
    __synthetic__name TEXT,
    risk_tolerance TEXT,
    aum_usd REAL,
    advisor_id INTEGER,
    holdings_json TEXT
);

CREATE TABLE advisors (
    id INTEGER PRIMARY KEY,
    __synthetic__name TEXT,
    region TEXT,
    book_size INTEGER
);

CREATE TABLE advisor_notes (
    id INTEGER PRIMARY KEY,
    wealth_client_id INTEGER,
    advisor_id INTEGER,
    meeting_date TEXT,
    note_text TEXT,
    FOREIGN KEY(wealth_client_id) REFERENCES wealth_clients(id),
    FOREIGN KEY(advisor_id) REFERENCES advisors(id)
);

CREATE TABLE kyc_flags (
    id INTEGER PRIMARY KEY,
    wealth_client_id INTEGER,
    flag_type TEXT,
    severity TEXT,
    notes TEXT,
    raised_at TEXT,
    FOREIGN KEY(wealth_client_id) REFERENCES wealth_clients(id)
);

CREATE TABLE claims (
    id INTEGER PRIMARY KEY,
    policy_number TEXT,
    claimant TEXT,
    product TEXT,
    incident_date TEXT,
    filed_date TEXT,
    amount REAL,
    status TEXT
);

CREATE TABLE claim_narratives (
    id INTEGER PRIMARY KEY,
    claim_id INTEGER,
    narrative TEXT,
    author_role TEXT,
    FOREIGN KEY(claim_id) REFERENCES claims(id)
);

CREATE TABLE fraud_indicators (
    id INTEGER PRIMARY KEY,
    claim_id INTEGER,
    indicator TEXT,
    score REAL,
    notes TEXT,
    FOREIGN KEY(claim_id) REFERENCES claims(id)
);

CREATE TABLE reg_docs (
    id INTEGER PRIMARY KEY,
    doc_type TEXT,
    title TEXT,
    issued_date TEXT,
    body TEXT
);

CREATE TABLE policies (
    id INTEGER PRIMARY KEY,
    policy_area TEXT,
    title TEXT,
    snippet TEXT
);
"""


SEGMENTS = ["Mass Market", "Mass Affluent", "Private Client", "Small Business"]
TXN_CATEGORIES = ["Groceries", "Dining", "Travel", "Utilities", "Transfer", "Payroll", "Subscription", "ATM", "Cash Advance", "Wire"]
TXN_FLAGS = ["ok", "ok", "ok", "ok", "ok", "disputed", "pending_review", "cleared"]
TICKET_CHANNELS = ["phone", "chat", "email", "branch"]
TICKET_STATUS = ["open", "in_progress", "escalated", "resolved"]
INDUSTRIES = ["Manufacturing", "Healthcare", "CRE Office", "CRE Retail", "Logistics", "Tech Services", "Hospitality", "Energy"]
INSURANCE_PRODUCTS = ["Auto", "Homeowners", "Commercial Property", "Workers Comp", "General Liability"]
CLAIM_STATUS = ["received", "under_review", "approved", "denied", "paid", "escalated"]
KYC_FLAG_TYPES = ["PEP match", "Sanctions screening hit", "Unusual source of funds", "Cash-intensive activity", "Jurisdiction risk"]


TICKET_SUBJECT_TEMPLATES = [
    "cant log in to mbl app",
    "charge i dont recognize {amt}",
    "wire stuck",
    "why is my debit card declined?",
    "need to dispute a charge",
    "pls reset my online banking pwd",
    "how do i order checks",
    "mortage pmt didnt go thru",
    "acct frozen???",
    "bill pay not showing",
]

TICKET_BODY_TEMPLATES = [
    "tried 3x, keeps saying 'invalid credentials' but i KNOW my pwd. pls help asap, i need to send rent.",
    "saw a charge from {merchant} on {date} for ${amt}. never been there. fraud??",
    "sent wire yesterday to vendor, status still 'initiated'. getting yelled at.",
    "card declined at grocery store, embarrassing. did u guys block it? nothing weird on my end.",
    "txn from last tues looks wrong amt. i paid $45 not $145. fix plz",
    "new phone, lost authenticator, now cant get in. been 2 days",
    "need to close joint acct, spouse passed away last month. what do i need to bring in",
    "why did u charge overdraft fee when deposit was pending same day???",
    "zelle showing sent but recipient says nothing recvd. 3 hrs now",
    "my business acct got flagged for review. we just had a big customer pmt come in, nothing shady",
]


def gen_customers(cur, n=500):
    rows = []
    for i in range(1, n + 1):
        rows.append((
            i,
            fake.name(),
            f"XXX-XX-{fake.random_int(1000, 9999)}",
            fake.date_of_birth(minimum_age=21, maximum_age=82).isoformat(),
            fake.address().replace("\n", ", "),
            fake.email(),
            random.choice(SEGMENTS),
            random.randint(0, 30),
        ))
    cur.executemany(
        "INSERT INTO customers VALUES (?,?,?,?,?,?,?,?)", rows
    )


def gen_transactions(cur, n=2000, customer_count=500):
    rows = []
    for i in range(1, n + 1):
        cid = random.randint(1, customer_count)
        d = fake.date_between(start_date="-90d", end_date="today").isoformat()
        merchant = fake.company()
        amt = round(random.uniform(2.5, 2500.0), 2)
        rows.append((i, cid, d, merchant, amt, random.choice(TXN_CATEGORIES), random.choice(TXN_FLAGS)))
    cur.executemany("INSERT INTO transactions VALUES (?,?,?,?,?,?,?)", rows)


def gen_tickets(cur, n=100, customer_count=500):
    rows = []
    for i in range(1, n + 1):
        cid = random.randint(1, customer_count)
        d = fake.date_time_between(start_date="-60d", end_date="now").isoformat()
        subj = random.choice(TICKET_SUBJECT_TEMPLATES).format(amt=round(random.uniform(5, 800), 2))
        body = random.choice(TICKET_BODY_TEMPLATES).format(
            merchant=fake.company(),
            date=fake.date_between(start_date="-30d", end_date="today").isoformat(),
            amt=round(random.uniform(10, 600), 2),
        )
        rows.append((i, cid, d, random.choice(TICKET_CHANNELS), subj, body, random.choice(TICKET_STATUS)))
    cur.executemany("INSERT INTO tickets VALUES (?,?,?,?,?,?,?)", rows)


def gen_loans_and_memos(cur, n=50):
    loans = []
    memos = []
    covenants = []
    for i in range(1, n + 1):
        borrower = fake.company()
        industry = random.choice(INDUSTRIES)
        amt = round(random.uniform(250_000, 25_000_000), -3)
        submitted = fake.date_between(start_date="-365d", end_date="-10d").isoformat()
        app_text = (
            f"Loan application for {borrower}, a {industry.lower()} business. "
            f"Requested amount: ${amt:,.0f}. Purpose: expansion of operations, "
            f"working capital, and equipment acquisition. Revenue last fiscal year: "
            f"${random.randint(5, 120)}M. EBITDA margin approximately "
            f"{random.randint(4, 28)}%. Primary collateral includes real estate "
            f"and equipment. The borrower has been a customer for "
            f"{random.randint(1, 18)} years. Reference customers and audited "
            f"financials attached. Applicant proposes a "
            f"{random.choice(['5-year','7-year','10-year'])} term with "
            f"{random.choice(['monthly','quarterly'])} amortization."
        )
        status = random.choice(["submitted", "in_underwriting", "approved", "declined", "funded"])
        loans.append((i, borrower, industry, amt, status, submitted, app_text))

        memos.append((
            i, i, fake.name(),
            (
                f"CREDIT MEMO — {borrower}\n\n"
                f"Background: {borrower} operates in {industry}. The relationship "
                f"spans multiple product lines. Historical performance has been "
                f"{'stable' if random.random() > 0.3 else 'uneven'} over the last three years.\n\n"
                f"Financial profile: leverage ratio of {random.uniform(1.2, 5.8):.1f}x, "
                f"interest coverage of {random.uniform(1.4, 9.2):.1f}x, current ratio "
                f"{random.uniform(0.9, 2.4):.1f}. Free cash flow is "
                f"{'positive and growing' if random.random() > 0.4 else 'compressed YoY'}.\n\n"
                f"Industry notes: {industry} is currently "
                f"{'expanding' if random.random() > 0.5 else 'facing cyclical pressure'}. "
                f"Key risks: supply chain, rate sensitivity, customer concentration.\n\n"
                f"Collateral: real estate appraised at ${random.randint(2,40)}M, "
                f"equipment ${random.randint(1,15)}M. Advance rate proposed "
                f"{random.choice([65, 70, 75, 80])}%.\n\n"
                f"Recommendation: {random.choice(['APPROVE with standard covenants','APPROVE with tightened reporting','DECLINE pending updated financials','APPROVE conditional on guarantor'])}."
            ),
            random.choice(["approve", "approve_conditional", "decline", "defer"]),
        ))

        for _ in range(random.randint(1, 3)):
            ctype = random.choice(["DSCR", "Max Leverage", "Min Liquidity", "EBITDA floor"])
            thr = round(random.uniform(1.0, 5.0), 2)
            cur_val = round(thr + random.uniform(-1.2, 1.5), 2)
            cstatus = "compliant" if cur_val >= thr else "breach"
            covenants.append((None, i, ctype, thr, cur_val, cstatus, fake.sentence(nb_words=12)))

    cur.executemany("INSERT INTO loans VALUES (?,?,?,?,?,?,?)", loans)
    cur.executemany("INSERT INTO credit_memos VALUES (?,?,?,?,?)", memos)
    cur.executemany("INSERT INTO covenants VALUES (?,?,?,?,?,?,?)", covenants)


def gen_wealth(cur, n_clients=100, n_advisors=12, n_notes=200, n_flags=50):
    advisors = [(i, fake.name(), random.choice(["Northeast","Midwest","Southeast","West","Southwest"]),
                 random.randint(25, 120)) for i in range(1, n_advisors + 1)]
    cur.executemany("INSERT INTO advisors VALUES (?,?,?,?)", advisors)

    clients = []
    for i in range(1, n_clients + 1):
        holdings = {
            "equities_pct": random.randint(20, 80),
            "fixed_income_pct": random.randint(5, 50),
            "alt_pct": random.randint(0, 25),
            "cash_pct": random.randint(1, 20),
        }
        clients.append((
            i, fake.name(),
            random.choice(["conservative","moderate","growth","aggressive"]),
            round(random.uniform(250_000, 75_000_000), -3),
            random.randint(1, n_advisors),
            json.dumps(holdings),
        ))
    cur.executemany("INSERT INTO wealth_clients VALUES (?,?,?,?,?,?)", clients)

    notes = []
    topics = [
        "Client is nervous about rate cuts and wants to increase duration. "
        "Mentioned concern re: ageing parent care costs. Wants to revisit in 6wks.",
        "Reviewed 529 plan for grandkids. Wants to explore muni bond ladder. "
        "Spouse joining next meeting. Follow up with trust officer.",
        "Liquidity event from recent private equity distribution — roughly $2.4M "
        "expected next quarter. Client wants diversification plan pre-receipt.",
        "Upset about underperformance vs peer benchmark YTD. Requested side-by-side "
        "attribution analysis. Temperature: cooling.",
        "Discussed estate planning refresh. New grandchild, wants to add beneficiary. "
        "Referred to estate attorney on our preferred list.",
        "Client retiring in 9 months. Wants Monte Carlo for 30-yr horizon, spending "
        "scenarios at $180k, $220k, $260k annual draw.",
    ]
    for i in range(1, n_notes + 1):
        cid = random.randint(1, n_clients)
        aid = random.randint(1, n_advisors)
        mdate = fake.date_between(start_date="-180d", end_date="today").isoformat()
        notes.append((i, cid, aid, mdate, random.choice(topics)))
    cur.executemany("INSERT INTO advisor_notes VALUES (?,?,?,?,?)", notes)

    flags = []
    for i in range(1, n_flags + 1):
        flags.append((
            i, random.randint(1, n_clients),
            random.choice(KYC_FLAG_TYPES),
            random.choice(["low","medium","high"]),
            fake.sentence(nb_words=18),
            fake.date_between(start_date="-365d", end_date="today").isoformat(),
        ))
    cur.executemany("INSERT INTO kyc_flags VALUES (?,?,?,?,?,?)", flags)


def gen_claims(cur, n=300, n_narr=100, n_fraud=50):
    claims = []
    for i in range(1, n + 1):
        incident = fake.date_between(start_date="-2y", end_date="-10d")
        filed = incident + timedelta(days=random.randint(1, 45))
        claims.append((
            i,
            f"POL-{fake.random_int(100000, 999999)}",
            fake.name(),
            random.choice(INSURANCE_PRODUCTS),
            incident.isoformat(),
            filed.isoformat(),
            round(random.uniform(500, 180_000), 2),
            random.choice(CLAIM_STATUS),
        ))
    cur.executemany("INSERT INTO claims VALUES (?,?,?,?,?,?,?,?)", claims)

    narrative_templates = [
        "Insured reports rear-end collision at intersection. No injuries reported at scene. "
        "Other driver cited. Vehicle towed. Damage estimate pending adjuster review. "
        "Insured seemed cooperative; police report filed.",
        "Water damage to basement following heavy rainfall. Sump pump reportedly failed. "
        "Insured has receipts for recent HVAC work but no sump pump maintenance record. "
        "Mitigation company on scene within 18 hours. Requesting coverage under dwelling.",
        "Theft claim — insured states laptop and jewelry taken from vehicle overnight. "
        "Parked on street. Window broken. Police report filed but no suspects. "
        "Inventory list submitted but receipts only for ~40% of items. Further docs requested.",
        "Workers comp — employee slipped on warehouse floor. Spill reportedly unmarked. "
        "Employee taken to urgent care, soft tissue injury. Incident report filed same day. "
        "Safety officer interviewed. Training records requested.",
        "Roof damage following hailstorm 3 weeks ago. Insured noticed leaks after subsequent "
        "rain. Local contractor provided estimate of $28k. Adjuster photos scheduled. "
        "Neighborhood has multiple claims from same storm event.",
    ]
    narratives = []
    for i in range(1, n_narr + 1):
        narratives.append((
            i, random.randint(1, n),
            random.choice(narrative_templates),
            random.choice(["adjuster","SIU","intake_agent","field_inspector"]),
        ))
    cur.executemany("INSERT INTO claim_narratives VALUES (?,?,?,?)", narratives)

    fraud = []
    indicators = [
        "Claim filed shortly after policy binding",
        "Inventory values inconsistent with receipts",
        "Prior claims within 24 months",
        "Geographic clustering of similar claims",
        "Estimator relationship flagged in prior cases",
        "Narrative inconsistencies across statements",
    ]
    for i in range(1, n_fraud + 1):
        fraud.append((
            i, random.randint(1, n),
            random.choice(indicators),
            round(random.uniform(0.1, 0.95), 2),
            fake.sentence(nb_words=20),
        ))
    cur.executemany("INSERT INTO fraud_indicators VALUES (?,?,?,?,?)", fraud)


def gen_reg_docs(cur, n_docs=20, n_policies=100):
    doc_types = ["Supervisory Letter", "Guidance Bulletin", "Regulatory Advisory", "Examination Bulletin"]
    titles = [
        "Third-Party Risk Management Expectations",
        "Model Risk Management — AI/ML Applications",
        "Operational Resilience and Critical Service Dependencies",
        "Consumer Complaint Response Time Standards",
        "Sanctions Screening Program Requirements",
        "Customer Identification Program — Updated Guidance",
        "Interest Rate Risk in the Banking Book",
        "Liquidity Stress Testing Expectations",
        "Fair Lending — Algorithmic Decisioning",
        "Cybersecurity Incident Notification",
    ]
    docs = []
    for i in range(1, n_docs + 1):
        title = titles[(i - 1) % len(titles)] + (" (Addendum)" if i > len(titles) else "")
        body = (
            f"PURPOSE\nThis document communicates supervisory expectations for "
            f"{title.lower()}. Institutions are expected to adopt and maintain "
            f"sound risk management practices consistent with the principles "
            f"articulated herein.\n\n"
            f"SCOPE\nAll federally regulated institutions engaged in activities "
            f"within the subject area. Branches, subsidiaries, and affiliated "
            f"entities are expected to operate under an enterprise-wide framework.\n\n"
            f"EXPECTATIONS\n1. Governance and Oversight — the board and senior "
            f"management should ensure clear accountability, periodic reporting, "
            f"and independent challenge.\n"
            f"2. Risk Assessment — institutions should perform documented "
            f"assessments at least annually, with ad hoc refreshes for material "
            f"changes.\n"
            f"3. Controls and Monitoring — risk-tiered controls, commensurate "
            f"with the complexity and materiality of activities, should be "
            f"implemented and periodically tested.\n"
            f"4. Reporting — examiners expect timely escalation of material "
            f"incidents, control breakdowns, and emerging risk themes.\n\n"
            f"EXAMINATION APPROACH\nExaminers will evaluate the design and "
            f"operating effectiveness of programs described above. Supporting "
            f"documentation, evidence of independent review, and remediation "
            f"tracking will be reviewed. Institutions should be prepared to "
            f"demonstrate how identified weaknesses have been addressed."
        )
        docs.append((
            i,
            random.choice(doc_types),
            title,
            fake.date_between(start_date="-4y", end_date="-30d").isoformat(),
            body,
        ))
    cur.executemany("INSERT INTO reg_docs VALUES (?,?,?,?,?)", docs)

    areas = ["BSA/AML", "Privacy", "Fair Lending", "Information Security", "Consumer Protection", "Model Risk", "Third-Party Risk"]
    policies = []
    for i in range(1, n_policies + 1):
        area = random.choice(areas)
        policies.append((
            i, area,
            f"{area} Policy — Section {random.randint(1, 30)}.{random.randint(1, 15)}",
            (
                f"Employees and contractors acting on behalf of the institution "
                f"must comply with {area}-related requirements as described in "
                f"this section. Specific obligations include timely reporting of "
                f"suspected violations, completion of required training, and "
                f"adherence to the approved control framework. Exceptions require "
                f"documented approval from the {random.choice(['Chief Risk Officer','Chief Compliance Officer','General Counsel'])}."
            ),
        ))
    cur.executemany("INSERT INTO policies VALUES (?,?,?,?)", policies)


def write_doc_corpus(conn):
    """Export long-form text (credit memos, reg docs, claim narratives) as
    flat files under data/docs/ for ingestion by the RAG pipeline."""
    cur = conn.cursor()
    for loan_id, memo in cur.execute("SELECT loan_id, memo_text FROM credit_memos"):
        (DOCS_DIR / f"credit_memo_{loan_id:03d}.txt").write_text(memo)
    for rid, title, body in cur.execute("SELECT id, title, body FROM reg_docs"):
        safe = "".join(c if c.isalnum() or c in "_- " else "_" for c in title)[:40].replace(" ", "_")
        (DOCS_DIR / f"reg_{rid:02d}_{safe}.txt").write_text(f"{title}\n\n{body}")
    for cid, narr in cur.execute("SELECT claim_id, narrative FROM claim_narratives"):
        (DOCS_DIR / f"claim_{cid:03d}.txt").write_text(narr)


def main():
    if DB_PATH.exists():
        DB_PATH.unlink()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.executescript(SCHEMA)

    gen_customers(cur)
    gen_transactions(cur)
    gen_tickets(cur)
    gen_loans_and_memos(cur)
    gen_wealth(cur)
    gen_claims(cur)
    gen_reg_docs(cur)

    conn.commit()
    write_doc_corpus(conn)
    conn.close()

    print(f"[OK] wrote {DB_PATH}")
    print(f"[OK] wrote {len(list(DOCS_DIR.glob('*.txt')))} docs to {DOCS_DIR}")


if __name__ == "__main__":
    main()
