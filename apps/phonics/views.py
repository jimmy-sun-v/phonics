from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.phonics.models import Phoneme
from apps.phonics.serializers import CategorySerializer, PhonemeSerializer
from apps.phonics.services import get_all_categories, get_phoneme_detail, get_phonemes_by_category


@api_view(["GET"])
def category_list(request):
    categories = get_all_categories()
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def phoneme_list(request):
    category = request.query_params.get("category")
    if category:
        try:
            phonemes = get_phonemes_by_category(category)
        except ValueError:
            return Response({"error": f"Invalid category: {category}"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        phonemes = Phoneme.objects.all().order_by("category", "display_order")
    serializer = PhonemeSerializer(phonemes, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def phoneme_detail(request, symbol):
    phoneme = get_phoneme_detail(symbol)
    if phoneme is None:
        return Response({"error": f"Phoneme '{symbol}' not found"}, status=status.HTTP_404_NOT_FOUND)
    serializer = PhonemeSerializer(phoneme)
    return Response(serializer.data)
