import hashlib
import os
import sqlite3
from datetime import date, datetime

import pandas as pd
import streamlit as st


DB_PATH = os.environ.get("SMART_CRM_STREAMLIT_DB", "smart_crm_streamlit.db")


def db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = db()
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS shops (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            business_name TEXT NOT NULL,
            owner_name TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            shop_id INTEGER NOT NULL,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            shop_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            sku TEXT NOT NULL,
            category TEXT,
            cost_price REAL NOT NULL,
            selling_price REAL NOT NULL,
            UNIQUE(shop_id, sku)
        );
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            shop_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            current_stock INTEGER NOT NULL,
            low_stock_threshold INTEGER NOT NULL,
            UNIQUE(shop_id, product_id)
        );
        CREATE TABLE IF NOT EXISTS stock_movements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            shop_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            movement_type TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            note TEXT,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            shop_id INTEGER NOT NULL,
            full_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            role TEXT NOT NULL,
            monthly_salary REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            shop_id INTEGER NOT NULL,
            employee_id INTEGER NOT NULL,
            work_date TEXT NOT NULL,
            status TEXT NOT NULL,
            note TEXT
        );
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            shop_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            customer_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            total_revenue REAL NOT NULL,
            total_cost REAL NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            shop_id INTEGER NOT NULL,
            expense_date TEXT NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            note TEXT
        );
        """
    )
    conn.commit()


def password_hash(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def query(sql, params=()):
    conn = db()
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def execute(sql, params=()):
    conn = db()
    cur = conn.execute(sql, params)
    conn.commit()
    last_id = cur.lastrowid
    conn.close()
    return last_id


def table(rows):
    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.info("No records yet.")


def current_shop_id():
    return st.session_state.user["shop_id"]


def register():
    st.subheader("Create client account")
    business_name = st.text_input("Business name")
    owner_name = st.text_input("Owner name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Create account", type="primary"):
        if not business_name or not owner_name or not email or not password:
            st.error("Please fill all signup fields.")
            return
        try:
            shop_id = execute(
                "INSERT INTO shops (business_name, owner_name, created_at) VALUES (?, ?, ?)",
                (business_name, owner_name, datetime.utcnow().isoformat()),
            )
            execute(
                "INSERT INTO users (shop_id, full_name, email, password_hash, created_at) VALUES (?, ?, ?, ?, ?)",
                (shop_id, owner_name, email.lower(), password_hash(password), datetime.utcnow().isoformat()),
            )
            st.success("Account created. Please login.")
        except sqlite3.IntegrityError:
            st.error("Email is already registered.")


def login():
    st.subheader("Login")
    email = st.text_input("Login email")
    password = st.text_input("Login password", type="password")
    if st.button("Login", type="primary"):
        users = query(
            "SELECT * FROM users WHERE email = ? AND password_hash = ?",
            (email.lower(), password_hash(password)),
        )
        if not users:
            st.error("Invalid email or password.")
            return
        st.session_state.user = users[0]
        st.rerun()


def auth_screen():
    st.title("Smart CRM SaaS")
    tab1, tab2 = st.tabs(["Login", "Register"])
    with tab1:
        login()
    with tab2:
        register()


def products_page():
    shop_id = current_shop_id()
    st.header("Product Management")
    with st.form("product_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        name = c1.text_input("Product name")
        sku = c2.text_input("SKU")
        category = c1.text_input("Category")
        cost = c2.number_input("Cost price", min_value=0.0, step=1.0)
        selling = c1.number_input("Selling price", min_value=0.0, step=1.0)
        if st.form_submit_button("Save product"):
            if selling < cost:
                st.error("Selling price cannot be lower than cost price.")
            else:
                try:
                    execute(
                        "INSERT INTO products (shop_id, name, sku, category, cost_price, selling_price) VALUES (?, ?, ?, ?, ?, ?)",
                        (shop_id, name, sku, category, cost, selling),
                    )
                    st.success("Product saved.")
                except sqlite3.IntegrityError:
                    st.error("SKU already exists for this business.")
    table(query("SELECT id, name, sku, category, cost_price, selling_price FROM products WHERE shop_id = ?", (shop_id,)))


def inventory_page():
    shop_id = current_shop_id()
    st.header("Inventory Management")
    products = query("SELECT id, name FROM products WHERE shop_id = ?", (shop_id,))
    product_map = {p["name"]: p["id"] for p in products}
    if not products:
        st.warning("Add products first.")
        return
    with st.form("stock_form", clear_on_submit=True):
        product_name = st.selectbox("Product", list(product_map))
        stock = st.number_input("Current stock", min_value=0, step=1)
        threshold = st.number_input("Low stock threshold", min_value=0, step=1, value=5)
        if st.form_submit_button("Save stock"):
            product_id = product_map[product_name]
            execute(
                """
                INSERT INTO inventory (shop_id, product_id, current_stock, low_stock_threshold)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(shop_id, product_id) DO UPDATE SET
                current_stock = excluded.current_stock,
                low_stock_threshold = excluded.low_stock_threshold
                """,
                (shop_id, product_id, stock, threshold),
            )
            st.success("Stock saved.")
    rows = query(
        """
        SELECT p.name, i.current_stock, i.low_stock_threshold,
        CASE WHEN i.current_stock <= i.low_stock_threshold THEN 'Low' ELSE 'OK' END AS status
        FROM inventory i JOIN products p ON p.id = i.product_id
        WHERE i.shop_id = ?
        """,
        (shop_id,),
    )
    table(rows)


def employees_page():
    shop_id = current_shop_id()
    st.header("Employee Management")
    with st.form("employee_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        name = c1.text_input("Employee name")
        phone = c2.text_input("Phone")
        role = c1.text_input("Role")
        salary = c2.number_input("Monthly salary", min_value=0.0, step=100.0)
        if st.form_submit_button("Save employee"):
            execute(
                "INSERT INTO employees (shop_id, full_name, phone, role, monthly_salary) VALUES (?, ?, ?, ?, ?)",
                (shop_id, name, phone, role, salary),
            )
            st.success("Employee saved.")
    table(query("SELECT id, full_name, phone, role, monthly_salary FROM employees WHERE shop_id = ?", (shop_id,)))


def attendance_page():
    shop_id = current_shop_id()
    st.header("Attendance Management")
    employees = query("SELECT id, full_name FROM employees WHERE shop_id = ?", (shop_id,))
    employee_map = {e["full_name"]: e["id"] for e in employees}
    if not employees:
        st.warning("Add employees first.")
        return
    with st.form("attendance_form", clear_on_submit=True):
        employee_name = st.selectbox("Employee", list(employee_map))
        work_date = st.date_input("Date", value=date.today())
        status = st.selectbox("Status", ["present", "late", "absent"])
        note = st.text_input("Note")
        if st.form_submit_button("Save attendance"):
            execute(
                "INSERT INTO attendance (shop_id, employee_id, work_date, status, note) VALUES (?, ?, ?, ?, ?)",
                (shop_id, employee_map[employee_name], work_date.isoformat(), status, note),
            )
            st.success("Attendance saved.")
    table(
        query(
            """
            SELECT a.work_date, e.full_name, a.status, a.note
            FROM attendance a JOIN employees e ON e.id = a.employee_id
            WHERE a.shop_id = ?
            ORDER BY a.work_date DESC
            """,
            (shop_id,),
        )
    )


def sales_page():
    shop_id = current_shop_id()
    st.header("Sales Management")
    products = query("SELECT id, name, cost_price, selling_price FROM products WHERE shop_id = ?", (shop_id,))
    product_map = {p["name"]: p for p in products}
    if not products:
        st.warning("Add products first.")
        return
    with st.form("sale_form", clear_on_submit=True):
        customer = st.text_input("Customer", value="Walk-in Customer")
        product_name = st.selectbox("Product", list(product_map))
        quantity = st.number_input("Quantity", min_value=1, step=1)
        unit_price = st.number_input("Unit price", min_value=0.0, value=float(product_map[product_name]["selling_price"]), step=1.0)
        if st.form_submit_button("Record sale"):
            product = product_map[product_name]
            revenue = quantity * unit_price
            cost = quantity * float(product["cost_price"])
            execute(
                "INSERT INTO sales (shop_id, product_id, customer_name, quantity, unit_price, total_revenue, total_cost, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (shop_id, product["id"], customer, quantity, unit_price, revenue, cost, datetime.utcnow().isoformat()),
            )
            execute(
                "UPDATE inventory SET current_stock = MAX(current_stock - ?, 0) WHERE shop_id = ? AND product_id = ?",
                (quantity, shop_id, product["id"]),
            )
            st.success("Sale recorded.")
    table(
        query(
            """
            SELECT s.created_at, s.customer_name, p.name AS product, s.quantity, s.total_revenue, s.total_cost
            FROM sales s JOIN products p ON p.id = s.product_id
            WHERE s.shop_id = ?
            ORDER BY s.created_at DESC
            """,
            (shop_id,),
        )
    )


def finance_page():
    shop_id = current_shop_id()
    st.header("Profit & Loss")
    with st.form("expense_form", clear_on_submit=True):
        expense_date = st.date_input("Expense date", value=date.today())
        category = st.text_input("Category")
        amount = st.number_input("Amount", min_value=0.0, step=1.0)
        note = st.text_input("Note")
        if st.form_submit_button("Save expense"):
            execute(
                "INSERT INTO expenses (shop_id, expense_date, category, amount, note) VALUES (?, ?, ?, ?, ?)",
                (shop_id, expense_date.isoformat(), category, amount, note),
            )
            st.success("Expense saved.")
    sales = query("SELECT COALESCE(SUM(total_revenue), 0) AS revenue, COALESCE(SUM(total_cost), 0) AS cost FROM sales WHERE shop_id = ?", (shop_id,))[0]
    expenses = query("SELECT COALESCE(SUM(amount), 0) AS expenses FROM expenses WHERE shop_id = ?", (shop_id,))[0]["expenses"]
    profit = sales["revenue"] - sales["cost"] - expenses
    c1, c2, c3 = st.columns(3)
    c1.metric("Revenue", f"{sales['revenue']:.2f}")
    c2.metric("Expenses", f"{expenses:.2f}")
    c3.metric("Net Profit", f"{profit:.2f}")
    table(query("SELECT expense_date, category, amount, note FROM expenses WHERE shop_id = ? ORDER BY expense_date DESC", (shop_id,)))


def ai_brief_page():
    shop_id = current_shop_id()
    st.header("AI Business Brief")
    low_stock = query(
        """
        SELECT p.name, i.current_stock, i.low_stock_threshold
        FROM inventory i JOIN products p ON p.id = i.product_id
        WHERE i.shop_id = ? AND i.current_stock <= i.low_stock_threshold
        """,
        (shop_id,),
    )
    attendance_issues = query(
        """
        SELECT e.full_name, a.status, a.work_date
        FROM attendance a JOIN employees e ON e.id = a.employee_id
        WHERE a.shop_id = ? AND a.status IN ('late', 'absent')
        """,
        (shop_id,),
    )
    sales = query("SELECT COUNT(*) AS count, COALESCE(SUM(total_revenue), 0) AS revenue, COALESCE(SUM(total_revenue - total_cost), 0) AS gross_profit FROM sales WHERE shop_id = ?", (shop_id,))[0]

    st.subheader("Business Summary")
    st.write("This brief uses only available CRM data for the logged-in business account.")
    st.subheader("Key Metrics")
    st.write(f"Total Sales: {sales['count']}")
    st.write(f"Total Revenue: {sales['revenue']:.2f}")
    st.write(f"Gross Profit: {sales['gross_profit']:.2f}")
    st.write(f"Low Stock Items: {len(low_stock)}")
    st.write(f"Attendance Issues: {len(attendance_issues)}")
    st.subheader("Important Alerts")
    if not low_stock and not attendance_issues:
        st.success("No supported operational alerts found in available CRM data.")
    for item in low_stock:
        st.warning(f"Low stock: {item['name']} has {item['current_stock']} left. Restock this product.")
    for item in attendance_issues:
        st.warning(f"Attendance issue: {item['full_name']} was {item['status']} on {item['work_date']}.")
    st.subheader("Recommended Actions")
    if low_stock:
        st.write("1. Restock low stock products.")
    if attendance_issues:
        st.write("2. Review attendance issues with employees.")
    if not low_stock and not attendance_issues:
        st.write("Keep entering daily sales, stock, and attendance records.")


def main_app():
    user = st.session_state.user
    shop = query("SELECT * FROM shops WHERE id = ?", (user["shop_id"],))[0]
    st.sidebar.title(shop["business_name"])
    st.sidebar.caption(f"Logged in as {user['full_name']}")
    if st.sidebar.button("Logout"):
        del st.session_state.user
        st.rerun()
    page = st.sidebar.radio(
        "Modules",
        ["AI Brief", "Products", "Inventory", "Employees", "Attendance", "Sales", "Profit/Loss"],
    )
    if page == "AI Brief":
        ai_brief_page()
    elif page == "Products":
        products_page()
    elif page == "Inventory":
        inventory_page()
    elif page == "Employees":
        employees_page()
    elif page == "Attendance":
        attendance_page()
    elif page == "Sales":
        sales_page()
    elif page == "Profit/Loss":
        finance_page()


def main():
    st.set_page_config(page_title="Smart CRM SaaS", page_icon="📊", layout="wide")
    init_db()
    if "user" not in st.session_state:
        auth_screen()
    else:
        main_app()


if __name__ == "__main__":
    main()
