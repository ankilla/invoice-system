import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "db", "invoice.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_db()
    c = conn.cursor()

    c.executescript("""
    CREATE TABLE IF NOT EXISTS owner (
        id INTEGER PRIMARY KEY,
        company_name TEXT NOT NULL,
        address TEXT,
        state TEXT,
        email TEXT,
        mobile TEXT,
        gstin TEXT
    );

    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_code TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        address TEXT,
        state TEXT,
        email TEXT,
        phone TEXT,
        gstin TEXT
    );

    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_code TEXT UNIQUE NOT NULL,
        description TEXT NOT NULL,
        rate REAL NOT NULL DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS invoices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        invoice_no TEXT UNIQUE NOT NULL,
        date TEXT NOT NULL,
        customer_id INTEGER NOT NULL,
        ship_same_as_bill INTEGER DEFAULT 1,
        ship_address TEXT,
        ship_mobile TEXT,
        freight_charges REAL DEFAULT 0,
        gunni_charges REAL DEFAULT 0,
        round_off REAL DEFAULT 0,
        terms TEXT,
        lr_no TEXT,
        transport TEXT,
        place_of_supply TEXT,
        no_of_bundles TEXT,
        total_qty REAL DEFAULT 0,
        total_gross REAL DEFAULT 0,
        total_net REAL DEFAULT 0,
        net_payable REAL DEFAULT 0,
        FOREIGN KEY(customer_id) REFERENCES customers(id)
    );

    CREATE TABLE IF NOT EXISTS invoice_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        invoice_id INTEGER NOT NULL,
        sno INTEGER NOT NULL,
        product_id INTEGER,
        product_code TEXT,
        description TEXT,
        qty REAL DEFAULT 0,
        rate REAL DEFAULT 0,
        gross_amount REAL DEFAULT 0,
        discount_pct REAL DEFAULT 0,
        net_amount REAL DEFAULT 0,
        FOREIGN KEY(invoice_id) REFERENCES invoices(id) ON DELETE CASCADE,
        FOREIGN KEY(product_id) REFERENCES products(id)
    );
    """)
    conn.commit()
    conn.close()

def generate_customer_code(name):
    """Generate unique alpha-numeric code from customer name"""
    import re, random, string
    conn = get_db()
    base = re.sub(r'[^A-Za-z]', '', name).upper()[:4]
    if len(base) < 2:
        base = (base + 'CUST')[:4]
    # Find existing codes with same prefix
    existing = [row[0] for row in conn.execute(
        "SELECT customer_code FROM customers WHERE customer_code LIKE ?", (base + '%',)
    ).fetchall()]
    conn.close()
    num = 1
    while True:
        code = f"{base}{num:03d}"
        if code not in existing:
            return code
        num += 1

def generate_invoice_no():
    conn = get_db()
    row = conn.execute("SELECT invoice_no FROM invoices ORDER BY id DESC LIMIT 1").fetchone()
    conn.close()
    if not row:
        return "INV0001"
    last = row[0]
    match = re.search(r'(\d+)$', last)
    if match:
        num = int(match.group(1)) + 1
        prefix = last[:match.start()]
        return f"{prefix}{num:04d}"
    return "INV0001"

import re

if __name__ == "__main__":
    init_db()
    print("Database initialized.")
