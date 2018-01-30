from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('log/', views.log, name='log'),
    path('csv/', views.csv_download,name='csv'),
    path('result/', views.result,name='result'),
]
