from django.shortcuts import render
from rest_framework import viewsets, status, permissions, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import EmailTemplate, EmailCampaign, EmailDraft
from .serializers import EmailTemplateSerializer, EmailCampaignSerializer, EmailDraftSerializer
import openai
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class EmailTemplateViewSet(viewsets.ModelViewSet):
    queryset = EmailTemplate.objects.all()
    serializer_class = EmailTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Filter templates to show only active ones created by the current user
        """
        return EmailTemplate.objects.filter(
            is_active=True
        ).order_by('-created_at')

    def perform_create(self, serializer):
        """
        Set the created_by field to the current user before saving
        """
        try:
            logger.info(f"Creating template with data: {serializer.validated_data}")
            serializer.save(created_by=self.request.user)
            logger.info("Template created successfully")
        except Exception as e:
            logger.error(f"Error in perform_create: {str(e)}")
            raise

    def create(self, request, *args, **kwargs):
        try:
            logger.info(f"Received template creation request with data: {request.data}")
            
            # Check if user is authenticated
            if not request.user.is_authenticated:
                logger.error("Unauthenticated user attempted to create template")
                return Response(
                    {'detail': 'Authentication required'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            serializer = self.get_serializer(data=request.data)
            
            # Log validation errors if any
            if not serializer.is_valid():
                logger.error(f"Validation errors: {serializer.errors}")
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )

            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
                headers=headers
            )
            
        except serializers.ValidationError as e:
            logger.error(f"Validation error in create: {str(e)}")
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Unexpected error in create: {str(e)}", exc_info=True)
            return Response(
                {'detail': 'An unexpected error occurred'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Unexpected error in list: {str(e)}", exc_info=True)
            return Response(
                {'detail': 'An unexpected error occurred'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class EmailCampaignViewSet(viewsets.ModelViewSet):
    queryset = EmailCampaign.objects.all()  # Default queryset for router
    serializer_class = EmailCampaignSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Filter campaigns to show only those created by the current user
        """
        return EmailCampaign.objects.filter(
            created_by=self.request.user
        ).order_by('-created_at')

    def perform_create(self, serializer):
        """
        Set the created_by field to the current user before saving
        """
        serializer.save(created_by=self.request.user)

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except serializers.ValidationError as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Unexpected error in create: {str(e)}", exc_info=True)
            return Response(
                {'detail': 'An unexpected error occurred'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def generate_email(self, request, pk=None):
        campaign = self.get_object()
        recipient_data = request.data.get('recipient_data', {})
        
        try:
            # Prepare prompt for GPT
            template = campaign.template
            custom_prompt = campaign.custom_prompt
            
            prompt = f"""
            Generate a professional email based on the following template and customization:
            Template: {template.body_template if template else 'No template provided'}
            Custom Instructions: {custom_prompt}
            Recipient Details: {recipient_data}
            """

            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional email writer."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )

            generated_email = response.choices[0].message.content

            # Create email draft
            draft = EmailDraft.objects.create(
                campaign=campaign,
                recipient_email=recipient_data.get('email'),
                recipient_name=recipient_data.get('name'),
                subject=template.subject_template if template else 'Subject',
                body=generated_email,
                personalization_data=recipient_data
            )
            draft.mark_as_generated()

            return Response({
                'draft_id': draft.id,
                'generated_email': generated_email
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Unexpected error in generate_email: {str(e)}", exc_info=True)
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class EmailDraftViewSet(viewsets.ModelViewSet):
    queryset = EmailDraft.objects.all()  # Default queryset for router
    serializer_class = EmailDraftSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Filter drafts to show only those from campaigns created by the current user
        """
        return EmailDraft.objects.filter(
            campaign__created_by=self.request.user
        ).order_by('-created_at')

    def perform_create(self, serializer):
        """
        Set the created_by field to the current user before saving
        """
        serializer.save(created_by=self.request.user)

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except serializers.ValidationError as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Unexpected error in create: {str(e)}", exc_info=True)
            return Response(
                {'detail': 'An unexpected error occurred'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def mark_sent(self, request, pk=None):
        draft = self.get_object()
        draft.mark_as_sent()
        serializer = self.get_serializer(draft)
        return Response(serializer.data)
