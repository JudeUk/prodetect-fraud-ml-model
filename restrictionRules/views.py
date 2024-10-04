from django.http import JsonResponse
# from django.shortcuts import render
from django.views.decorators.csrf  import csrf_exempt

# Create your views here.


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404
import requests
from .models import Rule, Transaction, SenderReceiver
import json

# 1. Create a Rule
@csrf_exempt
@require_http_methods(["POST"])
def create_rule(request):
    try:
        data = json.loads(request.body)

         # Check for required fields in the data
        required_fields = ['rule_name', 'sending_country', 'receiving_country', 'currency', 'transaction_amount', 'transaction_type', 'device', 'ip', 'sender', 'receiver']
        for field in required_fields:
            if field not in data:
                return JsonResponse({'error': f'Missing field: {field}'}, status=400)


         # Create sender
        sender = SenderReceiver.objects.create(
            firstname=data['sender']['firstname'],
            surname=data['sender']['surname'],
            nationality=data['sender']['nationality']
        )
        
        # Create receiver
        receiver = SenderReceiver.objects.create(
            firstname=data['receiver']['firstname'],
            surname=data['receiver']['surname'],
            nationality=data['receiver']['nationality']
        )
        rule = Rule.objects.create(
            rule_name=data['rule_name'],
            sending_country=data['sending_country'],
            receiving_country=data['receiving_country'],
            currency=data['currency'],
            status=data.get('status', False),  # Default to False if not provided
            sender=sender,
            receiver=receiver,
            transaction_amount=data['transaction_amount'],
            transaction_type=data['transaction_type'],
            device=data['device'],
            ip=data['ip']
        )
        return JsonResponse({'message': 'Rule created successfully', 'rule_id': rule.id}, status=201)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

# 2. Activate a Rule
@csrf_exempt
@require_http_methods(["POST"])
def activate_rule(request, rule_id):
    try:
        rule = get_object_or_404(Rule, id=rule_id)
        rule.status = True
        rule.save()
        return JsonResponse({'message': 'Rule activated successfully'}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

# 3. Deactivate a Rule
@csrf_exempt
@require_http_methods(["POST"])
def deactivate_rule(request, rule_id):
    try:
        rule = get_object_or_404(Rule, id=rule_id)
        rule.status = False
        rule.save()
        return JsonResponse({'message': 'Rule deactivated successfully'}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

# 4. Delete a Rule
@csrf_exempt
@require_http_methods(["DELETE"])
def delete_rule(request, rule_id):
    try:
        rule = get_object_or_404(Rule, id=rule_id)
        rule.delete()
        return JsonResponse({'message': 'Rule deleted successfully'}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

# 5. View Suspended Transactions
@csrf_exempt
@require_http_methods(["GET"])
def view_suspended_transactions(request):
    try:
        # Retrieve only transactions with status 'on_hold'
        suspended_transactions = Transaction.objects.filter(
            status='on hold'  # Assuming 'status' field is used to track "on hold" transactions
        ).values(
            'transaction_id', 'amount', 'time', 'device', 
            'sender__firstname', 'sender__surname', 
            'receiver__firstname', 'receiver__surname', 
            'sending_country', 'receiving_country', 'description', 'currency'
        )
        
        # Return the transactions as a JSON response
        return JsonResponse(list(suspended_transactions), safe=False, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


# 6. Check Transactions against Restrictions Rules
@csrf_exempt
@require_http_methods(["POST"])
def check_transaction(request):
    try:
        data = json.loads(request.body)
        
        # Assume sender and receiver are already existing entities
         # Create sender
        sender = SenderReceiver.objects.create(
            firstname=data['sender']['firstname'],
            surname=data['sender']['surname'],
            nationality=data['sender']['nationality']
        )
        
        # Create receiver
        receiver = SenderReceiver.objects.create(
            firstname=data['receiver']['firstname'],
            surname=data['receiver']['surname'],
            nationality=data['receiver']['nationality']
        )
        
        # Create the transaction object
        transaction = Transaction.objects.create(
            transaction_id=data['transaction_id'],
            amount=data['amount'],
            time=data['time'],
            device=data['device'],
            sender=sender,
            receiver=receiver,
            sending_country=data['sending_country'],
            receiving_country=data['receiving_country'],
            description=data['description'],
            currency=data['currency']
        )
        
        # Check against active rules
        active_rules = Rule.objects.filter(status=True)
        for rule in active_rules:
            if (rule.sending_country == transaction.sending_country and
                rule.receiving_country == transaction.receiving_country and
                rule.currency == transaction.currency and
                rule.transaction_amount == transaction.amount and
                rule.transaction_type == data['transaction_type'] and
                rule.device == transaction.device and
                rule.ip == data['ip']):
                transaction.status = 'on hold'
                transaction.save()
                return JsonResponse({'message': 'Transaction on hold due to matching rule', 'transaction_id': transaction.id}, status=200)

        return JsonResponse({'message': 'Transaction processed successfully', 'transaction_id': transaction.id}, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
    

# 7. View Suspended Transactions
@csrf_exempt
@require_http_methods(["POST"])
def manage_transaction(request, transaction_id):
    try:
        data = json.loads(request.body)
        transaction = get_object_or_404(Transaction, id=transaction_id, status='on hold')
        
        action = data.get('action')

        if action == 'approve':
            # Send the transaction to the fulfillment URL
            fulfillment_url = 'https://example.com/fulfill-transaction/'  # Replace with actual URL
            response = requests.post(fulfillment_url, json={
                'transaction_id': transaction.transaction_id,
                'amount': transaction.amount,
                'currency': transaction.currency,
                'sender': {
                    'firstname': transaction.sender.firstname,
                    'surname': transaction.sender.surname,
                    'nationality': transaction.sender.nationality
                },
                'receiver': {
                    'firstname': transaction.receiver.firstname,
                    'surname': transaction.receiver.surname,
                    'nationality': transaction.receiver.nationality
                },
                'description': transaction.description
            })
            
            if response.status_code == 200:
                transaction.status = 'approved'
                transaction.save()
                return JsonResponse({'message': 'Transaction approved and fulfilled'}, status=200)
            else:
                return JsonResponse({'error': 'Failed to fulfill the transaction'}, status=400)
        
        elif action == 'reject':
            transaction.status = 'rejected'
            transaction.save()
            return JsonResponse({'message': 'Transaction rejected'}, status=200)
        
        else:
            return JsonResponse({'error': 'Invalid action'}, status=400)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


