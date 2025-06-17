import os
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model

User = get_user_model()

def validate_image_size(value):
    filesize = value.size
    if filesize > 2 * 1024 * 1024:
        raise ValidationError("Максимальный размер изображения 2MB")
    
def validate_image_extension(value):
    ext = os.path.splitext(value.name)[1]
    valid_extansions = ['.jpg', '.jpeg', '.png']
    if not ext.lower() in valid_extansions:
        raise ValidationError('Поддерживается только JPG и PNG форматы')

class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Director(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    bio = models.TextField(blank=True, null=True)
    photo = models.ImageField(
        upload_to='directors/',
        validators=[validate_image_extension, validate_image_size]
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    

class Actors(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    bio = models.TextField(blank=True, null=True)
    photo = models.ImageField(
        upload_to='actors/',
        validators=[validate_image_extension, validate_image_size]
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    

class Movie(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    duration = models.IntegerField(help_text="Длительность в минутах")
    retease_date = models.DateField()
    genres = models.ManyToManyField(Genre)
    directors = models.ForeignKey(Director, on_delete=models.CASCADE)
    actors = models.ManyToManyField(Actors)
    poster = models.ImageField(
        upload_to='posters/',
        validators=[validate_image_extension, validate_image_size]
    )
    rating = models.FloatField(
        null=True, blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)]
    )

    def __str__(self):
        return self.title
    
 
class CinemaHall(models.Model):
    name = models.CharField(max_length=100)
    seat = models.IntegerField(validators=[MinValueValidator(1)])

    def __str__(self):
        return f"{self.name} ({self.seat} мест)"
    

class Session(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    start_time =  models.DateTimeField()
    hall = models.ForeignKey(CinemaHall, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    
    def __str__(self):
        return f"{self.movie} - {self.start_time}"
    

class Booking(models.Model):
    STATUS_CHOICES = [
        ('confirmed', 'Подтверждено'),
        ('cancrled', 'Отменено'),
        ('pending', 'В обработке'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    seat = models.CharField(max_length=10)
    booked_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    class Meta: 
        unique_together = ('session','seat')
    
    def __str__(self):
        return f"{self.user} - {self.session} - {self.seat}"