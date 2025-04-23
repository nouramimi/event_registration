# models.py

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Categories"

class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    location = models.CharField(max_length=200)
    capacity = models.PositiveIntegerField(default=0)  # 0 means unlimited
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='events')
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_events')
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='event_images/', blank=True, null=True)
    is_published = models.BooleanField(default=False)
    
    def __str__(self):
        return self.title
    
    @property
    def is_past(self):
        return self.end_date < timezone.now()
        
    @property
    def available_seats(self):
        if self.capacity == 0:  # unlimited capacity
            return None
        registered = self.registrations.count()
        return max(0, self.capacity - registered)
    
    @property
    def is_full(self):
        if self.capacity == 0:  # unlimited capacity
            return False
        return self.registrations.count() >= self.capacity

class Registration(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    )
    
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='event_registrations')
    registration_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    attendance_confirmed = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('event', 'user')
        
    def __str__(self):
        return f"{self.user.username} - {self.event.title}"