import os
import sys
from fpdf import FPDF
from datetime import datetime

# PyInstaller-friendly path resolution
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

COUNTER_FILE = resource_path("invoice_counter.txt")

def get_next_invoice_number():
    os.makedirs(os.path.dirname(COUNTER_FILE), exist_ok=True)

    year_suffix = datetime.now().strftime("%y")

    if not os.path.exists(COUNTER_FILE):
        with open(COUNTER_FILE, "w") as f:
            f.write("1")
        return f"LSK{year_suffix}-00001"

    with open(COUNTER_FILE, "r+") as f:
        content = f.read().strip()

        if not content.isdigit() or int(content) < 1:
            f.seek(0)
            f.write("1")
            f.truncate()
            return f"LSK{year_suffix}-00001"

        current = int(content)
        next_num = current + 1

        f.seek(0)
        f.write(str(next_num))
        f.truncate()

        return f"LSK{year_suffix}-{next_num:05d}"

def generate_invoice(student_name, course, duration, date, particulars, total, payment_mode, balance, total_fees, save_folder):
    invoice_no = get_next_invoice_number()
    os.makedirs(save_folder, exist_ok=True)
    filename = os.path.join(save_folder, f"{invoice_no}.pdf")

    pdf = FPDF()
    pdf.add_page()

    # Logo
    logo_path = resource_path("new-logo.png")
    if os.path.exists(logo_path):
        pdf.image(logo_path, x=10, y=10, w=30)
    pdf.ln(20)

    pdf.set_auto_page_break(auto=True, margin=25)

    # Title and Header
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "LITTLE SKY KIDS", ln=True, align="C")
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, "Unit 236-237, Lodha Signet, Kolshet Road, Thane West, Maharashtra - 400607", ln=True, align="C")
    pdf.cell(0, 8, "www.littleskykids.com | info.littleskykids@gmail.com", ln=True, align="C")
    pdf.cell(0, 8, "+91 8097918044 / +91 8600333649", ln=True, align="C")
    pdf.ln(10)

    # Receipt Info
    pdf.set_font("Arial", "B", 12)
    pdf.cell(100, 10, f"Receipt No: {invoice_no}", ln=False)
    pdf.cell(0, 10, f"Date: {date}", ln=True)
    pdf.cell(0, 10, f"Total Fees: Rs {float(total_fees):,.2f}", ln=True)

    # Student Info
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Name of Student: {student_name}", ln=True)
    pdf.cell(0, 10, f"Course: {course}", ln=True)
    pdf.cell(0, 10, f"Course Duration: {duration}", ln=True)

    pdf.ln(5)

    # Fee Particulars Table Header
    pdf.set_font("Arial", "B", 12)
    pdf.cell(10, 10, "Sr", border=1)
    pdf.cell(100, 10, "Particulars", border=1)
    pdf.cell(0, 10, "Amount", border=1, ln=True)

    # Fee Particulars Rows
    pdf.set_font("Arial", "", 12)
    for i, (name, amt) in enumerate(particulars, start=1):
        pdf.cell(10, 10, str(i), border=1)
        pdf.cell(100, 10, name, border=1)
        pdf.cell(0, 10, f"Rs {float(amt):,.2f}", border=1, ln=True)

    # Total Paid
   # Total Paid Row
    pdf.set_font("Arial", "B", 12)
    pdf.cell(110, 10, "Total", border=1)
    pdf.cell(0, 10, f"Rs {float(total):,.2f}", border=1, ln=True)

    # Balance Row (inside table)
    pdf.set_font("Arial", "", 12)
    pdf.cell(110, 10, "Balance : Rs", border=1)
    pdf.cell(0, 10, f"Rs {float(balance):,.2f}", border=1, ln=True)

    pdf.ln(5)

    # Payment Mode & Balance
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Payment Mode: {payment_mode}", ln=True)
    

    pdf.ln(10)
    pdf.set_draw_color(200, 200, 200)
    pdf.set_line_width(0.3)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())

    # Footer



    pdf.ln(15)
    pdf.set_font("Arial", "I", 12)  # Bold font
    pdf.set_text_color(0)           # Black color
    pdf.cell(0, 10, "Terms and Conditions:", ln=True)

    pdf.set_font("Arial", "I", 10)
    terms = [
        "1. Payment once made is non-refundable.",
        "2. This receipt serves as official proof of payment.",
        "3. Please preserve this invoice for future reference.",
        "4. In case of any discrepancies, kindly report within 7 days of issue.",
        "5. This is a computer-generated receipt. No signature is required."
        
]

    for line in terms:
        pdf.multi_cell(0, 8, line)






    pdf.output(filename)
    return filename
