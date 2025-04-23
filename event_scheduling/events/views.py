# views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.utils import timezone

from .models import Event, Category, Registration
from .forms import EventForm, RegistrationForm

def home(request):
    upcoming_events = Event.objects.filter(
        is_published=True,
        start_date__gte=timezone.now()
    ).order_by('start_date')[:5]
    
    categories = Category.objects.annotate(
        event_count=Count('events', filter=Q(events__is_published=True))
    ).filter(event_count__gt=0)
    
    return render(request, 'events/home.html', {
        'upcoming_events': upcoming_events,
        'categories': categories,
    })

def event_list(request):
    events = Event.objects.filter(is_published=True).order_by('start_date')
    
    # Filter by category if requested
    category_id = request.GET.get('category')
    if category_id:
        events = events.filter(category_id=category_id)
        
    # Filter by search query if provided
    query = request.GET.get('q')
    if query:
        events = events.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(location__icontains=query)
        )
    
    # Pagination
    paginator = Paginator(events, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = Category.objects.all()
    
    return render(request, 'events/event_list.html', {
        'page_obj': page_obj,
        'categories': categories,
        'selected_category': category_id,
        'query': query,
    })

def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id, is_published=True)
    user_registered = False
    registration_status = None
    
    if request.user.is_authenticated:
        try:
            registration = Registration.objects.get(event=event, user=request.user)
            user_registered = True
            registration_status = registration.status
        except Registration.DoesNotExist:
            pass
    
    return render(request, 'events/event_detail.html', {
        'event': event,
        'user_registered': user_registered,
        'registration_status': registration_status,
    })

@login_required
def register_for_event(request, event_id):
    event = get_object_or_404(Event, id=event_id, is_published=True)
    
    # Check if already registered
    if Registration.objects.filter(event=event, user=request.user).exists():
        messages.warning(request, 'You are already registered for this event.')
        return redirect('event_detail', event_id=event.id)
    
    # Check if event is full
    if event.is_full:
        messages.error(request, 'Sorry, this event is already at full capacity.')
        return redirect('event_detail', event_id=event.id)
    
    # Check if event is in the past
    if event.is_past:
        messages.error(request, 'This event has already ended.')
        return redirect('event_detail', event_id=event.id)
    
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            registration = form.save(commit=False)
            registration.event = event
            registration.user = request.user
            registration.save()
            messages.success(request, 'You have successfully registered for this event.')
            return redirect('event_detail', event_id=event.id)
    else:
        form = RegistrationForm()
    
    return render(request, 'events/register.html', {
        'form': form,
        'event': event,
    })

@login_required
def cancel_registration(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    registration = get_object_or_404(Registration, event=event, user=request.user)
    
    if request.method == 'POST':
        registration.status = 'cancelled'
        registration.save()
        messages.success(request, 'Your registration has been cancelled.')
        return redirect('event_detail', event_id=event.id)
    
    return render(request, 'events/cancel_registration.html', {
        'event': event,
    })

@login_required
def my_events(request):
    # Events user is registered for
    registrations = Registration.objects.filter(
        user=request.user
    ).select_related('event').order_by('event__start_date')
    
    # Events user is organizing
    organized_events = Event.objects.filter(
        organizer=request.user
    ).order_by('start_date')
    
    return render(request, 'events/my_events.html', {
        'registrations': registrations,
        'organized_events': organized_events,
    })

@login_required
def create_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.organizer = request.user
            event.save()
            messages.success(request, 'Event created successfully!')
            return redirect('event_detail', event_id=event.id)
        else:
            print(form.errors)
    else:
        form = EventForm()
    
    return render(request, 'events/event_form.html', {
        'form': form,
        'title': 'Create Event',
    })

@login_required
def edit_event(request, event_id):
    event = get_object_or_404(Event, id=event_id, organizer=request.user)
    
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, 'Event updated successfully!')
            return redirect('event_detail', event_id=event.id)
    else:
        form = EventForm(instance=event)
    
    return render(request, 'events/event_form.html', {
        'form': form,
        'title': 'Edit Event',
        'event': event,
    })

@login_required
def manage_event(request, event_id):
    event = get_object_or_404(Event, id=event_id, organizer=request.user)
    registrations = Registration.objects.filter(event=event)
    
    return render(request, 'events/manage_event.html', {
        'event': event,
        'registrations': registrations,
    })

@login_required
def update_registration_status(request, registration_id):
    registration = get_object_or_404(Registration, id=registration_id)
    event = registration.event
    
    # Ensure current user is the event organizer
    if event.organizer != request.user:
        messages.error(request, 'You are not authorized to manage this event.')
        return redirect('my_events')
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        attendance = request.POST.get('attendance') == 'on'
        
        if new_status in [s[0] for s in Registration.STATUS_CHOICES]:
            registration.status = new_status
            registration.attendance_confirmed = attendance
            registration.save()
            messages.success(request, 'Registration status updated.')
        
    return redirect('manage_event', event_id=event.id)