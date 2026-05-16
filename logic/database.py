import os
import sys
import sqlite3
import pandas as pd
import datetime as dt
import shutil

DB_FILE = "data/bills.db"

def get_db_path():
    """Get database path - works in both dev and exe mode"""
    if hasattr(sys, 'frozen'):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, DB_FILE)

def init_db():
    if not os.path.exists("data"):
        os.makedirs("data")

    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bill_no INTEGER,
            date TEXT,
            customer_name TEXT,
            address TEXT,
            mobile TEXT,
            company TEXT,
            item TEXT,
            qty REAL,
            rate REAL,
            total_amount REAL,
            tax REAL,
            grand_total REAL,
            paid_amount REAL,
            due_amount REAL,
            dob TEXT
        )
    ''')

    # Create index for fast queries
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_bill_no ON bills(bill_no)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_date ON bills(date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_company ON bills(company)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_mobile ON bills(mobile)')

    conn.commit()
    conn.close()

    # Migrate from Excel if exists
    migrate_from_excel()

def migrate_from_excel():
    """Convert existing Excel data to SQLite"""
    excel_file = "data/bills.xlsx"
    if not os.path.exists(excel_file):
        return

    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check if already migrated
    cursor.execute("SELECT COUNT(*) FROM bills")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return

    try:
        df = pd.read_excel(excel_file)
        df.to_sql('bills', conn, if_exists='append', index=False)
        print(f"Migrated {len(df)} rows from Excel to SQLite")
    except Exception as e:
        print(f"Migration error: {e}")
    finally:
        conn.close()

def get_next_bill_no():
    init_db()
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT MAX(bill_no) FROM bills WHERE bill_no IS NOT NULL")
    result = cursor.fetchone()[0]
    conn.close()

    return (result or 0) + 1

def save_bill(bill_data):
    init_db()
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    for item in bill_data["items"]:
        comp = item.get("company", "Other").strip()
        if not comp:
            comp = "Other"

        item_display = item["name"]
        if item.get("desc"):
            item_display = f"{item_display} ({item['desc']})"

        cursor.execute('''
            INSERT INTO bills (
                bill_no, date, customer_name, address, mobile, company,
                item, qty, rate, total_amount, tax, grand_total,
                paid_amount, due_amount, dob
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            bill_data["bill_no"], bill_data["date"], bill_data["customer_name"],
            bill_data["address"], bill_data["mobile"], comp,
            item_display, item["qty"], item["rate"], item["amount"],
            bill_data["tax"], bill_data["grand_total"],
            bill_data.get("paid_amount", bill_data["grand_total"]),
            bill_data.get("due_amount", 0.0), bill_data.get("dob", "")
        ))

    conn.commit()
    conn.close()

def get_dashboard_data():
    init_db()
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)

    now = dt.datetime.now()
    today_str = now.strftime("%d-%m-%Y")
    month_str = now.strftime("-%m-%Y")

    # Get unique bills
    query = "SELECT DISTINCT bill_no, date, grand_total, paid_amount, due_amount, tax FROM bills"
    df = pd.read_sql(query, conn)
    conn.close()

    if df.empty:
        return {
            "today_sales": 0.0, "today_bills": 0, "month_sales": 0.0,
            "all_time_sales": 0.0, "company_sales": {}, "today_birthdays": []
        }

    df['date_str'] = df['date'].astype(str).str.strip()

    # Today
    df_today = df[df['date_str'] == today_str]
    today_sales = float(df_today['grand_total'].sum())
    today_bills = len(df_today)

    # Month
    df_month = df[df['date_str'].str.endswith(month_str, na=False)]
    month_sales = float(df_month['grand_total'].sum())

    # All time
    all_time_sales = float(df['grand_total'].sum())

    # Company sales
    conn = sqlite3.connect(db_path)
    comp_df = pd.read_sql("SELECT company, SUM(total_amount) as total FROM bills GROUP BY company", conn)
    conn.close()
    company_sales = {str(k): float(v) for k, v in zip(comp_df['company'], comp_df['total'])}

    # Birthdays
    today_birthdays = []
    if 'DOB' in df.columns:
        dob_match = now.strftime("-%m-%d")
        conn = sqlite3.connect(db_path)
        bday_df = pd.read_sql(f"SELECT DISTINCT customer_name, mobile FROM bills WHERE dob LIKE '%{dob_match}'", conn)
        conn.close()
        for _, row in bday_df.iterrows():
            if row['customer_name'] and str(row['customer_name']).lower() != 'nan':
                today_birthdays.append({"name": row['customer_name'], "mobile": str(row['mobile'])})

    return {
        "today_sales": today_sales,
        "today_bills": today_bills,
        "month_sales": month_sales,
        "all_time_sales": all_time_sales,
        "company_sales": company_sales,
        "today_birthdays": today_birthdays
    }

def get_analytics_data():
    init_db()
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)

    # KPIs
    kpi_df = pd.read_sql("""
        SELECT DISTINCT bill_no, grand_total, paid_amount, due_amount, tax
        FROM bills
    """, conn)

    kpis = {
        "total_revenue": float(kpi_df['grand_total'].sum()) if not kpi_df.empty else 0.0,
        "total_received": float(kpi_df['paid_amount'].sum()) if not kpi_df.empty else 0.0,
        "total_due": float(kpi_df['due_amount'].sum()) if not kpi_df.empty else 0.0,
        "total_tax": float(kpi_df['tax'].sum()) if not kpi_df.empty else 0.0,
        "total_bills": len(kpi_df),
        "total_items_sold": 0
    }

    qty_df = pd.read_sql("SELECT SUM(qty) as total FROM bills", conn)
    kpis["total_items_sold"] = int(qty_df['total'].iloc[0]) if not qty_df.empty else 0

    # Top items
    top_items = pd.read_sql("""
        SELECT item, SUM(qty) as qty FROM bills
        GROUP BY item ORDER BY qty DESC LIMIT 5
    """, conn)

    # Company revenue
    company_df = pd.read_sql("""
        SELECT company, SUM(total_amount) as revenue FROM bills
        GROUP BY company ORDER BY revenue DESC
    """, conn)

    conn.close()

    # Last 7 days trend
    today = dt.datetime.now().date()
    last_7_days = [(today - dt.timedelta(days=i)) for i in range(6, -1, -1)]
    trend_labels = [d.strftime('%d %b') for d in last_7_days]
    trend_revenue = []

    conn = sqlite3.connect(db_path)
    for d in last_7_days:
        date_str = d.strftime("%d-%m-%Y")
        daily = pd.read_sql(f"""
            SELECT DISTINCT bill_no, grand_total FROM bills WHERE date LIKE '%{date_str}%'
        """, conn)
        trend_revenue.append(float(daily['grand_total'].sum()) if not daily.empty else 0.0)
    conn.close()

    return {
        "kpis": kpis,
        "trends": {"labels": trend_labels, "revenue": trend_revenue},
        "top_items": {
            "labels": top_items['item'].tolist() if not top_items.empty else [],
            "quantities": [float(x) for x in top_items['qty'].tolist()] if not top_items.empty else []
        },
        "companies": {
            "labels": company_df['company'].tolist() if not company_df.empty else [],
            "revenue": [float(x) for x in company_df['revenue'].tolist()] if not company_df.empty else []
        }
    }

def get_pending_payments():
    init_db()
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)

    df = pd.read_sql("""
        SELECT DISTINCT bill_no, date, customer_name, mobile,
               grand_total, paid_amount, due_amount
        FROM bills WHERE due_amount > 0
    """, conn)
    conn.close()

    if df.empty:
        return []

    today = dt.datetime.now().date()
    result = []

    for _, row in df.iterrows():
        try:
            bill_date = dt.datetime.strptime(str(row['date'])[:10], "%d-%m-%Y").date()
            days_pending = (today - bill_date).days
        except:
            days_pending = 0

        result.append({
            "bill_no": row['bill_no'],
            "date": row['date'],
            "name": str(row['customer_name']),
            "mobile": str(row['mobile']),
            "total": float(row['grand_total']),
            "paid": float(row['paid_amount']),
            "due": float(row['due_amount']),
            "days_pending": days_pending
        })

    result.sort(key=lambda x: x["days_pending"], reverse=True)
    return result

def get_all_bills():
    """Get all bills data for master data table"""
    init_db()
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)

    # Return all columns like the original Excel format
    df = pd.read_sql("""
        SELECT bill_no, date, customer_name, address, mobile, company,
               item, qty, rate, total_amount, tax, grand_total,
               paid_amount, due_amount, dob
        FROM bills ORDER BY bill_no DESC, id ASC
    """, conn)
    conn.close()

    # Rename columns to match Excel format
    column_mapping = {
        "bill_no": "Bill No",
        "date": "Date",
        "customer_name": "Customer Name",
        "address": "Address",
        "mobile": "Mobile",
        "company": "Company",
        "item": "Item",
        "qty": "Qty",
        "rate": "Rate",
        "total_amount": "Total Amount",
        "tax": "Tax",
        "grand_total": "Grand Total",
        "paid_amount": "Paid Amount",
        "due_amount": "Due Amount",
        "dob": "DOB"
    }
    df = df.rename(columns=column_mapping)

    # Ensure numeric fields are proper
    numeric_cols = ["Qty", "Rate", "Total Amount", "Tax", "Grand Total", "Paid Amount", "Due Amount"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)

    return df.to_dict(orient="records")

def search_bills(query):
    """Search bills by customer name, mobile or bill number"""
    init_db()
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)

    search_term = f"%{query}%"
    df = pd.read_sql(f"""
        SELECT DISTINCT bill_no, date, customer_name, mobile,
               grand_total, paid_amount, due_amount
        FROM bills
        WHERE customer_name LIKE ? OR mobile LIKE ? OR bill_no LIKE ?
        ORDER BY bill_no DESC
    """, conn, params=(search_term, search_term, search_term))
    conn.close()
    return df.to_dict('records')

def delete_bill(bill_no):
    """Delete a bill by bill number"""
    init_db()
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM bills WHERE bill_no = ?", (bill_no,))
    conn.commit()
    conn.close()

def get_bill_details(bill_no):
    """Get all items for a specific bill"""
    init_db()
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)

    df = pd.read_sql("SELECT * FROM bills WHERE bill_no = ?", conn, params=(bill_no,))
    conn.close()
    return df.to_dict('records')