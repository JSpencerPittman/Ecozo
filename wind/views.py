from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def wind(request):
    return render(request, 'wind.html')