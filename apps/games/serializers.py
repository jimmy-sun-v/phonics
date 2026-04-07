from rest_framework import serializers

from apps.games.models import Game


class GameListSerializer(serializers.ModelSerializer):
    game_type_display = serializers.CharField(source="get_game_type_display", read_only=True)

    class Meta:
        model = Game
        fields = ["id", "name", "game_type", "game_type_display", "description", "is_active"]
        read_only_fields = fields


class GameDetailSerializer(serializers.ModelSerializer):
    game_type_display = serializers.CharField(source="get_game_type_display", read_only=True)
    phonemes = serializers.SerializerMethodField()

    class Meta:
        model = Game
        fields = ["id", "name", "game_type", "game_type_display", "description", "is_active", "phonemes"]
        read_only_fields = fields

    def get_phonemes(self, obj):
        return list(obj.phonemes.values_list("symbol", flat=True))
