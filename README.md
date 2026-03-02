# 📄 Invoice Generation System

A complete invoice billing system for **desktop and web**, matching the Vikranth Publishers invoice format.

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install flask reportlab
```

### 2. Run the Application
```bash
python run.py
```
This starts the server and **opens your browser automatically** at `http://localhost:5000`

---

## 📋 Features

### ✅ Owner / Company Setup
- Set your company name, address, GSTIN, contact details
- Used automatically on every invoice header

### ✅ Customer Master
- Add / Edit / Delete customers
- Auto-generates unique customer code (e.g. `PSAN001`) based on name
- Fields: Name, Address, State, Email, Phone, GSTIN

### ✅ Product Master
- Add / Edit / Delete products
- Fields: Product Code, Description, Rate

### ✅ Invoice Creation
- **Auto invoice numbering** (INV0001, INV0002…)
- Select customer with **live search autocomplete**
- Shipping address: same as billing OR different (with address + mobile)
- **Line items table:**
  - S.No (auto)
  - Product Code → auto-fills Description & Rate
  - Quantity
  - Rate (auto from product, editable)
  - Gross Amount (auto = Qty × Rate)
  - Discount %
  - Net Amount (auto = Gross − Discount)
- Running totals: Total Qty, Total Gross, Total Net
- Freight Charges, Gunni Charges, Round Off
- **Net Payable** = Total Net + Freight + Gunni + Round Off
- **Amount in Words** (Indian format: Lakhs, Crores)
- Editable Terms & Conditions
- **Transport, LR No, No. of Bundles, Place of Supply**
- **PDF Download** and **Print** buttons

### ✅ Invoice PDF Format
Matches the sample format:
- Company header with copy labels (ORIGINAL / DUPLICATE / TRIPLICATE / EXTRA COPY)
- Transport, LR No, Invoice No, Date meta block
- Billed To / Shipped To two-column layout
- Items table with all columns
- Totals row
- Charges summary + Rupees in words + Signature block
- Terms & Conditions

### ✅ Invoice Search & Edit
**By Customer Name:**
- Type partial name (e.g. "san") → see all matching customers
- Double-click customer → see all their invoices
- Double-click invoice → open for view/edit

**By Date:**
- Pick a date → see all invoices that day
- Click any invoice → open for view/edit

---

## 📁 Project Structure
```
invoice_system/
├── run.py           ← Start here
├── app.py           ← Flask web application
├── database.py      ← SQLite database layer
├── pdf_gen.py       ← PDF generation (ReportLab)
├── requirements.txt
├── db/
│   └── invoice.db   ← Auto-created SQLite database
└── templates/
    ├── base.html
    ├── index.html
    ├── owner.html
    ├── customers.html
    ├── products.html
    ├── invoice_form.html
    └── invoice_search.html
```

---

## 💻 Access
- **Local (same computer):** http://localhost:5000
- **Network (same Wi-Fi):** http://YOUR-IP:5000

---

## 🔧 Troubleshooting
- If port 5000 is busy, edit `PORT = 5000` in `run.py`
- Database is at `db/invoice.db` — back this up regularly
- To reset: delete `db/invoice.db` and restart
