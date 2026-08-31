from django.urls import path
from . import views

app_name = "appointment"

urlpatterns = [
    path('', views.appointment, name='appointment'),
    path('book/', views.book_appointment, name='book_appointment'),
    path('add-dependent/', views.add_dependent, name='add_dependent'),
]
