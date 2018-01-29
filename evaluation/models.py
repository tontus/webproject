from django.db import models


# Create your models here.
class AnswerData(models.Model):
    modelAnswer = models.TextField()
    answer = models.TextField()
    score = models.FloatField()
