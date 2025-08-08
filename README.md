# Expense Tracker

This is a simple Flask application to track expenses with a SQLite database, input validation, and data visualization.

## Features

- Add new expenses with amount, category, and date.
- View all expenses in a table, sorted by date.
- Edit and delete expenses.
- Input validation to ensure all fields are filled and the amount is a positive number.
- Error messages are displayed if validation fails.
- A pie chart showing spending by category.
- Month selector to filter the pie chart by a specific month (YYYY-MM).
- A summary section showing total spent this month and the highest expense category.

## Setup

1.  Install Flask:
    ```
    pip install Flask
    ```
2.  Run the application. This will create the `expenses.db` file.
    ```
    python app.py
    ```
3.  Open your browser and go to `http://127.0.0.1:4000`

## Visualization

- The dashboard shows a pie chart of expenses by category.
- Use the "Filter by Month" dropdown to select a month (format `YYYY-MM`). The chart updates instantly to show only that month's spending distribution.

## API

- `GET /chart-data?month=YYYY-MM`
  - Returns JSON for the chart.
  - Response shape:
    ```json
    { "labels": ["Food", "Transportation"], "data": [123.45, 67.89] }
    ```
  - If `month` is omitted, returns all-time aggregated totals.

## Notes

- The app initializes the SQLite database from `schema.sql` on first run.
- This project uses Bootstrap 4 and Chart.js via CDNs.
