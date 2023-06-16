from django.shortcuts import render


def insights(request):
    return render(request, 'insights.html')
