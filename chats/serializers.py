from rest_framework import serializers
from .models import Conversation, Message, User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id', 'email', 'first_name', 'last_name', 'role', 'created_at' ]
        read_only_fields = ['user_id', 'role', 'created_at']

class MessageSerializer(serializers.ModelSerializer):
    sender_email = serializers.ReadOnlyField(source='sender.email')
    class Meta:
        model = Message
        fields = ['message_id','conversation', 'sender','sender_email', 'message_body', 'sent_at']
        read_only_fields = ['message_id', 'sent_at', 'sender_email']

class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True, source='messages')

    class Meta:
        model = Conversation
        fields = ['conversation_id', 'participants', 'created_at', 'messages']
        read_only_fields = ['conversation_id', 'created_at']
