from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, make_response
import sqlite3
import csv
import io
from datetime import datetime, date
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'budget-tracker-secret-2024')

DATABASE = os.environ.get('DATABASE_PATH', 'budget.db')

CATEGORIES = [
    'Food & Dining', 'Transport', 'Housing', 'Healthcare',
    'Entertainment', 'Shopping', 'Education', 'Savings',
    'Utilities', 'Other'
]

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            date TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT UNIQUE NOT NULL,
            monthly_limit REAL NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# THIS LINE IS THE FIX — runs when gunicorn imports the file
init_db()

@app.route('/')
def index():
    conn = get_db()
    today = date.today()
    month_start = today.replace(day=1).isoformat()

    expenses = conn.execute(
        'SELECT * FROM expenses ORDER BY date DESC LIMIT 50'
    ).fetchall()

    monthly_expenses = conn.execute(
        'SELECT * FROM expenses WHERE date >= ? ORDER BY date DESC',
        (month_start,)
    ).fetchall()

    category_totals = conn.execute(
        '''SELECT category, SUM(amount) as total 
           FROM expenses WHERE date >= ? 
           GROUP BY category ORDER BY total DESC''',
        (month_start,)
    ).fetchall()

    budgets = conn.execute('SELECT * FROM budgets').fetchall()
    budget_map = {b['category']: b['monthly_limit'] for b in budgets}

    monthly_total = sum(e['amount'] for e in monthly_expenses)
    conn.close()

    return render_template('index.html',
        expenses=expenses,
        category_totals=category_totals,
        monthly_total=monthly_total,
        categories=CATEGORIES,
        budget_map=budget_map,
        current_month=today.strftime('%B %Y')
    )

@app.route('/add', methods=['POST'])
def add_expense():
    amount = request.form.get('amount')
    category = request.form.get('category')
    description = request.form.get('description', '')
    expense_date = request.form.get('date') or date.today().isoformat()

    if not amount or not category:
        flash('Amount and category are required.', 'error')
        return redirect(url_for('index'))

    try:
        amount = float(amount)
        if amount <= 0:
            raise ValueError
    except ValueError:
        flash('Please enter a valid positive amount.', 'error')
        return redirect(url_for('index'))

    conn = get_db()
    conn.execute(
        'INSERT INTO expenses (amount, category, description, date) VALUES (?, ?, ?, ?)',
        (amount, category, description, expense_date)
    )
    conn.commit()
    conn.close()
    flash(f'Expense of KES {amount:,.2f} added successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/delete/<int:expense_id>', methods=['POST'])
def delete_expense(expense_id):
    conn = get_db()
    conn.execute('DELETE FROM expenses WHERE id = ?', (expense_id,))
    conn.commit()
    conn.close()
    flash('Expense deleted.', 'success')
    return redirect(url_for('index'))

@app.route('/budgets', methods=['GET', 'POST'])
def budgets():
    conn = get_db()
    if request.method == 'POST':
        category = request.form.get('category')
        limit = request.form.get('limit')
        try:
            limit = float(limit)
            conn.execute(
                'INSERT OR REPLACE INTO budgets (category, monthly_limit) VALUES (?, ?)',
                (category, limit)
            )
            conn.commit()
            flash(f'Budget set for {category}!', 'success')
        except:
            flash('Invalid budget amount.', 'error')

    today = date.today()
    month_start = today.replace(day=1).isoformat()
    all_budgets = conn.execute('SELECT * FROM budgets').fetchall()
    spending = conn.execute(
        '''SELECT category, SUM(amount) as total 
           FROM expenses WHERE date >= ? GROUP BY category''',
        (month_start,)
    ).fetchall()
    spending_map = {s['category']: s['total'] for s in spending}
    conn.close()

    return render_template('budgets.html',
        budgets=all_budgets,
        spending_map=spending_map,
        categories=CATEGORIES,
        current_month=today.strftime('%B %Y')
    )

@app.route('/export/csv')
def export_csv():
    conn = get_db()
    expenses = conn.execute('SELECT * FROM expenses ORDER BY date DESC').fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Amount (KES)', 'Category', 'Description', 'Date', 'Created At'])
    for e in expenses:
        writer.writerow([e['id'], e['amount'], e['category'], e['description'], e['date'], e['created_at']])

    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=expenses.csv'
    response.headers['Content-Type'] = 'text/csv'
    return response

@app.route('/api/chart-data')
def chart_data():
    conn = get_db()
    today = date.today()
    month_start = today.replace(day=1).isoformat()
    data = conn.execute(
        '''SELECT category, SUM(amount) as total 
           FROM expenses WHERE date >= ? 
           GROUP BY category ORDER BY total DESC''',
        (month_start,)
    ).fetchall()
    conn.close()
    return jsonify({
        'labels': [r['category'] for r in data],
        'values': [r['total'] for r in data]
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
