import logging

from django.conf import settings
from rest_framework import serializers, status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.ai_tutor.llm_client import call_llm
from apps.ai_tutor.services import get_active_template
from apps.games.models import StorySession
from apps.sessions.models import LearningSession

logger = logging.getLogger(__name__)

FALLBACK_STORY = "And they all lived happily ever after!"


class StoryTurnRequestSerializer(serializers.Serializer):
    session_id = serializers.UUIDField()
    story_session_id = serializers.IntegerField(required=False)
    text = serializers.CharField(max_length=500)


class StoryTurnResponseSerializer(serializers.Serializer):
    story_session_id = serializers.IntegerField()
    llm_response = serializers.CharField()
    round_number = serializers.IntegerField()
    total_rounds = serializers.IntegerField()
    is_complete = serializers.BooleanField()
    summary = serializers.CharField(allow_blank=True)


@api_view(["POST"])
def story_turn(request):
    serializer = StoryTurnRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    session_id = serializer.validated_data["session_id"]
    story_session_id = serializer.validated_data.get("story_session_id")
    child_text = serializer.validated_data["text"]

    try:
        learning_session = LearningSession.objects.get(session_id=session_id)
    except LearningSession.DoesNotExist:
        return Response({"error": "Session not found"}, status=status.HTTP_404_NOT_FOUND)

    max_rounds = getattr(settings, "STORY_BUILDER_MAX_ROUNDS", 4)

    if story_session_id:
        try:
            story = StorySession.objects.get(pk=story_session_id, session=learning_session)
        except StorySession.DoesNotExist:
            return Response({"error": "Story session not found"}, status=status.HTTP_404_NOT_FOUND)
        if story.is_complete:
            return Response({"error": "Story is already complete"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        story = StorySession.objects.create(
            session=learning_session,
            max_rounds=max_rounds,
        )

    story.turns.append({"role": "child", "text": child_text})

    is_final = story.child_turn_count >= story.max_rounds

    llm_response_text = _generate_story_continuation(story, child_text, is_final)

    story.turns.append({"role": "llm", "text": llm_response_text})

    if is_final:
        story.is_complete = True
        story.summary = _generate_story_summary(story)

    story.save()

    response_data = {
        "story_session_id": story.pk,
        "llm_response": llm_response_text,
        "round_number": story.child_turn_count,
        "total_rounds": story.max_rounds,
        "is_complete": story.is_complete,
        "summary": story.summary,
    }

    return Response(StoryTurnResponseSerializer(response_data).data, status=status.HTTP_200_OK)


def _build_story_text(turns: list[dict]) -> str:
    parts = []
    for turn in turns:
        role_label = "Child" if turn["role"] == "child" else "Storyteller"
        parts.append(f"{role_label}: {turn['text']}")
    return "\n".join(parts)


def _generate_story_continuation(story: StorySession, child_text: str, is_final: bool) -> str:
    try:
        template = get_active_template("story_builder")
    except Exception:
        logger.exception("Story builder template not found")
        return FALLBACK_STORY

    story_so_far = _build_story_text(story.turns[:-1]) if len(story.turns) > 1 else "(This is the beginning)"

    if is_final:
        instruction = "This is the FINAL round. Wrap up the story with a happy ending. Do NOT ask the child to continue."
    else:
        instruction = "Continue the story with 1-2 sentences, then gently invite the child to add to it."

    user_message = template.user_template.format(
        story_so_far=story_so_far,
        child_text=child_text,
        round_number=story.child_turn_count,
        total_rounds=story.max_rounds,
        instruction=instruction,
    )

    messages = [
        {"role": "system", "content": template.system_prompt},
        {"role": "user", "content": user_message},
    ]

    llm_result = call_llm(messages)
    if llm_result.is_successful:
        return llm_result.text
    else:
        logger.warning("LLM call failed for story: %s", llm_result.error_message)
        return FALLBACK_STORY


def _generate_story_summary(story: StorySession) -> str:
    story_text = _build_story_text(story.turns)
    messages = [
        {
            "role": "system",
            "content": (
                "You are a friendly storytelling buddy for children aged 5-7. "
                "Summarize the following story in simple, fun language that a 5-year-old would enjoy. "
                "Keep it to 3-4 short sentences."
            ),
        },
        {
            "role": "user",
            "content": f"Please summarize this story:\n\n{story_text}",
        },
    ]

    llm_result = call_llm(messages)
    if llm_result.is_successful:
        return llm_result.text
    else:
        logger.warning("LLM summary call failed: %s", llm_result.error_message)
        return "What a wonderful story we made together!"
