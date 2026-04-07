from rest_framework import serializers

from apps.sessions.models import LearningSession


class SessionCreateSerializer(serializers.Serializer):
    pass


class SessionResponseSerializer(serializers.ModelSerializer):
    current_phoneme_symbol = serializers.CharField(source="current_phoneme.symbol", read_only=True, default=None)
    progress = serializers.SerializerMethodField()

    class Meta:
        model = LearningSession
        fields = ["session_id", "current_phoneme_symbol", "started_at", "last_active_at", "is_active", "progress"]
        read_only_fields = fields

    def get_progress(self, obj):
        from apps.sessions.progress import get_progress

        try:
            return get_progress(obj.session_id)
        except Exception:
            return None


class SessionUpdateSerializer(serializers.Serializer):
    phoneme = serializers.CharField(max_length=10)
