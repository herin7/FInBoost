# finances/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ExpenseViewSet, SharedExpenseViewSet,BudgetViewSet

router = DefaultRouter()
router.register(r'expenses', ExpenseViewSet, basename='expense')
router.register(r'shared-expenses', SharedExpenseViewSet, basename='shared-expense')
router.register(r'budget',BudgetViewSet , basename='budget')

urlpatterns = [
    path('', include(router.urls)),
]