from django.urls import path

from . import views

app_name = 'markdocs'
urlpatterns = [
    path('', views.MarkdocsView.as_view(), name='index'),
    path('<document>', views.MarkdocsView.as_view(), name='document'),
    path('<document>/', views.MarkdocsView.as_view(), name='document'),
]
