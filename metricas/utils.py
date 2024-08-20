from django.http import HttpRequest
from .models import Response
from datetime import datetime

def save_response(params: dict, service: str, response: dict):
    """
    Saves params and response into the data base

    :param params: Dict of params of the request.
    :param service: Name of the service; Youtube, Twitter, Instagram, Facebook.
    """
    response_instance = Response(
        service=service,
        params=params,
        response=response
    )

    try:
        response_instance.save()
        print("Data saved successfully.")
    except Exception as e:
        print(f"Error saving parameters to database: {e}")

def search_responses(params: dict, service: str):
    """
    Search responses from the database
    
    :param params: Dict of params of the request.
    :param service: Name of the service; Youtube, Twitter, Instagram, Facebook.
    """
    response = Response.objects.filter(service=service).filter(params=params)
    return response