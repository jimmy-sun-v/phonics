from rest_framework import serializers

from apps.phonics.models import Phoneme


class CategorySerializer(serializers.Serializer):
    value = serializers.CharField()
    label = serializers.CharField()
    count = serializers.IntegerField()


class PhonemeSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source="get_category_display", read_only=True)

    class Meta:
        model = Phoneme
        fields = ["id", "symbol", "category", "category_display", "example_words", "display_order"]
        read_only_fields = fields
