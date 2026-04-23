import os
import sys
import datetime
import pandas as pd
from flask import Flask, render_template, request, jsonify, send_file

# ── Path Setup: Works both normally and as PyInstaller EXE ────────────
# BASE_DIR: where bundled files (templates, static, logic) are located
# WORK_DIR: writable folder next to EXE (for data/, bills/, reports/)
if getattr(sys, 'frozen', False):
    # Running as compiled .exe — bundled files are in sys._MEIPASS
    BASE_DIR = sys._MEIPASS
    WORK_DIR = os.path.dirname(sys.executable)
else:
    # Running normally with Python
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    WORK_DIR = BASE_DIR

# Change working directory so relative paths (data/, bills/, reports/) work
os.chdir(WORK_DIR)

# Make sure logic subpackage is importable
sys.path.insert(0, BASE_DIR)

from logic.bill_logic import calculate_grand_total
from logic.excel_handler import get_next_bill_no, save_bill, get_dashboard_data, get_pending_payments
from logic.pdf_generator import generate_pdf
from logic.report_generator import generate_master_pdf, generate_pending_pdf

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, 'templates'),
    static_folder=os.path.join(BASE_DIR, 'static'),
)


# ══════════════════════════════════════════════════════════════
# PAGES
# ══════════════════════════════════════════════════════════════

@app.route("/")
def index():
    return render_template("dashboard.html")


@app.route("/billing")
def billing():
    return render_template("billing.html")


@app.route("/khata")
def khata():
    return render_template("khata.html")


@app.route("/master")
def master():
    return render_template("master_data.html")


# ══════════════════════════════════════════════════════════════
# API ENDPOINTS
# ══════════════════════════════════════════════════════════════

@app.route("/api/dashboard")
def api_dashboard():
    try:
        data = get_dashboard_data()
        return jsonify({"success": True, "data": data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/pending")
def api_pending():
    try:
        data = get_pending_payments()
        return jsonify({"success": True, "data": data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/generate_bill", methods=["POST"])
def api_generate_bill():
    try:
        payload = request.get_json()

        customer_name = payload.get("customer_name", "").strip()
        mobile        = payload.get("mobile", "").strip()
        address       = payload.get("address", "").strip()
        items         = payload.get("items", [])
        tax           = float(payload.get("tax", 0.0))
        paid_amount   = payload.get("paid_amount", None)

        # Validations
        if not customer_name:
            return jsonify({"success": False, "error": "Customer ka naam zaroori hai!"}), 400
        if not items:
            return jsonify({"success": False, "error": "Kam az kam ek item add karo!"}), 400

        # Calculate totals
        _, grand_total = calculate_grand_total(items, tax)

        if paid_amount is None or paid_amount == "":
            paid_amount = grand_total
        else:
            paid_amount = float(paid_amount)

        paid_amount = min(paid_amount, grand_total)
        paid_amount = max(paid_amount, 0.0)
        due_amount  = round(grand_total - paid_amount, 2)

        bill_no = get_next_bill_no()
        bill_data = {
            "bill_no":       bill_no,
            "date":          datetime.datetime.now().strftime("%d-%m-%Y"),
            "customer_name": customer_name,
            "mobile":        mobile,
            "address":       address,
            "items":         items,
            "tax":           tax,
            "grand_total":   grand_total,
            "paid_amount":   paid_amount,
            "due_amount":    due_amount,
        }

        # Save to Excel
        save_bill(bill_data)

        # Generate PDF
        pdf_path = generate_pdf(bill_data)
        abs_pdf  = os.path.abspath(pdf_path)

        return jsonify({
            "success":     True,
            "bill_no":     bill_no,
            "grand_total": grand_total,
            "paid":        paid_amount,
            "due":         due_amount,
            "pdf_path":    abs_pdf,
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/open_pdf", methods=["POST"])
def api_open_pdf():
    """Tell OS to open the PDF file."""
    try:
        pdf_path = request.get_json().get("pdf_path", "")
        if os.path.exists(pdf_path):
            os.startfile(pdf_path)
            return jsonify({"success": True})
        return jsonify({"success": False, "error": "PDF file nahi mili."}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ══════════════════════════════════════════════════════════════
# MASTER DATA API
# ══════════════════════════════════════════════════════════════

EXCEL_FILE = "data/bills.xlsx"

@app.route("/api/master")
def api_master():
    """Return all bills data as JSON for the master data table."""
    try:
        if not os.path.exists(EXCEL_FILE):
            return jsonify({"success": True, "data": []})
        df = pd.read_excel(EXCEL_FILE)
        if df.empty:
            return jsonify({"success": True, "data": []})
        # Fill NaN
        df = df.fillna("")
        # Convert to list of dicts
        records = df.to_dict(orient="records")
        # Ensure numeric fields are proper
        for r in records:
            for key in ["Qty", "Rate", "Total Amount", "Tax", "Grand Total", "Paid Amount", "Due Amount"]:
                try:
                    r[key] = float(r[key]) if r[key] != "" else 0.0
                except Exception:
                    r[key] = 0.0
            r["Bill No"] = int(r["Bill No"]) if str(r.get("Bill No","")).replace(".","").isdigit() else r["Bill No"]
        return jsonify({"success": True, "data": records})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ══════════════════════════════════════════════════════════════
# EXPORT ROUTES
# ══════════════════════════════════════════════════════════════

@app.route("/api/export/master-pdf", methods=["POST"])
def export_master_pdf():
    """Generate a master data PDF and return it as a download."""
    try:
        if not os.path.exists(EXCEL_FILE):
            return jsonify({"success": False, "error": "Data file nahi mili."}), 404
        df = pd.read_excel(EXCEL_FILE)
        pdf_path = generate_master_pdf(df)
        # Also open it locally
        try:
            os.startfile(pdf_path)
        except Exception:
            pass
        return jsonify({"success": True, "pdf_path": pdf_path})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/export/pending-pdf", methods=["POST"])
def export_pending_pdf():
    """Generate a pending payments PDF and return file path."""
    try:
        min_days = int(request.get_json().get("min_days", 0))
        pending  = get_pending_payments()
        filtered = [p for p in pending if p["days_pending"] >= min_days]
        pdf_path = generate_pending_pdf(filtered, min_days=min_days)
        try:
            os.startfile(pdf_path)
        except Exception:
            pass
        return jsonify({"success": True, "pdf_path": pdf_path, "count": len(filtered)})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/send_whatsapp", methods=["POST"])
def api_send_whatsapp():
    try:
        from logic.whatsapp_sender import send_whatsapp_bill
        payload   = request.get_json()
        pdf_path  = payload.get("pdf_path", "")
        mobile    = payload.get("mobile", "")
        name      = payload.get("customer_name", "")

        if not os.path.exists(pdf_path):
            return jsonify({"success": False, "error": "PDF file nahi mili."}), 404

        success, response = send_whatsapp_bill(pdf_path, mobile, name)
        if success:
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": str(response)}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5055)
