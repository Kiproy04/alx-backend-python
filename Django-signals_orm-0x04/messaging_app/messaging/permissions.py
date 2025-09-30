from rest_framework import permissions
from .models import Conversation, Message


class IsParticipantOfConversation(permissions.BasePermission):
    """
    Allow only authenticated users who are participants of the conversation
    to view, send, update, and delete messages.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        
        if isinstance(obj, Conversation):
            return request.user in obj.participants.all()

        
        if isinstance(obj, Message):
            if request.user not in obj.conversation.participants.all():
                return False
            if request.method in ["PUT", "PATCH", "DELETE"]:
                return True  
            if request.method in permissions.SAFE_METHODS:  
                return True
            if request.method == "POST":  
                return True
            return False
        return False
    
