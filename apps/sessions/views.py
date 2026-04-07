from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.sessions.serializers import SessionResponseSerializer, SessionUpdateSerializer
from apps.sessions.services import (
    SessionInactiveError,
    SessionNotFoundError,
    create_session,
    get_session,
    update_current_phoneme,
)


@api_view(["POST"])
def session_create(request):
    session = create_session()
    serializer = SessionResponseSerializer(session)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET", "PATCH"])
def session_detail(request, session_id):
    if request.method == "GET":
        try:
            session = get_session(session_id)
        except SessionNotFoundError:
            return Response({"error": "Session not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = SessionResponseSerializer(session)
        return Response(serializer.data)

    elif request.method == "PATCH":
        serializer = SessionUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        try:
            session = update_current_phoneme(session_id, serializer.validated_data["phoneme"])
        except SessionNotFoundError:
            return Response({"error": "Session not found"}, status=status.HTTP_404_NOT_FOUND)
        except SessionInactiveError:
            return Response({"error": "Session is no longer active"}, status=status.HTTP_409_CONFLICT)
        except Exception:
            return Response({"error": "Invalid phoneme"}, status=status.HTTP_400_BAD_REQUEST)
        response_serializer = SessionResponseSerializer(session)
        return Response(response_serializer.data)
