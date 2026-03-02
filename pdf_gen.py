"""PDF Invoice generator matching Vikranth Publishers format"""
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle,
                                 Paragraph, Spacer, HRFlowable, KeepTogether)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit
import io, os, re

def number_to_words(n):
    """Convert number to Indian currency words"""
    ones = ['','ONE','TWO','THREE','FOUR','FIVE','SIX','SEVEN','EIGHT','NINE',
            'TEN','ELEVEN','TWELVE','THIRTEEN','FOURTEEN','FIFTEEN','SIXTEEN',
            'SEVENTEEN','EIGHTEEN','NINETEEN']
    tens = ['','','TWENTY','THIRTY','FORTY','FIFTY','SIXTY','SEVENTY','EIGHTY','NINETY']

    def two_digits(n):
        if n < 20: return ones[n]
        return tens[n // 10] + (' ' + ones[n % 10] if n % 10 else '')

    def three_digits(n):
        if n >= 100:
            return ones[n // 100] + ' HUNDRED' + (' AND ' + two_digits(n % 100) if n % 100 else '')
        return two_digits(n)

    if n == 0: return 'ZERO'
    n = int(round(n))
    parts = []
    if n >= 10000000:
        parts.append(three_digits(n // 10000000) + ' CRORE')
        n %= 10000000
    if n >= 100000:
        parts.append(three_digits(n // 100000) + ' LAKH')
        n %= 100000
    if n >= 1000:
        parts.append(three_digits(n // 1000) + ' THOUSAND')
        n %= 1000
    if n >= 100:
        parts.append(three_digits(n // 100) + ' HUNDRED')
        n %= 100
    if n:
        parts.append(two_digits(n))
    return ' '.join(parts)

def rupees_in_words(amount):
    amount = round(float(amount), 2)
    rupees = int(amount)
    paise = round((amount - rupees) * 100)
    words = number_to_words(rupees) + ' RUPEES'
    if paise:
        words += ' AND ' + number_to_words(paise) + ' PAISE'
    words += ' ONLY'
    return words

def generate_invoice_pdf(invoice_data, output_path=None):
    """
    invoice_data: dict with all invoice fields
    Returns bytes if output_path is None, else writes to file.
    """
    buf = io.BytesIO()
    target = output_path or buf

    doc = SimpleDocTemplate(
        target,
        pagesize=A4,
        leftMargin=10*mm, rightMargin=10*mm,
        topMargin=8*mm, bottomMargin=8*mm
    )

    W = A4[0] - 20*mm  # usable width

    styles = getSampleStyleSheet()
    normal = styles['Normal']

    def S(text, size=8, bold=False, align=TA_LEFT, color=colors.black, leading=None):
        return ParagraphStyle('s', fontSize=size, fontName='Helvetica-Bold' if bold else 'Helvetica',
                              alignment=align, textColor=color, leading=leading or size+2)

    owner = invoice_data.get('owner', {})
    customer = invoice_data.get('customer', {})
    inv = invoice_data.get('invoice', {})
    items = invoice_data.get('items', [])

    elems = []

    # ── COPY LABELS (top right) ──
    copy_labels = ['INVOICE ORIGINAL', 'DUPLICATE', 'TRIPLICATE', 'EXTRA COPY']

    # ── HEADER ──
    company_name = owner.get('company_name', 'COMPANY NAME')
    addr = owner.get('address', '')
    phone_line = f"Phone: {owner.get('mobile','')}  |  email: {owner.get('email','')}"
    gstin_line = f"GSTIN NO: {owner.get('gstin','')}"

    # Header table: company info left, copy labels right
    copy_text = '\n'.join(copy_labels)
    header_data = [[
        Paragraph(f"<b><font size=14>{company_name}</font></b><br/>"
                  f"<font size=7>{addr}</font><br/>"
                  f"<font size=7>{phone_line}</font><br/>"
                  f"<font size=7>{gstin_line}</font>", styles['Normal']),
        Paragraph('<br/>'.join(f"<b><font size=7>{c}</font></b>" for c in copy_labels),
                  ParagraphStyle('r', alignment=TA_RIGHT, fontSize=7, leading=10))
    ]]
    ht = Table(header_data, colWidths=[W*0.72, W*0.28])
    ht.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.8, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    elems.append(ht)
    elems.append(Spacer(1, 1*mm))

    # ── TRANSPORT / LR / INVOICE META ──
    transport = inv.get('transport', '')
    lr_no = inv.get('lr_no', '')
    no_bundles = inv.get('no_of_bundles', '')
    inv_no = inv.get('invoice_no', '')
    inv_date = inv.get('date', '')
    place_supply = inv.get('place_of_supply', '')

    meta_data = [[
        Paragraph(f"<font size=7>Transpotation: <b>{transport}</b></font>", styles['Normal']),
        Paragraph(f"<font size=7>LR No: <b>{lr_no}</b></font>", styles['Normal']),
        Paragraph(f"<font size=8><b>INVOICE NO:</b> {inv_no}</font>", styles['Normal']),
        Paragraph(f"<font size=7>No of Bundles: <b>{no_bundles}</b></font>", styles['Normal']),
    ],[
        Paragraph(f"<font size=7>Place of Supply: <b>{place_supply}</b></font>", styles['Normal']),
        Paragraph("", styles['Normal']),
        Paragraph(f"<font size=8><b>DATE:</b> {inv_date}</font>", styles['Normal']),
        Paragraph("", styles['Normal']),
    ]]
    mt = Table(meta_data, colWidths=[W*0.28, W*0.20, W*0.28, W*0.24])
    mt.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.8, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.3, colors.grey),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    elems.append(mt)
    elems.append(Spacer(1, 1*mm))

    # ── BILLED TO / SHIPPED TO ──
    bill_name = customer.get('name', '')
    bill_addr = customer.get('address', '')
    bill_state = customer.get('state', '')
    bill_phone = customer.get('phone', '')
    bill_gstin = customer.get('gstin', '')

    ship_same = inv.get('ship_same_as_bill', True)
    if ship_same:
        ship_name = bill_name
        ship_addr = bill_addr
        ship_phone = bill_phone
    else:
        ship_name = inv.get('ship_name', '')
        ship_addr = inv.get('ship_address', '')
        ship_phone = inv.get('ship_mobile', '')

    def addr_para(label, name, addr, phone='', gstin='', state='', extra=''):
        lines = [f"<b><font size=7>{label}</font></b>"]
        if name: lines.append(f"<font size=7><b>M/s. {name}</b></font>")
        if addr: lines.append(f"<font size=7>{addr}</font>")
        if phone: lines.append(f"<font size=7>{phone}</font>")
        if state: lines.append(f"<font size=7>State: {state}</font>")
        if gstin: lines.append(f"<font size=7>GSTIN: {gstin}</font>")
        return Paragraph('<br/>'.join(lines), styles['Normal'])

    addr_data = [[
        addr_para('Details of Receiver (Billed to)', bill_name, bill_addr,
                  bill_phone, bill_gstin, bill_state),
        addr_para('Details of Consignee (Shipped to)', ship_name, ship_addr, ship_phone),
    ]]
    at = Table(addr_data, colWidths=[W*0.5, W*0.5])
    at.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.8, colors.black),
        ('LINEAFTER', (0,0), (0,-1), 0.5, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    elems.append(at)
    elems.append(Spacer(1, 1*mm))

    # ── ITEMS TABLE ──
    item_headers = ['Sn', 'Code', 'Description', 'Qty', 'Rate', 'Gross\nAmount', 'Disc\n%', 'Net\nAmount']
    col_w = [W*0.04, W*0.08, W*0.30, W*0.06, W*0.08, W*0.12, W*0.07, W*0.12]  # adjusted to sum W

    # Adjust last col to fill remaining
    col_w[-1] = W - sum(col_w[:-1])

    hstyle = ParagraphStyle('hdr', fontSize=7, fontName='Helvetica-Bold',
                            alignment=TA_CENTER, leading=9)
    item_table_data = [[Paragraph(h, hstyle) for h in item_headers]]

    total_qty = 0; total_gross = 0; total_net = 0
    for item in items:
        qty = float(item.get('qty', 0))
        rate = float(item.get('rate', 0))
        gross = float(item.get('gross_amount', qty * rate))
        disc = float(item.get('discount_pct', 0))
        net = float(item.get('net_amount', gross * (1 - disc/100)))
        total_qty += qty; total_gross += gross; total_net += net

        def cp(t, align=TA_CENTER):
            return Paragraph(f"<font size=7>{t}</font>",
                             ParagraphStyle('c', fontSize=7, alignment=align, leading=9))
        item_table_data.append([
            cp(str(item.get('sno', ''))),
            cp(str(item.get('product_code', ''))),
            cp(str(item.get('description', '')), TA_LEFT),
            cp(str(int(qty)) if qty == int(qty) else str(qty)),
            cp(f"{rate:.2f}"),
            cp(f"{gross:.2f}"),
            cp(f"{int(disc)}" if disc == int(disc) else f"{disc}"),
            cp(f"{net:.2f}"),
        ])

    # Totals row
    def bp(t, align=TA_CENTER):
        return Paragraph(f"<b><font size=7>{t}</font></b>",
                         ParagraphStyle('b', fontSize=7, fontName='Helvetica-Bold',
                                        alignment=align, leading=9))
    item_table_data.append([
        bp('Total'), bp(''), bp(''), bp(str(int(total_qty)) if total_qty==int(total_qty) else str(total_qty)),
        bp(''), bp(f"{total_gross:.2f}"), bp(''), bp(f"{total_net:.2f}")
    ])

    it = Table(item_table_data, colWidths=col_w)
    it.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.8, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.3, colors.grey),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#E8E8E8')),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#F5F5F5')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('LEFTPADDING', (0,0), (-1,-1), 2),
        ('RIGHTPADDING', (0,0), (-1,-1), 2),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('LINEBELOW', (0,-1), (-1,-1), 0.8, colors.black),
        ('LINEABOVE', (0,-1), (-1,-1), 0.5, colors.black),
        ('SPAN', (0,-1), (1,-1)),
    ]))
    elems.append(it)
    elems.append(Spacer(1, 1*mm))

    # ── CHARGES / TOTALS / SIGNATURE ──
    freight = float(inv.get('freight_charges', 0))
    gunni = float(inv.get('gunni_charges', 0))
    round_off = float(inv.get('round_off', 0))
    net_payable = total_net + freight + gunni + round_off
    words = rupees_in_words(net_payable)

    terms_raw = inv.get('terms', '1. All disputes subject to jurisdiction only.')
    terms_lines = [l.strip() for l in terms_raw.split('\n') if l.strip()]

    def rp(t): return Paragraph(f"<font size=7>{t}</font>",
                                 ParagraphStyle('r', fontSize=7, alignment=TA_RIGHT, leading=10))
    def lp(t, bold=False):
        fn = 'Helvetica-Bold' if bold else 'Helvetica'
        return Paragraph(f"<font size=7>{t}</font>",
                         ParagraphStyle('l', fontSize=7, fontName=fn, alignment=TA_LEFT, leading=10))

    charges_left = []
    charges_left.append(lp(f"<b>Rupees: {words}</b>", bold=True))
    charges_left.append(Spacer(1, 2*mm))
    charges_left.append(lp("<b>Term &amp; Condition:</b>", bold=True))
    for line in terms_lines:
        charges_left.append(lp(line))

    from reportlab.platypus import KeepInFrame
    from reportlab.platypus import ListFlowable, ListItem

    charges_right_data = [
        [lp('Gross:'), rp(f"{total_gross:.2f}")],
        [lp('Freight Charges :'), rp(f"{freight:.2f}" if freight else '')],
        [lp('Gunni Charges :'), rp(f"{gunni:.2f}" if gunni else '')],
        [lp('Round Off :'), rp(f"{round_off:.2f}" if round_off else '')],
        [lp('<b>NET AMOUNT:</b>', bold=True), rp(f"<b>{net_payable:,.2f}</b>")],
    ]
    crt = Table(charges_right_data, colWidths=[W*0.20, W*0.16])
    crt.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.8, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.3, colors.grey),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#EFEFEF')),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
    ]))

    # Signature block
    sig_data = [[
        Paragraph(f"<font size=7>For <b>{company_name}</b></font>",
                  ParagraphStyle('s', fontSize=7, alignment=TA_RIGHT, leading=10)),
    ],[
        Paragraph("<font size=7>Signature</font>",
                  ParagraphStyle('s', fontSize=7, alignment=TA_RIGHT, leading=10)),
    ]]
    sigt = Table(sig_data, colWidths=[W*0.36])
    sigt.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.8, colors.black),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 16),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
    ]))

    from reportlab.platypus import Frame
    # Bottom section: terms left, charges+sig right
    right_col = Table([[crt], [sigt]], colWidths=[W*0.36])
    right_col.setStyle(TableStyle([
        ('TOPPADDING', (0,0), (-1,-1), 1),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1),
    ]))

    terms_table_data = [
        [Paragraph('<br/>'.join(
            [f"<b><font size=7>Term &amp; Condition:</font></b>"] +
            [f"<font size=7>{l}</font>" for l in terms_lines]
         ), styles['Normal']),
         Paragraph("", styles['Normal'])
        ],
        [Paragraph(f"<b><font size=7>Rupees: {words}</font></b>", styles['Normal']),
         Paragraph("", styles['Normal'])
        ],
    ]

    # Build bottom as one wide table
    bottom_left_content = (
        [Paragraph(f"<b><font size=7>Term &amp; Condition:</font></b>", styles['Normal'])] +
        [Paragraph(f"<font size=7>{l}</font>", styles['Normal']) for l in terms_lines] +
        [Spacer(1, 2*mm),
         Paragraph(f"<b><font size=8>Rupees: {words}</font></b>", styles['Normal'])]
    )

    from reportlab.platypus import TopPadder
    bottom_data = [[bottom_left_content, [crt, Spacer(1, 2*mm), sigt]]]

    def nested(items):
        from reportlab.platypus import KeepInFrame
        return items

    # Simple bottom layout table
    bl_para = [
        Paragraph(f"<b><font size=7>Term &amp; Condition:</font></b>", styles['Normal'])
    ] + [Paragraph(f"<font size=7>{l}</font>", styles['Normal']) for l in terms_lines] + [
        Spacer(1, 3*mm),
        Paragraph(f"<b><font size=8>Rupees: {words}</font></b>", styles['Normal']),
        Spacer(1, 2*mm),
        Paragraph(f"<font size=7><b>NET AMOUNT: ₹{net_payable:,.2f}</b></font>", styles['Normal']),
    ]

    bottom_t = Table(
        [[bl_para, [crt, Spacer(1,2*mm), sigt]]],
        colWidths=[W*0.60, W*0.40]
    )
    bottom_t.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.8, colors.black),
        ('LINEAFTER', (0,0), (0,-1), 0.5, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    elems.append(bottom_t)

    doc.build(elems)

    if output_path is None:
        return buf.getvalue()
    return output_path


if __name__ == '__main__':
    # Test
    test_data = {
        'owner': {
            'company_name': 'VIKRANTH PUBLISHERS',
            'address': '#33-3-33, GNR Mansion, Ramanaidu Street, Seetharampuram, Vijayawada-2.',
            'mobile': '9985099998', 'email': 'vikranthpublishers@gmail.com',
            'gstin': '37ACOPG1874G1ZE'
        },
        'customer': {
            'name': 'P. SANTHOSH KUMAR [RS] - HYD',
            'address': 'H.NO;5-3-741, PHASE -1, VIJAYAPURI COLONY, VANASHALIPURAM',
            'phone': '9849865677', 'state': '', 'gstin': ''
        },
        'invoice': {
            'invoice_no': '750', 'date': '11-06-2025',
            'transport': 'KALESWARI', 'lr_no': '3680',
            'no_of_bundles': '1CB', 'place_of_supply': '',
            'ship_same_as_bill': True,
            'freight_charges': 0, 'gunni_charges': 20, 'round_off': 0,
            'terms': '1. All disputes subject to Vijayawada Jurisdiction only.',
        },
        'items': [
            {'sno':1,'product_code':'1051A','description':'TELUGU II LANGUAGE - 1','qty':50,'rate':148,'gross_amount':7400,'discount_pct':50,'net_amount':3700},
            {'sno':2,'product_code':'1052A','description':'TELUGU II LANGUAGE - 2','qty':50,'rate':148,'gross_amount':7400,'discount_pct':50,'net_amount':3700},
            {'sno':3,'product_code':'1053A','description':'TELUGU II LANGUAGE - 3','qty':50,'rate':168,'gross_amount':8400,'discount_pct':50,'net_amount':4200},
        ]
    }
    pdf = generate_invoice_pdf(test_data, '/tmp/test_invoice.pdf')
    print("PDF generated:", pdf)
