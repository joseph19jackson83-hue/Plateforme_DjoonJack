from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    credits = models.IntegerField(default=100)
    score = models.IntegerField(default=0)
    phone = models.CharField(max_length=30, blank=True)

    def __str__(self):
        return self.user.username

class Transaction(models.Model):
    TX_STATUS = [('pending','pending'),('success','success'),('failed','failed')]
    tx_ref = models.CharField(max_length=150, unique=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    provider = models.CharField(max_length=60)
    amount = models.IntegerField()
    status = models.CharField(max_length=20, choices=TX_STATUS, default='pending')
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tx_ref} - {self.user}"