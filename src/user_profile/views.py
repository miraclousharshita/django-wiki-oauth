from django.shortcuts import render

def index(request):
    context = {}
    return render(request, 'user_profile/index.dtl', context)