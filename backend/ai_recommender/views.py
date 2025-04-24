from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework import status
from .serializers import *
from .models import *
import uuid


class UserPreferenceView(generics.CreateAPIView):
    serializer_class = UserPreferenceSerializer
    permission_classes = []  # Allow anonymous access

    def perform_create(self, serializer):
        # Handle anonymous or logged-in user
        user = self.request.user if self.request.user.is_authenticated else None
        session_id = self.request.data.get("session_id")

        if not session_id:
            session_id = str(uuid.uuid4())  # Make sure it's stored as string

        # Save the main preference object
        preference = serializer.save(user=user, session_id=session_id)

        # Handle saving answers from questionnaire
        answers = self.request.data.get("answers", {})
        for slug, value in answers.items():
            try:
                question = Question.objects.get(slug=slug)
                UserAnswer.objects.create(
                    preference=preference, question=question, answer=value
                )
            except Question.DoesNotExist:
                continue
