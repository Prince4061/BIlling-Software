import os
import pandas as pd
import datetime as dt

EXCEL_FILE = "data/bills.xlsx"

def init_excel():
    if not os.path.exists("data"):
        os.makedirs("data")
    if not os.path.exists(EXCEL_FILE):
        df = pd.DataFrame(columns=[
            "Bill No", "Date", "Customer Name", "Address", "Mobile", 
            "Company", "Item", "Qty", "Rate", "Total Amount", "Tax",
            "Grand Total", "Paid Amount", "Due Amount"
        ])
        df.to_excel(EXCEL_FILE, index=False, sheet_name="Master")

def get_next_bill_no():
    init_excel()
    if not os.path.exists(EXCEL_FILE):
        return 1
    try:
        df = pd.read_excel(EXCEL_FILE)
        if df.empty or "Bill No" not in df.columns:
            return 1
        max_bill_no = df["Bill No"].max()
        if pd.isna(max_bill_no):
            return 1
        return int(max_bill_no) + 1
    except Exception:
        return 1

def get_dashboard_data():
    empty_data = {
        "today_sales": 0.0,
        "today_bills": 0,
        "month_sales": 0.0,
        "all_time_sales": 0.0,
        "company_sales": {}
    }
    
    if not os.path.exists(EXCEL_FILE):
        return empty_data
        
    try:
        df = pd.read_excel(EXCEL_FILE) # Reads Master sheet
    except Exception:
        return empty_data
        
    if df.empty:
        return empty_data

    # Fill NA
    df['Company'] = df['Company'].fillna("Other")
    df['Qty'] = pd.to_numeric(df['Qty'], errors='coerce').fillna(0)
    df['Total Amount'] = pd.to_numeric(df['Total Amount'], errors='coerce').fillna(0)
    df['Grand Total'] = pd.to_numeric(df['Grand Total'], errors='coerce').fillna(0)
    
    now = dt.datetime.now()
    today_str = now.strftime("%d-%m-%Y")
    month_str = now.strftime("-%m-%Y") # To match the end of string, e.g. "-04-2026"
    
    df_unique_bills = df.drop_duplicates(subset=['Bill No'])
    df_unique_bills_date_str = df_unique_bills['Date'].astype(str).str.strip()
    
    # Today KPIs
    df_today = df_unique_bills[df_unique_bills_date_str == today_str]
    today_sales = float(df_today['Grand Total'].sum())
    today_bills = int(len(df_today))
    
    # Month KPIs
    df_month = df_unique_bills[df_unique_bills_date_str.str.endswith(month_str)]
    month_sales = float(df_month['Grand Total'].sum())
    
    # All Time
    all_time_sales = float(df_unique_bills['Grand Total'].sum())
    
    # Total sales by company (item level)
    company_sales_df = df.groupby('Company')['Total Amount'].sum()
    company_sales = {str(k): float(v) for k, v in company_sales_df.to_dict().items()}
    
    return {
        "today_sales": today_sales,
        "today_bills": today_bills,
        "month_sales": month_sales,
        "all_time_sales": all_time_sales,
        "company_sales": company_sales
    }

def get_pending_payments():
    """Return list of customers who have Due Amount > 0, grouped by Bill No."""
    if not os.path.exists(EXCEL_FILE):
        return []
    try:
        df = pd.read_excel(EXCEL_FILE)
    except Exception:
        return []
    if df.empty:
        return []
    if "Due Amount" not in df.columns:
        return []

    df["Due Amount"]  = pd.to_numeric(df["Due Amount"],  errors="coerce").fillna(0)
    df["Grand Total"] = pd.to_numeric(df["Grand Total"], errors="coerce").fillna(0)
    df["Paid Amount"] = pd.to_numeric(df["Paid Amount"], errors="coerce").fillna(0)

    # One row per bill
    df_bills = df.drop_duplicates(subset=["Bill No"])

    # Filter only bills with due > 0
    df_due = df_bills[df_bills["Due Amount"] > 0].copy()

    today = dt.datetime.now().date()

    result = []
    for _, row in df_due.iterrows():
        # Calculate days pending
        raw_date = str(row.get("Date", "")).strip()
        try:
            bill_date = dt.datetime.strptime(raw_date[:10], "%d-%m-%Y").date()
            days_pending = (today - bill_date).days
        except Exception:
            days_pending = 0

        result.append({
            "bill_no":      row.get("Bill No", ""),
            "date":         raw_date,
            "name":         str(row.get("Customer Name", "")),
            "mobile":       str(row.get("Mobile", "")),
            "total":        float(row.get("Grand Total", 0)),
            "paid":         float(row.get("Paid Amount",  0)),
            "due":          float(row.get("Due Amount",   0)),
            "days_pending": days_pending,
        })

    # Sort: most days pending first
    result.sort(key=lambda x: x["days_pending"], reverse=True)
    return result

def save_bill(bill_data):
    init_excel()
    
    # Read all sheets into a dictionary
    try:
        all_sheets = pd.read_excel(EXCEL_FILE, sheet_name=None)
    except Exception:
        all_sheets = {"Master": pd.DataFrame()}

    # Identify the master sheet (Sheet1 from old versions, or Master)
    if "Master" in all_sheets:
        master_sheet_name = "Master"
    elif "Sheet1" in all_sheets:
        master_sheet_name = "Sheet1"
    else:
        master_sheet_name = list(all_sheets.keys())[0] if all_sheets else "Master"
        if master_sheet_name not in all_sheets:
            all_sheets[master_sheet_name] = pd.DataFrame()

    rows = []
    company_rows = {}

    for item in bill_data["items"]:
        comp = item.get("company", "Other").strip()
        if not comp:
             comp = "Other"
             
        item_display = item["name"]
        if item.get("desc"):
            item_display = f"{item_display} ({item['desc']})"
             
        row = {
            "Bill No": bill_data["bill_no"],
            "Date": bill_data["date"],
            "Customer Name": bill_data["customer_name"],
            "Address": bill_data["address"],
            "Mobile": bill_data["mobile"],
            "Company": comp,
            "Item": item_display,
            "Qty": item["qty"],
            "Rate": item["rate"],
            "Total Amount": item["amount"],
            "Tax": bill_data["tax"],
            "Grand Total": bill_data["grand_total"],
            "Paid Amount": bill_data.get("paid_amount", bill_data["grand_total"]),
            "Due Amount": bill_data.get("due_amount", 0.0)
        }
        rows.append(row)
        
        if comp not in company_rows:
            company_rows[comp] = []
        company_rows[comp].append(row)
        
    # Append to Master
    df_new_master = pd.DataFrame(rows)
    if not all_sheets[master_sheet_name].empty:
        all_sheets[master_sheet_name] = pd.concat([all_sheets[master_sheet_name], df_new_master], ignore_index=True)
    else:
        all_sheets[master_sheet_name] = df_new_master
    
    # Append to Company specific sheets
    for comp, c_rows in company_rows.items():
        safe_comp = "".join([c for c in comp if c.isalnum() or c in " _-"])[:30]
        if not safe_comp:
            safe_comp = "Other"
            
        df_comp_new = pd.DataFrame(c_rows)
        if safe_comp in all_sheets and not all_sheets[safe_comp].empty:
            all_sheets[safe_comp] = pd.concat([all_sheets[safe_comp], df_comp_new], ignore_index=True)
        else:
            all_sheets[safe_comp] = df_comp_new
            
    # Write back all sheets, keeping master sheet first
    with pd.ExcelWriter(EXCEL_FILE) as writer:
        all_sheets[master_sheet_name].to_excel(writer, sheet_name=master_sheet_name, index=False)
        for sheet_name, df in all_sheets.items():
            if sheet_name != master_sheet_name:
                df.to_excel(writer, sheet_name=sheet_name, index=False)

