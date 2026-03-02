"""
Invoice Generation System - Flask Web Application
"""
from flask import Flask, render_template, request, jsonify, redirect, url_for, send_file, make_response
import os, sys, json, io

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from database import get_db, init_db, generate_customer_code, generate_invoice_no
from pdf_gen import generate_invoice_pdf

app = Flask(__name__)
app.secret_key = 'invoice_secret_2024'

@app.before_request
def setup():
    init_db()

# ── HOME ──
@app.route('/')
def index():
    return render_template('index.html')

# ────────────────────────────────────────────
# OWNER
# ────────────────────────────────────────────
@app.route('/owner', methods=['GET'])
def owner():
    db = get_db()
    row = db.execute("SELECT * FROM owner LIMIT 1").fetchone()
    db.close()
    return render_template('owner.html', owner=dict(row) if row else {})

@app.route('/api/owner', methods=['GET'])
def api_owner_get():
    db = get_db()
    row = db.execute("SELECT * FROM owner LIMIT 1").fetchone()
    db.close()
    return jsonify(dict(row) if row else {})

@app.route('/api/owner', methods=['POST'])
def api_owner_save():
    data = request.json
    db = get_db()
    existing = db.execute("SELECT id FROM owner LIMIT 1").fetchone()
    if existing:
        db.execute("""UPDATE owner SET company_name=?,address=?,state=?,email=?,mobile=?,gstin=?
                      WHERE id=?""",
                   (data['company_name'], data['address'], data['state'],
                    data['email'], data['mobile'], data['gstin'], existing['id']))
    else:
        db.execute("""INSERT INTO owner(company_name,address,state,email,mobile,gstin)
                      VALUES(?,?,?,?,?,?)""",
                   (data['company_name'], data['address'], data['state'],
                    data['email'], data['mobile'], data['gstin']))
    db.commit(); db.close()
    return jsonify({'success': True})

# ────────────────────────────────────────────
# CUSTOMERS
# ────────────────────────────────────────────
@app.route('/customers')
def customers():
    return render_template('customers.html')

@app.route('/api/customers', methods=['GET'])
def api_customers_list():
    db = get_db()
    rows = db.execute("SELECT * FROM customers ORDER BY name").fetchall()
    db.close()
    return jsonify([dict(r) for r in rows])

@app.route('/api/customers/search', methods=['GET'])
def api_customers_search():
    q = request.args.get('q', '')
    db = get_db()
    rows = db.execute("SELECT * FROM customers WHERE name LIKE ? ORDER BY name",
                      (f'%{q}%',)).fetchall()
    db.close()
    return jsonify([dict(r) for r in rows])

@app.route('/api/customers', methods=['POST'])
def api_customer_create():
    data = request.json
    code = generate_customer_code(data['name'])
    db = get_db()
    try:
        db.execute("""INSERT INTO customers(customer_code,name,address,state,email,phone,gstin)
                      VALUES(?,?,?,?,?,?,?)""",
                   (code, data['name'], data.get('address',''), data.get('state',''),
                    data.get('email',''), data.get('phone',''), data.get('gstin','')))
        db.commit()
        row = db.execute("SELECT * FROM customers WHERE customer_code=?", (code,)).fetchone()
        db.close()
        return jsonify({'success': True, 'customer': dict(row)})
    except Exception as e:
        db.close()
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/customers/<int:cid>', methods=['GET'])
def api_customer_get(cid):
    db = get_db()
    row = db.execute("SELECT * FROM customers WHERE id=?", (cid,)).fetchone()
    db.close()
    return jsonify(dict(row) if row else {})

@app.route('/api/customers/<int:cid>', methods=['PUT'])
def api_customer_update(cid):
    data = request.json
    db = get_db()
    db.execute("""UPDATE customers SET name=?,address=?,state=?,email=?,phone=?,gstin=?
                  WHERE id=?""",
               (data['name'], data.get('address',''), data.get('state',''),
                data.get('email',''), data.get('phone',''), data.get('gstin',''), cid))
    db.commit(); db.close()
    return jsonify({'success': True})

@app.route('/api/customers/<int:cid>', methods=['DELETE'])
def api_customer_delete(cid):
    db = get_db()
    db.execute("DELETE FROM customers WHERE id=?", (cid,))
    db.commit(); db.close()
    return jsonify({'success': True})

# ────────────────────────────────────────────
# PRODUCTS
# ────────────────────────────────────────────
@app.route('/products')
def products():
    return render_template('products.html')

@app.route('/api/products', methods=['GET'])
def api_products_list():
    db = get_db()
    rows = db.execute("SELECT * FROM products ORDER BY product_code").fetchall()
    db.close()
    return jsonify([dict(r) for r in rows])

@app.route('/api/products/search', methods=['GET'])
def api_products_search():
    q = request.args.get('q', '')
    db = get_db()
    rows = db.execute("""SELECT * FROM products WHERE product_code LIKE ? OR description LIKE ?
                         ORDER BY product_code""", (f'%{q}%', f'%{q}%')).fetchall()
    db.close()
    return jsonify([dict(r) for r in rows])

@app.route('/api/products/<code>', methods=['GET'])
def api_product_by_code(code):
    db = get_db()
    row = db.execute("SELECT * FROM products WHERE product_code=?", (code,)).fetchone()
    db.close()
    return jsonify(dict(row) if row else {})

@app.route('/api/products', methods=['POST'])
def api_product_create():
    data = request.json
    db = get_db()
    try:
        db.execute("""INSERT INTO products(product_code,description,rate) VALUES(?,?,?)""",
                   (data['product_code'], data['description'], float(data.get('rate',0))))
        db.commit()
        row = db.execute("SELECT * FROM products WHERE product_code=?", (data['product_code'],)).fetchone()
        db.close()
        return jsonify({'success': True, 'product': dict(row)})
    except Exception as e:
        db.close()
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/products/<int:pid>', methods=['PUT'])
def api_product_update(pid):
    data = request.json
    db = get_db()
    db.execute("""UPDATE products SET product_code=?,description=?,rate=? WHERE id=?""",
               (data['product_code'], data['description'], float(data.get('rate',0)), pid))
    db.commit(); db.close()
    return jsonify({'success': True})

@app.route('/api/products/<int:pid>', methods=['DELETE'])
def api_product_delete(pid):
    db = get_db()
    db.execute("DELETE FROM products WHERE id=?", (pid,))
    db.commit(); db.close()
    return jsonify({'success': True})

# ────────────────────────────────────────────
# INVOICES
# ────────────────────────────────────────────
@app.route('/invoice/new')
def invoice_new():
    return render_template('invoice_form.html', mode='new')

@app.route('/invoice/<int:inv_id>/edit')
def invoice_edit(inv_id):
    return render_template('invoice_form.html', mode='edit', inv_id=inv_id)

@app.route('/invoice/search')
def invoice_search():
    return render_template('invoice_search.html')

@app.route('/api/invoices/next_no', methods=['GET'])
def api_next_invoice_no():
    return jsonify({'invoice_no': generate_invoice_no()})

@app.route('/api/invoices', methods=['POST'])
def api_invoice_create():
    data = request.json
    inv_no = data.get('invoice_no') or generate_invoice_no()
    db = get_db()
    try:
        db.execute("""INSERT INTO invoices(invoice_no,date,customer_id,ship_same_as_bill,
                      ship_address,ship_mobile,freight_charges,gunni_charges,round_off,terms,
                      lr_no,transport,place_of_supply,no_of_bundles,
                      total_qty,total_gross,total_net,net_payable)
                      VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                   (inv_no, data['date'], data['customer_id'],
                    1 if data.get('ship_same_as_bill') else 0,
                    data.get('ship_address',''), data.get('ship_mobile',''),
                    float(data.get('freight_charges',0)), float(data.get('gunni_charges',0)),
                    float(data.get('round_off',0)), data.get('terms',''),
                    data.get('lr_no',''), data.get('transport',''),
                    data.get('place_of_supply',''), data.get('no_of_bundles',''),
                    float(data.get('total_qty',0)), float(data.get('total_gross',0)),
                    float(data.get('total_net',0)), float(data.get('net_payable',0))))
        inv_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
        _save_items(db, inv_id, data.get('items', []))
        db.commit(); db.close()
        return jsonify({'success': True, 'id': inv_id, 'invoice_no': inv_no})
    except Exception as e:
        db.close()
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/invoices/<int:inv_id>', methods=['GET'])
def api_invoice_get(inv_id):
    db = get_db()
    inv = db.execute("SELECT * FROM invoices WHERE id=?", (inv_id,)).fetchone()
    if not inv:
        db.close(); return jsonify({}), 404
    inv_d = dict(inv)
    items = db.execute("SELECT * FROM invoice_items WHERE invoice_id=? ORDER BY sno", (inv_id,)).fetchall()
    inv_d['items'] = [dict(i) for i in items]
    cust = db.execute("SELECT * FROM customers WHERE id=?", (inv_d['customer_id'],)).fetchone()
    inv_d['customer'] = dict(cust) if cust else {}
    db.close()
    return jsonify(inv_d)

@app.route('/api/invoices/<int:inv_id>', methods=['PUT'])
def api_invoice_update(inv_id):
    data = request.json
    db = get_db()
    try:
        db.execute("""UPDATE invoices SET date=?,customer_id=?,ship_same_as_bill=?,
                      ship_address=?,ship_mobile=?,freight_charges=?,gunni_charges=?,round_off=?,
                      terms=?,lr_no=?,transport=?,place_of_supply=?,no_of_bundles=?,
                      total_qty=?,total_gross=?,total_net=?,net_payable=? WHERE id=?""",
                   (data['date'], data['customer_id'],
                    1 if data.get('ship_same_as_bill') else 0,
                    data.get('ship_address',''), data.get('ship_mobile',''),
                    float(data.get('freight_charges',0)), float(data.get('gunni_charges',0)),
                    float(data.get('round_off',0)), data.get('terms',''),
                    data.get('lr_no',''), data.get('transport',''),
                    data.get('place_of_supply',''), data.get('no_of_bundles',''),
                    float(data.get('total_qty',0)), float(data.get('total_gross',0)),
                    float(data.get('total_net',0)), float(data.get('net_payable',0)), inv_id))
        db.execute("DELETE FROM invoice_items WHERE invoice_id=?", (inv_id,))
        _save_items(db, inv_id, data.get('items', []))
        db.commit(); db.close()
        return jsonify({'success': True})
    except Exception as e:
        db.close()
        return jsonify({'success': False, 'error': str(e)}), 400

def _save_items(db, inv_id, items):
    for item in items:
        qty = float(item.get('qty', 0))
        rate = float(item.get('rate', 0))
        gross = qty * rate
        disc = float(item.get('discount_pct', 0))
        net = gross * (1 - disc / 100)
        # Override if explicitly provided
        if 'gross_amount' in item: gross = float(item['gross_amount'])
        if 'net_amount' in item: net = float(item['net_amount'])
        db.execute("""INSERT INTO invoice_items(invoice_id,sno,product_id,product_code,
                      description,qty,rate,gross_amount,discount_pct,net_amount)
                      VALUES(?,?,?,?,?,?,?,?,?,?)""",
                   (inv_id, item.get('sno',1),
                    item.get('product_id'), item.get('product_code',''),
                    item.get('description',''), qty, rate, gross, disc, net))

@app.route('/api/invoices/by_customer/<int:cid>', methods=['GET'])
def api_invoices_by_customer(cid):
    db = get_db()
    rows = db.execute("""SELECT i.*, c.name as customer_name
                         FROM invoices i JOIN customers c ON i.customer_id=c.id
                         WHERE i.customer_id=? ORDER BY i.date DESC, i.id DESC""", (cid,)).fetchall()
    db.close()
    return jsonify([dict(r) for r in rows])

@app.route('/api/invoices/by_date', methods=['GET'])
def api_invoices_by_date():
    date = request.args.get('date', '')
    db = get_db()
    rows = db.execute("""SELECT i.*, c.name as customer_name
                         FROM invoices i JOIN customers c ON i.customer_id=c.id
                         WHERE i.date=? ORDER BY i.id DESC""", (date,)).fetchall()
    db.close()
    return jsonify([dict(r) for r in rows])

# ── PDF / PRINT ──
@app.route('/api/invoices/<int:inv_id>/pdf', methods=['GET'])
def api_invoice_pdf(inv_id):
    db = get_db()
    inv = db.execute("SELECT * FROM invoices WHERE id=?", (inv_id,)).fetchone()
    if not inv:
        db.close(); return "Not found", 404
    inv_d = dict(inv)
    items = db.execute("SELECT * FROM invoice_items WHERE invoice_id=? ORDER BY sno", (inv_id,)).fetchall()
    cust = db.execute("SELECT * FROM customers WHERE id=?", (inv_d['customer_id'],)).fetchone()
    owner = db.execute("SELECT * FROM owner LIMIT 1").fetchone()
    db.close()

    pdf_data = {
        'owner': dict(owner) if owner else {},
        'customer': dict(cust) if cust else {},
        'invoice': inv_d,
        'items': [dict(i) for i in items]
    }
    pdf_bytes = generate_invoice_pdf(pdf_data)
    response = make_response(pdf_bytes)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=invoice_{inv_d["invoice_no"]}.pdf'
    return response

if __name__ == '__main__':
    init_db()
    print("\n" + "="*50)
    print("  Invoice Generation System")
    print("  Open: http://localhost:5000")
    print("="*50 + "\n")
    app.run(debug=False, host='0.0.0.0', port=5000)
