
import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector



# DATABASE CONNECTION
# =========================================================

def connect_database():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="sql_password_enter",
            database="employee_db"
        )
        return connection

    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", str(e))
        return None



# CREATE TABLE
# =========================================================

def create_table():
    connection = connect_database()

    if connection:
        try:
            cursor = connection.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS employees (
                    employee_id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    email VARCHAR(100) NOT NULL,
                    phone VARCHAR(20) NOT NULL,
                    department VARCHAR(50) NOT NULL,
                    salary DECIMAL(10,2) NOT NULL
                )
            """)

            connection.commit()

        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", str(e))

        finally:
            cursor.close()
            connection.close()



# CLEAR FORM
# =========================================================

def clear_form():
    employee_id_entry.config(state="normal")
    employee_id_entry.delete(0, tk.END)
    employee_id_entry.config(state="readonly")

    name_entry.delete(0, tk.END)
    email_entry.delete(0, tk.END)
    phone_entry.delete(0, tk.END)
    department_entry.delete(0, tk.END)
    salary_entry.delete(0, tk.END)

    employee_tree.selection_remove(
        employee_tree.selection()
    )



# GET AND VALIDATE FORM DATA
# =========================================================

def get_form_data():
    name = name_entry.get().strip()
    email = email_entry.get().strip()
    phone = phone_entry.get().strip()
    department = department_entry.get().strip()
    salary = salary_entry.get().strip()

    if not all([name, email, phone, department, salary]):
        messagebox.showwarning(
            "Validation",
            "Please fill all fields."
        )
        return None

    if not phone.isdigit() or len(phone) != 10:
        messagebox.showwarning(
            "Validation",
            "Phone number must contain exactly 10 digits."
        )
        return None

    try:
        salary_value = float(salary)

        if salary_value <= 0:
            messagebox.showwarning(
                "Validation",
                "Salary must be greater than 0."
            )
            return None

    except ValueError:
        messagebox.showwarning(
            "Validation",
            "Salary must be a valid number."
        )
        return None

    return (
        name,
        email,
        phone,
        department,
        salary_value
    )



# ADD EMPLOYEE
# =========================================================

def add_employee():
    data = get_form_data()

    if data is None:
        return

    connection = connect_database()

    if connection:
        cursor = None

        try:
            cursor = connection.cursor()

            query = """
                INSERT INTO employees
                (name, email, phone, department, salary)
                VALUES (%s, %s, %s, %s, %s)
            """

            cursor.execute(query, data)
            connection.commit()

            messagebox.showinfo(
                "Success",
                "Employee added successfully."
            )

            clear_form()
            display_employees()

        except mysql.connector.Error as e:
            messagebox.showerror(
                "Database Error",
                str(e)
            )

        finally:
            if cursor:
                cursor.close()
            connection.close()



# DISPLAY EMPLOYEES
# =========================================================

def display_employees():
    for item in employee_tree.get_children():
        employee_tree.delete(item)

    connection = connect_database()

    if connection:
        cursor = None

        try:
            cursor = connection.cursor()

            cursor.execute("""
                SELECT employee_id, name, email,
                       phone, department, salary
                FROM employees
                ORDER BY employee_id
            """)

            employees = cursor.fetchall()

            for employee in employees:
                employee_tree.insert(
                    "",
                    tk.END,
                    values=employee
                )

        except mysql.connector.Error as e:
            messagebox.showerror(
                "Database Error",
                str(e)
            )

        finally:
            if cursor:
                cursor.close()
            connection.close()



# SELECT EMPLOYEE
# =========================================================

def select_employee(event):
    selected = employee_tree.selection()

    if not selected:
        return

    values = employee_tree.item(
        selected[0],
        "values"
    )

    clear_form()

    employee_id_entry.config(state="normal")
    employee_id_entry.insert(0, values[0])
    employee_id_entry.config(state="readonly")

    name_entry.insert(0, values[1])
    email_entry.insert(0, values[2])
    phone_entry.insert(0, values[3])
    department_entry.insert(0, values[4])
    salary_entry.insert(0, values[5])



# UPDATE EMPLOYEE
# =========================================================

def update_employee():
    employee_id = employee_id_entry.get().strip()

    if not employee_id:
        messagebox.showwarning(
            "Update",
            "Please select an employee first."
        )
        return

    data = get_form_data()

    if data is None:
        return

    connection = connect_database()

    if connection:
        cursor = None

        try:
            cursor = connection.cursor()

            query = """
                UPDATE employees
                SET name = %s,
                    email = %s,
                    phone = %s,
                    department = %s,
                    salary = %s
                WHERE employee_id = %s
            """

            values = data + (employee_id,)
            cursor.execute(query, values)

            if cursor.rowcount == 0:
                messagebox.showwarning(
                    "Update",
                    "Employee not found or no changes made."
                )
                return

            connection.commit()

            messagebox.showinfo(
                "Success",
                "Employee updated successfully."
            )

            clear_form()
            display_employees()

        except mysql.connector.Error as e:
            messagebox.showerror(
                "Database Error",
                str(e)
            )

        finally:
            if cursor:
                cursor.close()
            connection.close()



# DELETE EMPLOYEE
# =========================================================

def delete_employee():
    employee_id = employee_id_entry.get().strip()

    if not employee_id:
        messagebox.showwarning(
            "Delete",
            "Please select an employee first."
        )
        return

    answer = messagebox.askyesno(
        "Confirm Delete",
        "Are you sure you want to delete this employee?"
    )

    if not answer:
        return

    connection = connect_database()

    if connection:
        cursor = None

        try:
            cursor = connection.cursor()

            cursor.execute(
                """
                DELETE FROM employees
                WHERE employee_id = %s
                """,
                (employee_id,)
            )

            if cursor.rowcount == 0:
                messagebox.showwarning(
                    "Delete",
                    "Employee not found."
                )
                return

            connection.commit()

            # Reset AUTO_INCREMENT only when table is empty
            cursor.execute(
                "SELECT COUNT(*) FROM employees"
            )
            count = cursor.fetchone()[0]

            if count == 0:
                cursor.execute(
                    "ALTER TABLE employees AUTO_INCREMENT = 1"
                )
                connection.commit()

            messagebox.showinfo(
                "Success",
                "Employee deleted successfully."
            )

            clear_form()
            display_employees()

        except mysql.connector.Error as e:
            messagebox.showerror(
                "Database Error",
                str(e)
            )

        finally:
            if cursor:
                cursor.close()
            connection.close()



# SEARCH EMPLOYEE
# =========================================================

def search_employee():
    search_text = search_entry.get().strip()

    for item in employee_tree.get_children():
        employee_tree.delete(item)

    connection = connect_database()

    if connection:
        cursor = None

        try:
            cursor = connection.cursor()

            query = """
                SELECT employee_id, name, email,
                       phone, department, salary
                FROM employees
                WHERE name LIKE %s
                   OR email LIKE %s
                   OR phone LIKE %s
                   OR department LIKE %s
                ORDER BY employee_id
            """

            search_value = "%" + search_text + "%"

            cursor.execute(
                query,
                (
                    search_value,
                    search_value,
                    search_value,
                    search_value
                )
            )

            employees = cursor.fetchall()

            for employee in employees:
                employee_tree.insert(
                    "",
                    tk.END,
                    values=employee
                )

            if not employees:
                messagebox.showinfo(
                    "Search",
                    "No employees found."
                )

        except mysql.connector.Error as e:
            messagebox.showerror(
                "Database Error",
                str(e)
            )

        finally:
            if cursor:
                cursor.close()
            connection.close()



# MAIN WINDOW
# =========================================================

root = tk.Tk()
root.title("Employee Management System")
root.geometry("1100x650")
root.minsize(900, 550)



# TITLE
# =========================================================

title_label = tk.Label(
    root,
    text="Employee Management System",
    bg="green",
    fg="white",
    font=("Arial", 24, "bold"),
    pady=10
)
title_label.pack(fill="x", pady=10)



# FORM FRAME
# =========================================================

form_frame = tk.Frame(root)
form_frame.pack(padx=20, pady=10, fill="x")


# Employee ID
tk.Label(
    form_frame,
    text="Employee ID"
).grid(row=0, column=0, padx=10, pady=8, sticky="w")

employee_id_entry = tk.Entry(
    form_frame,
    width=30,
    state="readonly"
)
employee_id_entry.grid(
    row=0, column=1, padx=10, pady=8
)


# Name
tk.Label(
    form_frame,
    text="Name"
).grid(row=0, column=2, padx=10, pady=8, sticky="w")

name_entry = tk.Entry(form_frame, width=30)
name_entry.grid(
    row=0, column=3, padx=10, pady=8
)


# Email
tk.Label(
    form_frame,
    text="Email"
).grid(row=1, column=0, padx=10, pady=8, sticky="w")

email_entry = tk.Entry(form_frame, width=30)
email_entry.grid(
    row=1, column=1, padx=10, pady=8
)


# Phone
tk.Label(
    form_frame,
    text="Phone"
).grid(row=1, column=2, padx=10, pady=8, sticky="w")

phone_entry = tk.Entry(form_frame, width=30)
phone_entry.grid(
    row=1, column=3, padx=10, pady=8
)


# Department
tk.Label(
    form_frame,
    text="Department"
).grid(row=2, column=0, padx=10, pady=8, sticky="w")

department_entry = tk.Entry(form_frame, width=30)
department_entry.grid(
    row=2, column=1, padx=10, pady=8
)


# Salary
tk.Label(
    form_frame,
    text="Salary"
).grid(row=2, column=2, padx=10, pady=8, sticky="w")

salary_entry = tk.Entry(form_frame, width=30)
salary_entry.grid(
    row=2, column=3, padx=10, pady=8
)



# BUTTON FRAME
# =========================================================

button_frame = tk.Frame(root)
button_frame.pack(pady=10)

tk.Button(
    button_frame,
    text="Add Employee",
    width=15,
    command=add_employee
).grid(row=0, column=0, padx=5)

tk.Button(
    button_frame,
    text="Update",
    width=15,
    command=update_employee
).grid(row=0, column=1, padx=5)

tk.Button(
    button_frame,
    text="Delete",
    width=15,
    command=delete_employee
).grid(row=0, column=2, padx=5)

tk.Button(
    button_frame,
    text="Clear",
    width=15,
    command=clear_form
).grid(row=0, column=3, padx=5)



# SEARCH FRAME
# =========================================================

search_frame = tk.Frame(root)
search_frame.pack(
    fill="x",
    padx=20,
    pady=10
)

tk.Label(
    search_frame,
    text="Search Employee:"
).pack(side="left")

search_entry = tk.Entry(
    search_frame,
    width=40
)
search_entry.pack(side="left", padx=10)

tk.Button(
    search_frame,
    text="Search",
    command=search_employee
).pack(side="left")

tk.Button(
    search_frame,
    text="Show All",
    command=display_employees
).pack(side="left", padx=5)



# TREEVIEW FRAME
# =========================================================

tree_frame = tk.Frame(root)
tree_frame.pack(
    fill="both",
    expand=True,
    padx=20,
    pady=10
)


# Scrollbars
vertical_scrollbar = ttk.Scrollbar(
    tree_frame,
    orient="vertical"
)
vertical_scrollbar.pack(
    side="right",
    fill="y"
)

horizontal_scrollbar = ttk.Scrollbar(
    tree_frame,
    orient="horizontal"
)
horizontal_scrollbar.pack(
    side="bottom",
    fill="x"
)



# TREEVIEW
# =========================================================

columns = (
    "ID",
    "Name",
    "Email",
    "Phone",
    "Department",
    "Salary"
)

employee_tree = ttk.Treeview(
    tree_frame,
    columns=columns,
    show="headings",
    yscrollcommand=vertical_scrollbar.set,
    xscrollcommand=horizontal_scrollbar.set
)

vertical_scrollbar.config(
    command=employee_tree.yview
)

horizontal_scrollbar.config(
    command=employee_tree.xview
)


# Headings
employee_tree.heading("ID", text="Employee ID")
employee_tree.heading("Name", text="Name")
employee_tree.heading("Email", text="Email")
employee_tree.heading("Phone", text="Phone")
employee_tree.heading("Department", text="Department")
employee_tree.heading("Salary", text="Salary")


# Column widths
employee_tree.column("ID", width=100)
employee_tree.column("Name", width=180)
employee_tree.column("Email", width=220)
employee_tree.column("Phone", width=130)
employee_tree.column("Department", width=150)
employee_tree.column("Salary", width=120)


employee_tree.pack(
    fill="both",
    expand=True
)



# SELECT ROW WHEN CLICKED
# =========================================================

employee_tree.bind(
    "<ButtonRelease-1>",
    select_employee
)



# START APPLICATION
# =========================================================

create_table()
display_employees()

root.mainloop()