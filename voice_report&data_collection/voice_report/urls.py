from django.conf.urls import url

from voice_report import views

urlpatterns = [
    url(r'^rec/', views.index, name='index'),
]