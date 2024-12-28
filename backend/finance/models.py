from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

class Expense(models.Model):
    CATEGORY_CHOICES = [
        ('BILLS', 'Bills'),
        ('GROCERIES', 'Groceries'),
        ('ENTERTAINMENT', 'Entertainment'),
        ('CHARITY', 'Charity'),
        ('ECO_FRIENDLY', 'Eco Friendly'),
        ('SOCIAL_IMPACT', 'Social Impact'),
        ('OTHER', 'Other'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.CharField(max_length=200)
    date = models.DateTimeField(auto_now_add=True)
    is_recurring = models.BooleanField(default=False)
    recurring_frequency = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1)])  # Ensure frequency is at least 1 day if provided
    month = models.DateField(null=True,blank=True) 
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'category', 'month'], name='unique_expense_per_user_category_month')
        ]

class SharedExpense(models.Model):
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE)
    shared_with = models.ManyToManyField(settings.AUTH_USER_MODEL, through='ExpenseShare')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    is_settled = models.BooleanField(default=False)

    def clean(self):
        # Ensure total_amount is the sum of all share amounts
        total_share = sum(share.share_amount for share in self.expenseshare_set.all())
        if self.total_amount != total_share:
            raise ValueError("The total shared amount must equal the sum of individual share amounts.")

class ExpenseShare(models.Model):
    shared_expense = models.ForeignKey(SharedExpense, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    share_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    is_paid = models.BooleanField(default=False)

    class Meta:
        unique_together = ('shared_expense', 'user')

class Budget(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category = models.CharField(max_length=20, choices=Expense.CATEGORY_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    month = models.DateField()  # Store first day of the month

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'category', 'month'], name='unique_budget_per_user_category_month')
        ]

class FinancialHealthScore(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    spending_score = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    social_impact_score = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    total_score = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'date'], name='unique_score_per_user_date')
        ]

class ExpensePrediction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category = models.CharField(max_length=20, choices=Expense.CATEGORY_CHOICES)
    predicted_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    prediction_date = models.DateField()
    confidence_score = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(1)])

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'category', 'prediction_date'], name='unique_prediction_per_user_category_date')
        ]
