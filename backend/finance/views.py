from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum
from datetime import datetime
from .models import (
    Expense, SharedExpense, ExpenseShare, 
    Budget, FinancialHealthScore, ExpensePrediction
)
from .serializers import (
    ExpenseSerializer, SharedExpenseSerializer, 
    BudgetSerializer, FinancialHealthScoreSerializer, ExpensePredictionSerializer
)
from ml_services.expense_validator import ExpensePredictor, FinancialHealthScorer



class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Expense.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def health_score(self, request):
        current_month = datetime.now().month
        current_date = datetime.now().date()  # Get today's date for unique constraint check
        
        expenses = self.get_queryset()
        
        total_budget = Budget.objects.filter(
            user=request.user,
            month__month=current_month  # Filter budgets for the current month
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        scorer = FinancialHealthScorer()
        score = scorer.calculate_score(expenses.values(), total_budget)

        health_score, created = FinancialHealthScore.objects.update_or_create(
            user=request.user,
            date=current_date,  # Ensure the score is calculated only once per day
            defaults={
                'spending_score': score['spending'],
                'social_impact_score': score['social_impact'],
                'total_score': score['total']
            }
        )
        
        return Response(FinancialHealthScoreSerializer(health_score).data)

    @action(detail=False, methods=['get'])
    def predict_expenses(self, request):
        expenses_data = list(self.get_queryset().values(
            'amount', 'category', 'date', 'is_recurring'
        ))

        if not expenses_data:
            return Response(
                {'error': 'No historical expense data available for prediction'},
                status=status.HTTP_400_BAD_REQUEST
            )

        predictor = ExpensePredictor()

        if not predictor.train_model(expenses_data):
            return Response(
                {'error': 'Failed to train prediction model'},
                status=status.HTTP_400_BAD_REQUEST
            )

        predictions = predictor.predict_future_expenses(expenses_data, request.user)

        if not predictions:
            return Response(
                {'error': 'Failed to generate predictions'},
                status=status.HTTP_400_BAD_REQUEST
            )

        prediction_objects = []
        for pred in predictions:
            prediction, created = ExpensePrediction.objects.update_or_create(
                user=request.user,
                category=pred['category'],
                prediction_date=pred['prediction_date'],
                defaults={
                    'predicted_amount': pred['predicted_amount'],
                    'confidence_score': pred['confidence_score']
                }
            )
            prediction_objects.append(prediction)

        return Response(
            ExpensePredictionSerializer(prediction_objects, many=True).data,
            status=status.HTTP_200_OK
        )

class SharedExpenseViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = SharedExpenseSerializer

    def get_queryset(self):
        return SharedExpense.objects.filter(
            shared_with=self.request.user
        )
    def create(self, request, *args, **kwargs):
        data = request.data
        
        total_shared = sum(share['amount'] for share in data['shares'])
        if total_shared != data['total_amount']:
            return Response(
                {'error': 'Shared amounts do not add up to the total amount.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        expense = Expense.objects.create(
            user=request.user,
            amount=data['total_amount'],
            category=data['category'],
            description=data['description']
        )
        
        shared_expense = SharedExpense.objects.create(
            expense=expense,
            total_amount=data['total_amount']
        )
        
        for share in data['shares']:
            user_id = share['user_id']
            ExpenseShare.objects.create(
                shared_expense=shared_expense,
                user_id=user_id,
                share_amount=share['amount']
            )
        
        return Response(
            self.serializer_class(shared_expense).data, 
            status=status.HTTP_201_CREATED
        )

class BudgetViewSet(viewsets.ModelViewSet):
    queryset = Budget.objects.all()
    serializer_class = BudgetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return the budgets for the authenticated user."""
        return Budget.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        """Create a new budget entry."""
        data = request.data
        category = data.get('category')
        amount = data.get('amount')
        month = data.get('month')

        existing_budget = Budget.objects.filter(
            user=request.user, category=category, month=month
        ).first()

        if existing_budget:
            return Response(
                {'error': 'Budget for this category and month already exists.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        budget = Budget.objects.create(
            user=request.user,
            category=category,
            amount=amount,
            month=month
        )

        return Response(
            self.serializer_class(budget).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=False, methods=['get'])
    def monthly_budget(self, request):
        """Get the total budget for the current month."""
        current_month = datetime.now().month
        total_budget = Budget.objects.filter(
            user=request.user, month__month=current_month
        ).aggregate(Sum('amount'))['amount__sum'] or 0

        return Response({'total_budget': total_budget})

    @action(detail=False, methods=['get'])
    def category_budget(self, request):
        """Get the budget details for each category in the current month."""
        current_month = datetime.now().month
        budgets = Budget.objects.filter(
            user=request.user, month__month=current_month
        ).values('category', 'amount')

        return Response(budgets)
