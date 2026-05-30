from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import User
from .serializers import UserSerializer


class CurrentUserView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        serializer = UserSerializer(request.user)

        return Response(serializer.data)
    
class SuperAdminUsersView(APIView):

    permission_classes = [IsAuthenticated]



    def get(self, request):

        if not request.user.is_superuser:

            return Response(

                {

                    "error": "Unauthorized"
                },

                status=status.HTTP_403_FORBIDDEN
            )



        users = User.objects.all()



        serializer = UserSerializer(

            users,
            many=True
        )



        return Response(serializer.data)




class ChangeUserRoleView(APIView):

    permission_classes = [IsAuthenticated]



    def put(self, request, user_id):

        if not request.user.is_superuser:

            return Response(

                {

                    "error": "Unauthorized"
                },

                status=status.HTTP_403_FORBIDDEN
            )



        try:

            user = User.objects.get(

                id=user_id
            )

        except User.DoesNotExist:

            return Response(

                {

                    "error": "User not found"
                },

                status=status.HTTP_404_NOT_FOUND
            )



        role = request.data.get(

            "role"
        )



        user.role = role

        user.save()



        return Response(

            {

                "message": "Role updated"
            }
        )
