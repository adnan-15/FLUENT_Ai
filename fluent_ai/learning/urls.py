from django.urls import path
from . import views


urlpatterns = [
    # Home
    path("", views.landing, name="landing"),

    # Authentication
    path("signup/", views.signup_view, name="signup"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    # Dashboard
    path("dashboard/", views.dashboard, name="dashboard"),
    path(
        "api/dashboard-stats/",
        views.dashboard_stats_api,
        name="dashboard_stats_api",
    ),

    # Learning path
    path(
        "learning-path/",
        views.learning_path,
        name="learning_path",
    ),
    path(
        "learning-path/<str:module_name>/",
        views.module_detail,
        name="module_detail",
    ),

    # Lessons
    path(
        "lesson/<int:lesson_id>/",
        views.lesson_detail,
        name="lesson_detail",
    ),
    path(
        "lesson/<int:lesson_id>/complete/",
        views.complete_lesson,
        name="complete_lesson",
    ),
    path(
        "lesson/<int:lesson_id>/test/",
        views.lesson_test,
        name="lesson_test",
    ),

    # Practice
    path("practice/", views.practice, name="practice"),
    path(
        "practice/<str:practice_type>/submit/",
        views.practice_submit,
        name="practice_submit",
    ),

    # Games
    path("games/", views.games, name="games"),
    path(
        "games/save/",
        views.save_game_result,
        name="save_game_result",
    ),
    path(
        "games/<str:game_type>/",
        views.game_page,
        name="game_page",
    ),

    # Leaderboard
    path(
        "leaderboard/",
        views.leaderboard,
        name="leaderboard",
    ),

    # Assessments
    path(
        "assessment/",
        views.assessment,
        name="assessment",
    ),
    path(
        "assessment/writing/<int:attempt_id>/",
        views.assessment_writing,
        name="assessment_writing",
    ),
    path(
        "assessment/result/<int:attempt_id>/",
        views.assessment_result,
        name="assessment_result",
    ),

    # AI Tutor
    path(
        "ai-tutor/",
        views.ai_tutor,
        name="ai_tutor",
    ),
    path(
        "clear-chat/",
        views.clear_chat_history,
        name="clear_chat_history",
    ),

    # Voice notes
    path("vnotes/", views.vnotes, name="vnotes"),

    # User profile and settings
    path("profile/", views.profile, name="profile"),
    path("settings/", views.settings_view, name="settings"),
]