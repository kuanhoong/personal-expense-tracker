# Expense Tracker

This is a simple Flask application to track expenses with a SQLite database, input validation, and data visualization.

## Features

- Add new expenses with amount, category, and date.
- View all expenses in a table, sorted by date.
- Edit and delete expenses.
- Input validation to ensure all fields are filled and the amount is a positive number.
- Error messages are displayed if validation fails.
- A pie chart showing spending by category.
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
