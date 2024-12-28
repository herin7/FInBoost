import os
import django
import random
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from users.models import User
from finance.models import Expense, SharedExpense, ExpenseShare, Budget, FinancialHealthScore, ExpensePrediction

def populate_database():
    # Create Users
    users = []
    for i in range(5):
        user = User.objects.create_user(
            username=f'user{i}',
            password='password123',
            profile_picture=None,
            role='user' if i != 0 else 'admin',
        )
        users.append(user)

    # Create Expenses
    categories = ['BILLS', 'GROCERIES', 'ENTERTAINMENT', 'CHARITY', 'ECO_FRIENDLY', 'SOCIAL_IMPACT', 'OTHER']
    expenses = []
    for _ in range(20):
        user = random.choice(users)
        expense = Expense.objects.create(
            user=user,
            amount=round(random.uniform(10.0, 1000.0), 2),
            category=random.choice(categories),
            description=f'Description for {user.username}',
            is_recurring=random.choice([True, False]),
            recurring_frequency=random.choice([7, 30, None]),
        )
        expenses.append(expense)

    # Create Shared Expenses
    for _ in range(10):
        expense = random.choice(expenses)
        shared_expense = SharedExpense.objects.create(
            expense=expense,
            total_amount=expense.amount,
            is_settled=random.choice([True, False]),
        )
        participants = random.sample(users, random.randint(2, len(users)))
        for participant in participants:
            share_amount = expense.amount / len(participants)
            ExpenseShare.objects.create(
                shared_expense=shared_expense,
                user=participant,
                share_amount=round(share_amount, 2),
                is_paid=random.choice([True, False]),
            )

    # Create Budgets
    for user in users:
        for category in categories:
            Budget.objects.create(
                user=user,
                category=category,
                amount=round(random.uniform(100.0, 500.0), 2),
                month=datetime.now().replace(day=1),
            )

    # Create Financial Health Scores
    for user in users:
        for _ in range(5):
            FinancialHealthScore.objects.create(
                user=user,
                spending_score=random.randint(0, 100),
                social_impact_score=random.randint(0, 100),
                total_score=random.randint(0, 100),
            )

    # Create Expense Predictions
    for user in users:
        for category in categories:
            ExpensePrediction.objects.create(
                user=user,
                category=category,
                predicted_amount=round(random.uniform(50.0, 500.0), 2),
                prediction_date=datetime.now().date() + timedelta(days=random.randint(1, 30)),
                confidence_score=round(random.uniform(0.5, 1.0), 2),
            )

if __name__ == '__main__':
    populate_database()
    print("Database populated successfully!")
