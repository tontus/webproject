from __future__ import division

import csv

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from .forms import AnswerInputForm
from .models import AnswerData
from .calculate import Calculate
from .tasks import start_calculation


def index(request):
    form = AnswerInputForm()
    return render(request, 'evaluation/index.html', {'form': form})


def log(request):
    answer_datas = AnswerData.objects.all()
    return render(request, 'evaluation/log.html', {'answerdatas': answer_datas})


# Create your views here.

def csv_download(request):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="log.csv"'

    writer = csv.writer(response)
    log = AnswerData.objects.all()
    writer.writerow(['Model Answer', 'Answer', 'Total Marks', 'Score'])
    for data in log:
        writer.writerow([data.modelAnswer, data.answer, data.marks, data.score])

    return response


def result(request):
    if request.method == 'POST':
        postFlag = True
        formdata = AnswerInputForm(request.POST)
        if formdata.is_valid():
            form = AnswerInputForm()
            answerdata = AnswerData()
            answerdata.question = formdata.cleaned_data['question']
            print(formdata.cleaned_data['answer'])
            answerdata.modelAnswer = formdata.cleaned_data['model_answer']
            answerdata.answer = formdata.cleaned_data['answer']
            answerdata.marks = formdata.cleaned_data['marks']
            start_calculation.delay(answerdata.question, answerdata.modelAnswer, answerdata.answer, answerdata.marks)
            return render(request, 'evaluation/result.html',
                          {'form': answerdata, 'postFlag': postFlag})
        return HttpResponse("invalid")
