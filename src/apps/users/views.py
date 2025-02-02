import logging

from rest_framework.decorators import action
from rest_framework.status import (HTTP_201_CREATED, HTTP_400_BAD_REQUEST,
                                   HTTP_401_UNAUTHORIZED)
from rest_framework.views import Response
from rest_framework.viewsets import ViewSet

from apps.users.serializers import (SignInSerializer, SignUpSerializer,
                                    UserSerializer)

logger = logging.getLogger(__name__)


class UsersViewSet(ViewSet):
    serializer_class = UserSerializer

    @action(detail=False, methods=["post"], serializer_class=SignUpSerializer)
    def signup(self, request):
        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserSerializer(user).data, status=HTTP_201_CREATED)
        return Response({"status": "error", "errors": serializer.errors}, status=HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"], serializer_class=SignInSerializer)
    def login(self, request):
        serializer = SignInSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.get_user()
            return Response(UserSerializer(user).data)
        return Response({"status": "error", "errors": serializer.errors}, status=HTTP_401_UNAUTHORIZED)
