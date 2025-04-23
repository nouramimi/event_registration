from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('events/', views.event_list, name='event_list'),
    path('events/<int:event_id>/', views.event_detail, name='event_detail'),
    path('events/<int:event_id>/register/', views.register_for_event, name='register_for_event'),
    path('events/<int:event_id>/cancel/', views.cancel_registration, name='cancel_registration'),
    path('events/create/', views.create_event, name='create_event'),
    path('events/<int:event_id>/edit/', views.edit_event, name='edit_event'),
    path('events/<int:event_id>/manage/', views.manage_event, name='manage_event'),
    path('registrations/<int:registration_id>/update/', views.update_registration_status, name='update_registration_status'),
    path('my-events/', views.my_events, name='my_events'),
]