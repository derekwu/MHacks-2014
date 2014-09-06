from django.db import models

# Create your models here.
class Matches(models.Model):
  gender = models.CharField(max_length=30)
  pref = models.CharField(max_length=30)
  money = models.IntegerField()
