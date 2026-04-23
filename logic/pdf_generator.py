import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors

def generate_pdf(bill_data):
    if not os.path.exists("bills"):
        os.makedirs("bills")
        
    filename = f"bills/Bill_{bill_data['bill_no']}.pdf"
    
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    
    # Colors
    primary_blue = colors.HexColor('#13488B')
    light_blue = colors.HexColor('#A8C3E5')
    text_dark = colors.black
    bg_color = colors.HexColor('#EBF2FA')
    
    MARGIN = 35
    
    # 1. Outer Border
    c.setStrokeColor(primary_blue)
    c.setLineWidth(1.5)
    c.rect(MARGIN, MARGIN, width - 2*MARGIN, height - 2*MARGIN, stroke=1, fill=0)
    c.setLineWidth(1)
    
    # 2. Header
    y = height - 55
    c.setFont("Helvetica", 10)
    c.setFillColor(text_dark)
    c.drawString(MARGIN + 10, y, "GSTIN:22AUVPD7913L1Z9")
    
    c.drawRightString(width - MARGIN - 10, y, "Mob. 7869000000")
    c.drawRightString(width - MARGIN - 10, y - 12, "Wtsp. 9893000005")
    
    # MI Logo placeholder & Shop Name
    y -= 35
    c.setFillColor(primary_blue)
    c.rect(MARGIN + 10, y - 18, 28, 28, stroke=0, fill=1)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(MARGIN + 15, y - 10, "MI")
    
    c.setFillColor(primary_blue)
    c.setFont("Helvetica-Bold", 26)
    c.drawCentredString(width/2 + 20, y - 12, "H.H. MOBILE & Enterprises")
    
    # Blue Address Bar
    y -= 25
    c.setFillColor(primary_blue)
    c.rect(MARGIN, y - 15, width - 2*MARGIN, 22, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(width/2, y - 10, "Near Makkad Complex Main Road, Takhatpur, 495330")
    
    # 3. Categories Bullet Points
    y -= 30
    c.setFillColor(primary_blue)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(MARGIN + 15, y, "• T.V.")
    c.drawString(MARGIN + 15, y - 18, "• A.C.")
    
    c.drawString(MARGIN + 120, y, "• Washing Machine")
    c.drawString(MARGIN + 120, y - 18, "• Inverter Battery")
    
    c.drawString(MARGIN + 320, y, "• Mobile")
    # Empty space
    
    c.drawString(MARGIN + 430, y, "• Fridge")
    c.drawString(MARGIN + 430, y - 18, "• Mobile")
    
    # Horizontal line below categories
    y -= 25
    c.setStrokeColor(primary_blue)
    c.line(MARGIN, y, width - MARGIN, y)
    
    # 4. Customer Info
    y -= 20
    c.setFillColor(text_dark)
    c.setFont("Helvetica", 11)
    c.drawString(MARGIN + 10, y, "No.")
    
    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(colors.red)
    c.drawString(MARGIN + 40, y, str(bill_data['bill_no']))
    
    c.setFillColor(text_dark)
    c.setFont("Helvetica", 11)
    c.drawString(width - MARGIN - 170, y, "Date: " + str(bill_data['date']))
    
    def dotted_line(x1, y1, x2):
        c.setStrokeColor(colors.gray)
        c.setDash(1, 2)
        c.line(x1, y1, x2, y1)
        c.setDash()
        c.setStrokeColor(primary_blue)
        
    y -= 25
    c.drawString(MARGIN + 10, y, "M/s")
    c.drawString(MARGIN + 40, y + 2, str(bill_data['customer_name']))
    dotted_line(MARGIN + 35, y, width - MARGIN - 10)
    
    y -= 25
    c.drawString(MARGIN + 10, y, "Add.")
    c.drawString(MARGIN + 40, y + 2, str(bill_data['address']))
    dotted_line(MARGIN + 35, y, width - MARGIN - 190)
    
    c.drawString(width - MARGIN - 180, y, "Wtsp. No.")
    c.drawString(width - MARGIN - 120, y + 2, str(bill_data['mobile']))
    dotted_line(width - MARGIN - 125, y, width - MARGIN - 10)
    
    # 5. Table Layout Setup
    y -= 20
    table_top = y
    row_h = 30
    header_h = 24
    header_bottom = table_top - header_h
    rows_bottom = header_bottom - (6 * row_h)
    graphics_h = 100
    table_bottom = rows_bottom - graphics_h
    
    # Columns X Coordinates
    col_sno = MARGIN
    col_part = MARGIN + 45
    col_qty = MARGIN + 280
    col_rate = MARGIN + 340
    col_amt = MARGIN + 420
    col_end = width - MARGIN
    
    # Header Background
    c.setFillColor(primary_blue)
    c.rect(col_sno, header_bottom, col_end - col_sno, header_h, fill=1, stroke=0)
    
    # Header Text
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString((col_sno + col_part)/2, header_bottom + 8, "S.No.")
    c.drawCentredString((col_part + col_qty)/2, header_bottom + 8, "PARTICULARS")
    c.drawCentredString((col_qty + col_rate)/2, header_bottom + 8, "Qty")
    c.drawCentredString((col_rate + col_amt)/2, header_bottom + 8, "RATE")
    c.drawCentredString((col_amt + col_end)/2, header_bottom + 8, "Amount")
    
    # Rows text & lines
    c.setFillColor(text_dark)
    c.setFont("Helvetica", 11)
    
    from reportlab.lib.utils import simpleSplit
    
    curr_y = header_bottom
    items = bill_data.get('items', [])
    
    for i in range(6):
        item_h = 30
        desc_lines = []
        if i < len(items):
            item = items[i]
            desc = item.get('desc', '').strip()
            if desc:
                for line in desc.split('\n'):
                    desc_lines.extend(simpleSplit(line, "Helvetica", 8, 220))
                required_h = 24 + len(desc_lines) * 12
                if required_h > 30:
                    item_h = required_h
                    
        row_top = curr_y
        curr_y -= item_h
        
        # Horizontal light blue row divider
        c.setStrokeColor(light_blue)
        c.line(MARGIN, curr_y, col_end, curr_y)
        
        text_y = row_top - 20
        c.drawCentredString((col_sno + col_part)/2, text_y, str(i + 1) + ".")
        
        if i < len(items):
            item = items[i]
            display_name = f"{item.get('company', '')} {item['name']}".strip()
            
            c.drawString(col_part + 10, text_y, display_name)
            
            if desc_lines:
                c.setFont("Helvetica", 8)
                c.setFillColor(colors.gray)
                desc_y = text_y - 12
                for line in desc_lines:
                    c.drawString(col_part + 10, desc_y, line)
                    desc_y -= 12
                c.setFillColor(text_dark)
                c.setFont("Helvetica", 11)
                
            c.drawCentredString((col_qty + col_rate)/2, text_y, str(item['qty']))
            c.drawCentredString((col_rate + col_amt)/2, text_y, f"{item['rate']:.1f}")
            c.drawCentredString((col_amt + col_end)/2, text_y, f"{item['amount']:.1f}")

    rows_bottom = curr_y
    table_bottom = rows_bottom - graphics_h
            
    # Bottom Right Cells - 4 rows: Tax / G.Total / Paid / Due
    paid_amount = bill_data.get('paid_amount', bill_data['grand_total'])
    due_amount  = bill_data.get('due_amount', 0.0)
    
    c.setStrokeColor(primary_blue)
    c.line(MARGIN, rows_bottom, col_end, rows_bottom)
    
    row_cell_h = graphics_h / 4  # 4 rows now
    for i in range(1, 4):  # 3 dividers inside
        c.line(col_qty, rows_bottom - i * row_cell_h, col_end, rows_bottom - i * row_cell_h)
    c.line(MARGIN, table_bottom, col_end, table_bottom)
    
    labels  = ["Tax", "G.Total", "Paid", "Due"]
    values  = [
        f"{bill_data['tax']:.1f}",
        f"{bill_data['grand_total']:.1f}",
        f"{paid_amount:.1f}",
        f"{due_amount:.1f}"
    ]
    fg_clrs = [text_dark, text_dark, colors.HexColor('#1ca350'), colors.HexColor('#c0392b')]
    
    c.setFont("Helvetica", 11)
    for idx, (lbl, val, clr) in enumerate(zip(labels, values, fg_clrs)):
        cy = rows_bottom - (idx * row_cell_h) - row_cell_h / 2 - 4
        c.setFillColor(text_dark)
        c.drawCentredString((col_qty + col_amt)/2, cy, lbl)
        c.setFillColor(clr)
        c.setFont("Helvetica-Bold", 12)
        c.drawCentredString((col_amt + col_end)/2, cy, val)
        c.setFont("Helvetica", 11)
    
    # Graphics Box Placeholder Text
    c.setFillColor(primary_blue)
    c.setFont("Helvetica", 11)
    c.drawCentredString(MARGIN + 120, table_bottom + 40, "Warranty at Company's")
    c.drawCentredString(MARGIN + 120, table_bottom + 25, "Authorised Service Center")
    c.setFillColor(text_dark)
    
    # Vertical Lines for Table
    c.setLineWidth(1)
    c.setStrokeColor(primary_blue)
    # Outer borders
    c.line(MARGIN, table_top, MARGIN, table_bottom)
    c.line(col_end, table_top, col_end, table_bottom)
    c.line(MARGIN, table_top, col_end, table_top)
    
    # Inner column separators
    c.line(col_part, table_top, col_part, rows_bottom) # Stops before graphics
    c.line(col_qty, table_top, col_qty, table_bottom)  # Goes to bottom
    c.line(col_rate, table_top, col_rate, rows_bottom) # Stops before Tax label
    c.line(col_amt, table_top, col_amt, table_bottom)  # Goes to bottom
    
    # 6. Footer Section
    # Left Details
    c.setFont("Helvetica", 10)
    terms_y = table_bottom - 20
    c.drawString(MARGIN + 10, terms_y, "• Goods once sold will not be taken back.")
    c.drawString(MARGIN + 10, terms_y - 15, "• Guarantee Service Center Only.")
    c.drawString(MARGIN + 10, terms_y - 30, "• S.T.Extra.")
    c.drawString(MARGIN + 10, terms_y - 45, "• 0% BAJAJ Finance available.")
    
    # Bajaj Logo Placeholder
    b_y = terms_y - 50
    c.setFillColor(primary_blue)
    c.circle(MARGIN + 210, b_y + 10, 14, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(MARGIN + 210, b_y + 4, "B")
    
    c.setFillColor(primary_blue)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(MARGIN + 230, b_y + 12, "BAJAJ")
    c.setFont("Helvetica-Bold", 13)
    c.drawString(MARGIN + 230, b_y, "FINSERV")
    
    c.setFont("Helvetica", 8)
    c.setFillColor(text_dark)
    c.drawCentredString(MARGIN + 250, b_y + 35, "Customer Signature")
    
    # (Proprietor info removed as requested)
    
    c.save()
    return filename
