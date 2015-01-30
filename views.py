from django.shortcuts import render, get_object_or_404
from django.contrib.auth import logout
from django.views import generic
from django.http import HttpResponseRedirect

import calendar
import datetime
import time

from ukbooking.models import Apartment, Bed, Booking, Visit
from ukbooking.forms import VisitForm

def prev_date(year, month):
    """ Return tuple of previous year & month for 1 month back."""
    if month == 1:
        return [year - 1, 12]
    else:
        return [year, month - 1]

def next_date(year, month):
    """ Return tuple of previous year & month for 1 month forward."""
    if month == 12:
        return [year + 1, 1]
    else:
        return [year, month + 1]

class Bookings(generic.ListView):
    model = Booking
    template_name = "ukbooking/bookings_dump.html"

def bookings_per_month(year, month):
    """ Bookings per day for the month."""
    day_information = []
    month_information = None
    year, month = int(year), int(month)
    cal = calendar.Calendar(6) # Weeks start on Sunday    
    for day in cal.itermonthdays(year, month):
        if day == 0: # Days not in month are 0 (yields full week)
            day_information.append([day,None])
            continue
        # Include bookings with a check in before or on today and exclude with a check out before today
        bookings = Booking.objects.filter(check_in__lte=datetime.datetime(year, month, day))
        bookings = bookings.exclude(check_out__lt=datetime.datetime(year, month, day))
        if month_information is None:
            month_information = bookings
        month_information = month_information | bookings
        day_information.append([day, bookings])
    return day_information, month_information

def bookings(request, year=time.localtime()[0], month=time.localtime()[1]):
    """ View of bookings in a month."""
    year = int(year)
    month = int(month)
    day_bookings, month_bookings = bookings_per_month(year, month)
    return render(request, 'ukbooking/bookings.html', {'day_bookings' : day_bookings,
                                                       'month_bookings' : month_bookings,
                                                       'now' : [year, month],
                                                       'prev' : prev_date(year, month),
                                                       'next' : next_date(year, month)})

class Visits(generic.ListView):
    model = Visit
    template_name = "ukbooking/visits_dump.html"

def visits_per_month(year, month):
    """ Vists per day for the month."""
    day_information = []
    month_information = None
    year, month = int(year), int(month)
    cal = calendar.Calendar(6) # Weeks start on Sunday    
    for day in cal.itermonthdays(year, month):
        if day == 0: # Days not in month are 0 (yields full week)
            day_information.append([day,None])
            continue
        # Include bookings with a check in before or on today and exclude with a check out before today
        visits = Visit.objects.filter(check_in__lte=datetime.datetime(year, month, day))
        visits = visits.exclude(check_out__lt=datetime.datetime(year, month, day))
        if month_information is None:
            month_information = visits
        month_information = month_information | visits
        day_information.append([day, visits])
    return day_information, month_information

def visits(request, year=time.localtime()[0], month=time.localtime()[1]):
    """ View of visits in a month."""
    year = int(year)
    month = int(month)
    day_visits, month_visits = visits_per_month(year, month)
    return render(request, 'ukbooking/visits.html', {'day_visits' : day_visits,
                                                     'month_visits' : month_visits,
                                                     'now' : [year, month],
                                                     'prev' : prev_date(year, month),
                                                     'next' : next_date(year, month)})

def index(request):
    """ View of visits and bookings in this month."""
    year, month = time.localtime()[:2]
    return render(request, 'ukbooking/index.html', {'day_visits' : visits_per_month(year, month),
                                                    'day_bookings' : bookings_per_month(year, month),
                                                    'now' : [year, month],
                                                    'prev' : prev_date(year, month),
                                                    'next' : next_date(year, month)})

class Apartments(generic.ListView):
    model = Apartment
    template_name = "ukbooking/apartments.html"

def apartment(request, apartment_id):
    """ Return apartment information."""
    apartment = get_object_or_404(Apartment, pk=apartment_id)
    try:
        beds = Bed.objects.filter(apartment=apartment_id)
        return render(request, 'ukbooking/apartment.html', {'apartment' : apartment, 'bed_list' : beds})
    except Bed.DoesNotExist:
        return render(request, 'ukbooking/apartment.html', {'apartment' : apartment, 'bed_list' : []})

def booking(request, booking_id):
    """ List a booking."""
    booking = get_object_or_404(Booking, pk=booking_id)
    return render(request, 'ukbooking/booking.html', {'booking' : booking})

def visit(request, visit_id):
    """ List a visit."""
    visit = get_object_or_404(Visit, pk=visit_id)
    return render(request, 'ukbooking/visit.html', {'visit' : visit})

def book_visit(request):
    """ Book visit form."""
    if request.method == 'POST': 
        form = VisitForm(request.POST) # A form bound to the POST data
        if form.is_valid():
            clean_data = form.cleaned_data
            visit = Visit(contact=clean_data['contact'], 
                          check_in=clean_data['check_in'],
                          check_out=clean_data['check_out'])
            visit.save()
            return render(request, 'ukbooking/book_visit.html') # Redirect after POST
    else:
        form = VisitForm() # An unbound form
    return render(request, 'ukbooking/book_visit.html', {'form': form})
