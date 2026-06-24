from rest_framework.views import APIView
from rest_framework.response import Response

from core.models import ChatHistory
from .ai_service import ask_ai


class AIChatView(APIView):

    def post(self, request):

        print("REQUEST DATA:", request.data)

        company_id = request.data.get("company_id")
        question = request.data.get("question")

        result = ask_ai(
            company_id,
            question
        )

        ChatHistory.objects.create(
            tenant_id=company_id,
            question=question,
            answer=result["answer"]
        )

        return Response(result)

    def get(self, request):

        return Response({
            "message": "AI endpoint working"
        })
    
class ChatHistoryView(APIView):

    def get(self, request, tenant_id):

        chats = ChatHistory.objects.filter(
            tenant_id=tenant_id
        ).order_by("-created_at")

        data = []

        for chat in chats:
            data.append({
                "question": chat.question,
                "answer": chat.answer,
                "created_at": chat.created_at
            })

        return Response(data)