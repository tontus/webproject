from django import forms


class AnswerInputForm(forms.Form):
    model_answer = forms.CharField(widget=forms.Textarea(attrs={'class': 'model_answer'}))
    answer = forms.CharField(widget=forms.Textarea(attrs={'class': 'answeer'}))
