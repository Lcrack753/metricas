from django.shortcuts import render
from django.http import HttpResponse

def api(request):
    pass    

# Create your views here.
def main(request):
    return HttpResponse('hello word!')