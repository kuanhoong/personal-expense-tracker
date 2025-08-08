from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import sqlite3
import os
from datetime import datetime
import json

app = Flask(__name__)
app.secret_key = 'supersecretkey'
DATABASE = 'expenses.db'

def init_db():
    with app.app_context():
        db = sqlite3.connect(DATABASE)
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

@app.route('/')
def index():
    db = get_db()
    expenses = db.execute('SELECT * FROM expenses ORDER BY date DESC').fetchall()

    # Available months (YYYY-MM) found in data, newest first
    months_rows = db.execute("SELECT DISTINCT substr(date, 1, 7) AS month FROM expenses ORDER BY month DESC").fetchall()
    months = [row['month'] for row in months_rows]

    # Selected month defaults to current month if present, else latest available, else None
    current_month = datetime.now().strftime('%Y-%m')
    selected_month = current_month if current_month in months else (months[0] if months else None)

    # Chart data filtered by selected month (or empty if no data)
    chart_labels = []
    chart_data = []
    if selected_month:
        chart_rows = db.execute(
            'SELECT category, SUM(amount) AS total FROM expenses WHERE date LIKE ? GROUP BY category',
            (f"{selected_month}%",)
        ).fetchall()
        chart_labels = [row['category'] for row in chart_rows]
        chart_data = [row['total'] for row in chart_rows]

    # Calculate summary data (kept as originally implemented)
    monthly_total = 0
    for expense in expenses:
        if expense['date'].startswith(current_month):
            monthly_total += expense['amount']

    # Highest category across all time (as originally implemented)
    category_totals_all_time = {}
    for expense in expenses:
        category_totals_all_time[expense['category']] = (
            category_totals_all_time.get(expense['category'], 0) + expense['amount']
        )
    highest_category = ""
    if category_totals_all_time:
        highest_category = max(category_totals_all_time, key=category_totals_all_time.get)

    db.close()

    return render_template(
        'index.html',
        expenses=expenses,
        chart_labels=json.dumps(chart_labels),
        chart_data=json.dumps(chart_data),
        monthly_total=monthly_total,
        highest_category=highest_category,
        months=months,
        selected_month=selected_month,
    )

@app.route('/add', methods=['POST'])
def add_expense():
    amount = request.form.get('amount')
    category = request.form.get('category')
    date = request.form.get('date')

    if not amount or not category or not date:
        flash('All fields are required.', 'danger')
        return redirect(url_for('index'))

    try:
        amount_float = float(amount)
        if amount_float <= 0:
            flash('Amount must be a positive number.', 'danger')
            return redirect(url_for('index'))
    except ValueError:
        flash('Invalid amount. Please enter a number.', 'danger')
        return redirect(url_for('index'))

    db = get_db()
    db.execute('INSERT INTO expenses (amount, category, date) VALUES (?, ?, ?)',
               (amount_float, category, date))
    db.commit()
    db.close()
    
    flash('Expense added successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_expense(id):
    db = get_db()
    expense = db.execute('SELECT * FROM expenses WHERE id = ?', (id,)).fetchone()

    if request.method == 'POST':
        amount = request.form.get('amount')
        category = request.form.get('category')
        date = request.form.get('date')

        if not amount or not category or not date:
            flash('All fields are required.', 'danger')
            return redirect(url_for('edit_expense', id=id))

        try:
            amount_float = float(amount)
            if amount_float <= 0:
                flash('Amount must be a positive number.', 'danger')
                return redirect(url_for('edit_expense', id=id))
        except ValueError:
            flash('Invalid amount. Please enter a number.', 'danger')
            return redirect(url_for('edit_expense', id=id))

        db.execute('UPDATE expenses SET amount = ?, category = ?, date = ? WHERE id = ?',
                   (amount_float, category, date, id))
        db.commit()
        db.close()
        flash('Expense updated successfully!', 'success')
        return redirect(url_for('index'))

    db.close()
    return render_template('edit_expense.html', expense=expense)

@app.route('/delete/<int:id>')
def delete_expense(id):
    db = get_db()
    db.execute('DELETE FROM expenses WHERE id = ?', (id,))
    db.commit()
    db.close()
    flash('Expense deleted successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/chart-data')
def chart_data():
    """Return chart data (labels and data) for a given month (YYYY-MM). If no month
    is provided, return all-time totals."""
    month = request.args.get('month')
    db = get_db()
    if month:
        rows = db.execute(
            'SELECT category, SUM(amount) AS total FROM expenses WHERE date LIKE ? GROUP BY category',
            (f"{month}%",)
        ).fetchall()
    else:
        rows = db.execute(
            'SELECT category, SUM(amount) AS total FROM expenses GROUP BY category'
        ).fetchall()
    db.close()

    labels = [row['category'] for row in rows]
    data = [row['total'] for row in rows]
    return jsonify({
        'labels': labels,
        'data': data,
    })

if not os.path.exists(DATABASE):
    init_db()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 4000))
    app.run(host='0.0.0.0', port=port, debug=True)
