from datetime import timedelta

from django.conf import settings
from django.db.models import Avg, Count, Q
from django.db.models.functions import TruncDate
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.speech.models import SpeechAttempt

CONFIDENCE_THRESHOLD = getattr(settings, "PHONEME_COMPLETION_THRESHOLD", 0.7)


@api_view(["GET"])
def diagnostics_summary(request):
    """Overall diagnostics summary."""
    attempts = SpeechAttempt.objects.all()
    total = attempts.count()

    if total == 0:
        return Response({
            "total_attempts": 0,
            "avg_confidence": 0,
            "correct_rate": 0,
            "total_sessions": 0,
        })

    stats = attempts.aggregate(
        avg_confidence=Avg("confidence"),
        correct_count=Count("id", filter=Q(confidence__gte=CONFIDENCE_THRESHOLD)),
    )

    session_count = attempts.values("session_id").distinct().count()

    return Response({
        "total_attempts": total,
        "avg_confidence": round(stats["avg_confidence"], 3),
        "correct_rate": round(stats["correct_count"] / total, 3),
        "total_sessions": session_count,
    })


@api_view(["GET"])
def diagnostics_by_phoneme(request):
    """Per-phoneme metrics."""
    phoneme_stats = (
        SpeechAttempt.objects
        .values("phoneme__symbol", "phoneme__category")
        .annotate(
            attempts=Count("id"),
            avg_confidence=Avg("confidence"),
            correct_count=Count("id", filter=Q(confidence__gte=CONFIDENCE_THRESHOLD)),
        )
        .order_by("phoneme__category", "phoneme__symbol")
    )

    results = []
    for row in phoneme_stats:
        results.append({
            "phoneme": row["phoneme__symbol"],
            "category": row["phoneme__category"],
            "attempts": row["attempts"],
            "avg_confidence": round(row["avg_confidence"], 3),
            "correct_rate": round(row["correct_count"] / row["attempts"], 3) if row["attempts"] else 0,
        })

    return Response(results)


@api_view(["GET"])
def diagnostics_daily(request):
    """Daily activity for the last 30 days."""
    since = timezone.now() - timedelta(days=30)

    daily = (
        SpeechAttempt.objects
        .filter(created_at__gte=since)
        .annotate(day=TruncDate("created_at"))
        .values("day")
        .annotate(
            attempts=Count("id"),
            avg_confidence=Avg("confidence"),
        )
        .order_by("day")
    )

    results = []
    for row in daily:
        results.append({
            "day": row["day"].isoformat() if row["day"] else None,
            "attempts": row["attempts"],
            "avg_confidence": round(row["avg_confidence"], 3) if row["avg_confidence"] else 0,
        })

    return Response(results)
