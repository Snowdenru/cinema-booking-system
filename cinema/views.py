from django.shortcuts import render, get_object_or_404, redirect
import logging
from cinema.models import Movie, Session, Booking
from django.contrib.auth.decorators import login_required
from cinema.forms import BookingForm, MovieFilterForm
from django.db.models import Q

logger = logging.getLogger(__name__)


def home(request):
    movies = Movie.objects.all().order_by("-retease_date")

    filter_form = MovieFilterForm(request.GET or None)
    
    if filter_form.is_valid():
        if filter_form.cleaned_data['search']:
            search_term = filter_form.cleaned_data['search']
            movies = movies.filter(
                Q(title__icontains=search_term) |
                Q(actors__first_name__icontains=search_term) |
                Q(actors__last_name__icontains=search_term) |
                Q(directors__first_name__icontains=search_term) |
                Q(directors__last_name__icontains=search_term)
            ).distinct()
        
        if filter_form.cleaned_data['genre']:
            movies = movies.filter(genres=filter_form.cleaned_data['genre'])
            
        if filter_form.cleaned_data['sort']:
            movies = movies.order_by(filter_form.cleaned_data['sort'])


    context = {
        "movies": movies,
        'filter_form': filter_form,
    }
    logger.info("Поиск фильмов")
    return render(request, "cinema/home.html", context)


def movie_detail(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    sessions = Session.objects.filter(movie=movie).order_by("start_time")

    sessions_by_date = {}
    for sessin in sessions:
        date = sessin.start_time.date()
        if date not in sessions_by_date:
            sessions_by_date[date] = []
        sessions_by_date[date].append(sessin)


    context = {"movie": movie, "sessions_by_date": sessions_by_date}
    return render(request,"cinema/movie_detail.html", context)


@login_required
def book_ticket(request, session_id):
    session = get_object_or_404(Session, pk=session_id)
    
    if request.method == 'POST':
        form = BookingForm(request.POST, session=session)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.session = session
            booking.status = 'confirmed'
            booking.save()
            
            logger.info(f"New booking created: {booking}")
            return redirect('profile')
    else:
        form = BookingForm(session=session)
    
    # Получаем занятые места для этого сеанса
    taken_seats = list(Booking.objects.filter(
        session=session,
        status__in=['confirmed', 'pending']
    ).values_list('seat', flat=True))
    
    context = {
        'session': session,
        'form': form,
        'taken_seats': taken_seats,
    }
    return render(request, 'cinema/book_ticket.html', context)


@login_required
def profile(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-booked_at')
    
    # Фильтрация по статусу
    status = request.GET.get('status')
    if status and status != 'all':
        bookings = bookings.filter(status=status)
    
    # Статистика
    stats = {
        'confirmed': Booking.objects.filter(user=request.user, status='confirmed').count(),
        'canceled': Booking.objects.filter(user=request.user, status='canceled').count(),
        'pending': Booking.objects.filter(user=request.user, status='pending').count(),
    }
    
    context = {
        'bookings': bookings,
        'stats': stats,
    }
    return render(request, 'cinema/profile.html', context)

@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id, user=request.user)
    if booking.status == 'confirmed':
        booking.status = 'canceled'
        booking.save()
        logger.info(f"Booking canceled: {booking}")
    return redirect('profile')