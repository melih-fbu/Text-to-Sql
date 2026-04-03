"""Demo database setup with sample sales data in SQLite."""

import sqlite3
import random
from datetime import datetime, timedelta
import os


COMPANIES = [
    "Acme Corp", "TechVision Inc", "Global Solutions", "DataFlow Ltd",
    "CloudPeak Systems", "NexGen Analytics", "Innovate AI", "PrimeStack",
    "BlueSky Ventures", "CoreLogic Tech", "SmartBridge Co", "Quantum Dynamics",
    "Apex Digital", "FusionWorks", "CyberNest", "MetaScale",
    "DeepRoot Labs", "SwiftCloud", "BrightNode", "OmniTech Solutions",
    "SilverLine Partners", "Horizon Data", "Pulse Analytics", "Zenith Corp",
    "Atlas Enterprises", "Vertex Systems", "Momentum Labs", "Catalyst Group",
    "Synergy Digital", "Titan Software"
]

REPS = [
    "Ahmet Yılmaz", "Elif Kaya", "Mehmet Demir", "Zeynep Çelik",
    "Can Özkan", "Ayşe Arslan", "Burak Şahin", "Deniz Koç",
    "Selin Yıldız", "Emre Aydın"
]

STAGES = ["Prospecting", "Qualification", "Proposal", "Negotiation", "Closed Won", "Closed Lost"]
PRODUCTS = ["Enterprise Suite", "Analytics Pro", "Data Platform", "AI Assistant", "Cloud Storage"]
DEAL_SOURCES = ["Inbound", "Outbound", "Referral", "Partner", "Event"]
ACTIVITY_TYPES = ["Email", "Call", "Meeting", "Demo", "Proposal Sent", "Follow-up"]
DEPARTMENTS = ["Sales", "Marketing", "Engineering", "Product", "Finance", "HR", "Operations"]
REGIONS = ["Türkiye", "EMEA", "North America", "APAC"]


def create_demo_database(db_path: str):
    """Create a SQLite database with realistic sample sales data."""
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # ─── Create Tables ───
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS deals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT NOT NULL,
            deal_name TEXT NOT NULL,
            amount REAL NOT NULL,
            stage TEXT NOT NULL,
            rep_name TEXT NOT NULL,
            product TEXT NOT NULL,
            source TEXT NOT NULL,
            region TEXT NOT NULL,
            probability INTEGER DEFAULT 0,
            close_date TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            deal_id INTEGER NOT NULL,
            activity_type TEXT NOT NULL,
            description TEXT,
            rep_name TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (deal_id) REFERENCES deals(id)
        );

        CREATE TABLE IF NOT EXISTS revenue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            product TEXT NOT NULL,
            region TEXT NOT NULL,
            quarter TEXT NOT NULL,
            year INTEGER NOT NULL,
            month INTEGER NOT NULL,
            booked_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT NOT NULL,
            industry TEXT NOT NULL,
            employee_count INTEGER,
            annual_revenue REAL,
            region TEXT NOT NULL,
            account_manager TEXT NOT NULL,
            contract_value REAL,
            contract_start TEXT,
            contract_end TEXT,
            health_score INTEGER DEFAULT 80,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS team_performance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rep_name TEXT NOT NULL,
            department TEXT NOT NULL,
            deals_closed INTEGER DEFAULT 0,
            revenue_generated REAL DEFAULT 0,
            quota REAL NOT NULL,
            quota_attainment REAL DEFAULT 0,
            avg_deal_size REAL DEFAULT 0,
            avg_sales_cycle_days INTEGER DEFAULT 0,
            quarter TEXT NOT NULL,
            year INTEGER NOT NULL
        );
    """)

    # ─── Insert Deals ───
    deals = []
    now = datetime(2026, 3, 31)
    for i in range(200):
        company = random.choice(COMPANIES)
        product = random.choice(PRODUCTS)
        stage = random.choice(STAGES)
        probability = {
            "Prospecting": 10, "Qualification": 25, "Proposal": 50,
            "Negotiation": 75, "Closed Won": 100, "Closed Lost": 0
        }[stage]
        amount = round(random.uniform(5000, 500000), 2)
        days_ago = random.randint(0, 365)
        created = now - timedelta(days=days_ago)
        close_offset = random.randint(14, 120)
        close_date = created + timedelta(days=close_offset)

        deals.append((
            company,
            f"{company} - {product}",
            amount,
            stage,
            random.choice(REPS),
            product,
            random.choice(DEAL_SOURCES),
            random.choice(REGIONS),
            probability,
            close_date.strftime("%Y-%m-%d"),
            created.strftime("%Y-%m-%d %H:%M:%S"),
            (created + timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d %H:%M:%S"),
        ))

    cursor.executemany("""
        INSERT INTO deals (company_name, deal_name, amount, stage, rep_name, product, source, region, probability, close_date, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, deals)

    # ─── Insert Activities ───
    activities = []
    for deal_id in range(1, 201):
        num_activities = random.randint(1, 8)
        for _ in range(num_activities):
            act_type = random.choice(ACTIVITY_TYPES)
            days_ago = random.randint(0, 180)
            created = now - timedelta(days=days_ago)
            activities.append((
                deal_id,
                act_type,
                f"{act_type} with {random.choice(COMPANIES)}",
                random.choice(REPS),
                created.strftime("%Y-%m-%d %H:%M:%S"),
            ))

    cursor.executemany("""
        INSERT INTO activities (deal_id, activity_type, description, rep_name, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, activities)

    # ─── Insert Revenue ───
    revenue = []
    for year in [2024, 2025, 2026]:
        for quarter_num in range(1, 5):
            if year == 2026 and quarter_num > 1:
                continue
            quarter = f"Q{quarter_num}"
            for month_offset in range(3):
                month = (quarter_num - 1) * 3 + month_offset + 1
                for _ in range(random.randint(5, 15)):
                    amount = round(random.uniform(10000, 200000), 2)
                    day = random.randint(1, 28)
                    booked = datetime(year, month, day)
                    revenue.append((
                        amount,
                        random.choice(PRODUCTS),
                        random.choice(REGIONS),
                        quarter,
                        year,
                        month,
                        booked.strftime("%Y-%m-%d"),
                    ))

    cursor.executemany("""
        INSERT INTO revenue (amount, product, region, quarter, year, month, booked_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, revenue)

    # ─── Insert Customers ───
    industries = ["Technology", "Finance", "Healthcare", "Retail", "Manufacturing", "Education"]
    customers = []
    for i, company in enumerate(COMPANIES):
        contract_start = now - timedelta(days=random.randint(30, 730))
        contract_end = contract_start + timedelta(days=365)
        customers.append((
            company,
            random.choice(industries),
            random.randint(50, 10000),
            round(random.uniform(1000000, 500000000), 2),
            random.choice(REGIONS),
            random.choice(REPS),
            round(random.uniform(20000, 500000), 2),
            contract_start.strftime("%Y-%m-%d"),
            contract_end.strftime("%Y-%m-%d"),
            random.randint(40, 100),
            (now - timedelta(days=random.randint(60, 730))).strftime("%Y-%m-%d %H:%M:%S"),
        ))

    cursor.executemany("""
        INSERT INTO customers (company_name, industry, employee_count, annual_revenue, region, account_manager, contract_value, contract_start, contract_end, health_score, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, customers)

    # ─── Insert Team Performance ───
    perf = []
    for rep in REPS:
        for year in [2025, 2026]:
            for q in range(1, 5):
                if year == 2026 and q > 1:
                    continue
                quota = round(random.uniform(200000, 800000), 2)
                rev = round(random.uniform(quota * 0.4, quota * 1.3), 2)
                closed = random.randint(3, 20)
                perf.append((
                    rep,
                    "Sales",
                    closed,
                    rev,
                    quota,
                    round(rev / quota * 100, 1),
                    round(rev / max(closed, 1), 2),
                    random.randint(15, 60),
                    f"Q{q}",
                    year,
                ))

    cursor.executemany("""
        INSERT INTO team_performance (rep_name, department, deals_closed, revenue_generated, quota, quota_attainment, avg_deal_size, avg_sales_cycle_days, quarter, year)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, perf)

    conn.commit()
    conn.close()
    print(f"✅ Demo database created at {db_path}")
    print(f"   - 200 deals")
    print(f"   - {len(activities)} activities")
    print(f"   - {len(revenue)} revenue records")
    print(f"   - {len(customers)} customers")
    print(f"   - {len(perf)} team performance records")


if __name__ == "__main__":
    create_demo_database("demo_data.db")
