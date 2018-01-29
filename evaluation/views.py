from django.shortcuts import render
from django.http import HttpResponse
from .forms import AnswerInputForm


def index(request):
    if request.method == 'POST':
        postFlag = True
        formdata = AnswerInputForm(request.POST)
        if formdata.is_valid():
            form = AnswerInputForm()
            return render(request, 'evaluation/index.html', {'formdata': formdata, 'form': form, 'postFlag': postFlag})
    else:
        postFlag = False
        form = AnswerInputForm()
    return render(request, 'evaluation/index.html', {'form': form})
# Create your views here.
