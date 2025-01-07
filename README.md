# Financial Management API

![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)
![Django REST Framework](https://img.shields.io/badge/DJANGO-REST-ff1709?style=for-the-badge&logo=django&logoColor=white&color=ff1709&labelColor=gray)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)

Welcome to the **Financial Management API**! This project is a backend API built with Django and Django REST Framework (DRF) to help users manage their finances. It includes features like expense tracking, shared expenses, budgeting, financial health scoring, and expense predictions using machine learning.

---

## Features

- **Expense Management**: Track personal expenses with categories like Bills, Groceries, Entertainment, etc.
- **Shared Expenses**: Split expenses among multiple users and track who has paid their share.
- **Budgeting**: Set monthly budgets for different categories and monitor spending.
- **Financial Health Scoring**: Get a financial health score based on your spending habits and social impact.
- **Expense Predictions**: Use machine learning to predict future expenses based on historical data.

---

## API Endpoints

### Expenses
- **GET /expenses/**: Retrieve all expenses for the authenticated user.
- **POST /expenses/**: Create a new expense.
- **GET /expenses/{id}/**: Retrieve a specific expense.
- **PUT /expenses/{id}/**: Update a specific expense.
- **DELETE /expenses/{id}/**: Delete a specific expense.
- **GET /expenses/health_score/**: Calculate and retrieve the financial health score.
- **GET /expenses/predict_expenses/**: Predict future expenses.

### Shared Expenses
- **GET /shared-expenses/**: Retrieve all shared expenses for the authenticated user.
- **POST /shared-expenses/**: Create a new shared expense.
- **GET /shared-expenses/{id}/**: Retrieve a specific shared expense.
- **PUT /shared-expenses/{id}/**: Update a specific shared expense.
- **DELETE /shared-expenses/{id}/**: Delete a specific shared expense.

### Budgets
- **GET /budget/**: Retrieve all budgets for the authenticated user.
- **POST /budget/**: Create a new budget.
- **GET /budget/{id}/**: Retrieve a specific budget.
- **PUT /budget/{id}/**: Update a specific budget.
- **DELETE /budget/{id}/**: Delete a specific budget.
- **GET /budget/monthly_budget/**: Retrieve the total budget for the current month.
- **GET /budget/category_budget/**: Retrieve the budget details for each category in the current month.

---

## Installation

### Prerequisites
- Python 3.8+
- Django 4.0+
- Django REST Framework

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/herin7/FInboost.git
   cd FInBoost
I'll help format this content as a proper Markdown document.

```markdown
# API Setup Guide

## Initial Setup

### Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Install dependencies:
```bash
pip install -r requirements.txt
```

### Run migrations:
```bash
python manage.py migrate
```

### Start the development server:
```bash
python manage.py runserver
```

Access the API at http://127.0.0.1:8000/.

## Example Requests

### Create an Expense
POST `/expenses/`
```json
{
    "amount": 100.00,
    "category": "GROCERIES",
    "description": "Weekly groceries",
    "is_recurring": false
}
```

### Predict Future Expenses
GET `/expenses/predict_expenses/`

### Retrieve Financial Health Score
GET `/expenses/health_score/`

### Create a Shared Expense
POST `/shared-expenses/`
```json
{
    "total_amount": 200.00,
    "category": "ENTERTAINMENT",
    "description": "Dinner with friends",
    "shares": [
        {"user_id": 2, "amount": 100.00},
        {"user_id": 3, "amount": 100.00}
    ]
}
```

### Create a Budget
POST `/budget/`
```json
{
    "category": "GROCERIES",
    "amount": 500.00,
    "month": "2023-10-01"
}
```

## Machine Learning Integration

The API uses machine learning models to predict future expenses and calculate financial health scores. The ExpensePredictor and FinancialHealthScorer classes handle these tasks.

## Happy coding!
