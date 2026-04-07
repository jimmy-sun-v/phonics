from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.games.models import Game
from apps.games.serializers import GameDetailSerializer, GameListSerializer
from apps.phonics.models import Phoneme


@api_view(["GET"])
def game_list(request):
    games = Game.objects.filter(is_active=True)
    serializer = GameListSerializer(games, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def game_detail(request, pk):
    try:
        game = Game.objects.get(pk=pk)
    except Game.DoesNotExist:
        return Response({"error": "Game not found"}, status=status.HTTP_404_NOT_FOUND)
    serializer = GameDetailSerializer(game)
    return Response(serializer.data)


@api_view(["GET"])
def games_for_phoneme(request, symbol):
    try:
        phoneme = Phoneme.objects.get(symbol=symbol)
    except Phoneme.DoesNotExist:
        return Response({"error": f"Phoneme '{symbol}' not found"}, status=status.HTTP_404_NOT_FOUND)
    games = Game.objects.filter(is_active=True, phonemes=phoneme)
    serializer = GameListSerializer(games, many=True)
    return Response(serializer.data)
