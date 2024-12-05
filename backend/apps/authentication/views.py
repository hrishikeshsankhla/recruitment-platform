from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from google.oauth2 import id_token
from google.auth.transport import requests
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
import json

# Create your views here.

@api_view(['POST'])
@permission_classes([AllowAny])
def google_auth(request):
    try:
        print("Request data:", request.data)  # Debug print
        token = request.data.get('token')
        if not token:
            error_msg = 'No token provided'
            print(error_msg)
            return Response({'error': error_msg}, status=status.HTTP_400_BAD_REQUEST)
            
        print("Attempting to verify token with client ID:", settings.GOOGLE_CLIENT_ID)
        
        try:
            # Verify the token
            idinfo = id_token.verify_oauth2_token(
                token, requests.Request(), settings.GOOGLE_CLIENT_ID)
            print("Token verification successful. ID info:", idinfo)
        except ValueError as e:
            error_msg = f'Token verification failed: {str(e)}'
            print(error_msg)
            return Response({'error': error_msg}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            error_msg = f'Unexpected error during token verification: {str(e)}'
            print(error_msg)
            return Response({'error': error_msg}, status=status.HTTP_400_BAD_REQUEST)

        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            error_msg = f'Invalid token issuer: {idinfo["iss"]}'
            print(error_msg)
            return Response({'error': error_msg}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Get or create user
            user, created = User.objects.get_or_create(
                email=idinfo['email'],
                defaults={
                    'username': idinfo['email'],
                    'first_name': idinfo.get('given_name', ''),
                    'last_name': idinfo.get('family_name', ''),
                    'google_id': idinfo['sub'],
                    'profile_picture': idinfo.get('picture', '')
                }
            )

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
                'user': {
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'profile_picture': user.profile_picture
                }
            })
        except Exception as e:
            error_msg = f'Error creating/retrieving user: {str(e)}'
            print(error_msg)
            return Response({'error': error_msg}, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        error_msg = f'Authentication failed: {str(e)}'
        print(error_msg)
        return Response({'error': error_msg}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token(request):
    try:
        refresh_token = request.data.get('refresh_token')
        token = RefreshToken(refresh_token)
        return Response({
            'access_token': str(token.access_token),
            'refresh_token': str(token)
        })
    except Exception as e:
        return Response({'error': 'Invalid refresh token'}, 
                      status=status.HTTP_400_BAD_REQUEST)
