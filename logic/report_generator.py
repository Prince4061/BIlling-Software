"""
report_generator.py
Generates printable PDF reports for:
  - Master Data (all bills)
  - Pending Payments (Baaki Khata)
"""
import os
import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

# ── Colors ───────────────────────────────────────────────────
C_BLUE   = colors.HexColor('#13488B')
C_LBLUE  = colors.HexColor('#A8C3E5')
C_BG     = colors.HexColor('#EBF2FA')
C_GREEN  = colors.HexColor('#1ca350')
C_RED    = colors.HexColor('#e74c3c')
C_ORANGE = colors.HexColor('#e67e22')
C_YELLOW = colors.HexColor('#f39c12')
C_GREY   = colors.HexColor('#f0f4f9')
C_WHITE  = colors.white
C_BLACK  = colors.black
C_DARK   = colors.HexColor('#1a1a2e')
C_MUTED  = colors.HexColor('#6b7280')

SHOP_NAME    = "H.H. Mobile & Enterprises"
SHOP_ADDRESS = "Near Makkad Complex, Main Road, Takhatpur — 495330"
SHOP_CONTACT = "📞 7869000000  |  💬 9893000005  |  GSTIN: 22AUVPD7913L1Z9"

REPORTS_DIR = "reports"


def _ensure_dir():
    if not os.path.exists(REPORTS_DIR):
        os.makedirs(REPORTS_DIR)


def _styles():
    base = getSampleStyleSheet()
    styles = {
        'shop': ParagraphStyle('shop', fontSize=20, fontName='Helvetica-Bold',
                               textColor=C_BLUE, alignment=TA_CENTER, spaceAfter=2),
        'addr': ParagraphStyle('addr', fontSize=9,  fontName='Helvetica',
                               textColor=C_MUTED, alignment=TA_CENTER, spaceAfter=2),
        'rpt_title': ParagraphStyle('rpt_title', fontSize=14, fontName='Helvetica-Bold',
                                    textColor=C_DARK, alignment=TA_CENTER, spaceBefore=8, spaceAfter=4),
        'meta': ParagraphStyle('meta', fontSize=8, fontName='Helvetica',
                               textColor=C_MUTED, alignment=TA_CENTER, spaceAfter=10),
        'summary_label': ParagraphStyle('sl', fontSize=9, fontName='Helvetica',
                                        textColor=C_MUTED, alignment=TA_RIGHT),
        'summary_val':   ParagraphStyle('sv', fontSize=11, fontName='Helvetica-Bold',
                                        textColor=C_DARK, alignment=TA_RIGHT),
        'footer': ParagraphStyle('footer', fontSize=7, fontName='Helvetica',
                                 textColor=C_MUTED, alignment=TA_CENTER, spaceBefore=8),
    }
    return styles


def _header_elements(report_title, subtitle="", styles=None):
    if styles is None:
        styles = _styles()
    now = datetime.datetime.now().strftime("%d %B %Y, %I:%M %p")
    elems = [
        Paragraph(SHOP_NAME, styles['shop']),
        Paragraph(SHOP_ADDRESS, styles['addr']),
        Paragraph(SHOP_CONTACT, styles['addr']),
        Spacer(1, 6),
        HRFlowable(width="100%", thickness=1.5, color=C_BLUE),
        Spacer(1, 6),
        Paragraph(report_title, styles['rpt_title']),
    ]
    if subtitle:
        elems.append(Paragraph(subtitle, styles['meta']))
    elems.append(Paragraph(f"Generated on: {now}", styles['meta']))
    elems.append(Spacer(1, 8))
    return elems


# ══════════════════════════════════════════════════════════════
# 1. MASTER DATA REPORT
# ══════════════════════════════════════════════════════════════
def generate_master_pdf(bills_df):
    """
    bills_df: pandas DataFrame with columns:
      Bill No, Date, Customer Name, Mobile, Company, Item,
      Qty, Rate, Total Amount, Tax, Grand Total, Paid Amount, Due Amount
    Returns: absolute path to generated PDF
    """
    _ensure_dir()
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath  = os.path.join(REPORTS_DIR, f"Master_Data_{timestamp}.pdf")

    doc = SimpleDocTemplate(
        filepath,
        pagesize=landscape(A4),
        leftMargin=15*mm, rightMargin=15*mm,
        topMargin=12*mm,  bottomMargin=12*mm,
    )

    styles = _styles()
    elems  = _header_elements("📊 Master Data Report — Sabhi Bills", styles=styles)

    # ── Summary row ───────────────────────────────────────────
    if not bills_df.empty:
        import pandas as pd
        unique_bills = bills_df.drop_duplicates(subset=['Bill No'])
        total_bills   = len(unique_bills)
        total_revenue = unique_bills['Grand Total'].sum()
        total_paid    = unique_bills['Paid Amount'].sum()
        total_due     = unique_bills['Due Amount'].sum()

        summary_data = [
            ['Total Bills', 'Total Revenue', 'Total Received', 'Total Pending'],
            [
                str(total_bills),
                f"\u20b9 {total_revenue:,.2f}",
                f"\u20b9 {total_paid:,.2f}",
                f"\u20b9 {total_due:,.2f}",
            ]
        ]
        summary_table = Table(summary_data, colWidths=[60*mm]*4)
        summary_table.setStyle(TableStyle([
            ('BACKGROUND',   (0,0), (-1,0), C_BLUE),
            ('TEXTCOLOR',    (0,0), (-1,0), C_WHITE),
            ('FONTNAME',     (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE',     (0,0), (-1,0), 9),
            ('FONTNAME',     (0,1), (-1,1), 'Helvetica-Bold'),
            ('FONTSIZE',     (0,1), (-1,1), 13),
            ('TEXTCOLOR',    (0,1), (0,1), C_DARK),
            ('TEXTCOLOR',    (1,1), (1,1), C_BLUE),
            ('TEXTCOLOR',    (2,1), (2,1), C_GREEN),
            ('TEXTCOLOR',    (3,1), (3,1), C_RED),
            ('ALIGN',        (0,0), (-1,-1), 'CENTER'),
            ('VALIGN',       (0,0), (-1,-1), 'MIDDLE'),
            ('ROWBACKGROUNDS',(0,1), (-1,1), [C_GREY]),
            ('GRID',         (0,0), (-1,-1), 0.5, C_LBLUE),
            ('TOPPADDING',   (0,0), (-1,-1), 6),
            ('BOTTOMPADDING',(0,0), (-1,-1), 6),
            ('ROUNDEDCORNERS', [4]),
        ]))
        elems.append(summary_table)
        elems.append(Spacer(1, 12))

    # ── Main data table ───────────────────────────────────────
    col_headers = ['Bill#', 'Date', 'Customer', 'Mobile', 'Company',
                   'Item', 'Qty', 'Rate (₹)', 'Amount (₹)',
                   'Grand Total', 'Paid', 'Due']
    col_widths  = [18, 24, 42, 28, 24, 54, 12, 22, 24, 28, 24, 22]
    col_widths  = [w*mm for w in col_widths]

    rows = [col_headers]

    if bills_df.empty:
        rows.append(['—'] * len(col_headers))
    else:
        for _, r in bills_df.iterrows():
            rows.append([
                str(int(r.get('Bill No', 0))) if str(r.get('Bill No','')).replace('.','').isdigit() else str(r.get('Bill No','')),
                str(r.get('Date', ''))[:10],
                str(r.get('Customer Name', '')),
                str(r.get('Mobile', '')),
                str(r.get('Company', '')),
                str(r.get('Item', '')),
                str(r.get('Qty', '')),
                f"{float(r.get('Rate', 0)):,.1f}",
                f"{float(r.get('Total Amount', 0)):,.2f}",
                f"{float(r.get('Grand Total', 0)):,.2f}",
                f"{float(r.get('Paid Amount', 0)):,.2f}",
                f"{float(r.get('Due Amount', 0)):,.2f}",
            ])

    tbl = Table(rows, colWidths=col_widths, repeatRows=1)

    row_count = len(rows)
    style_cmds = [
        # Header
        ('BACKGROUND',    (0,0),  (-1,0),  C_BLUE),
        ('TEXTCOLOR',     (0,0),  (-1,0),  C_WHITE),
        ('FONTNAME',      (0,0),  (-1,0),  'Helvetica-Bold'),
        ('FONTSIZE',      (0,0),  (-1,0),  8),
        # Body
        ('FONTNAME',      (0,1),  (-1,-1), 'Helvetica'),
        ('FONTSIZE',      (0,1),  (-1,-1), 7.5),
        ('TEXTCOLOR',     (0,1),  (-1,-1), C_DARK),
        # Alignment
        ('ALIGN',         (0,0),  (-1,0),  'CENTER'),
        ('ALIGN',         (0,1),  (0,-1),  'CENTER'),
        ('ALIGN',         (6,1),  (6,-1),  'CENTER'),
        ('ALIGN',         (7,1),  (-1,-1), 'RIGHT'),
        # Grid
        ('GRID',          (0,0),  (-1,-1), 0.4, C_LBLUE),
        ('LINEBELOW',     (0,0),  (-1,0),  1.2, C_BLUE),
        # Padding
        ('TOPPADDING',    (0,0),  (-1,-1), 4),
        ('BOTTOMPADDING', (0,0),  (-1,-1), 4),
        ('LEFTPADDING',   (0,0),  (-1,-1), 4),
        ('RIGHTPADDING',  (0,0),  (-1,-1), 4),
        # Alternating rows
        ('ROWBACKGROUNDS',(0,1),  (-1,-1), [C_WHITE, C_GREY]),
        # Due column — highlight if > 0 (handled per row below)
    ]

    # Color due column red if due > 0
    for i, row in enumerate(rows[1:], start=1):
        try:
            due_val = float(str(row[-1]).replace(',',''))
            if due_val > 0:
                style_cmds.append(('TEXTCOLOR', (-1, i), (-1, i), C_RED))
                style_cmds.append(('FONTNAME',  (-1, i), (-1, i), 'Helvetica-Bold'))
            else:
                style_cmds.append(('TEXTCOLOR', (-2, i), (-2, i), C_GREEN))
        except Exception:
            pass

    tbl.setStyle(TableStyle(style_cmds))
    elems.append(tbl)

    # Footer
    elems.append(Spacer(1, 10))
    elems.append(HRFlowable(width="100%", thickness=0.5, color=C_LBLUE))
    elems.append(Paragraph(
        f"Ali Mobiles Billing Software — Confidential Business Report | {SHOP_NAME}",
        styles['footer']
    ))

    doc.build(elems)
    return os.path.abspath(filepath)


# ══════════════════════════════════════════════════════════════
# 2. PENDING PAYMENTS REPORT
# ══════════════════════════════════════════════════════════════
def generate_pending_pdf(pending_list, min_days=0):
    """
    pending_list: list of dicts from get_pending_payments()
    min_days: filter applied (for subtitle)
    Returns: absolute path to generated PDF
    """
    _ensure_dir()
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath  = os.path.join(REPORTS_DIR, f"Pending_Payments_{timestamp}.pdf")

    doc = SimpleDocTemplate(
        filepath,
        pagesize=A4,
        leftMargin=15*mm, rightMargin=15*mm,
        topMargin=12*mm,  bottomMargin=12*mm,
    )

    styles = _styles()
    subtitle = f"Filter: {min_days}+ din se pending" if min_days > 0 else "Sabhi Pending Bills"
    elems = _header_elements("💰 Baaki Khata — Pending Payments Report", subtitle=subtitle, styles=styles)

    # ── Summary ───────────────────────────────────────────────
    if pending_list:
        total_due   = sum(p['due']   for p in pending_list)
        total_paid  = sum(p['paid']  for p in pending_list)
        total_grand = sum(p['total'] for p in pending_list)
        count       = len(pending_list)

        summary_data = [
            ['Pending Records', 'Total Kul Rakam', 'Total Diya Gaya', 'Total Baaki'],
            [
                str(count),
                f"\u20b9 {total_grand:,.2f}",
                f"\u20b9 {total_paid:,.2f}",
                f"\u20b9 {total_due:,.2f}",
            ]
        ]
        sum_tbl = Table(summary_data, colWidths=[42*mm]*4)
        sum_tbl.setStyle(TableStyle([
            ('BACKGROUND',    (0,0), (-1,0), C_RED),
            ('TEXTCOLOR',     (0,0), (-1,0), C_WHITE),
            ('FONTNAME',      (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE',      (0,0), (-1,0), 9),
            ('FONTNAME',      (0,1), (-1,1), 'Helvetica-Bold'),
            ('FONTSIZE',      (0,1), (-1,1), 13),
            ('TEXTCOLOR',     (3,1), (3,1),  C_RED),
            ('TEXTCOLOR',     (2,1), (2,1),  C_GREEN),
            ('TEXTCOLOR',     (1,1), (1,1),  C_BLUE),
            ('ALIGN',         (0,0), (-1,-1), 'CENTER'),
            ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
            ('ROWBACKGROUNDS',(0,1), (-1,1), [C_GREY]),
            ('GRID',          (0,0), (-1,-1), 0.5, colors.HexColor('#fca5a5')),
            ('TOPPADDING',    (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ]))
        elems.append(sum_tbl)
        elems.append(Spacer(1, 12))

    # ── Age Legend ────────────────────────────────────────────
    legend_data = [['🔴 30+ din — Bahut Urgent', '🟠 8–30 din — Thodi Jaldi', '🟡 0–7 din — Normal']]
    leg_tbl = Table(legend_data, colWidths=[57*mm]*3)
    leg_tbl.setStyle(TableStyle([
        ('FONTNAME',      (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE',      (0,0), (-1,-1), 8),
        ('ALIGN',         (0,0), (-1,-1), 'CENTER'),
        ('BACKGROUND',    (0,0), (0,0),  colors.HexColor('#fde8e8')),
        ('BACKGROUND',    (1,0), (1,0),  colors.HexColor('#fff0e0')),
        ('BACKGROUND',    (2,0), (2,0),  colors.HexColor('#fffbe6')),
        ('GRID',          (0,0), (-1,-1), 0.4, C_LBLUE),
        ('TOPPADDING',    (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    elems.append(leg_tbl)
    elems.append(Spacer(1, 10))

    # ── Main Table ────────────────────────────────────────────
    headers = ['Bill#', 'Tarikh', 'Customer Ka Naam', 'Mobile',
               'Kul (₹)', 'Diya (₹)', 'Baaki (₹)', 'Pending Days']
    col_w   = [18, 25, 52, 30, 28, 28, 28, 28]
    col_w   = [w*mm for w in col_w]

    rows = [headers]
    if not pending_list:
        rows.append(['—'] * len(headers))
    else:
        for p in pending_list:
            rows.append([
                str(p['bill_no']),
                str(p['date'])[:10],
                str(p['name']),
                str(p['mobile']) if p['mobile'] else '—',
                f"{p['total']:,.2f}",
                f"{p['paid']:,.2f}",
                f"{p['due']:,.2f}",
                f"{p['days_pending']} din",
            ])

    tbl = Table(rows, colWidths=col_w, repeatRows=1)

    style_cmds = [
        ('BACKGROUND',    (0,0),  (-1,0),  colors.HexColor('#c0392b')),
        ('TEXTCOLOR',     (0,0),  (-1,0),  C_WHITE),
        ('FONTNAME',      (0,0),  (-1,0),  'Helvetica-Bold'),
        ('FONTSIZE',      (0,0),  (-1,0),  8.5),
        ('FONTNAME',      (0,1),  (-1,-1), 'Helvetica'),
        ('FONTSIZE',      (0,1),  (-1,-1), 8),
        ('ALIGN',         (0,0),  (-1,0),  'CENTER'),
        ('ALIGN',         (0,1),  (1,-1),  'CENTER'),
        ('ALIGN',         (4,1),  (-1,-1), 'RIGHT'),
        ('GRID',          (0,0),  (-1,-1), 0.4, colors.HexColor('#fca5a5')),
        ('LINEBELOW',     (0,0),  (-1,0),  1, colors.HexColor('#c0392b')),
        ('TOPPADDING',    (0,0),  (-1,-1), 5),
        ('BOTTOMPADDING', (0,0),  (-1,-1), 5),
        ('LEFTPADDING',   (0,0),  (-1,-1), 5),
        ('RIGHTPADDING',  (0,0),  (-1,-1), 5),
        ('ROWBACKGROUNDS',(0,1),  (-1,-1), [C_WHITE, C_GREY]),
    ]

    # Color rows by urgency
    for i, p in enumerate(pending_list, start=1):
        d = p['days_pending']
        if d > 30:
            style_cmds.append(('BACKGROUND', (0,i), (-1,i), colors.HexColor('#fff5f5')))
            style_cmds.append(('TEXTCOLOR',  (-1,i),(-1,i), C_RED))
            style_cmds.append(('FONTNAME',   (-1,i),(-1,i), 'Helvetica-Bold'))
        elif d > 7:
            style_cmds.append(('BACKGROUND', (0,i), (-1,i), colors.HexColor('#fffaf0')))
            style_cmds.append(('TEXTCOLOR',  (-1,i),(-1,i), C_ORANGE))
        else:
            style_cmds.append(('TEXTCOLOR',  (-1,i),(-1,i), C_YELLOW))

        # Due amount column always red+bold
        style_cmds.append(('TEXTCOLOR',  (-2,i),(-2,i), C_RED))
        style_cmds.append(('FONTNAME',   (-2,i),(-2,i), 'Helvetica-Bold'))

    tbl.setStyle(TableStyle(style_cmds))
    elems.append(tbl)

    # Footer
    elems.append(Spacer(1, 12))
    elems.append(HRFlowable(width="100%", thickness=0.5, color=C_LBLUE))
    elems.append(Paragraph(
        f"Ali Mobiles Billing Software — Confidential | {SHOP_NAME} | {SHOP_ADDRESS}",
        styles['footer']
    ))

    doc.build(elems)
    return os.path.abspath(filepath)
