from django.contrib import admin

from .models import (
    UserProfile,
    Lesson,
    LessonProgress,
    Quiz,
    Question,
    QuizAttempt,
    PracticeSession,
    AssessmentQuestion,
    AssessmentAttempt,
    VideoNote,
    ChatMessage,
    Achievement,
    UserAchievement,
    LearningEvent,
    InterviewQuestion,
    PracticeQuestion,
)


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "lesson",
        "created_at",
    )

    inlines = [
        QuestionInline
    ]


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "level",
        "cefr_level",
        "points",
        "streak",
        "progress_percent",
    )


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "level",
        "stage_number",
        "topic_number",
        "is_active",
    )

    list_filter = (
        "level",
        "is_active",
    )


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "lesson",
        "completed",
        "progress_percent",
    )


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):

    list_display = (
        "question_text",
        "quiz",
        "correct_answer",
    )


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "quiz",
        "score",
        "total_questions",
        "created_at",
    )


@admin.register(PracticeSession)
class PracticeSessionAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "practice_type",
        "score",
        "created_at",
    )


from django.contrib import admin
from .models import PracticeQuestion


@admin.register(PracticeQuestion)
class PracticeQuestionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "category",
        "question_type",
        "question_text",
        "is_active",
    )
    list_filter = ("category", "question_type", "is_active")
    search_fields = ("question_text",)
    list_editable = ("is_active",)

@admin.register(AssessmentQuestion)
class AssessmentQuestionAdmin(admin.ModelAdmin):

    list_display = (
        "question",
        "difficulty",
        "correct_answer",
    )

    list_filter = (
        "difficulty",
    )


@admin.register(AssessmentAttempt)
class AssessmentAttemptAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "predicted_level",
        "final_score",
        "ml_confidence",
        "created_at",
    )



@admin.register(VideoNote)
class VideoNoteAdmin(admin.ModelAdmin):
    list_display = ("title", "topic", "level", "is_active")
    list_filter = ("topic", "level", "is_active")
    search_fields = ("title", "description", "topic")



@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "message",
        "created_at",
    )


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "points_required",
    )


@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "achievement",
        "unlocked_at",
    )


@admin.register(LearningEvent)
class LearningEventAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "event_type",
        "title",
        "score",
        "created_at",
    )



@admin.register(InterviewQuestion)
class InterviewQuestionAdmin(admin.ModelAdmin):
    list_display = (
        "question_text",
        "category",
        "is_active",
        "created_at",
    )

    list_filter = ("category", "is_active")

    search_fields = (
        "question_text",
        "sample_answer",
    )

    list_editable = ("is_active",)

    ordering = ("category", "id")
