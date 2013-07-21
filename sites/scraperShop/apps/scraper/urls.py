from django.conf.urls import patterns, include, url
import views

urlpatterns = patterns('',
     url(r'run/', views.RunView.as_view()),
)

