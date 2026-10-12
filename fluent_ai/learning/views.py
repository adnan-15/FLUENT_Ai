import json

import random

import re

from datetime import timedelta

from pathlib import Path

from .ai_service import generate_ai_response

from django.contrib.auth.decorators import login_required

from django.http import JsonResponse

from django.views.decorators.http import require_POST



from .models import ChatMessage



import joblib



from django.contrib import messages

from django.contrib.auth import (

    authenticate,

    login,

    logout,

)

from django.contrib.auth.decorators import login_required

from django.contrib.auth.hashers import check_password

from django.contrib.auth.models import User

from django.db.models import Avg, Count, Sum

from django.http import JsonResponse

from django.shortcuts import (

    get_object_or_404,

    redirect,

    render,

)

from django.utils import timezone

from django.views.decorators.http import require_POST



from .models import (

    Achievement,

    AssessmentAttempt,

    AssessmentQuestion,

    ChatMessage,

    GameResult,

    LearningEvent,

    Lesson,

    LessonProgress,

    PracticeSession,

    QuizAttempt,

    UserAchievement,

    UserProfile,

    VideoNote,

)





BASE_DIR = Path(__file__).resolve().parent.parent





def get_profile(user):

    profile, created = UserProfile.objects.get_or_create(

        user=user

    )

    return profile





def refresh_profile_stats(user):



    profile = get_profile(user)



    total_lessons = Lesson.objects.filter(

        is_active=True

    ).count()



    completed_lessons = LessonProgress.objects.filter(

        user=user,

        completed=True

    ).count()



    if total_lessons:

        progress = (

            completed_lessons /

            total_lessons

        ) * 100

    else:

        progress = 0



    events = LearningEvent.objects.filter(

        user=user

    )



    dates = sorted(

        {

            event.created_at.date()

            for event in events

        },

        reverse=True

    )



    streak = 0



    if dates:



        today = timezone.localdate()



        if dates[0] == today:

            current = today

        elif dates[0] == today - timedelta(days=1):

            current = today - timedelta(days=1)

        else:

            current = None



        if current:



            for date in dates:



                if date == current:

                    streak += 1

                    current -= timedelta(days=1)

                else:

                    break



    profile.completed_lessons = completed_lessons

    profile.progress_percent = round(

        progress,

        1

    )

    profile.streak = streak



    profile.save()



    return profile





def log_event(

    user,

    event_type,

    title,

    score=0

):



    event = LearningEvent.objects.create(

        user=user,

        event_type=event_type,

        title=title,

        score=score

    )



    profile = get_profile(user)



    profile.points += int(score)



    profile.last_active = timezone.now()



    profile.save()



    refresh_profile_stats(user)



    achievements = Achievement.objects.filter(

        points_required__lte=profile.points

    )



    for achievement in achievements:



        UserAchievement.objects.get_or_create(

            user=user,

            achievement=achievement

        )



    return event





def dashboard_payload(user):



    profile = refresh_profile_stats(user)



    events = LearningEvent.objects.filter(

        user=user

    ).order_by("-created_at")



    avg_score = events.aggregate(

        value=Avg("score")

    )["value"] or 0



    labels = []

    scores = []



    for event in events.order_by(

        "created_at"

    )[:12]:



        labels.append(

            event.created_at.strftime("%d %b")

        )



        scores.append(

            round(event.score, 1)

        )



    payload = {

        "progress": profile.progress_percent,

        "streak": profile.streak,

        "points": profile.points,

        "cefr": profile.cefr_level,

        "average_score": round(

            avg_score,

            1

        ),

        "lessons": LessonProgress.objects.filter(

            user=user,

            completed=True

        ).count(),

        "practice": PracticeSession.objects.filter(

            user=user

        ).count(),

        "games": GameResult.objects.filter(

            user=user

        ).count(),

        "assessments": AssessmentAttempt.objects.filter(

            user=user

        ).count(),

        "labels": labels,

        "scores": scores,

    }



    return payload





def landing(request):



    return render(

        request,

        "landing.html"

    )





def signup_view(request):



    if request.user.is_authenticated:

        return redirect("dashboard")



    if request.method == "POST":



        username = request.POST.get(

            "username",

            ""

        ).strip()



        email = request.POST.get(

            "email",

            ""

        ).strip().lower()



        password = request.POST.get(

            "password",

            ""

        )



        confirm_password = request.POST.get(

            "confirm_password",

            ""

        )



        # -------------------------

        # REQUIRED FIELDS

        # -------------------------



        if not username or not email or not password:



            messages.error(

                request,

                "Please fill all required fields."

            )



            return render(

                request,

                "signup.html",

                {

                    "username": username,

                    "email": email,

                }

            )



        # -------------------------

        # PASSWORD MATCH

        # -------------------------



        if password != confirm_password:



            messages.error(

                request,

                "Passwords do not match."

            )



            return render(

                request,

                "signup.html",

                {

                    "username": username,

                    "email": email,

                }

            )



        # -------------------------

        # PASSWORD LENGTH

        # -------------------------



        if len(password) < 8:



            messages.error(

                request,

                "Password must contain at least 8 characters."

            )



            return render(

                request,

                "signup.html",

                {

                    "username": username,

                    "email": email,

                }

            )



        # -------------------------

        # USERNAME CHECK

        # -------------------------



        if User.objects.filter(

            username__iexact=username

        ).exists():



            messages.error(

                request,

                "Username already exists."

            )



            return render(

                request,

                "signup.html",

                {

                    "username": username,

                    "email": email,

                }

            )



        # -------------------------

        # EMAIL CHECK

        # -------------------------



        if User.objects.filter(

            email__iexact=email

        ).exists():



            messages.error(

                request,

                "Email is already registered."

            )



            return render(

                request,

                "signup.html",

                {

                    "username": username,

                    "email": email,

                }

            )



        # -------------------------

        # CREATE USER

        # -------------------------



        user = User.objects.create_user(

            username=username,

            email=email,

            password=password

        )



        # -------------------------

        # CREATE PROFILE

        # -------------------------



        UserProfile.objects.create(

            user=user,

            level="BEGINNER",

            cefr_level="A1",

            points=0,

            streak=0,

            progress_percent=0,

            completed_lessons=0

        )



        messages.success(

            request,

            "Account created successfully. Please login."

        )



        return redirect("login")



    return render(

        request,

        "signup.html"

    )





def login_view(request):



    if request.user.is_authenticated:

        return redirect("dashboard")



    if request.method == "POST":



        username = request.POST.get(

            "username",

            ""

        ).strip()



        password = request.POST.get(

            "password",

            ""

        )



        user = authenticate(

            request,

            username=username,

            password=password

        )



        if user:



            login(

                request,

                user

            )



            get_profile(user)



            return redirect("dashboard")



        messages.error(

            request,

            "Invalid username or password."

        )



    return render(

        request,

        "login.html"

    )





@require_POST

def logout_view(request):



    logout(request)



    return redirect("landing")







@login_required

@require_POST

def clear_chat_history(request):

    """

    Permanently delete chat history belonging to the logged-in user.

    """

    ChatMessage.objects.filter(user=request.user).delete()



    return JsonResponse({

        "success": True,

        "message": "Chat history cleared successfully."

    })





@login_required

def dashboard(request):



    payload = dashboard_payload(

        request.user

    )



    recent = LearningEvent.objects.filter(

        user=request.user

    ).order_by("-created_at")[:6]



    return render(

        request,

        "dashboard.html",

        {

            "profile": get_profile(request.user),

            "payload": payload,

            "recent": recent,

        }

    )





@login_required

def dashboard_stats_api(request):



    return JsonResponse(

        dashboard_payload(

            request.user

        )

    )



# ik

@login_required

def learning_path(request):



    profile = get_profile(request.user)

    modules = [

        {

            "key": "BEGINNER",

            "name": "Beginner",

            "icon": "🌱",

            "description": "Build your English foundations and everyday communication skills.",

            "stage_start": 1,

            "stage_end": 3,

        },

        {

            "key": "ELEMENTARY",

            "name": "Elementary",

            "icon": "🌿",

            "description": "Expand your vocabulary and improve your grammar and fluency.",

            "stage_start": 4,

            "stage_end": 6,

        },

        {

            "key": "INTERMEDIATE",

            "name": "Intermediate",

            "icon": "🌳",

            "description": "Develop your English skills for work, study and social situations.",

            "stage_start": 7,

            "stage_end": 9,

        },

        {

            "key": "ADVANCED",

            "name": "Advanced",

            "icon": "🌲",

            "description": "Refine your English skills for professional and academic success.",

            "stage_start": 10,

            "stage_end": 12,

        },

    ]



    for module in modules:

        lessons = Lesson.objects.filter(

            level=module["key"],

            is_active=True

        )



        completed = LessonProgress.objects.filter(

            user=request.user,

            lesson__in=lessons,

            completed=True

        ).count()



        module["total_levels"] = 15

        module["completed_levels"] = completed



        module["progress_percent"] = round(

            (completed / 15) * 100,

            1

        )



    return render(

        request,

        "learning_path.html",

        {

            "profile": profile,

            "modules": modules,

        }

    )  





@login_required

def lesson_detail(

    request,

    lesson_id

):



    lesson = get_object_or_404(

        Lesson,

        id=lesson_id,

        is_active=True

    )



    progress, created = LessonProgress.objects.get_or_create(

        user=request.user,

        lesson=lesson

    )



    return render(

        request,

        "lesson_detail.html",

        {

            "lesson": lesson,

            "progress": progress,

        }

    )





@login_required

@require_POST

def complete_lesson(

    request,

    lesson_id

):



    lesson = get_object_or_404(

        Lesson,

        id=lesson_id,

        is_active=True

    )



    progress, created = LessonProgress.objects.get_or_create(

        user=request.user,

        lesson=lesson

    )



    if not progress.completed:



        progress.completed = True

        progress.progress_percent = 100

        progress.completed_at = timezone.now()

        progress.save()



        log_event(

            request.user,

            "lesson",

            lesson.title,

            10

        )



        messages.success(

            request,

            "Lesson completed! +10 points."

        )



    return redirect(

        "lesson_detail",

        lesson_id=lesson.id

    )





@login_required

def lesson_test(

    request,

    lesson_id

):



    lesson = get_object_or_404(

        Lesson,

        id=lesson_id

    )



    quiz = lesson.quizzes.first()



    if not quiz:

        messages.warning(

            request,

            "No test is available for this lesson yet."

        )



        return redirect(

            "lesson_detail",

            lesson_id=lesson.id

        )



    questions = list(

        quiz.questions.all()

    )



    if request.method == "POST":



        correct = 0



        for question in questions:



            answer = request.POST.get(

                f"question_{question.id}"

            )



            if answer == question.correct_answer:

                correct += 1



        total = len(questions)



        score = (

            correct / total * 100

            if total

            else 0

        )



        #ik



        # Check if the student passed the test

        passed = score >= 70



        if passed:

            progress, created = LessonProgress.objects.get_or_create(

                user=request.user,

                lesson=lesson

            )



            if not progress.completed:

                progress.completed = True

                progress.progress_percent = 100

                progress.completed_at = timezone.now()

                progress.save()



        QuizAttempt.objects.create(

            user=request.user,

            quiz=quiz,

            score=score,

            total_questions=total

        )



        log_event(

            request.user,

            "quiz",

            quiz.title,

            score

        )



        return render(

            request,

            "test_result.html",

            {

                "quiz": quiz,

                "score": score,

                "correct": correct,

                "total": total,

            }

        )



    return render(

        request,

        "lesson_test.html",

        {

            "lesson": lesson,

            "quiz": quiz,

            "questions": questions,

        }

    )





@login_required

def practice(request):



    practice_types = [

        (

            "conversation",

            "Conversation Practice",

            "Improve everyday English conversations."

        ),

        (

            "speaking",

            "Speaking Practice",

            "Build confidence and fluency."

        ),

        (

            "grammar",

            "Grammar Practice",

            "Improve sentence accuracy."

        ),

        (

            "structure",

            "Sentence Structure",

            "Learn how to form better sentences."

        ),

    ]



    return render(

        request,

        "practice.html",

        {

            "practice_types": practice_types

        }

    )





@login_required

@require_POST

def practice_submit(

    request,

    practice_type

):



    prompts = {

        "conversation":

            "Introduce yourself and describe your daily routine.",

        "speaking":

            "Talk about your favorite hobby.",

        "grammar":

            "Write five sentences using the present perfect tense.",

        "structure":

            "Write a sentence containing a subject, verb and object.",

    }



    prompt = prompts.get(

        practice_type,

        "Write a short paragraph in English."

    )



    response = request.POST.get(

        "response",

        ""

    ).strip()



    words = response.split()



    score = min(

        100,

        max(

            20,

            len(words) * 4

        )

    )



    if len(words) < 5:



        feedback = (

            "Try writing longer answers "

            "with complete sentences."

        )



    elif len(words) < 15:



        feedback = (

            "Good start. Try adding more "

            "details and examples."

        )



    else:



        feedback = (

            "Good response. Continue working "

            "on grammar, vocabulary and fluency."

        )



    PracticeSession.objects.create(

        user=request.user,

        practice_type=practice_type,

        prompt=prompt,

        response=response,

        score=score,

        feedback=feedback

    )



    log_event(

        request.user,

        "practice",

        f"{practice_type.title()} Practice",

        score

    )



    return render(

        request,

        "practice_result.html",

        {

            "prompt": prompt,

            "response": response,

            "score": score,

            "feedback": feedback,

        }

    )





@login_required

def games(request):



    game_list = [

        (

            "jumble",

            "Word Jumble",

            "Unscramble English words."

        ),

        (

            "vocabulary",

            "Vocabulary Puzzle",

            "Test your vocabulary."

        ),

        (

            "grammar",

            "Grammar Challenge",

            "Choose the correct sentence."

        ),

        (

            "memory",

            "Memory Match",

            "Match words with meanings."

        ),

    ]



    return render(

        request,

        "games.html",

        {

            "games": game_list

        }

    )





@login_required

def game_page(

    request,

    game_type

):



    game_names = {

        "jumble": "Word Jumble",

        "vocabulary": "Vocabulary Puzzle",

        "grammar": "Grammar Challenge",

        "memory": "Memory Match",

    }



    if game_type not in game_names:



        return redirect("games")



    return render(

        request,

        "game.html",

        {

            "game_type": game_type,

            "game_name": game_names[game_type],

        }

    )





@login_required

@require_POST

def save_game_result(request):



    game_type = request.POST.get(

        "game_type"

    )



    score = int(

        request.POST.get(

            "score",

            0

        )

    )



    total = int(

        request.POST.get(

            "total",

            10

        )

    )



    valid_games = {

        "jumble",

        "vocabulary",

        "grammar",

        "memory",

    }



    if game_type not in valid_games:



        return JsonResponse(

            {

                "success": False,

                "message": "Invalid game."

            },

            status=400

        )



    GameResult.objects.create(

        user=request.user,

        game_type=game_type,

        score=score,

        total=total

    )



    percentage = (

        score / total * 100

        if total

        else 0

    )



    log_event(

        request.user,

        "game",

        game_type.title(),

        percentage

    )



    return JsonResponse(

        {

            "success": True

        }

    )





@login_required

def leaderboard(request):



    users = UserProfile.objects.select_related(

        "user"

    ).order_by(

        "-points"

    )[:20]



    return render(

        request,

        "leaderboard.html",

        {

            "users": users

        }

    )





@login_required

def assessment(request):



    questions = list(

        AssessmentQuestion.objects.all()

    )



    random.shuffle(

        questions

    )



    if request.method == "POST":



        correct = 0



        for question in questions:



            answer = request.POST.get(

                f"question_{question.id}"

            )



            if answer == question.correct_answer:

                correct += 1



        total = len(questions)



        mcq_score = (

            correct / total * 100

            if total

            else 0

        )



        attempt = AssessmentAttempt.objects.create(

            user=request.user,

            mcq_score=mcq_score

        )



        return redirect(

            "assessment_writing",

            attempt_id=attempt.id

        )



    return render(

        request,

        "assessment.html",

        {

            "questions": questions

        }

    )





@login_required

def assessment_writing(

    request,

    attempt_id

):



    attempt = get_object_or_404(

        AssessmentAttempt,

        id=attempt_id,

        user=request.user

    )



    if request.method == "POST":



        writing = request.POST.get(

            "writing",

            ""

        ).strip()



        if len(writing) < 20:



            messages.error(

                request,

                "Please write at least 20 characters."

            )



            return redirect(

                "assessment_writing",

                attempt_id=attempt.id

            )



        model_path = (

            BASE_DIR

            / "ml_models"

            / "cefr_model.pkl"

        )



        if not model_path.exists():



            messages.error(

                request,

                "CEFR model not found. Run train_model.py first."

            )



            return redirect(

                "assessment_writing",

                attempt_id=attempt.id

            )



        model = joblib.load(

            model_path

        )



        predicted = model.predict(

            [writing]

        )[0]



        probabilities = model.predict_proba(

            [writing]

        )[0]



        confidence = (

            max(probabilities) * 100

        )



        words = writing.split()



        sentences = re.split(

            r"[.!?]+",

            writing

        )



        sentences = [

            sentence.strip()

            for sentence in sentences

            if sentence.strip()

        ]



        avg_sentence_length = (

            len(words) / len(sentences)

            if sentences

            else len(words)

        )



        vocabulary = len(

            set(

                word.lower()

                for word in words

            )

        )



        writing_score = min(

            100,

            (

                min(len(words), 150) / 150 * 40

                +

                min(vocabulary, 80) / 80 * 30

                +

                min(avg_sentence_length, 25) / 25 * 30

            )

        )



        final_score = (

            attempt.mcq_score * 0.35

            +

            writing_score * 0.25

            +

            confidence * 0.40

        )



        recommendations = {

            "A1": "Focus on basic vocabulary, simple grammar and everyday sentences.",

            "A2": "Practice common conversations, past/future forms and vocabulary.",

            "B1": "Work on fluency, paragraph writing and more complex grammar.",

            "B2": "Practice advanced vocabulary, argumentation and natural expressions.",

            "C1": "Focus on precision, academic writing, idiomatic language and advanced fluency.",

        }



        attempt.writing_response = writing

        attempt.writing_score = round(

            writing_score,

            2

        )

        attempt.ml_confidence = round(

            confidence,

            2

        )

        attempt.final_score = round(

            final_score,

            2

        )

        attempt.predicted_level = predicted

        attempt.recommendations = recommendations.get(

            predicted,

            "Continue practicing English regularly."

        )



        attempt.save()



        profile = get_profile(

            request.user

        )



        profile.cefr_level = predicted



        level_mapping = {

            "A1": "BEGINNER",

            "A2": "ELEMENTARY",

            "B1": "INTERMEDIATE",

            "B2": "INTERMEDIATE",

            "C1": "ADVANCED",

        }



        profile.level = level_mapping.get(

            predicted,

            profile.level

        )



        profile.save()



        log_event(

            request.user,

            "assessment",

            "Level Assessment",

            final_score

        )



        return redirect(

            "assessment_result",

            attempt_id=attempt.id

        )



    return render(

        request,

        "assessment_writing.html",

        {

            "attempt": attempt

        }

    )





@login_required

def assessment_result(

    request,

    attempt_id

):



    attempt = get_object_or_404(

        AssessmentAttempt,

        id=attempt_id,

        user=request.user

    )



    return render(

        request,

        "assessment_result.html",

        {

            "attempt": attempt

        }

    )





def generate_tutor_response(

    user,

    message

):



    message_lower = message.lower()



    words = set(

        re.findall(

            r"\b[a-zA-Z]+\b",

            message_lower

        )

    )



    lessons = Lesson.objects.filter(

        is_active=True

    )



    best_lesson = None

    best_score = 0



    for lesson in lessons:



        searchable = (

            f"{lesson.title} "

            f"{lesson.description} "

            f"{lesson.content}"

        ).lower()



        lesson_words = set(

            re.findall(

                r"\b[a-zA-Z]+\b",

                searchable

            )

        )



        overlap = len(

            words.intersection(

                lesson_words

            )

        )



        if overlap > best_score:



            best_score = overlap

            best_lesson = lesson



    if best_lesson:



        snippet = best_lesson.content[:700]



        return (

            f"I found a useful lesson: "

            f"{best_lesson.title}.\n\n"

            f"{snippet}\n\n"

            f"Try practicing this topic and "

            f"ask me another question if you need help."

        )



    if "grammar" in message_lower:



        return (

            "For grammar practice, start with "

            "subject + verb + object. Example: "

            "I read books every day. "

            "You can ask me about tenses, articles, "

            "prepositions or sentence structure."

        )



    if "vocabulary" in message_lower:



        return (

            "For vocabulary improvement, learn words "

            "in context instead of memorizing isolated words. "

            "Try creating three sentences with every new word."

        )



    if (

        "speak" in message_lower

        or "speaking" in message_lower

    ):



        return (

            "For speaking practice, choose a simple topic "

            "and speak for one minute. Focus on fluency first, "

            "then work on grammar and pronunciation."

        )



    return (

        "I'm your Fluent AI Tutor. "

        "Ask me about grammar, vocabulary, speaking, "

        "sentence structure or any lesson topic."

    )





@login_required



def ai_tutor(request):

    is_ajax = (

        request.headers.get("X-Requested-With") == "XMLHttpRequest"

    )



    if request.method == "POST":

        message = request.POST.get("message", "").strip()



        if not message:

            if is_ajax:

                return JsonResponse(

                    {"error": "Please say something first."},

                    status=400,

                )

            return redirect("ai_tutor")



        if len(message) > 2000:

            if is_ajax:

                return JsonResponse(

                    {"error": "Please keep your message under 2000 characters."},

                    status=400,

                )

            return redirect("ai_tutor")



        try:

            response = generate_ai_response(message)

            fallback = False

        except Exception:

            import logging



            logging.getLogger(__name__).exception(

                "Fluent AI response generation failed"

            )



            # Voice chat: report the API failure instead of reading an

            # unrelated lesson as though it were an AI-generated answer.

            if is_ajax:

                return JsonResponse(

                    {

                        "error": (

                            "I couldn't generate a response. "

                            "Please check the AI service configuration."

                        )

                    },

                    status=502,

                )



            # Keep the old fallback for regular, non-voice form submissions.

            response = generate_tutor_response(request.user, message)

            fallback = True



        ChatMessage.objects.create(

            user=request.user,

            message=message,

            response=response,

        )



        if is_ajax:

            return JsonResponse({

                "response": response,

                "fallback": fallback,

            })



        return redirect("ai_tutor")



    chat_messages = ChatMessage.objects.filter(

        user=request.user

    ).order_by("created_at")[:50]



    return render(

        request,

        "ai_tutor.html",

        {"chat_messages": chat_messages},

    )





@login_required

def vnotes(request):



    notes = VideoNote.objects.filter(

        is_active=True

    )



    return render(

        request,

        "vnotes.html",

        {

            "notes": notes

        }

    )





@login_required

def profile(request):



    profile = get_profile(

        request.user

    )



    achievements = UserAchievement.objects.filter(

        user=request.user

    ).select_related(

        "achievement"

    )



    recent = LearningEvent.objects.filter(

        user=request.user

    )[:10]



    return render(

        request,

        "profile.html",

        {

            "profile": profile,

            "achievements": achievements,

            "recent": recent,

        }

    )





@login_required

def settings_view(request):



    profile = get_profile(

        request.user

    )



    if request.method == "POST":



        action = request.POST.get(

            "action"

        )



        if action == "profile":



            request.user.first_name = request.POST.get(

                "first_name",

                ""

            ).strip()



            request.user.last_name = request.POST.get(

                "last_name",

                ""

            ).strip()



            request.user.email = request.POST.get(

                "email",

                ""

            ).strip()



            request.user.save()



            profile.bio = request.POST.get(

                "bio",

                ""

            )



            profile.notifications_enabled = (

                request.POST.get(

                    "notifications"

                ) == "on"

            )



            profile.save()



            messages.success(

                request,

                "Profile settings updated."

            )



            return redirect("settings")



        if action == "password":



            old_password = request.POST.get(

                "old_password",

                ""

            )



            new_password = request.POST.get(

                "new_password",

                ""

            )



            confirm_password = request.POST.get(

                "confirm_password",

                ""

            )



            if not check_password(

                old_password,

                request.user.password

            ):



                messages.error(

                    request,

                    "Current password is incorrect."

                )



            elif new_password != confirm_password:



                messages.error(

                    request,

                    "New passwords do not match."

                )



            elif len(new_password) < 8:



                messages.error(

                    request,

                    "New password must contain at least 8 characters."

                )



            else:



                request.user.set_password(

                    new_password

                )



                request.user.save()



                login(

                    request,

                    request.user

                )



                messages.success(

                    request,

                    "Password changed successfully."

                )



            return redirect("settings")



    return render(

        request,

        "settings.html",

        {

            "profile": profile

        }

    )



# ik

@login_required

def module_detail(request, module_name):

    module_map = {

        "beginner": {

            "key": "BEGINNER",

            "name": "Beginner",

        },

        "elementary": {

            "key": "ELEMENTARY",

            "name": "Elementary",

        },

        "intermediate": {

            "key": "INTERMEDIATE",

            "name": "Intermediate",

        },

        "advanced": {

            "key": "ADVANCED",

            "name": "Advanced",

        },

    }



    module = module_map.get(module_name.lower())



    if not module:

        return redirect("learning_path")



    stage_names = {

        1: "English Foundations",

        2: "Everyday English",

        3: "Basic Communication",



        4: "Building Conversations",

        5: "Real-Life English",

        6: "Expressing Yourself",



        7: "Confident Communication",

        8: "Professional English",

        9: "Natural English",



        10: "Precision & Nuance",

        11: "Powerful Communication",

        12: "English Mastery",

    }



    stages = []



    if module["key"] == "BEGINNER":

        stage_numbers = [1, 2, 3]

    elif module["key"] == "ELEMENTARY":

        stage_numbers = [4, 5, 6]

    elif module["key"] == "INTERMEDIATE":

        stage_numbers = [7, 8, 9]

    else:

        stage_numbers = [10, 11, 12]



    for stage_number in stage_numbers:



        lessons = Lesson.objects.filter(

            level=module["key"],

            stage_number=stage_number,

            is_active=True

        ).order_by("topic_number")



        stages.append({

            "number": stage_number,

            "name": stage_names[stage_number],

            "lessons": lessons,

        })



    return render(

        request,

        "module_detail.html",

        {

            "module": module,

            "stages": stages,

        }

    )