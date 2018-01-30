from django.db import models


# Create your models here.
class AnswerData(models.Model):
    question = models.TextField()
    modelAnswer = models.TextField()
    answer = models.TextField()
    marks = models.IntegerField()
    score = models.FloatField()
