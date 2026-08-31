import os

from flask import Flask, render_template, request, redirect, url_for, flash
from database import get_connection

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")


# ==========================================
# HELPERS
# ==========================================

def query_one(cursor, sql, params=None):
    cursor.execute(sql, params or ())
    row = cursor.fetchone()
    return row[0] if row else 0


# ==========================================
# DASHBOARD
# ==========================================

@app.route("/")
def home():

    connection = get_connection()

    if connection is None:
        flash("Database connection failed! Please check your MySQL server.", "error")
        return render_template("index.html", active_page="dashboard",
                                total_customers=0, total_accounts=0,
                                total_transactions=0, total_fraud_alerts=0,
                                high_risk_alerts=0, recent_transactions=[])

    try:
        cursor = connection.cursor()

        total_customers = query_one(cursor, "SELECT COUNT(*) FROM customers")
        total_accounts = query_one(cursor, "SELECT COUNT(*) FROM accounts")
        total_transactions = query_one(cursor, "SELECT COUNT(*) FROM transactions")
        total_fraud_alerts = query_one(cursor, "SELECT COUNT(*) FROM fraud_alerts")
        high_risk_alerts = query_one(
            cursor, "SELECT COUNT(*) FROM fraud_alerts WHERE risk_level = 'High'"
        )

        cursor.execute("""
            SELECT
                transactions.transaction_id,
                accounts.account_number,
                merchants.merchant_name,
                transactions.transaction_amount,
                transactions.transaction_type,
                transactions.transaction_time
            FROM transactions
            JOIN accounts ON transactions.account_id = accounts.account_id
            JOIN merchants ON transactions.merchant_id = merchants.merchant_id
            ORDER BY transactions.transaction_time DESC
            LIMIT 5
        """)
        recent_transactions = cursor.fetchall()

        cursor.close()
        connection.close()

        return render_template(
            "index.html",
            active_page="dashboard",
            total_customers=total_customers,
            total_accounts=total_accounts,
            total_transactions=total_transactions,
            total_fraud_alerts=total_fraud_alerts,
            high_risk_alerts=high_risk_alerts,
            recent_transactions=recent_transactions
        )

    except Exception as error:
        connection.close()
        flash(f"Dashboard error: {error}", "error")
        return redirect(url_for("home"))


# ==========================================
# CUSTOMERS PAGE
# ==========================================

@app.route("/customers")
def customers():

    connection = get_connection()

    if connection is None:
        flash("Database connection failed! Please check your MySQL server.", "error")
        return render_template("customers.html", active_page="customers", customers=[])

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT CustomerID, firstname, lastname, email, city, created_at
            FROM customers
            ORDER BY CustomerID DESC
        """)
        customer_data = cursor.fetchall()

        cursor.close()
        connection.close()

        return render_template("customers.html", active_page="customers", customers=customer_data)

    except Exception as error:
        connection.close()
        flash(f"Error loading customers: {error}", "error")
        return redirect(url_for("home"))


# ==========================================
# ADD CUSTOMER
# ==========================================

@app.route("/add-customer", methods=["POST"])
def add_customer():

    firstname = request.form.get("firstname", "").strip()
    lastname = request.form.get("lastname", "").strip()
    email = request.form.get("email", "").strip()
    city = request.form.get("city", "").strip()

    if not (firstname and lastname and email and city):
        flash("All customer fields are required.", "error")
        return redirect(url_for("customers"))

    connection = get_connection()

    if connection is None:
        flash("Database connection failed!", "error")
        return redirect(url_for("customers"))

    try:
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO customers (firstname, lastname, email, city, created_at)
            VALUES (%s, %s, %s, %s, CURDATE())
        """, (firstname, lastname, email, city))

        connection.commit()
        cursor.close()
        connection.close()

        flash("Customer added successfully.", "success")
        return redirect(url_for("customers"))

    except Exception as error:
        connection.rollback()
        connection.close()
        flash(f"Error while adding customer: {error}", "error")
        return redirect(url_for("customers"))


# ==========================================
# EDIT / UPDATE / DELETE CUSTOMER
# ==========================================

@app.route("/edit-customer/<int:customer_id>")
def edit_customer(customer_id):

    connection = get_connection()

    if connection is None:
        flash("Database connection failed!", "error")
        return redirect(url_for("customers"))

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT CustomerID, firstname, lastname, email, city
            FROM customers
            WHERE CustomerID = %s
        """, (customer_id,))
        customer = cursor.fetchone()

        cursor.close()
        connection.close()

        if not customer:
            flash("Customer not found.", "error")
            return redirect(url_for("customers"))

        return render_template("edit_customer.html", active_page="customers", customer=customer)

    except Exception as error:
        connection.close()
        flash(f"Error: {error}", "error")
        return redirect(url_for("customers"))


@app.route("/update-customer/<int:customer_id>", methods=["POST"])
def update_customer(customer_id):

    firstname = request.form.get("firstname", "").strip()
    lastname = request.form.get("lastname", "").strip()
    email = request.form.get("email", "").strip()
    city = request.form.get("city", "").strip()

    connection = get_connection()

    if connection is None:
        flash("Database connection failed!", "error")
        return redirect(url_for("customers"))

    try:
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE customers
            SET firstname = %s, lastname = %s, email = %s, city = %s
            WHERE CustomerID = %s
        """, (firstname, lastname, email, city, customer_id))

        connection.commit()
        cursor.close()
        connection.close()

        flash("Customer updated successfully.", "success")
        return redirect(url_for("customers"))

    except Exception as error:
        connection.rollback()
        connection.close()
        flash(f"Error while updating customer: {error}", "error")
        return redirect(url_for("customers"))


@app.route("/delete-customer/<int:customer_id>")
def delete_customer(customer_id):

    connection = get_connection()

    if connection is None:
        flash("Database connection failed!", "error")
        return redirect(url_for("customers"))

    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM customers WHERE CustomerID = %s", (customer_id,))
        connection.commit()
        cursor.close()
        connection.close()

        flash("Customer deleted.", "success")
        return redirect(url_for("customers"))

    except Exception as error:
        connection.rollback()
        connection.close()
        flash(f"Error while deleting customer: {error}", "error")
        return redirect(url_for("customers"))


# ==========================================
# ACCOUNTS PAGE
# ==========================================

@app.route("/accounts")
def accounts():

    connection = get_connection()

    if connection is None:
        flash("Database connection failed! Please check your MySQL server.", "error")
        return render_template("accounts.html", active_page="accounts", customers=[], accounts=[])

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT CustomerID, firstname, lastname
            FROM customers
            ORDER BY firstname ASC
        """)
        customer_data = cursor.fetchall()

        cursor.execute("""
            SELECT
                accounts.account_id,
                customers.firstname,
                customers.lastname,
                accounts.account_number,
                accounts.account_type,
                accounts.balance,
                accounts.status
            FROM accounts
            LEFT JOIN customers ON accounts.customerID = customers.CustomerID
            ORDER BY accounts.account_id DESC
        """)
        account_data = cursor.fetchall()

        cursor.close()
        connection.close()

        return render_template("accounts.html", active_page="accounts",
                                customers=customer_data, accounts=account_data)

    except Exception as error:
        connection.close()
        flash(f"Error loading accounts: {error}", "error")
        return redirect(url_for("home"))


# ==========================================
# ADD ACCOUNT
# ==========================================

@app.route("/add-account", methods=["POST"])
def add_account():

    customerID = request.form.get("customerID")
    account_number = request.form.get("account_number", "").strip()
    account_type = request.form.get("account_type")
    balance = request.form.get("balance")
    status = request.form.get("status")

    if not (customerID and account_number and account_type and balance and status):
        flash("All account fields are required.", "error")
        return redirect(url_for("accounts"))

    connection = get_connection()

    if connection is None:
        flash("Database connection failed!", "error")
        return redirect(url_for("accounts"))

    try:
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO accounts (customerID, account_number, account_type, balance, status)
            VALUES (%s, %s, %s, %s, %s)
        """, (customerID, account_number, account_type, balance, status))

        connection.commit()
        cursor.close()
        connection.close()

        flash("Account created successfully.", "success")
        return redirect(url_for("accounts"))

    except Exception as error:
        connection.rollback()
        connection.close()
        flash(f"Error while creating account: {error}", "error")
        return redirect(url_for("accounts"))


# ==========================================
# EDIT / UPDATE / DELETE ACCOUNT
# ==========================================

@app.route("/edit-account/<int:account_id>")
def edit_account(account_id):

    connection = get_connection()

    if connection is None:
        flash("Database connection failed!", "error")
        return redirect(url_for("accounts"))

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT CustomerID, firstname, lastname
            FROM customers
            ORDER BY firstname ASC
        """)
        customer_data = cursor.fetchall()

        cursor.execute("""
            SELECT account_id, customerID, account_number, account_type, balance, status
            FROM accounts
            WHERE account_id = %s
        """, (account_id,))
        account = cursor.fetchone()

        cursor.close()
        connection.close()

        if not account:
            flash("Account not found.", "error")
            return redirect(url_for("accounts"))

        return render_template("edit_account.html", active_page="accounts",
                                account=account, customers=customer_data)

    except Exception as error:
        connection.close()
        flash(f"Error: {error}", "error")
        return redirect(url_for("accounts"))


@app.route("/update-account/<int:account_id>", methods=["POST"])
def update_account(account_id):

    customerID = request.form.get("customerID")
    account_number = request.form.get("account_number", "").strip()
    account_type = request.form.get("account_type")
    balance = request.form.get("balance")
    status = request.form.get("status")

    connection = get_connection()

    if connection is None:
        flash("Database connection failed!", "error")
        return redirect(url_for("accounts"))

    try:
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE accounts
            SET customerID = %s, account_number = %s, account_type = %s,
                balance = %s, status = %s
            WHERE account_id = %s
        """, (customerID, account_number, account_type, balance, status, account_id))

        connection.commit()
        cursor.close()
        connection.close()

        flash("Account updated successfully.", "success")
        return redirect(url_for("accounts"))

    except Exception as error:
        connection.rollback()
        connection.close()
        flash(f"Error while updating account: {error}", "error")
        return redirect(url_for("accounts"))


@app.route("/delete-account/<int:account_id>")
def delete_account(account_id):

    connection = get_connection()

    if connection is None:
        flash("Database connection failed!", "error")
        return redirect(url_for("accounts"))

    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM accounts WHERE account_id = %s", (account_id,))
        connection.commit()
        cursor.close()
        connection.close()

        flash("Account deleted.", "success")
        return redirect(url_for("accounts"))

    except Exception as error:
        connection.rollback()
        connection.close()
        flash(f"Error while deleting account: {error}", "error")
        return redirect(url_for("accounts"))


# ==========================================
# MERCHANTS PAGE
# ==========================================

@app.route("/merchants")
def merchants():

    connection = get_connection()

    if connection is None:
        flash("Database connection failed! Please check your MySQL server.", "error")
        return render_template("merchants.html", active_page="merchants", merchants=[])

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT merchant_id, merchant_name, category, city
            FROM merchants
            ORDER BY merchant_id DESC
        """)
        merchant_data = cursor.fetchall()

        cursor.close()
        connection.close()

        return render_template("merchants.html", active_page="merchants", merchants=merchant_data)

    except Exception as error:
        connection.close()
        flash(f"Error loading merchants: {error}", "error")
        return redirect(url_for("home"))


# ==========================================
# ADD MERCHANT
# ==========================================

@app.route("/add-merchant", methods=["POST"])
def add_merchant():

    merchant_name = request.form.get("merchant_name", "").strip()
    category = request.form.get("category")
    city = request.form.get("city", "").strip()

    if not merchant_name:
        flash("Merchant name is required.", "error")
        return redirect(url_for("merchants"))

    connection = get_connection()

    if connection is None:
        flash("Database connection failed!", "error")
        return redirect(url_for("merchants"))

    try:
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO merchants (merchant_name, category, city)
            VALUES (%s, %s, %s)
        """, (merchant_name, category, city))

        connection.commit()
        cursor.close()
        connection.close()

        flash("Merchant added successfully.", "success")
        return redirect(url_for("merchants"))

    except Exception as error:
        connection.rollback()
        connection.close()
        flash(f"Error while adding merchant: {error}", "error")
        return redirect(url_for("merchants"))


# ==========================================
# EDIT / UPDATE / DELETE MERCHANT
# ==========================================

@app.route("/edit-merchant/<int:merchant_id>")
def edit_merchant(merchant_id):

    connection = get_connection()

    if connection is None:
        flash("Database connection failed!", "error")
        return redirect(url_for("merchants"))

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT merchant_id, merchant_name, category, city
            FROM merchants
            WHERE merchant_id = %s
        """, (merchant_id,))
        merchant = cursor.fetchone()

        cursor.close()
        connection.close()

        if not merchant:
            flash("Merchant not found.", "error")
            return redirect(url_for("merchants"))

        return render_template("edit_merchant.html", active_page="merchants", merchant=merchant)

    except Exception as error:
        connection.close()
        flash(f"Error: {error}", "error")
        return redirect(url_for("merchants"))


@app.route("/update-merchant/<int:merchant_id>", methods=["POST"])
def update_merchant(merchant_id):

    merchant_name = request.form.get("merchant_name", "").strip()
    category = request.form.get("category")
    city = request.form.get("city", "").strip()

    connection = get_connection()

    if connection is None:
        flash("Database connection failed!", "error")
        return redirect(url_for("merchants"))

    try:
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE merchants
            SET merchant_name = %s, category = %s, city = %s
            WHERE merchant_id = %s
        """, (merchant_name, category, city, merchant_id))

        connection.commit()
        cursor.close()
        connection.close()

        flash("Merchant updated successfully.", "success")
        return redirect(url_for("merchants"))

    except Exception as error:
        connection.rollback()
        connection.close()
        flash(f"Error while updating merchant: {error}", "error")
        return redirect(url_for("merchants"))


@app.route("/delete-merchant/<int:merchant_id>")
def delete_merchant(merchant_id):

    connection = get_connection()

    if connection is None:
        flash("Database connection failed!", "error")
        return redirect(url_for("merchants"))

    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM merchants WHERE merchant_id = %s", (merchant_id,))
        connection.commit()
        cursor.close()
        connection.close()

        flash("Merchant deleted.", "success")
        return redirect(url_for("merchants"))

    except Exception as error:
        connection.rollback()
        connection.close()
        flash(f"Error while deleting merchant: {error}", "error")
        return redirect(url_for("merchants"))


# ==========================================
# TRANSACTIONS PAGE
# ==========================================

@app.route("/transactions")
def transactions():

    connection = get_connection()

    if connection is None:
        flash("Database connection failed! Please check your MySQL server.", "error")
        return render_template("transactions.html", active_page="transactions",
                                accounts=[], merchants=[], transactions=[])

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT accounts.account_id, customers.firstname, accounts.account_number
            FROM accounts
            JOIN customers ON accounts.customerID = customers.CustomerID
            ORDER BY accounts.account_id DESC
        """)
        account_data = cursor.fetchall()

        cursor.execute("""
            SELECT merchant_id, merchant_name, category
            FROM merchants
            ORDER BY merchant_name ASC
        """)
        merchant_data = cursor.fetchall()

        cursor.execute("""
            SELECT
                transactions.transaction_id,
                accounts.account_number,
                merchants.merchant_name,
                transactions.transaction_amount,
                transactions.transaction_type,
                transactions.transaction_time,
                transactions.location
            FROM transactions
            JOIN accounts ON transactions.account_id = accounts.account_id
            JOIN merchants ON transactions.merchant_id = merchants.merchant_id
            ORDER BY transactions.transaction_id DESC
        """)
        transaction_data = cursor.fetchall()

        cursor.close()
        connection.close()

        return render_template("transactions.html", active_page="transactions",
                                accounts=account_data, merchants=merchant_data,
                                transactions=transaction_data)

    except Exception as error:
        connection.close()
        flash(f"Error loading transactions: {error}", "error")
        return redirect(url_for("home"))


# ==========================================
# ADD TRANSACTION
# ==========================================

@app.route("/add-transaction", methods=["POST"])
def add_transaction():

    account_id = request.form.get("account_id")
    merchant_id = request.form.get("merchant_id")
    transaction_amount = request.form.get("transaction_amount")
    transaction_type = request.form.get("transaction_type")
    transaction_time = request.form.get("transaction_time")
    location = request.form.get("location", "").strip()

    if not (account_id and merchant_id and transaction_amount and transaction_type and transaction_time):
        flash("All required transaction fields must be filled.", "error")
        return redirect(url_for("transactions"))

    connection = get_connection()

    if connection is None:
        flash("Database connection failed!", "error")
        return redirect(url_for("transactions"))

    try:
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO transactions
            (account_id, merchant_id, transaction_amount, transaction_type, transaction_time, location)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (account_id, merchant_id, transaction_amount, transaction_type, transaction_time, location))

        connection.commit()
        cursor.close()
        connection.close()

        flash("Transaction added successfully.", "success")
        return redirect(url_for("transactions"))

    except Exception as error:
        connection.rollback()
        connection.close()
        flash(f"Error while adding transaction: {error}", "error")
        return redirect(url_for("transactions"))


# ==========================================
# EDIT / UPDATE / DELETE TRANSACTION
# ==========================================

@app.route("/edit-transaction/<int:transaction_id>")
def edit_transaction(transaction_id):

    connection = get_connection()

    if connection is None:
        flash("Database connection failed!", "error")
        return redirect(url_for("transactions"))

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT accounts.account_id, customers.firstname, accounts.account_number
            FROM accounts
            JOIN customers ON accounts.customerID = customers.CustomerID
            ORDER BY accounts.account_id DESC
        """)
        account_data = cursor.fetchall()

        cursor.execute("""
            SELECT merchant_id, merchant_name, category
            FROM merchants
            ORDER BY merchant_name ASC
        """)
        merchant_data = cursor.fetchall()

        cursor.execute("""
            SELECT transaction_id, account_id, merchant_id, transaction_amount,
                   transaction_type, DATE_FORMAT(transaction_time, '%%Y-%%m-%%dT%%H:%%i'), location
            FROM transactions
            WHERE transaction_id = %s
        """, (transaction_id,))
        transaction = cursor.fetchone()

        cursor.close()
        connection.close()

        if not transaction:
            flash("Transaction not found.", "error")
            return redirect(url_for("transactions"))

        return render_template("edit_transaction.html", active_page="transactions",
                                transaction=transaction, accounts=account_data,
                                merchants=merchant_data)

    except Exception as error:
        connection.close()
        flash(f"Error: {error}", "error")
        return redirect(url_for("transactions"))


@app.route("/update-transaction/<int:transaction_id>", methods=["POST"])
def update_transaction(transaction_id):

    account_id = request.form.get("account_id")
    merchant_id = request.form.get("merchant_id")
    transaction_amount = request.form.get("transaction_amount")
    transaction_type = request.form.get("transaction_type")
    transaction_time = request.form.get("transaction_time")
    location = request.form.get("location", "").strip()

    connection = get_connection()

    if connection is None:
        flash("Database connection failed!", "error")
        return redirect(url_for("transactions"))

    try:
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE transactions
            SET account_id = %s, merchant_id = %s, transaction_amount = %s,
                transaction_type = %s, transaction_time = %s, location = %s
            WHERE transaction_id = %s
        """, (account_id, merchant_id, transaction_amount, transaction_type,
              transaction_time, location, transaction_id))

        connection.commit()
        cursor.close()
        connection.close()

        flash("Transaction updated successfully.", "success")
        return redirect(url_for("transactions"))

    except Exception as error:
        connection.rollback()
        connection.close()
        flash(f"Error while updating transaction: {error}", "error")
        return redirect(url_for("transactions"))


@app.route("/delete-transaction/<int:transaction_id>")
def delete_transaction(transaction_id):

    connection = get_connection()

    if connection is None:
        flash("Database connection failed!", "error")
        return redirect(url_for("transactions"))

    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM transactions WHERE transaction_id = %s", (transaction_id,))
        connection.commit()
        cursor.close()
        connection.close()

        flash("Transaction deleted.", "success")
        return redirect(url_for("transactions"))

    except Exception as error:
        connection.rollback()
        connection.close()
        flash(f"Error while deleting transaction: {error}", "error")
        return redirect(url_for("transactions"))


# ==========================================
# FRAUD DETECTION PAGE
# ==========================================

@app.route("/fraud-detection")
def fraud_detection():

    connection = get_connection()

    if connection is None:
        flash("Database connection failed! Please check your MySQL server.", "error")
        return render_template("fraud_detection.html", active_page="fraud", alerts=[])

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                fraud_alerts.alert_id,
                transactions.transaction_id,
                accounts.account_number,
                merchants.merchant_name,
                transactions.transaction_amount,
                fraud_alerts.fraud_reason,
                fraud_alerts.risk_level,
                fraud_alerts.detected_at
            FROM fraud_alerts
            JOIN transactions ON fraud_alerts.transaction_id = transactions.transaction_id
            JOIN accounts ON transactions.account_id = accounts.account_id
            JOIN merchants ON transactions.merchant_id = merchants.merchant_id
            ORDER BY fraud_alerts.alert_id DESC
        """)
        fraud_data = cursor.fetchall()

        cursor.close()
        connection.close()

        return render_template("fraud_detection.html", active_page="fraud", alerts=fraud_data)

    except Exception as error:
        connection.close()
        flash(f"Error loading fraud alerts: {error}", "error")
        return redirect(url_for("home"))


# ==========================================
# ANALYZE FRAUD
# ==========================================

@app.route("/analyze-fraud", methods=["POST"])
def analyze_fraud():

    connection = get_connection()

    if connection is None:
        flash("Database connection failed!", "error")
        return redirect(url_for("fraud_detection"))

    try:
        cursor = connection.cursor()

        # Clear previous alerts before re-running the analysis
        cursor.execute("DELETE FROM fraud_alerts")

        # ==================================
        # RULE 1: Transaction above ₹50,000 -> High risk
        # ==================================
        cursor.execute("""
            SELECT transaction_id
            FROM transactions
            WHERE transaction_amount > 50000
        """)

        for (transaction_id,) in cursor.fetchall():
            cursor.execute("""
                INSERT INTO fraud_alerts (transaction_id, fraud_reason, risk_level)
                VALUES (%s, %s, %s)
            """, (transaction_id, "Transaction amount is above ₹50,000", "High"))

        # ==================================
        # RULE 2: 5+ transactions from the same account within 10 minutes -> High risk
        # ==================================
        cursor.execute("""
            SELECT DISTINCT t1.transaction_id
            FROM transactions t1
            JOIN transactions t2
                ON t1.account_id = t2.account_id
                AND t1.transaction_id != t2.transaction_id
                AND t2.transaction_time BETWEEN
                    DATE_SUB(t1.transaction_time, INTERVAL 10 MINUTE)
                    AND DATE_ADD(t1.transaction_time, INTERVAL 10 MINUTE)
            GROUP BY t1.transaction_id
            HAVING COUNT(t2.transaction_id) >= 4
        """)

        for (transaction_id,) in cursor.fetchall():
            already_flagged = query_one(
                cursor, "SELECT COUNT(*) FROM fraud_alerts WHERE transaction_id = %s",
                (transaction_id,)
            )
            if not already_flagged:
                cursor.execute("""
                    INSERT INTO fraud_alerts (transaction_id, fraud_reason, risk_level)
                    VALUES (%s, %s, %s)
                """, (transaction_id,
                      "5 or more transactions detected from the same account within 10 minutes",
                      "High"))

        # ==================================
        # RULE 3: Transaction between ₹20,000 and ₹50,000 -> Medium risk
        # ==================================
        cursor.execute("""
            SELECT transaction_id
            FROM transactions
            WHERE transaction_amount BETWEEN 20000 AND 50000
        """)

        for (transaction_id,) in cursor.fetchall():
            already_flagged = query_one(
                cursor, "SELECT COUNT(*) FROM fraud_alerts WHERE transaction_id = %s",
                (transaction_id,)
            )
            if not already_flagged:
                cursor.execute("""
                    INSERT INTO fraud_alerts (transaction_id, fraud_reason, risk_level)
                    VALUES (%s, %s, %s)
                """, (transaction_id, "Transaction amount is unusually high (₹20,000–₹50,000)", "Medium"))

        connection.commit()
        cursor.close()
        connection.close()

        flash("Fraud analysis completed.", "success")
        return redirect(url_for("fraud_detection"))

    except Exception as error:
        connection.rollback()
        connection.close()
        flash(f"Error while analyzing fraud: {error}", "error")
        return redirect(url_for("fraud_detection"))


# ==========================================
# REPORTS PAGE
# ==========================================

@app.route("/reports")
def reports():

    connection = get_connection()

    if connection is None:
        flash("Database connection failed! Please check your MySQL server.", "error")
        return render_template("reports.html", active_page="reports",
                                total_customers=0, total_accounts=0, total_transactions=0,
                                total_fraud_alerts=0, high_risk=0, medium_risk=0, alerts=[])

    try:
        cursor = connection.cursor()

        total_customers = query_one(cursor, "SELECT COUNT(*) FROM customers")
        total_accounts = query_one(cursor, "SELECT COUNT(*) FROM accounts")
        total_transactions = query_one(cursor, "SELECT COUNT(*) FROM transactions")
        total_fraud_alerts = query_one(cursor, "SELECT COUNT(*) FROM fraud_alerts")
        high_risk = query_one(cursor, "SELECT COUNT(*) FROM fraud_alerts WHERE risk_level = 'High'")
        medium_risk = query_one(cursor, "SELECT COUNT(*) FROM fraud_alerts WHERE risk_level = 'Medium'")

        cursor.execute("""
            SELECT
                fraud_alerts.alert_id,
                transactions.transaction_id,
                accounts.account_number,
                merchants.merchant_name,
                transactions.transaction_amount,
                fraud_alerts.fraud_reason,
                fraud_alerts.risk_level,
                fraud_alerts.detected_at
            FROM fraud_alerts
            JOIN transactions ON fraud_alerts.transaction_id = transactions.transaction_id
            JOIN accounts ON transactions.account_id = accounts.account_id
            JOIN merchants ON transactions.merchant_id = merchants.merchant_id
            ORDER BY fraud_alerts.detected_at DESC
            LIMIT 10
        """)
        alerts = cursor.fetchall()

        cursor.close()
        connection.close()

        return render_template(
            "reports.html",
            active_page="reports",
            total_customers=total_customers,
            total_accounts=total_accounts,
            total_transactions=total_transactions,
            total_fraud_alerts=total_fraud_alerts,
            high_risk=high_risk,
            medium_risk=medium_risk,
            alerts=alerts
        )

    except Exception as error:
        connection.close()
        flash(f"Reports error: {error}", "error")
        return redirect(url_for("home"))


# ==========================================
# ERROR HANDLERS
# ==========================================

@app.errorhandler(404)
def not_found(error):
    return "<h1>404 - Page Not Found</h1><p><a href='/'>Return to Dashboard</a></p>", 404


# ==========================================
# RUN APPLICATION
# ==========================================

if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "True") == "True"
    app.run(debug=debug_mode)
