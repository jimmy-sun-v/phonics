import base64

from rest_framework import serializers


class SpeechAttemptRequestSerializer(serializers.Serializer):
    session_id = serializers.UUIDField()
    phoneme = serializers.CharField(max_length=10)
    audio = serializers.CharField(help_text="Base64-encoded audio data")

    def validate_audio(self, value):
        try:
            audio_bytes = base64.b64decode(value)
        except Exception as err:
            raise serializers.ValidationError("Invalid base64-encoded audio data") from err
        max_size = 5 * 1024 * 1024
        if len(audio_bytes) > max_size:
            raise serializers.ValidationError("Audio data exceeds maximum size (5 MB)")
        if len(audio_bytes) == 0:
            raise serializers.ValidationError("Audio data is empty")
        return audio_bytes


class SpeechAttemptResponseSerializer(serializers.Serializer):
    confidence = serializers.FloatField()
    is_correct = serializers.BooleanField()
    feedback = serializers.CharField()
    detected_error = serializers.CharField(allow_null=True)
    attempt_number = serializers.IntegerField()
