from rest_framework import serializers
from .models import EmailTemplate, EmailCampaign, EmailDraft
import logging

logger = logging.getLogger(__name__)

class EmailTemplateSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = EmailTemplate
        fields = ['id', 'name', 'description', 'subject_template', 'body_template', 
                 'created_at', 'updated_at', 'created_by', 'created_by_name', 'is_active']
        read_only_fields = ['created_at', 'updated_at', 'created_by', 'created_by_name']

    def get_created_by_name(self, obj):
        return obj.created_by.get_full_name() if obj.created_by else None

    def validate(self, data):
        logger.info(f"Validating template data: {data}")
        
        # Validate required fields
        required_fields = {
            'name': 'Name is required',
            'subject_template': 'Subject template is required',
            'body_template': 'Body template is required'
        }
        
        errors = {}
        for field, message in required_fields.items():
            if not data.get(field):
                errors[field] = message
        
        if errors:
            logger.error(f"Validation errors: {errors}")
            raise serializers.ValidationError(errors)
        
        logger.info("Template data validation successful")
        return data

    def create(self, validated_data):
        logger.info(f"Creating template with validated data: {validated_data}")
        try:
            template = super().create(validated_data)
            logger.info(f"Template created successfully with ID: {template.id}")
            return template
        except Exception as e:
            logger.error(f"Error creating template: {str(e)}")
            raise

class EmailDraftSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailDraft
        fields = ['id', 'campaign', 'recipient_email', 'recipient_name', 'subject',
                 'body', 'personalization_data', 'status', 'generated_at', 'sent_at',
                 'error_message']
        read_only_fields = ['generated_at', 'sent_at', 'status']

class EmailCampaignSerializer(serializers.ModelSerializer):
    drafts = EmailDraftSerializer(many=True, read_only=True)
    template_name = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = EmailCampaign
        fields = ['id', 'name', 'description', 'template', 'template_name', 'custom_prompt',
                 'created_by', 'created_by_name', 'status', 'scheduled_time', 'created_at',
                 'updated_at', 'drafts']
        read_only_fields = ['created_at', 'updated_at', 'created_by', 'created_by_name']

    def get_template_name(self, obj):
        return obj.template.name if obj.template else None

    def get_created_by_name(self, obj):
        return obj.created_by.get_full_name() if obj.created_by else None
