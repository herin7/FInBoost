# # ml_services/expense_predictor.py
# import pandas as pd
# from sklearn.ensemble import RandomForestRegressor
# from datetime import datetime, timedelta

# class ExpensePredictor:
#     def __init__(self):
#         self.model = RandomForestRegressor(n_estimators=100)
        
#     def prepare_data(self, expenses):
#         df = pd.DataFrame(expenses)
        
#         # Extract temporal features
#         df['date'] = pd.to_datetime(df['date'])
#         df['month'] = df['date'].dt.month
#         df['day'] = df['date'].dt.day
#         df['day_of_week'] = df['date'].dt.dayofweek
        
#         # Create category dummies
#         category_dummies = pd.get_dummies(df['category'], prefix='category')
#         df = pd.concat([df, category_dummies], axis=1)
        
#         return df

#     def train_model(self, user_expenses):
#         if not user_expenses:
#             return False
            
#         df = self.prepare_data(user_expenses)
        
#         # Features for training
#         features = ['month', 'day', 'day_of_week'] + [col for col in df.columns if col.startswith('category_')]
#         X = df[features]
#         y = df['amount']
        
#         self.model.fit(X, y)
#         return True
        
#     def predict_future_expenses(self, user_expenses, days_ahead=30):
#         if not self.train_model(user_expenses):
#             return []
            
#         # Generate future dates
#         future_dates = [datetime.now() + timedelta(days=i) for i in range(days_ahead)]
        
#         predictions = []
#         for date in future_dates:
#             for category in set([exp['category'] for exp in user_expenses]):
#                 # Create feature row for prediction
#                 feature_row = pd.DataFrame({
#                     'month': [date.month],
#                     'day': [date.day],
#                     'day_of_week': [date.weekday()],
#                 })
                
#                 # Add category dummies
#                 for cat in set([exp['category'] for exp in user_expenses]):
#                     feature_row[f'category_{cat}'] = 1 if cat == category else 0
                
#                 predicted_amount = self.model.predict(feature_row)[0]
#                 confidence = self.model.score(
#                     self.prepare_data(user_expenses)[['month', 'day', 'day_of_week']],
#                     [exp['amount'] for exp in user_expenses]
#                 )
                
#                 predictions.append({
#                     'date': date,
#                     'category': category,
#                     'predicted_amount': predicted_amount,
#                     'confidence': confidence
#                 })
                
#         return predictions




from sklearn.ensemble import RandomForestRegressor
from datetime import timedelta, datetime
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import pandas as pd
from finance.models import Expense, ExpensePrediction
class ExpensePredictor:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100)
        self.feature_columns = None

    def prepare_data(self, expenses_data):
        """
        Convert expenses data to DataFrame and prepare features
        """
        # Convert list of dictionaries to DataFrame
        df = pd.DataFrame(expenses_data)
        
        # Extract temporal features
        df['date'] = pd.to_datetime(df['date'])
        df['month'] = df['date'].dt.month
        df['day'] = df['date'].dt.day
        df['day_of_week'] = df['date'].dt.dayofweek
        
        # Create category dummies
        category_dummies = pd.get_dummies(df['category'], prefix='category')
        df = pd.concat([df, category_dummies], axis=1)
        
        # Define feature columns
        self.feature_columns = ['month', 'day', 'day_of_week'] + list(category_dummies.columns)
        
        return df

    def train_model(self, expenses_data):
        """
        Train the model using provided expenses data
        """
        if not expenses_data:
            return False
        
        # Prepare data
        df = self.prepare_data(expenses_data)
        
        # Prepare features and target
        X = df[self.feature_columns]
        y = df['amount'].astype(float)  # Convert Decimal to float
        
        # Train the model
        self.model.fit(X, y)
        return True

    def predict_future_expenses(self, expenses_data, user, days_ahead=30):
        """
        Predict future expenses for each category
        """
        if self.feature_columns is None:
            return []

        predictions = []
        future_dates = [datetime.now() + timedelta(days=i) for i in range(days_ahead)]
        
        # Get unique categories from the feature columns
        categories = [col.replace('category_', '') for col in self.feature_columns if col.startswith('category_')]
        
        for date in future_dates:
            for category in categories:
                # Create feature dictionary
                feature_dict = {
                    'month': date.month,
                    'day': date.day,
                    'day_of_week': date.weekday()
                }
                
                # Add category dummy variables
                for cat in categories:
                    feature_dict[f'category_{cat}'] = 1 if cat == category else 0
                
                # Convert to DataFrame
                feature_df = pd.DataFrame([feature_dict])
                
                # Ensure columns match training data
                feature_df = feature_df[self.feature_columns]
                
                # Make prediction
                predicted_amount = float(self.model.predict(feature_df)[0])
                
                predictions.append({
                    'user': user,
                    'category': category,
                    'predicted_amount': predicted_amount,
                    'prediction_date': date.date(),
                    'confidence_score': self.model.score(
                        self.prepare_data(expenses_data)[self.feature_columns],
                        self.prepare_data(expenses_data)['amount'].astype(float)
                    )
                })
        
        return predictions


# # health_score/scorer.py
class FinancialHealthScorer:
    def calculate_score(self, user_expenses, total_budget):
        if not user_expenses:
            return {'spending': 0, 'social_impact': 0, 'total': 0}
            
        # Calculate spending score
        total_expense = sum(exp['amount'] for exp in user_expenses)
        spending_score = min(100, (1 - (total_expense / total_budget)) * 100) if total_budget > 0 else 0
        
        # Calculate social impact score
        social_expenses = sum(exp['amount'] for exp in user_expenses 
                            if exp['category'] in ['CHARITY', 'ECO_FRIENDLY', 'SOCIAL_IMPACT'])
        social_score = min(100, (social_expenses / total_expense) * 100) if total_expense > 0 else 0
        
        # Calculate total score
        total_score = (float(spending_score) * 0.6) + (float(social_score) * 0.4)
        
        return {
            'spending': round(spending_score),
            'social_impact': round(social_score),
            'total': round(total_score)
        }
