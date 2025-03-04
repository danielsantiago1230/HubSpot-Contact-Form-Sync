from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication, BasicAuthentication, SessionAuthentication

# Create your views here.


class HelloWorldView(APIView):
    """
    A simple API view that returns a Hello World message.
    This view allows any access without authentication.
    """
    authentication_classes = [
        TokenAuthentication,
        SessionAuthentication,
        BasicAuthentication,
    ]

    def get(self, request, *args, **kwargs):
        return Response(
            {"message": "Hello World from HubSpot Contact Form Sync!"},
            status=status.HTTP_200_OK,
        )
