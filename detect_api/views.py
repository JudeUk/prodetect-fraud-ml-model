import json
import pickle
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import numpy as np
import pandas as pd
from django.db import connection

# Load the transformer and model
# with open('transformer.pkl', 'rb') as file:
#     transformer = pickle.load(file)

# with open('xgb_model.pkl', 'rb') as file:
#     model = pickle.load(file)


# # Load the model and transformer
# with open('rf_model.pkl', 'rb') as file:
#     loaded_model = pickle.load(file)

# with open('rf_transformer.pkl', 'rb') as file:
#     loaded_transformer = pickle.load(file)

# Load the model and transformer
with open('rf_model_two.pkl', 'rb') as file:
    loaded_model = pickle.load(file)

with open('rf_transformer_two.pkl', 'rb') as file:
    loaded_transformer = pickle.load(file)


@csrf_exempt
def predict(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Extract relevant features and drop unnecessary ones
            relevant_features = {
                # "Timestamp": [data["Timestamp"]],
                "From Bank": [data["From Bank"]],
                "Account.1": [data["Account.1"]],
                "Account": [data["Account"]],
                "To Bank": [data["To Bank"]],
                
                "Amount Received":[data["Amount Received"]],
                "Receiving Currency": [data["Receiving Currency"]],
                # "Payment Currency":[data["Payment Currency"]],
                "Payment Format":[data["Payment Format"]]      
            }

            # ['Timestamp', 'Amount Paid', 'Payment Currency']
            
            # # Transform the input data
            # input_data = np.array([list(relevant_features.values())])
            # transformed_data = transformer.transform(input_data)


            input_df = pd.DataFrame(relevant_features)

            # Transform the input data using the transformer
            input_df_transformed = pd.DataFrame(loaded_transformer.transform(input_df), columns=input_df.columns)

            
            # Make prediction
            prediction_proba = loaded_model.predict_proba(input_df_transformed)[:, 1]

            prediction = prediction_proba 
            # prediction = (prediction_proba >= 0.5).astype(int)
            
            return JsonResponse({'prediction': int(prediction[0]), 'probability': float(prediction_proba[0])})
        except Exception as e:
            print("error : ",e)
            return JsonResponse({'error': str(e)})
    else:
        return JsonResponse({'error': 'Invalid request method.'})







# old predict transaction method starts

# @csrf_exempt
# def predict_transaction(request):
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
            
#              # Extract relevant features and drop unnecessary ones
#             relevant_features = {
#                 # "Timestamp": [data["Timestamp"]],
#                 "CustomerID": [data["CustomerID"]],
#                 "Account Number": [data["Account Number"]],
#                 "Transaction Type": [data["Transaction Type"]],
#                 "Amount": [data["Amount"]],
                
#                 "Account Balance":[data["Account Balance"]],
#                 "Receiver Name": [data["Receiver Name"]],
#                 # "Payment Currency":[data["Payment Currency"]],
#                 "Transaction Time":[data["Transaction Time"]]      
#             }

#             input_data = pd.DataFrame(relevant_features)
            
#             # Preprocess the data
#             input_data_transformed = pd.DataFrame(loaded_transformer.transform(input_data),columns=input_data.columns) 
            
#             # Make prediction
#             prediction = loaded_model.predict(input_data_transformed)
            
#             return JsonResponse({'prediction': prediction[0]})
        
            
#         except Exception as e:
#             print("error : ",e)
#             return JsonResponse({'error': str(e)})
#     else:
#         return JsonResponse({'error': 'Invalid request method.'})

# old predict transaction method ends.





# def get_historical_transactions():
#     query = """
#     SELECT customerid, amount, transactiontime
#     FROM transactions
#     """
#     with connection.cursor() as cursor:
#         cursor.execute(query)
#         rows = cursor.fetchall()
#         columns = [col[0] for col in cursor.description]
#         return pd.DataFrame(rows, columns=columns)

# def calculate_avg_amount_and_freq(customer_id, transaction_time, historical_transactions):
#     customer_transactions = historical_transactions[historical_transactions['customerid'] == customer_id]
#     if customer_transactions.empty:
#         return None, None, None

#     avg_amount = customer_transactions['amount'].mean()

#     customer_transactions['transactiontime'] = pd.to_datetime(customer_transactions['transactiontime'])
#     customer_transactions = customer_transactions.sort_values('transactiontime')
#     customer_transactions['Prev Transaction Time'] = customer_transactions['transactiontime'].shift(1)
#     customer_transactions['Transaction Delta'] = customer_transactions['transactiontime'] - customer_transactions['Prev Transaction Time']
#     customer_transactions['Transaction Delta'] = customer_transactions['Transaction Delta'].dt.total_seconds().fillna(0)

#     transaction_count = customer_transactions.shape[0]

#     if transaction_count > 0:
#         last_transaction_time = customer_transactions['transactiontime'].iloc[-1]
#         transaction_freq = (transaction_time - last_transaction_time).total_seconds()
#     else:
#         transaction_freq = 0

#     return avg_amount, transaction_freq, transaction_count

# @csrf_exempt
# def predict_transaction(request):
#     if request.method == 'POST':
#         # form = TransactionForm(request.POST)
#         # if form.is_valid():
#         try:
# #             data = json.loads(request.body)

#             data = json.loads(request.body)
#             customer_id = data['CustomerID']
#             transaction_time = pd.to_datetime(data['Transaction Time'])

#             # Load historical transactions from the database
#             historical_transactions = get_historical_transactions()

#             # Calculate the average transaction amount and frequency
#             avg_amount, transaction_freq, transaction_count = calculate_avg_amount_and_freq(customer_id, transaction_time, historical_transactions)
#             if avg_amount is None or transaction_freq is None or transaction_count is None:
#                 return JsonResponse({'error': 'No historical data for this customer'}, status=400)

#             # Add the calculated columns to the input data
#             data['avg_amount'] = avg_amount
#             data['transaction_freq'] = transaction_freq
#             data['transaction_count'] = transaction_count

#             input_data = pd.DataFrame([data])

#             # Preprocess the data
#             input_data_transformed = loaded_transformer.transform(input_data)

#             # Make prediction
#             prediction = loaded_model.predict(input_data_transformed)

#             return JsonResponse({'prediction': prediction[0]})
#         except Exception as e:
#             print("error : ",e)
#             return JsonResponse({'error': str(e)})
#     else:
#         return JsonResponse({'error': 'Invalid request method.'})



def get_historical_transactions():
    query = """
    SELECT customerid, amount, transactiontime
    FROM transactions
    """
    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        return pd.DataFrame(rows, columns=columns)

def calculate_customer_stats(customer_id, transaction_time, historical_transactions):
    customer_transactions = historical_transactions[historical_transactions['customerid'] == customer_id]
    if customer_transactions.empty:
        return None, None, None, None, None, None

    avg_amount = customer_transactions['amount'].mean()

    customer_transactions['transactiontime'] = pd.to_datetime(customer_transactions['transactiontime'])
    customer_transactions = customer_transactions.sort_values('transactiontime')
    customer_transactions['Prev Transaction Time'] = customer_transactions['transactiontime'].shift(1)
    customer_transactions['Transaction Delta'] = customer_transactions['transactiontime'] - customer_transactions['Prev Transaction Time']
    customer_transactions['Transaction Delta'] = customer_transactions['Transaction Delta'].dt.total_seconds().fillna(0)

    transaction_count = customer_transactions.shape[0]

    if transaction_count > 0:
        last_transaction_time = customer_transactions['transactiontime'].iloc[-1]
        transaction_freq = (transaction_time - last_transaction_time).total_seconds()
    else:
        transaction_freq = 0

    customer_transactions['day'] = customer_transactions['transactiontime'].dt.date
    customer_transactions['week'] = customer_transactions['transactiontime'].dt.isocalendar().week
    customer_transactions['month'] = customer_transactions['transactiontime'].dt.month

    daily_count = customer_transactions[customer_transactions['day'] == transaction_time.date()].shape[0]
    weekly_count = customer_transactions[customer_transactions['week'] == transaction_time.isocalendar().week].shape[0]
    monthly_count = customer_transactions[customer_transactions['month'] == transaction_time.month].shape[0]

    return avg_amount, transaction_freq, transaction_count, daily_count, weekly_count, monthly_count

@csrf_exempt
def predict_transaction(request):
    if request.method == 'POST':
        # form = TransactionForm(request.POST)
        # if form.is_valid():
        try:
#             data = json.loads(request.body)

            data = json.loads(request.body)
            customer_id = data['CustomerID']
            transaction_time = pd.to_datetime(data['Transaction Time'])

            # Load historical transactions from the database
            historical_transactions = get_historical_transactions()

            # Calculate the average transaction amount, frequency, and counts
            avg_amount, transaction_freq, transaction_count, daily_count, weekly_count, monthly_count = calculate_customer_stats(customer_id, transaction_time, historical_transactions)
            if avg_amount is None or transaction_freq is None or transaction_count is None:
                return JsonResponse({'error': 'No historical data for this customer'}, status=400)

            # Add the calculated columns to the input data
            data['avg_amount'] = avg_amount
            data['transaction_freq'] = transaction_freq
            data['transaction_count'] = transaction_count
            data['daily_count'] = daily_count
            data['weekly_count'] = weekly_count
            data['monthly_count'] = monthly_count

            input_data = pd.DataFrame([data])

            # Preprocess the data
            input_data_transformed = loaded_transformer.transform(input_data)

            # Make prediction
            prediction = loaded_model.predict(input_data_transformed)

            return JsonResponse({'prediction': prediction[0]})
        except Exception as e:
            print("error : ",e)
            return JsonResponse({'error': str(e)})
    else:
        return JsonResponse({'error': 'Invalid request method.'})