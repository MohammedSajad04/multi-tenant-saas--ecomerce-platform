from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from core.models import ChatHistory
from .ai_service import ask_ai


class AIChatView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        company_id = request.data.get(
            "company_id"
        )

        question = request.data.get(
            "question"
        )

        result = ask_ai(
            company_id,
            question,
            request.user.id
        )

        ChatHistory.objects.create(
            tenant_id=company_id,
            user=request.user,
            question=question,
            answer=result["answer"]
        )

        return Response(result)


class ChatHistoryView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, tenant_id):

        chats = ChatHistory.objects.filter(
            tenant_id=tenant_id,
            user=request.user
        ).order_by(
            "-created_at"
        )

        data = []

        for chat in chats:

            data.append({
                "question": chat.question,
                "answer": chat.answer,
                "created_at": chat.created_at
            })

        return Response(data)