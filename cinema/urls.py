from django.urls import path
from cinema import views


urlpatterns = [
    path('', views.home, name='home'),
    path('movie/<int:pk>/', views.movie_detail, name='movie_detail'),
    path('book_ticket/<int:session_id>/', views.book_ticket, name='book_ticket'),

    path('profile/', views.profile, name='profile'),
    path('booking/<int:booking_id>/cancel/', views.cancel_booking, name='cancel_booking'),
    
]
