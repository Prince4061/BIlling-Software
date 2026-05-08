import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from logic.bill_logic import calculate_item_total, calculate_grand_total
from logic.excel_handler import get_next_bill_no, save_bill
from logic.pdf_generator import generate_pdf
from logic.whatsapp_sender import send_whatsapp_bill


class AppUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Ali Mobiles Billing Software")
        self.root.geometry("1000x720")
        self.root.configure(bg="#f4f6f9")

        # ── Style ──────────────────────────────────────────────────
        style = ttk.Style()
        if "clam" in style.theme_names():
            style.theme_use("clam")

        style.configure("TLabelframe",       background="#f4f6f9")
        style.configure("TLabelframe.Label", font=("Helvetica", 12, "bold"),
                        background="#f4f6f9", foreground="#13488B")
        style.configure("TLabel",            background="#f4f6f9", font=("Helvetica", 11))
        style.configure("Treeview.Heading",  font=("Helvetica", 11, "bold"),
                        background="#A8C3E5", foreground="#13488B")
        style.configure("Treeview",          font=("Helvetica", 11), rowheight=28)

        # ── Data ───────────────────────────────────────────────────
        self.items         = []
        self.last_pdf_path = None
        self.last_customer = None
        self.last_mobile   = None

        self.create_widgets()

    # ══════════════════════════════════════════════════════════════
    # WIDGETS
    # ══════════════════════════════════════════════════════════════
    def create_widgets(self):

        # Header ─────────────────────────────────────────────────
        hdr = tk.Frame(self.root, bg="#13488B")
        hdr.pack(fill="x")
        tk.Label(hdr,
                 text="H.H. MOBILE & Enterprises — Billing Software",
                 font=("Helvetica", 20, "bold"),
                 bg="#13488B", fg="white", pady=14).pack()

        # Customer Section ───────────────────────────────────────
        cust_frame = ttk.LabelFrame(self.root,
                                    text=" 👤 Customer Ki Details ", padding=15)
        cust_frame.pack(fill="x", padx=20, pady=10)

        ttk.Label(cust_frame, text="Naam:").grid(row=0, column=0, sticky="e", padx=5)
        self.ent_name = ttk.Entry(cust_frame, width=35, font=("Helvetica", 11))
        self.ent_name.grid(row=0, column=1, padx=5, pady=8)

        ttk.Label(cust_frame, text="Mobile No:").grid(row=0, column=2, sticky="e", padx=5)
        self.ent_mobile = ttk.Entry(cust_frame, width=22, font=("Helvetica", 11))
        self.ent_mobile.grid(row=0, column=3, padx=5, pady=8)

        ttk.Label(cust_frame, text="Pata (Address):").grid(row=1, column=0, sticky="e", padx=5)
        self.ent_address = ttk.Entry(cust_frame, width=35, font=("Helvetica", 11))
        self.ent_address.grid(row=1, column=1, padx=5, pady=6)

        # Item Section ───────────────────────────────────────────
        item_frame = ttk.LabelFrame(self.root, text=" 📦 Item Add Karo ", padding=12)
        item_frame.pack(fill="x", padx=20, pady=5)

        ttk.Label(item_frame, text="Company:").grid(row=0, column=0, sticky="e")
        self.combo_company = ttk.Combobox(
            item_frame,
            values=["Xiaomi", "iPhone", "Vivo", "Samsung",
                    "Oppo", "Realme", "OnePlus", "Nokia", "Other"],
            width=12, font=("Helvetica", 11))
        self.combo_company.grid(row=0, column=1, padx=5, pady=5)
        self.combo_company.current(0)

        ttk.Label(item_frame, text="Item Ka Naam:").grid(row=0, column=2, sticky="e", padx=4)
        self.ent_item_name = ttk.Entry(item_frame, width=20, font=("Helvetica", 11))
        self.ent_item_name.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(item_frame, text="Qty:").grid(row=0, column=4, sticky="e", padx=4)
        self.ent_qty = ttk.Entry(item_frame, width=8, font=("Helvetica", 11))
        self.ent_qty.grid(row=0, column=5, padx=5, pady=5)

        ttk.Label(item_frame, text="Rate (₹):").grid(row=0, column=6, sticky="e", padx=4)
        self.ent_rate = ttk.Entry(item_frame, width=12, font=("Helvetica", 11))
        self.ent_rate.grid(row=0, column=7, padx=5, pady=5)

        tk.Button(item_frame, text=" + Add Karo ",
                  bg="#A8C3E5", fg="#13488B",
                  font=("Helvetica", 11, "bold"), relief="flat",
                  padx=10, cursor="hand2",
                  command=self.add_item
                  ).grid(row=0, column=8, padx=12)

        # Item Table ─────────────────────────────────────────────
        tbl_frame = tk.Frame(self.root, bg="#f4f6f9")
        tbl_frame.pack(fill="both", expand=True, padx=20, pady=8)

        cols = ("company", "name", "qty", "rate", "amount")
        self.tree = ttk.Treeview(tbl_frame, columns=cols, show="headings")
        self.tree.heading("company", text="Company")
        self.tree.heading("name",    text="Item Ka Naam")
        self.tree.heading("qty",     text="Qty")
        self.tree.heading("rate",    text="Rate (₹)")
        self.tree.heading("amount",  text="Rakam (₹)")

        self.tree.column("company", width=120, anchor="center")
        self.tree.column("name",    width=260)
        self.tree.column("qty",     width=70,  anchor="center")
        self.tree.column("rate",    width=110, anchor="center")
        self.tree.column("amount",  width=120, anchor="center")

        vsb = ttk.Scrollbar(tbl_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)

        # Bottom Controls ────────────────────────────────────────
        bot = tk.Frame(self.root, bg="#f4f6f9")
        bot.pack(fill="x", padx=20, pady=10)

        # Left side: Tax / Paid / Totals / Shortcut buttons
        ttk.Label(bot, text="Tax (₹):").pack(side="left")
        self.ent_tax = ttk.Entry(bot, width=9, font=("Helvetica", 12))
        self.ent_tax.insert(0, "0.0")
        self.ent_tax.pack(side="left", padx=(4, 8))

        ttk.Label(bot, text="Paid (₹):").pack(side="left")
        self.ent_paid = ttk.Entry(bot, width=10, font=("Helvetica", 12))
        self.ent_paid.pack(side="left", padx=(4, 8))

        self.lbl_total = tk.Label(bot, text="Total: ₹0.00",
                                  font=("Helvetica", 13, "bold"),
                                  bg="#f4f6f9", fg="#eb3b5a")
        self.lbl_total.pack(side="left", padx=5)

        self.lbl_due = tk.Label(bot, text="Baaki: ₹0.00",
                                font=("Helvetica", 13, "bold"),
                                bg="#f4f6f9", fg="#1ca350")
        self.lbl_due.pack(side="left", padx=5)

        tk.Button(bot, text=" 📊 Dashboard ",
                  bg="#0984e3", fg="white",
                  font=("Helvetica", 10, "bold"), relief="flat",
                  padx=8, pady=6, cursor="hand2",
                  command=self.show_dashboard
                  ).pack(side="left", padx=(12, 4))

        tk.Button(bot, text=" 💰 Baaki Dekho ",
                  bg="#c0392b", fg="white",
                  font=("Helvetica", 10, "bold"), relief="flat",
                  padx=8, pady=6, cursor="hand2",
                  command=self.show_pending_payments
                  ).pack(side="left", padx=4)

        # Right side: Action buttons
        tk.Button(bot, text=" ✓ Bill Banao ",
                  bg="#1ca350", fg="white",
                  font=("Helvetica", 11, "bold"), relief="flat",
                  padx=10, pady=7, cursor="hand2",
                  command=self.generate_bill
                  ).pack(side="right")

        self.btn_whatsapp = tk.Button(bot, text=" 💬 WhatsApp ",
                                      bg="#25D366", fg="white",
                                      font=("Helvetica", 11, "bold"), relief="flat",
                                      padx=10, pady=7, cursor="hand2",
                                      state=tk.DISABLED,
                                      command=self.send_via_whatsapp)
        self.btn_whatsapp.pack(side="right", padx=8)

        tk.Button(bot, text=" ✖ Clear Karo ",
                  bg="#a4b0be", fg="white",
                  font=("Helvetica", 11, "bold"), relief="flat",
                  padx=10, pady=7, cursor="hand2",
                  command=self.clear_all
                  ).pack(side="right", padx=8)

        # Bindings
        self.ent_tax.bind("<KeyRelease>",  lambda e: self.update_totals())
        self.ent_paid.bind("<KeyRelease>", lambda e: self.update_totals())

    # ══════════════════════════════════════════════════════════════
    # ITEM LOGIC
    # ══════════════════════════════════════════════════════════════
    def add_item(self):
        # Edge case: max 6 items
        if len(self.items) >= 6:
            messagebox.showwarning(
                "Item Limit Poora Ho Gaya!",
                "Bill me maximum 6 items hi add ho sakte hain.\n"
                "Pehle 'Bill Banao' dabao, phir naya bill shuru karo."
            )
            return

        company = self.combo_company.get().strip()
        name    = self.ent_item_name.get().strip()
        qty_str = self.ent_qty.get().strip()
        rate_str = self.ent_rate.get().strip()

        # Edge case: empty fields
        if not name:
            messagebox.showwarning("Item Naam Chahiye!", "Item ka naam likhna zaroori hai.")
            self.ent_item_name.focus()
            return
        if not qty_str:
            messagebox.showwarning("Qty Chahiye!", "Kitne item hain? Qty likhna zaroori hai.")
            self.ent_qty.focus()
            return
        if not rate_str:
            messagebox.showwarning("Rate Chahiye!", "Item ka rate likhna zaroori hai.")
            self.ent_rate.focus()
            return

        # Edge case: non-numeric qty/rate
        try:
            qty  = float(qty_str)
            rate = float(rate_str)
        except ValueError:
            messagebox.showerror("Galat Value!", "Qty aur Rate sirf number mein likhein.")
            return

        # Edge case: negative or zero qty/rate
        if qty <= 0:
            messagebox.showerror("Galat Qty!", "Qty 0 ya minus nahi ho sakta.")
            return
        if rate < 0:
            messagebox.showerror("Galat Rate!", "Rate minus nahi ho sakta.")
            return

        amount = round(qty * rate, 2)

        self.items.append({
            "company": company,
            "name":    name,
            "qty":     qty,
            "rate":    rate,
            "amount":  amount
        })
        self.tree.insert("", "end", values=(company, name, qty, f"{rate:.2f}", f"{amount:.2f}"))

        # Clear item fields, keep focus
        self.combo_company.current(0)
        self.ent_item_name.delete(0, tk.END)
        self.ent_qty.delete(0, tk.END)
        self.ent_rate.delete(0, tk.END)
        self.update_totals()
        self.ent_item_name.focus()

    def clear_all(self):
        """Items + Tax + Paid reset karo."""
        self.items = []
        for row in self.tree.get_children():
            self.tree.delete(row)
        self.ent_tax.delete(0, tk.END)
        self.ent_tax.insert(0, "0.0")
        self.ent_paid.delete(0, tk.END)
        self.update_totals()

    def update_totals(self):
        try:
            tax = float(self.ent_tax.get())
        except ValueError:
            tax = 0.0

        try:
            paid = float(self.ent_paid.get()) if self.ent_paid.get().strip() else 0.0
        except ValueError:
            paid = 0.0

        _, grand_total = calculate_grand_total(self.items, tax)

        # Edge case: paid > total → due = 0 (not negative)
        due = max(0.0, round(grand_total - paid, 2))

        self.lbl_total.config(text=f"Total: ₹{grand_total:.2f}")
        self.lbl_due.config(
            text=f"Baaki: ₹{due:.2f}",
            fg="#d35400" if due > 0 else "#1ca350"
        )

    # ══════════════════════════════════════════════════════════════
    # BILL GENERATION
    # ══════════════════════════════════════════════════════════════
    def generate_bill(self):
        # Edge case: no items
        if not self.items:
            messagebox.showwarning("Item Nahi Hai!", "Pehle koi item add karo, phir bill banao.")
            return

        name = self.ent_name.get().strip()
        # Edge case: no customer name
        if not name:
            messagebox.showwarning("Customer Ka Naam Chahiye!",
                                   "Customer ka naam likhna zaroori hai.")
            self.ent_name.focus()
            return

        # Validate mobile (optional but warn if blank)
        mobile = self.ent_mobile.get().strip()
        if not mobile:
            proceed = messagebox.askyesno(
                "Mobile Number Nahi Diya",
                "Mobile number nahi diya hai. Phir bhi bill banana hai?"
            )
            if not proceed:
                return

        # Tax
        try:
            tax = float(self.ent_tax.get())
            if tax < 0:
                tax = 0.0
        except ValueError:
            tax = 0.0

        _, grand_total = calculate_grand_total(self.items, tax)

        # Paid / Due
        paid_str = self.ent_paid.get().strip()
        try:
            paid_amount = float(paid_str) if paid_str else grand_total
            if paid_amount < 0:
                paid_amount = 0.0
        except ValueError:
            paid_amount = grand_total

        # Edge case: paid more than total — clamp
        if paid_amount > grand_total:
            paid_amount = grand_total

        due_amount = round(grand_total - paid_amount, 2)

        bill_no = get_next_bill_no()
        bill_data = {
            "bill_no":       bill_no,
            "date":          datetime.datetime.now().strftime("%d-%m-%Y"),
            "customer_name": name,
            "mobile":        mobile,
            "address":       self.ent_address.get().strip(),
            "items":         self.items,
            "tax":           tax,
            "grand_total":   grand_total,
            "paid_amount":   paid_amount,
            "due_amount":    due_amount
        }

        # Save to Excel
        try:
            save_bill(bill_data)
        except Exception as e:
            messagebox.showerror("Excel Error!",
                                 f"Excel mein save karne mein problem hui:\n{e}")
            return

        # Generate PDF
        try:
            pdf_path = generate_pdf(bill_data)
            self.last_pdf_path = os.path.abspath(pdf_path)
            self.last_customer = name
            self.last_mobile   = mobile
            self.btn_whatsapp.config(state=tk.NORMAL if mobile else tk.DISABLED)

            msg = (f"Bill #{bill_no} ban gaya! 🎉\n"
                   f"PDF save hua: {self.last_pdf_path}")
            if due_amount > 0:
                msg += f"\n\n⚠️ Baaki Rakam: ₹{due_amount:.2f}"
            messagebox.showinfo("Bill Taiyaar Hai!", msg)

            try:
                os.startfile(self.last_pdf_path)
            except Exception:
                pass

            # Reset form
            self.ent_name.delete(0, tk.END)
            self.ent_mobile.delete(0, tk.END)
            self.ent_address.delete(0, tk.END)
            self.clear_all()

        except Exception as e:
            messagebox.showerror("PDF Error!",
                                 f"Bill PDF banane mein problem aayi:\n{e}")

    # ══════════════════════════════════════════════════════════════
    # WHATSAPP
    # ══════════════════════════════════════════════════════════════
    def send_via_whatsapp(self):
        if not self.last_pdf_path or not self.last_mobile:
            messagebox.showerror("WhatsApp Error",
                                 "Mobile number ya PDF path nahi mili. Pehle bill banao.")
            return
        try:
            success, response = send_whatsapp_bill(
                self.last_pdf_path, self.last_mobile, self.last_customer)
            if success:
                messagebox.showinfo("WhatsApp", "Bill WhatsApp par bhej diya gaya! ✅")
                self.btn_whatsapp.config(state=tk.DISABLED)
            else:
                messagebox.showerror("WhatsApp Error", f"Bill send nahi hua:\n{response}")
        except Exception as e:
            messagebox.showerror("WhatsApp Error", f"Kuch gadbad hui:\n{e}")

    # ══════════════════════════════════════════════════════════════
    # DASHBOARD
    # ══════════════════════════════════════════════════════════════
    def show_dashboard(self):
        from logic.excel_handler import get_dashboard_data
        try:
            dash_data = get_dashboard_data()
        except Exception as e:
            messagebox.showerror("Dashboard Error", f"Data load nahi hua:\n{e}")
            return

        win = tk.Toplevel(self.root)
        win.title("Business Dashboard")
        win.geometry("620x600")
        win.configure(bg="#f4f6f9")

        tk.Label(win, text="📊 Business Ka Hisaab — Live Dashboard",
                 font=("Helvetica", 17, "bold"),
                 bg="#13488B", fg="white", pady=14
                 ).pack(fill="x")

        # KPI Grid
        kpi_f = tk.Frame(win, bg="#f4f6f9")
        kpi_f.pack(fill="x", padx=20, pady=15)
        kpi_f.columnconfigure(0, weight=1)
        kpi_f.columnconfigure(1, weight=1)

        def kpi_box(parent, title, value, row, col, color):
            b = tk.Frame(parent, bg=color)
            b.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            tk.Label(b, text=title, font=("Helvetica", 11),
                     bg=color, fg="white").pack(pady=(14, 0))
            tk.Label(b, text=value, font=("Helvetica", 20, "bold"),
                     bg=color, fg="white").pack(pady=(4, 14))

        kpi_box(kpi_f, "Aaj Ki Bikri",
                f"₹{dash_data['today_sales']:,.2f}", 0, 0, "#1ca350")
        kpi_box(kpi_f, "Aaj Ke Bills",
                str(dash_data['today_bills']),        0, 1, "#f39c12")
        kpi_box(kpi_f, "Is Mahine Ki Bikri",
                f"₹{dash_data['month_sales']:,.2f}",  1, 0, "#2980b9")
        kpi_box(kpi_f, "Total Sabki Bikri",
                f"₹{dash_data['all_time_sales']:,.2f}", 1, 1, "#8e44ad")

        # Company-wise sales
        tk.Label(win,
                 text="📱 Company Ke Hisaab Se Bikri",
                 font=("Helvetica", 13, "bold"),
                 bg="#f4f6f9", fg="#13488B"
                 ).pack(pady=(10, 4))

        list_f = tk.Frame(win, bg="#f4f6f9")
        list_f.pack(fill="both", expand=True, padx=30, pady=5)

        if not dash_data["company_sales"]:
            tk.Label(list_f, text="Abhi koi data nahi hai.",
                     bg="#f4f6f9", font=("Helvetica", 11)).pack()
        else:
            for comp, total in sorted(dash_data["company_sales"].items(),
                                      key=lambda x: x[1], reverse=True):
                if total > 0:
                    r = tk.Frame(list_f, bg="white", pady=4)
                    r.pack(fill="x", pady=3)
                    tk.Label(r, text=comp, font=("Helvetica", 11, "bold"),
                             bg="white", fg="#333").pack(side="left", padx=15)
                    tk.Label(r, text=f"₹{total:,.2f}",
                             font=("Helvetica", 11, "bold"),
                             bg="white", fg="#1ca350").pack(side="right", padx=15)

    # ══════════════════════════════════════════════════════════════
    # PENDING PAYMENTS (BAAKI KHATA)
    # ══════════════════════════════════════════════════════════════
    def show_pending_payments(self):
        from logic.excel_handler import get_pending_payments
        try:
            all_pending = get_pending_payments()
        except Exception as e:
            messagebox.showerror("Error", f"Pending data load nahi hua:\n{e}")
            return

        win = tk.Toplevel(self.root)
        win.title("Baaki Khata — Pending Payments")
        win.geometry("880x560")
        win.configure(bg="#f4f6f9")

        # Header
        hdr = tk.Frame(win, bg="#c0392b")
        hdr.pack(fill="x")
        tk.Label(hdr, text="💰 Baaki Khata — Jinka Paisa Baki Hai",
                 font=("Helvetica", 15, "bold"),
                 bg="#c0392b", fg="white", pady=12
                 ).pack(side="left", padx=20)

        total_pending = sum(p["due"] for p in all_pending)
        lbl_total = tk.Label(hdr,
                             text=f"Kul Baaki: ₹{total_pending:,.2f}",
                             font=("Helvetica", 12, "bold"),
                             bg="#c0392b", fg="white")
        lbl_total.pack(side="right", padx=20)

        # Filter bar
        flt = tk.Frame(win, bg="#f4f6f9", pady=8)
        flt.pack(fill="x", padx=20)

        tk.Label(flt, text="Filter: Jinse zyada dino se payment nahi hua →",
                 font=("Helvetica", 11), bg="#f4f6f9").pack(side="left")

        spin_days = tk.Spinbox(flt, from_=0, to=3650, width=6,
                               font=("Helvetica", 12, "bold"), fg="#c0392b")
        spin_days.delete(0, "end")
        spin_days.insert(0, "0")
        spin_days.pack(side="left", padx=6)

        tk.Label(flt, text="din se zyada",
                 font=("Helvetica", 11), bg="#f4f6f9").pack(side="left")

        lbl_count = tk.Label(flt,
                             text=f"Dikha raha: {len(all_pending)} records",
                             font=("Helvetica", 10), bg="#f4f6f9", fg="#555")
        lbl_count.pack(side="right", padx=10)

        # Table
        tbl_f = tk.Frame(win, bg="#f4f6f9")
        tbl_f.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        style2 = ttk.Style()
        style2.configure("P.Treeview.Heading",
                         font=("Helvetica", 10, "bold"),
                         background="#fadbd8", foreground="#c0392b")
        style2.configure("P.Treeview", font=("Helvetica", 10), rowheight=28)

        cols = ("bill_no", "date", "name", "mobile", "total", "paid", "due", "days")
        tree = ttk.Treeview(tbl_f, columns=cols, show="headings", style="P.Treeview")

        hdgs = {
            "bill_no": "Bill No", "date": "Tarikh",
            "name": "Customer Ka Naam", "mobile": "Mobile",
            "total": "Kul (₹)", "paid": "Diya (₹)",
            "due": "Baaki (₹)", "days": "Din Se Pending"
        }
        wids = {
            "bill_no": 60, "date": 90, "name": 170, "mobile": 105,
            "total": 85, "paid": 85, "due": 105, "days": 105
        }
        for c in cols:
            tree.heading(c, text=hdgs[c])
            tree.column(c, width=wids[c], anchor="center")

        tree.tag_configure("red",    background="#fdecea", foreground="#c0392b")
        tree.tag_configure("orange", background="#fff3e0", foreground="#e67e22")
        tree.tag_configure("yellow", background="#fffde7", foreground="#856404")

        sb = ttk.Scrollbar(tbl_f, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)

        # Refresh / Filter
        def refresh(*_):
            try:
                min_days = max(0, int(spin_days.get()))
            except ValueError:
                min_days = 0

            filtered = [p for p in all_pending if p["days_pending"] >= min_days]
            f_total  = sum(p["due"] for p in filtered)

            lbl_total.config(text=f"Kul Baaki: ₹{f_total:,.2f}")
            lbl_count.config(text=f"Dikha raha: {len(filtered)} records")

            for row_id in tree.get_children():
                tree.delete(row_id)

            if not filtered:
                tree.insert("", "end",
                            values=("-", "-",
                                    "✓ Is filter mein koi baaki nahi hai!",
                                    "-", "", "", "", "-"))
            else:
                for p in filtered:
                    d   = p["days_pending"]
                    tag = "red" if d > 30 else "orange" if d > 7 else "yellow"
                    tree.insert("", "end", tag=tag, values=(
                        p["bill_no"],
                        p["date"][:10],
                        p["name"],
                        p["mobile"],
                        f"₹{p['total']:,.2f}",
                        f"₹{p['paid']:,.2f}",
                        f"₹{p['due']:,.2f}",
                        f"{d} din",
                    ))

        # Buttons
        tk.Button(flt, text=" 🔍 Filter Lagao ",
                  bg="#c0392b", fg="white",
                  font=("Helvetica", 10, "bold"), relief="flat",
                  padx=6, pady=4, cursor="hand2",
                  command=refresh
                  ).pack(side="left", padx=8)

        tk.Button(flt, text="Reset Karo",
                  bg="#a4b0be", fg="white",
                  font=("Helvetica", 10), relief="flat",
                  padx=6, pady=4, cursor="hand2",
                  command=lambda: [spin_days.delete(0, "end"),
                                   spin_days.insert(0, "0"),
                                   refresh()]
                  ).pack(side="left")

        refresh()
