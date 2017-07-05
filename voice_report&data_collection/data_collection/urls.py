from django.conf.urls import url
from data_collection import views

urlpatterns = [
    url(r'^InputPage/', views.index, name='index'),
    url(r'^segment/', views.seg, name='seg'),
    url(r'^terms/', views.terms, name='terms'),
]