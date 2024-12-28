# finances/serializers.py
from rest_framework import serializers
from .models import (
    Expense, 
    SharedExpense, 
    ExpenseShare, 
    Budget, 
    FinancialHealthScore,
    ExpensePrediction
)
from django.contrib.auth import get_user_model
from users.serializers import UserSerializer
from django.db import models
from datetime import datetime
User = get_user_model()

class ExpenseSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Expense
        fields = (
            'id', 
            'user',
            'amount', 
            'category', 
            'description', 
            'date', 
            'is_recurring',
            'recurring_frequency'
        )
        read_only_fields = ('user',)

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class ExpenseShareSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = ExpenseShare
        fields = ('id', 'user', 'user_id', 'share_amount', 'is_paid')

class SharedExpenseSerializer(serializers.ModelSerializer):
    expense = ExpenseSerializer()
    shares = ExpenseShareSerializer(source='expenseshare_set', many=True)
    shared_with = UserSerializer(many=True, read_only=True)
    
    class Meta:
        model = SharedExpense
        fields = ('id', 'expense', 'shared_with', 'shares', 'total_amount', 'is_settled')

    def validate(self, data):
        # Validate that share amounts sum up to total
        shares = data.get('expenseshare_set', [])
        total_shares = sum(share['share_amount'] for share in shares)
        if total_shares != data['total_amount']:
            raise serializers.ValidationError(
                "Sum of shares must equal total amount"
            )
        return data

    def create(self, validated_data):
        expense_data = validated_data.pop('expense')
        shares_data = validated_data.pop('expenseshare_set')
        
        # Create expense
        expense = Expense.objects.create(**expense_data)
        
        # Create shared expense
        shared_expense = SharedExpense.objects.create(
            expense=expense,
            **validated_data
        )
        
        # Create expense shares
        for share_data in shares_data:
            ExpenseShare.objects.create(
                shared_expense=shared_expense,
                **share_data
            )
            
        return shared_expense

class BudgetSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    remaining_amount = serializers.SerializerMethodField()
    
    class Meta:
        model = Budget
        fields = ('id', 'user', 'category', 'amount', 'month', 'remaining_amount')
        read_only_fields = ('user',)
    def get_remaining_amount(self, obj):
        # Parse the month string into a datetime object
        if isinstance(obj.month, str):
            month_date = datetime.strptime(obj.month, '%Y-%m-%d')
        else:
            # If it's already a datetime object, use it directly
            month_date = obj.month
        
        # Use the parsed month_date for filtering
        expenses_sum = Expense.objects.filter(
            user=obj.user,
            category=obj.category,
            date__month=month_date.month,
            date__year=month_date.year
        ).aggregate(total=models.Sum('amount'))['total'] or 0

        return obj.amount - expenses_sum

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class FinancialHealthScoreSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = FinancialHealthScore
        fields = (
            'id', 
            'user',
            'date',
            'spending_score',
            'social_impact_score',
            'total_score'
        )
        read_only_fields = ('user', 'date')

class ExpensePredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpensePrediction
        fields = ['id', 'category', 'predicted_amount', 'prediction_date', 'confidence_score']


class BatchSharedExpenseSerializer(serializers.Serializer):
    expenses = SharedExpenseSerializer(many=True)
    
    def create(self, validated_data):
        expenses = validated_data.get('expenses', [])
        created_expenses = []
        
        for expense_data in expenses:
            serializer = SharedExpenseSerializer(data=expense_data)
            serializer.is_valid(raise_exception=True)
            created_expenses.append(serializer.save())
            
        return created_expenses

class ExpenseStatisticsSerializer(serializers.Serializer):
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    category_breakdown = serializers.DictField(
        child=serializers.DecimalField(max_digits=10, decimal_places=2)
    )
    monthly_trend = serializers.ListField(
        child=serializers.DictField()
    )