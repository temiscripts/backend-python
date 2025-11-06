from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, status, serializers
from rest_framework.response import Response
from .models import Conversation, Message
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from rest_framework.exceptions import ValidationError
from .models import Conversation, Message
from .serializers import ConversationSerializer,MessageSerializer

User = get_user_model()


class ConversationViewSet(viewsets.ModelViewSet):

    queryset = Conversation.objects.all().prefetch_related('participants')
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return only conversations where the current user is a participant."""
        return self.queryset.filter(participants=self.request.user)

    def create(self, request, *args, **kwargs):
        participant_ids = request.data.get('participant_ids')

        if not participant_ids or not isinstance(participant_ids, list):
            raise ValidationError({"participant_ids": "Provide a list of participant IDs."})

        participants_to_add = set(participant_ids)
        participants_to_add.add(str(self.request.user.user_id))

        existing_users = User.objects.filter(user_id__in=participants_to_add)
        existing_ids = {str(u.user_id) for u in existing_users}
        missing_ids = participants_to_add - existing_ids

        if missing_ids:
            raise ValidationError({
                "invalid_participants": f"The following user IDs do not exist: {list(missing_ids)}"
            })

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            with transaction.atomic():
                conversation = serializer.save()
                conversation.participants.set(existing_users)
        except IntegrityError:
            raise ValidationError({"error": "A database error occurred while creating conversation."})

        response_serializer = self.get_serializer(conversation)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)



class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all().select_related('sender', 'conversation').order_by('sent_at')
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    http_method_names = ['get', 'post', 'head', 'options'] 

    def get_queryset(self):
        user_conversations = self.request.user.conversations.all()
        
        conversation_id = self.request.query_params.get('conversation_id')
        
        if conversation_id:
            return self.queryset.filter(conversation__conversation_id=conversation_id, conversation__in=user_conversations)
            
        return self.queryset.filter(conversation__in=user_conversations).order_by('sent_at')

    def perform_create(self, serializer):
        conversation_id = serializer.validated_data.get('conversation')
        
        try:
            conversation = get_object_or_404(
                Conversation.objects.filter(participants=self.request.user), 
                conversation_id = conversation_id.conversation_id
            )
        except Exception:
            raise serializers.ValidationError({
                'conversation': 'Conversation not found or you are not a participant.'
            })

        serializer.save(
            sender=self.request.user,
            conversation=conversation )