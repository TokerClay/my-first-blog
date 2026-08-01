from django.urls import path
from . import views

urlpatterns = [

]

urlpatterns = [
    path('', views.post_list, name='post_list'),
]