from django.db import models

# Create your models here.

class SenderReceiver(models.Model):
    firstname = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    nationality = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.firstname} {self.surname}"

class Rule(models.Model):
    rule_name = models.CharField(max_length=255)
    sending_country = models.CharField(max_length=100)
    receiving_country = models.CharField(max_length=100)
    currency = models.CharField(max_length=50)
    status = models.BooleanField(default=False)  # True for active, False for inactive
    sender = models.ForeignKey(SenderReceiver, on_delete=models.CASCADE, related_name='sender_rules')
    receiver = models.ForeignKey(SenderReceiver, on_delete=models.CASCADE, related_name='receiver_rules')
    transaction_amount = models.DecimalField(max_digits=15, decimal_places=2)
    transaction_type = models.CharField(max_length=50)
    device = models.CharField(max_length=100)
    ip = models.GenericIPAddressField()

    def __str__(self):
        return self.rule_name


class Transaction(models.Model):
    transaction_id = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    time = models.DateTimeField()
    device = models.CharField(max_length=100)
    sender = models.ForeignKey(SenderReceiver, related_name='sent_transactions', on_delete=models.CASCADE)
    receiver = models.ForeignKey(SenderReceiver, related_name='received_transactions', on_delete=models.CASCADE)
    sending_country = models.CharField(max_length=100)
    receiving_country = models.CharField(max_length=100)
    description = models.TextField()
    currency = models.CharField(max_length=10)
    status = models.CharField(max_length=20, default='pending')  # 'pending', 'on hold', 'approved', 'rejected'

    def __str__(self):
        return self.transaction_id

