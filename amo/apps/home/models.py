from django.db import models

# Create your models here.
from django.db import models


class Deal(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50)

    def __str__(self):
        return self.title
