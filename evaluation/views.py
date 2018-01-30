from django.shortcuts import render
from django.http import HttpResponse
from .forms import AnswerInputForm
from .dd import ff
from .models import AnswerData


def index(request):
    if request.method == 'POST':
        postFlag = True
        formdata = AnswerInputForm(request.POST)
        if formdata.is_valid():
            form = AnswerInputForm()
            result = ff()
            answerdata = AnswerData()
            answerdata.question = formdata.cleaned_data['question']
            print(formdata.cleaned_data['answer'])
            answerdata.modelAnswer = formdata.cleaned_data['model_answer']
            answerdata.answer = formdata.cleaned_data['answer']
            answerdata.marks = formdata.cleaned_data['marks']
            answerdata.score = result.sa()
            answerdata.save()
            return render(request, 'evaluation/index.html',
                          {'formdata': result.sa(), 'form': form, 'postFlag': postFlag})
    else:
        form = AnswerInputForm()
    return render(request, 'evaluation/index.html', {'form': form})


def log(request):
    answerdatas = AnswerData.objects.all()
    return render(request,'evaluation/log.html', {'answerdatas':answerdatas})
# Create your views here.
