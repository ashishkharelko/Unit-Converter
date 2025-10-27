from django.urls import path
from converter import views

app_name = 'converter'
urlpatterns = [
    path('', views.index, name='index'),
    path('convert/', views.convert, name='convert'),
]