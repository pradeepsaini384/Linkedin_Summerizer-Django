from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='home'),
     path('output', views.output, name='output'),
    path('result/<str:url>/<str:output>/', views.result, name='result'),
]
