import os
import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from invoice_generator import generate_invoice
from PIL import Image, ImageTk
import re
import platform
import subprocess


import sys

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  # When packaged by PyInstaller
    except Exception:
        base_path = os.path.abspath(".")  # When running normally
    return os.path.join(base_path, relative_path)


DEFAULT_FOLDER = os.path.join(os.path.expanduser("~"), "Desktop", "Invoices")
selected_folder = DEFAULT_FOLDER

all_fee_types = [
    "Admission Fee", "Tuition Fee", "Exam Fee",
    "Stationary Charges", "Security Deposits", "Activity Charges"
]

used_fee_types = set()
particular_rows = []

payment_modes = ["Cash", "Credit Card", "Debit Card", "UPI", "Netbanking", "Cheque", "Demand Draft"]
course_options = ["Day-Care", "Nursery", "Jr. Kg", "Sr. Kg", "Playgroup"]

# def update_add_particular_button():
#     remaining = [item for item in all_fee_types if item not in used_fee_types]
#     add_particular_btn.config(state='normal' if remaining else 'disabled')

def add_dropdown_particular():
    remaining = [item for item in all_fee_types if item not in used_fee_types]
    if not remaining:
        return
    selected = remaining[0]
    used_fee_types.add(selected)
    # update_add_particular_button()

    row_frame = tk.Frame(particulars_frame)
    row_frame.pack(fill='x', pady=5)

    fee_label = tk.Label(row_frame, text=selected, width=30, anchor='w' , font=("Arial", 14))
    fee_label.pack(side='left', padx=5)
    amount_entry = tk.Entry(row_frame, width=15 , font=("Arial", 13))
    amount_entry.pack(side='left', padx=5)

    def delete_row():
        used_fee_types.remove(selected)
        particular_rows.remove((row_frame, selected, amount_entry))
        row_frame.destroy()
        # update_add_particular_button()

    tk.Button(row_frame, text="Delete", command=delete_row, width=10 , font=("Arial", 14)).pack(side='left', padx=5)
    particular_rows.append((row_frame, selected, amount_entry))

def add_custom_particular():
    row_frame = tk.Frame(particulars_frame, bg="white")
    row_frame.pack(fill='x', pady=5)

    custom_entry = tk.Entry(row_frame, width=30 , font=("Arial", 14))
    custom_entry.insert(0, "Custom Fee Name")
    custom_entry.pack(side='left', padx=5)

    amount_entry = tk.Entry(row_frame, width=15 , font=("Arial", 13))
    amount_entry.pack(side='left', padx=5)

    def delete_row():
        particular_rows.remove((row_frame, custom_entry, amount_entry))
        row_frame.destroy()
        update_total_amount()

    tk.Button(row_frame, text="Delete", command=delete_row, width=10 , font=("Arial", 14)).pack(side='left', padx=5)
    particular_rows.append((row_frame, custom_entry, amount_entry))

    # Bind to update total when amount is changed
    amount_entry.bind("<KeyRelease>", lambda e: update_total_amount())
    update_total_amount()


def browse_folder():
    global selected_folder
    path = filedialog.askdirectory(title="Select Invoice Save Folder")
    if path:
        selected_folder = path
        folder_path_label.config(text=selected_folder)

def submit_invoice():
    name = name_entry.get().strip()
    course = course_var.get().strip()
    duration = duration_entry.get().strip()
    date = datetime.datetime.now().strftime("%d-%m-%Y")
    payment_mode = payment_mode_var.get().strip()
    balance = balance_entry.get().replace(',', '')
    total_fees = total_fees_entry.get().replace(',', '')



    if not name or not course or not duration or not payment_mode:
        messagebox.showerror("Input Error", "All fields are required.")
        return

    particulars = []
    total = 0
    for row in particular_rows:
        _, pname_widget, amount_widget = row
        pname = pname_widget if isinstance(pname_widget, str) else pname_widget.get().strip()
        amt = amount_widget.get().strip()
        if pname and amt:
            try:
                amt_float = float(amt)
                particulars.append((pname, amt_float))
                total += amt_float
            except ValueError:
                messagebox.showerror("Input Error", f"Invalid amount: {amt}")
                return

    try:
        balance_amt = float(balance) if balance else 0
    except ValueError:
        messagebox.showerror("Input Error", "Balance must be a number.")
        return

    if not particulars:
        messagebox.showerror("Input Error", "Add at least one fee item.")
        return

    invoice_path = generate_invoice(
        student_name=name,
        course=course,
        duration=duration,
        date=date,
        particulars=particulars,
        total=total,
        payment_mode=payment_mode,
        balance=balance_amt,
        total_fees=total_fees,
        save_folder=selected_folder
        
    )

    messagebox.showinfo("Invoice Generated", f"Invoice saved to:\n{invoice_path}")
    total_fees = total_fees_entry.get().replace(',', '')

    
    # try:
    #     invoice_path = generate_invoice(...)
    # except Exception as e:
    #     messagebox.showerror("Error", f"Failed to generate invoice: {e}")
def preview_pdf(pdf_path):
    try:
        if platform.system() == 'Windows':
            os.startfile(pdf_path)
        elif platform.system() == 'Darwin':  # macOS
            subprocess.call(['open', pdf_path])
        else:  # Linux
            subprocess.call(['xdg-open', pdf_path])
    except Exception as e:
        messagebox.showerror("Preview Error", f"Could not open PDF: {e}")


def delete_last_invoice():
    if not os.path.exists(selected_folder):
        messagebox.showinfo("No Invoices", "No invoices have been generated yet.")
        return
    files = sorted([f for f in os.listdir(selected_folder) if f.endswith(".pdf")])
    if not files:
        messagebox.showinfo("No Invoices", "No invoices found to delete.")
        return
    last_invoice = files[-1]
    confirm = messagebox.askyesno("Delete Invoice", f"Delete {last_invoice}?")
    if confirm:
        os.remove(os.path.join(selected_folder, last_invoice))
        messagebox.showinfo("Deleted", f"{last_invoice} deleted.")

def show_invoices():
    if not os.path.exists(selected_folder):
        messagebox.showinfo("No Invoices", "No invoices folder found.")
        return

    files = sorted([f for f in os.listdir(selected_folder) if f.endswith(".pdf")])
    if not files:
        messagebox.showinfo("No Invoices", "No invoices found.")
        return

    top = tk.Toplevel(app)
    top.title("Invoices")
    top.geometry("600x400")

    # Scrollable frame
    canvas = tk.Canvas(top)
    scrollbar = tk.Scrollbar(top, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    for f in files:
        frame = tk.Frame(scrollable_frame, bg="white")
        frame.pack(fill="x", padx=10, pady=5)

        tk.Label(frame, text=f, width=40, anchor="w").pack(side="left")
        tk.Button(frame, text="Open", command=lambda p=f: os.startfile(os.path.join(selected_folder, p))).pack(side="left", padx=5)
        tk.Button(frame, text="Delete", command=lambda p=f: delete_invoice_file(p, top)).pack(side="left", padx=5)


def delete_invoice_file(filename, window):
    path = os.path.join(selected_folder, filename)
    confirm = messagebox.askyesno("Delete Invoice", f"Are you sure you want to delete {filename}?")
    if confirm:
        os.remove(path)
        window.destroy()
        show_invoices()

# ====== UI ======

# ====== UI ======

app = tk.Tk()


app.title("Little Sky Kids Billing Software")
app.state('zoomed')  # Fullscreen
app.configure(bg="#f0f8ff")

# Load and display logo


# === Top Layout: Header and Buttons ===
top_frame = tk.Frame(app, bg="#f0f8ff")
top_frame.pack(fill="x", pady=(10, 0))

# Load and display logo on top-left
logo_image = Image.open(resource_path("new-logo.png"))

logo_image = logo_image.resize((60, 60))
logo_photo = ImageTk.PhotoImage(logo_image)
tk.Label(top_frame, image=logo_photo, bg="#f0f8ff").pack(side="left", padx=(20, 10))
app.logo_photo = logo_photo  # keep reference

# School name next to logo
tk.Label(top_frame, text="LITTLE SKY KIDS PRESCHOOL", font=("Arial", 30, "bold"),
         fg="#003366", bg="#f0f8ff").pack(side="left")

# Right: Action Buttons
btn_frame = tk.Frame(top_frame, bg="#f0f8ff")
btn_frame.pack(side="right", padx=30)

def open_latest_invoice():
    if not os.path.exists(selected_folder):
        messagebox.showinfo("No Invoices", "No invoices folder found.")
        return

    files = sorted([f for f in os.listdir(selected_folder) if f.endswith(".pdf")])
    if not files:
        messagebox.showinfo("No Invoices", "No invoices found.")
        return

    latest_invoice_path = os.path.join(selected_folder, files[-1])
    preview_pdf(latest_invoice_path)

tk.Button(btn_frame, text="Print Preview", command=open_latest_invoice,
          bg="blue", fg="white", width=20, font=("Arial", 12)).pack(side="left", padx=5)

tk.Button(btn_frame, text="Generate Invoice", command=submit_invoice, bg="green", fg="white", width=20 ,font=("Arial", 12) ).pack(side="left", padx=5)
tk.Button(btn_frame, text="Show Invoices", command=show_invoices, width=20 ,font=("Arial", 12)).pack(side="left", padx=5)
tk.Button(btn_frame, text="Delete Last Invoice", command=delete_last_invoice, bg="red", fg="white", width=20 ,font=("Arial", 12)).pack(side="left", padx=5)
tk.Button(btn_frame, text="Print Preview", command=open_latest_invoice,
          bg="blue", fg="white", width=20, font=("Arial", 12)).pack(side="left", padx=5)


# === Main Form Section ===
# === Scrollable Main Form Section ===
main_frame = tk.Frame(app, bg="#ffffff", bd=2, relief="ridge")
main_frame.place(relx=0.5, rely=0.18, anchor="n", relwidth=0.9, relheight=0.75)

canvas = tk.Canvas(main_frame, bg="white", highlightthickness=0)
scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
scrollable_frame = tk.Frame(canvas, bg="white")

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(
        scrollregion=canvas.bbox("all")
    )
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# Enable mouse wheel scrolling
def _on_mousewheel(event):
    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

canvas.bind_all("<MouseWheel>", _on_mousewheel)

form = scrollable_frame

form.grid_columnconfigure(0, weight=1)
form.grid_columnconfigure(1, weight=1)



tk.Label(form, text="Student Name", bg="white" , font=("Arial", 14)).grid(row=0, column=0, sticky="e", padx=15, pady=10)
name_entry = tk.Entry(form, width=60 , font=("Arial", 13))
name_entry.grid(row=0, column=1, padx=15, pady=10)

tk.Label(form, text="Course", bg="white" , font=("Arial", 14)).grid(row=1, column=0, sticky="e", padx=15, pady=10)
course_var = tk.StringVar()
course_combo = ttk.Combobox(form, textvariable=course_var,font=("Arial", 13), values=course_options, state='readonly', width=58)
course_combo.grid(row=1, column=1, padx=15, pady=10)
course_combo.set(course_options[0])

tk.Label(form, text="Course Duration", bg="white" , font=("Arial", 14)).grid(row=2, column=0, sticky="e", padx=15, pady=10)
duration_entry = tk.Entry(form, width=60 , font=("Arial", 13))
duration_entry.grid(row=2, column=1, padx=15, pady=10)

def validate_amount_with_commas(P):
    return bool(re.fullmatch(r"[0-9,]*", P))  # Allows only digits and commas

vcmd = (app.register(validate_amount_with_commas), '%P')

tk.Label(form, text="Total Fees", bg="white", font=("Arial", 14)).grid(row=3, column=0, sticky="e", padx=15, pady=10)

total_fees_frame = tk.Frame(form, bg="white")
total_fees_frame.grid(row=3, column=1, padx=15, pady=10, sticky="w")

tk.Label(total_fees_frame, text="Rs", font=("Arial", 13), bg="white").pack(side="left", padx=(0, 5))

total_fees_entry = tk.Entry(total_fees_frame, width=57, font=("Arial", 13), validate="key", validatecommand=vcmd)
total_fees_entry.pack(side="left")

tk.Label(form, text="Date of Payment", bg="white", font=("Arial", 14)).grid(row=4, column=0, sticky="e", padx=15, pady=10)

date_of_payment_entry = tk.Entry(form, width=60, font=("Arial", 13))
date_of_payment_entry.grid(row=4, column=1, padx=15, pady=10)
date_of_payment_entry.insert(0, datetime.datetime.now().strftime("%d-%m-%Y"))  # Prefill today's date




tk.Label(form, text="Fee Particulars", bg="white", font=("Arial", 15, "bold")).grid(row=5, column=0, columnspan=2, pady=(30, 5))

# Fee particulars frame
particulars_frame = tk.Frame(form, bg="white" , )
particulars_frame.grid(row=5, column=0, columnspan=2, pady=5)

total_amount_var = tk.StringVar(value="0")
def update_total_amount():
    total_paid = 0
    for row in particular_rows:
        _, name_widget, amount_widget = row
        try:
            amt = amount_widget.get().replace(",", "").strip()
            if amt:
                total_paid += float(amt)
        except ValueError:
            continue
    total_amount_var.set(f"{int(total_paid):,}")

    # Calculate balance
    try:
        total_fees = total_fees_entry.get().replace(",", "").strip()
        total_fees_float = float(total_fees) if total_fees else 0
        balance = total_fees_float - total_paid

        # Editable field: just update with commas
        balance_entry.delete(0, tk.END)
        balance_entry.insert(0, f"{int(balance):,}")
    except:
        pass


btn_total_frame = tk.Frame(form, bg="white")
btn_total_frame.grid(row=6, column=0, columnspan=2, pady=5)

add_custom_btn = tk.Button(btn_total_frame, text="Add Custom Particular", font=("Arial", 12),
                           command=add_custom_particular, width=25)
add_custom_btn.pack(side="left", padx=10)

tk.Label(btn_total_frame, text="Total Amount:", font=("Arial", 14), bg="white").pack(side="left")
tk.Label(btn_total_frame, textvariable=total_amount_var, font=("Arial", 14, "bold"),
         bg="white", fg="#003366").pack(side="left", padx=(5, 20))
tk.Label(btn_total_frame, text="Rs", font=("Arial", 13), bg="white").pack(side="left")


tk.Label(form, text="Payment Mode", bg="white",font=("Arial", 14)).grid(row=7, column=0, sticky="e", padx=15, pady=10)
payment_mode_var = tk.StringVar()
payment_mode_combo = ttk.Combobox(form, textvariable=payment_mode_var, font=("Arial", 13) ,values=payment_modes, state='readonly', width=58)
payment_mode_combo.grid(row=7, column=1, padx=15, pady=10)
payment_mode_combo.set(payment_modes[0])

tk.Label(form, text="Balance (Rs)", bg="white", font=("Arial", 14)).grid(row=8, column=0, sticky="e", padx=15, pady=10)
balance_entry = tk.Entry(form, width=60, font=("Arial", 13))
balance_entry.grid(row=8, column=1, padx=15, pady=10)



tk.Label(form, text="Invoice Save Folder", bg="white" , font=("Arial", 14)).grid(row=9, column=0, sticky="e", padx=15, pady=10)
folder_path_label = tk.Label(form, text=selected_folder, fg="blue", bg="white", wraplength=600, anchor="w", justify="left")
folder_path_label.grid(row=9, column=1, sticky="w", padx=15)

tk.Button(form, text="Browse Folder", command=browse_folder, width=25 , font=("Arial", 14)).grid(row=9, column=1, sticky="e", pady=10)

# update_add_particular_button()
app.mainloop()
