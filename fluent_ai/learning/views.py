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
from django.contrib.auth import (authenticate,login,logout,)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from django.db.models import Avg, Count, Sum
from django.shortcuts import (get_object_or_404,redirect,render,)
from django.utils import timezone

from .models import (
    Achievement,
    AssessmentAttempt,
    AssessmentQuestion,
    ChatMessage,
    LearningEvent,
    Lesson,
    LessonProgress,
    PracticeSession,
    PracticeQuestion,
    QuizAttempt,
    InterviewQuestion,
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

    total_lessons = Lesson.objects.filter(is_active=True).count()
    completed_lessons = LessonProgress.objects.filter(
        user=user,
        completed=True
    ).count()

    progress = (
        (completed_lessons / total_lessons) * 100
        if total_lessons else 0
    )

    # Convert activity timestamps to the configured local timezone.
    events = LearningEvent.objects.filter(user=user).only("created_at")

    activity_dates = {
        timezone.localtime(event.created_at).date()
        for event in events
        if event.created_at is not None
    }

    today = timezone.localdate()
    yesterday = today - timedelta(days=1)

    # If the user was active today, count backward from today.
    # If their latest activity was yesterday, preserve the streak
    # until they become active today.
    if today in activity_dates:
        current_date = today
    elif yesterday in activity_dates:
        current_date = yesterday
    else:
        current_date = None

    streak = 0

    while current_date and current_date in activity_dates:
        streak += 1
        current_date -= timedelta(days=1)

    profile.completed_lessons = completed_lessons
    profile.progress_percent = round(progress, 1)
    profile.streak = streak
    profile.save(
        update_fields=[
            "completed_lessons",
            "progress_percent",
            "streak",
        ]
    )

    return profile


def log_event(user,event_type,title,score=0):
    event = LearningEvent.objects.create(user=user,event_type=event_type,title=title,score=score)
    profile = get_profile(user)
    profile.points += int(score)
    profile.last_active = timezone.now()
    profile.save()
    refresh_profile_stats(user)
    achievements = Achievement.objects.filter(points_required__lte=profile.points)
    for achievement in achievements:
        UserAchievement.objects.get_or_create(user=user,achievement=achievement)
    return event


def dashboard_payload(user):
    profile = refresh_profile_stats(user)

    events = LearningEvent.objects.filter(user=user)
    avg_score = events.aggregate(value=Avg("score"))["value"] or 0

    chart_events = events.order_by("-created_at")[:12]
    chart_events = list(reversed(chart_events))

    labels = [
        event.created_at.strftime("%d %b")
        for event in chart_events
    ]
    scores = [
        round(event.score, 1)
        for event in chart_events
    ]

    return {
        "progress": profile.progress_percent,
        "streak": profile.streak,
        "points": profile.points,
        "cefr": profile.cefr_level,
        "average_score": round(avg_score, 1),
        "completed_lessons": LessonProgress.objects.filter(
            user=user,
            completed=True,
        ).count(),
        "practice": PracticeSession.objects.filter(user=user).count(),
        "assessments": AssessmentAttempt.objects.filter(user=user).count(),
        "labels": labels,
        "scores": scores,
    }



def landing(request):
    return render(request,"landing.html")

def signup_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "POST":
        username = request.POST.get("username","").strip()
        email = request.POST.get("email","").strip().lower()
        password = request.POST.get("password","")
        confirm_password = request.POST.get("confirm_password","")

        # REQUIRED FIELDS
        if not username or not email or not password:
            messages.error(request,"Please fill all required fields.")
            return render(request,"signup.html",{"username": username,"email": email,})
    
        # PASSWORD MATCH
        if password != confirm_password:
            messages.error(request,"Passwords do not match.")
            return render(request,"signup.html",{"username": username,"email": email,})



        
        # PASSWORD LENGTH
        if len(password) < 8:
            messages.error(request,"Password must contain at least 8 characters.")
            return render(request,"signup.html",{"username": username,"email": email,} )

        # USERNAME CHECK
        if User.objects.filter(username__iexact=username).exists():
            messages.error(request,"Username already exists.")
            return render(request,"signup.html",{"username": username,"email": email,})

        # EMAIL CHECK
        if User.objects.filter(email__iexact=email).exists():
            messages.error(request,"Email is already registered.")
            return render( request,"signup.html",{"username": username,"email": email,})

        # CREATE USER
        user = User.objects.create_user(username=username,email=email,password=password)

        # CREATE PROFILE
        UserProfile.objects.create(
            user=user,
            level="BEGINNER",
            cefr_level="A1",
            points=0,
            streak=0,
            progress_percent=0,
            completed_lessons=0
            )

        messages.success(request,"Account created successfully. Please login.")
        return redirect("login")

    return render(request,"signup.html")



def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        from django.contrib.auth import get_user_model

        User = get_user_model()
        user_record = User.objects.filter(username=username).first()

        print("LOGIN USERNAME:", username)
        print("LIVE USER FOUND:", user_record is not None)

        if user_record:
            print("LIVE USER ACTIVE:", user_record.is_active)
            print(
                "LIVE PASSWORD MATCH:",
                user_record.check_password(password)
            )

        user = authenticate(
            request,
            username=username,
            password=password
        )

        print("USER AUTHENTICATED:", user is not None)

        if user:
            login(request, user)
            get_profile(user)
            print("AFTER LOGIN:", request.user.is_authenticated)
            return redirect("dashboard")

        messages.error(request, "Invalid username or password.")

    return render(request, "login.html")


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
    return JsonResponse({"success": True,"message": "Chat history cleared successfully."})



@login_required
def dashboard(request):
    profile = refresh_profile_stats(request.user)
    payload = dashboard_payload(request.user)

    recent_events = (
        LearningEvent.objects
        .filter(user=request.user)
        .order_by("-created_at")[:6]
    )

    return render(
        request,
        "dashboard.html",
        {
            "profile": profile,
            "payload": payload,
            "recent_events": recent_events,
        },
    )



@login_required
def dashboard_stats_api(request):
    return JsonResponse(dashboard_payload(request.user))

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
    return render(request,"learning_path.html",{"profile": profile,"modules": modules,})  



@login_required
def lesson_detail(request,lesson_id):
    lesson = get_object_or_404(Lesson,id=lesson_id,is_active=True )
    progress, created = LessonProgress.objects.get_or_create(user=request.user,lesson=lesson)
    return render(request,"lesson_detail.html",{"lesson": lesson,"progress": progress,} )


@login_required
@require_POST
def complete_lesson(request,lesson_id):
    lesson = get_object_or_404(Lesson,id=lesson_id,is_active=True)
    progress, created = LessonProgress.objects.get_or_create(user=request.user,lesson=lesson)
    if not progress.completed:
        progress.completed = True
        progress.progress_percent = 100
        progress.completed_at = timezone.now()
        progress.save()

        log_event(request.user,"lesson",lesson.title,10)
        messages.success(request,"Lesson completed! +10 points.")

    return redirect("lesson_detail",lesson_id=lesson.id)

@login_required
def lesson_test(request,lesson_id):
    lesson = get_object_or_404(Lesson,id=lesson_id)
    quiz = lesson.quizzes.first()
    if not quiz:
        messages.warning(request,"No test is available for this lesson yet.")
        return redirect("lesson_detail",lesson_id=lesson.id)
    questions = list(quiz.questions.all())
    if request.method == "POST":
        correct = 0
        for question in questions:
            answer = request.POST.get(f"question_{question.id}")
            if answer == question.correct_answer:
                correct += 1
        total = len(questions)
        score = (correct / total * 100
            if total
            else 0
        )



        #ik
        # Check if the student passed the test
        passed = score >= 70
        if passed:
            progress, created = LessonProgress.objects.get_or_create(user=request.user,lesson=lesson)
            if not progress.completed:
                progress.completed = True
                progress.progress_percent = 100
                progress.completed_at = timezone.now()
                progress.save()

        QuizAttempt.objects.create(user=request.user,quiz=quiz,score=score,total_questions=total)
        log_event(request.user,"quiz",quiz.title,score)
        return render(request,"test_result.html",{"quiz": quiz,"score": score,"correct": correct,"total": total,} )
    return render(request,"lesson_test.html",{"lesson": lesson,"quiz": quiz,"questions": questions,})

@login_required
def practice(request):
    categories = [
        (
            "grammar",
            "Grammar",
            "Improve grammar rules and sentence accuracy.",
        ),
        (
            "vocabulary",
            "Vocabulary",
            "Build your vocabulary and learn word usage.",
        ),
        (
            "conversations",
            "Conversations",
            "Practice everyday English conversations.",
        ),
    ]
    return render(
        request,
        "practice.html",
        {"categories": categories},
    )


@login_required
def practice_category(request, category):
    category_titles = {
        "grammar": "Grammar",
        "vocabulary": "Vocabulary",
        "conversations": "Conversations",
    }
    if category not in category_titles:
        return redirect("practice")
    practice_types = [
        (
            "spot_error",
            "Spot the Error",
            "Identify errors in sentences.",
        ),
        (
            "mcq",
            "MCQ Questions",
            "Choose the correct answer.",
        ),
        (
            "one_word",
            "One Word",
            "Find the correct word.",
        ),
    ]

    return render(
        request,
        "practice_category.html",
        {
            "category": category,
            "category_title": category_titles[category],
            "practice_types": practice_types,
        },
    )
@login_required
def practice_type_page(request, category, practice_type):
    category_titles = {
        "grammar": "Grammar",
        "vocabulary": "Vocabulary",
        "conversations": "Conversations",
    }

    type_titles = {
        "spot_error": "Spot the Error",
        "mcq": "MCQ Questions",
        "one_word": "One Word",
    }

    if category not in category_titles:
        return redirect("practice")

    if practice_type not in type_titles:
        return redirect(
            "practice_category",
            category=category,
        )

    questions = PracticeQuestion.objects.filter(
        category=category,
        question_type=practice_type,
        is_active=True,
    )

    return render(
        request,
        "practice_type.html",
        {
            "category": category,
            "category_title": category_titles[category],
            "practice_type": practice_type,
            "practice_type_title": type_titles[practice_type],
            "questions": questions,
        },
    )



@login_required
@require_POST
def practice_question_submit(request, category, practice_type):
    category_titles = {
        "grammar": "Grammar",
        "vocabulary": "Vocabulary",
        "conversations": "Conversations",
    }

    type_titles = {
        "spot_error": "Spot the Error",
        "mcq": "MCQ Questions",
        "one_word": "One Word",
    }

    if category not in category_titles:
        return redirect("practice")

    if practice_type not in type_titles:
        return redirect(
            "practice_category",
            category=category,
        )

    questions = list(
        PracticeQuestion.objects.filter(
            category=category,
            question_type=practice_type,
            is_active=True,
        )
    )

    if not questions:
        return redirect(
            "practice_type_page",
            category=category,
            practice_type=practice_type,
        )

    results = []
    correct_count = 0

    for question in questions:
        submitted_answer = request.POST.get(
            f"answer_{question.id}", ""
        ).strip()

        correct_answer = question.correct_answer.strip()

        if practice_type == "mcq":
            is_correct = (
                submitted_answer.upper()
                == correct_answer.upper()
            )
        else:
            normalize = lambda value: " ".join(
                value.strip().casefold().split()
            ).rstrip(".,!?;:")

            is_correct = (
                normalize(submitted_answer)
                == normalize(correct_answer)
                and bool(submitted_answer)
            )

        if is_correct:
            correct_count += 1

        results.append({
            "question": question,
            "submitted_answer": submitted_answer,
            "correct_answer": correct_answer,
            "is_correct": is_correct,
            "explanation": question.explanation,
        })

    total_questions = len(questions)
    score = round(
        (correct_count / total_questions) * 100
    )

    if score >= 85:
        feedback = "Excellent work! You have demonstrated strong understanding."
    elif score >= 70:
        feedback = "Good job! Keep practising to improve further."
    elif score >= 50:
        feedback = "You're making progress. Review the incorrect answers and try again."
    else:
        feedback = "Keep practising. Review the explanations and attempt the exercise again."

    log_event(
        request.user,
        "practice",
        f"{category_titles[category]} - "
        f"{type_titles[practice_type]}",
        score,
    )

    return render(
        request,
        "practice_question_result.html",
        {
            "category": category,
            "category_title": category_titles[category],
            "practice_type": practice_type,
            "practice_type_title": type_titles[practice_type],
            "results": results,
            "correct_count": correct_count,
            "total_questions": total_questions,
            "score": score,
            "feedback": feedback,
        },
    )

@login_required
@require_POST
def practice_submit(request,practice_type):
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
    prompt = prompts.get(practice_type,"Write a short paragraph in English.")
    response = request.POST.get("response","").strip()
    words = response.split()
    score = min(100,max(20,len(words) * 4))



    if len(words) < 5:
        feedback = (
            "Try writing longer answers "
            "with complete sentences."
        )
    elif len(words) < 15:
        feedback = (
            "Good start.Try adding more "
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
        request.user,"practice",f"{practice_type.title()} Practice",score)
    return render(request,"practice_result.html",
        {
            "prompt": prompt,
            "response": response,
            "score": score,
            "feedback": feedback,
        }
    )

@login_required
def interview_hub(request):
    activities = [
        {
            "slug": "common",
            "title": "Common Interview Questions",
            "description": (
                "Explore interview questions, sample answers, "
                "and tips for answering confidently."
            ),
        },
        {
            "slug": "answer",
            "title": "Answer Practice",
            "description": (
                "Write your own answers and receive "
                "rule-based feedback."
            ),
        },
        {
            "slug": "mock",
            "title": "Mock Interview",
            "description": (
                "Attempt a series of interview questions "
                "and review your overall performance."
            ),
        },
    ]

    total_questions = InterviewQuestion.objects.filter(
        is_active=True
    ).count()

    return render(
        request,
        "interview_hub.html",
        {
            "activities": activities,
            "total_questions": total_questions,
        },
    )

@login_required
def interview_activity(request, activity):
    activity_titles = {
        "common": "Common Interview Questions",
        "answer": "Answer Practice",
        "mock": "Mock Interview",
    }
    if activity not in activity_titles:
        return redirect("interview_hub")
    questions = InterviewQuestion.objects.filter(
        is_active=True
    )
    if activity == "mock":
        questions = questions.order_by("?")[:5]
    else:
        questions = questions.order_by("category", "id")
    questions = list(questions)
    results = []
    total_score = 0
    answered_count = 0

    if request.method == "POST" and activity in ("answer", "mock"):
        for question in questions:
            answer = request.POST.get(
                f"answer_{question.id}", ""
            ).strip()

            if not answer:
                results.append({
                    "question": question,
                    "answer": answer,
                    "score": 0,
                    "feedback": "No answer provided. Try writing a complete response.",
                })
                continue

            words = answer.split()
            word_count = len(words)
            answer_lower = answer.lower()

            # Score answer length: maximum 30 points
            if word_count >= 50:
                length_score = 30
            elif word_count >= 30:
                length_score = 25
            elif word_count >= 15:
                length_score = 18
            elif word_count >= 5:
                length_score = 10
            else:
                length_score = 5

            # Score relevant keywords: maximum 50 points
            keywords = question.keywords or []
            keywords = [
                str(keyword).strip().lower()
                for keyword in keywords
                if str(keyword).strip()
            ]

            if keywords:
                matched = sum(
                    1 for keyword in keywords
                    if keyword in answer_lower
                )
                relevance_score = round(
                    50 * matched / len(keywords)
                )
            else:
                # No keywords configured: award partial credit
                # without pretending relevance was verified.
                relevance_score = 25 if word_count >= 15 else 10

            # Score examples and explanation structure: 20 points
            example_phrases = [
                "for example",
                "for instance",
                "when i",
                "in my project",
                "i learned",
                "as a result",
            ]

            has_example = any(
                phrase in answer_lower
                for phrase in example_phrases
            )

            structure_score = 20 if has_example else (
                10 if word_count >= 15 else 0
            )

            score = min(
                100,
                length_score + relevance_score + structure_score,
            )

            if word_count < 10:
                feedback = (
                    "Your answer is too short. Explain your point "
                    "and add supporting details."
                )
            elif not has_example:
                feedback = (
                    "Good start. Add a specific example from your "
                    "studies, projects, or experience."
                )
            elif score >= 75:
                feedback = (
                    "Good effort. Your answer has useful detail. "
                    "Review it to make sure it directly addresses "
                    "the question."
                )
            else:
                feedback = (
                    "Your answer has some useful content. Add "
                    "more relevant details and explain your "
                    "reasoning clearly."
                )

            results.append({
                "question": question,
                "answer": answer,
                "score": score,
                "feedback": feedback,
            })

            total_score += score
            answered_count += 1

        overall_score = round(
            total_score / len(questions)
        ) if questions else 0

        return render(
            request,
            "interview_activity.html",
            {
                "activity": activity,
                "activity_title": activity_titles[activity],
                "questions": questions,
                "results": results,
                "overall_score": overall_score,
                "answered_count": answered_count,
                "submitted": True,
            },
        )

    return render(
        request,
        "interview_activity.html",
        {
            "activity": activity,
            "activity_title": activity_titles[activity],
            "questions": questions,
            "submitted": False,
        },
    )

@login_required
def assessment(request):
    """Show the two independent assessment options."""
    return render(request, "assessment.html")

@login_required
def assessment_mcq(request):
    """Display 20 random MCQs and predict the student's level."""

    from collections import Counter
    import pandas as pd
    categories = {
        "Grammar": 7,
        "Vocabulary": 7,
        "Conversation": 6,
    }

    # GET: select and store 20 random questions.
    if request.method == "GET":
        selected_questions = []
        for category, count in categories.items():
            bank = list(
                AssessmentQuestion.objects.filter(category=category)
            )
            if len(bank) < count:
                messages.error(
                    request,
                    f"Add at least {count} {category} questions "
                    "to your question bank.",
                )
                return redirect("assessment")
            selected_questions.extend(random.sample(bank, count))
        random.shuffle(selected_questions)
        request.session["mcq_question_ids"] = [
            q.id for q in selected_questions
        ]

        return render(
            request,
            "assessment_mcq.html",
            {"questions": selected_questions},
        )

    # POST: use the exact questions shown to the student.
    selected_ids = request.session.get("mcq_question_ids", [])

    if len(selected_ids) != 20:
        messages.error(
            request,
            "Your assessment session expired. Please start again.",
        )
        return redirect("assessment_mcq")

    question_map = {
        q.id: q
        for q in AssessmentQuestion.objects.filter(id__in=selected_ids)
    }

    if len(question_map) != 20:
        messages.error(
            request,
            "Some questions are unavailable. Please start again.",
        )
        return redirect("assessment_mcq")

    # Validate all submitted answers before scoring.
    for qid in selected_ids:
        answer_key = f"question_{qid}"

        if answer_key not in request.POST:
            messages.error(
                request,
                "Please answer all 20 questions.",
            )
            return redirect("assessment_mcq")

        answer = request.POST.get(answer_key, "").strip().upper()

        if answer not in {"A", "B", "C", "D"}:
            messages.error(
                request,
                "Invalid answer submitted. Please try again.",
            )
            return redirect("assessment_mcq")

    correct_by_category = Counter()
    correct = 0

    for qid in selected_ids:
        question = question_map[qid]
        answer = request.POST.get(
            f"question_{qid}", ""
        ).strip().upper()

        category = question.category

        if answer == question.correct_answer.strip().upper():
            correct += 1
            correct_by_category[category] += 1

    grammar_correct = correct_by_category["Grammar"]
    vocabulary_correct = correct_by_category["Vocabulary"]
    conversation_correct = correct_by_category["Conversation"]

    total_percentage = round(correct / 20 * 100, 2)

    # These four features must match train_model.py.
    feature_values = {
        "TotalPercentage": total_percentage,
        "GrammarPercentage": round(grammar_correct / 7 * 100, 2),
        "VocabularyPercentage": round(vocabulary_correct / 7 * 100, 2),
        "ConversationPercentage": round(conversation_correct / 6 * 100, 2),
    }

    model_path = BASE_DIR / "ml_models" / "mcq_level_model.pkl"

    if not model_path.exists():
        messages.error(
            request,
            "MCQ model not found. Run train_model.py first.",
        )
        return redirect("assessment")

    try:
        saved = joblib.load(model_path)
        model = saved["model"]
        features = saved.get("features", list(feature_values.keys()))

        missing_features = [
            name for name in features if name not in feature_values
        ]

        if missing_features:
            messages.error(
                request,
                "Your MCQ model uses outdated features. Update "
                "train_model.py to use the four percentage features, "
                "then run python train_model.py.",
            )
            return redirect("assessment")

        X = pd.DataFrame(
            [[feature_values[name] for name in features]],
            columns=features,
        )

        predicted = str(model.predict(X)[0])

    except (KeyError, ValueError, TypeError, OSError) as exc:
        messages.error(
            request,
            f"Unable to predict your MCQ level: {exc}",
        )
        return redirect("assessment")
    
    allowed_labels = {
        "Needs Improvement",
        "Developing",
        "Proficient",
        "Advanced",
    }

    if predicted not in allowed_labels:
        messages.error(
            request,
            "Unexpected model label. Check train_model.py.",
        )
        return redirect("assessment")

    attempt = AssessmentAttempt.objects.create(
        user=request.user,
        mcq_score=total_percentage,
        writing_score=0,
        final_score=total_percentage,
        predicted_level=predicted,
        recommendations=(
            f"Grammar: {grammar_correct}/7 correct. "
            f"Vocabulary: {vocabulary_correct}/7 correct. "
            f"Conversation: {conversation_correct}/6 correct."
        ),
    )

    request.session.pop("mcq_question_ids", None)

    return redirect(
        "assessment_result",
        attempt_id=attempt.id,
    )

@login_required
def assessment_writing(request):
    """Run the independent writing proficiency model."""
    if request.method == "POST":
        writing = request.POST.get(
            "writing_response", ""
        ).strip()

        if len(writing) < 50:
            messages.error(
                request,
                "Please write at least 50 characters in English.",
            )
            return redirect("assessment_writing")

        model_path = (
            BASE_DIR / "ml_models" / "writing_level_model.pkl"
        )

        if not model_path.exists():
            messages.error(
                request,
                "Writing model not found. Run trainmodel1.py first.",
            )
            return redirect("assessment_writing")

        saved = joblib.load(model_path)
        model = saved["model"]
        predicted = str(model.predict([writing])[0])

        allowed_labels = {
            "Needs Improvement",
            "Developing",
            "Proficient",
            "Advanced",
        }

        if predicted not in allowed_labels:
            messages.error(
                request,
                "The writing model returned an unsupported label. "
                "Retrain trainmodel1.py.",
            )
            return redirect("assessment_writing")

        probabilities = model.predict_proba([writing])[0]
        confidence = float(max(probabilities) * 100)

        words = writing.split()
        sentences = [
            sentence.strip()
            for sentence in re.split(r"[.!?]+", writing)
            if sentence.strip()
        ]

        unique_words = len(set(word.lower() for word in words))
        avg_sentence_length = (
            len(words) / len(sentences) if sentences else 0
        )

        writing_score = min(
            100,
            min(len(words), 150) / 150 * 40
            + min(unique_words, 80) / 80 * 30
            + min(avg_sentence_length, 25) / 25 * 30,
        )

        recommendations = {
            "Needs Improvement": (
                "Practice basic sentence formation, everyday vocabulary, "
                "spelling, and essential grammar."
            ),
            "Developing": (
                "Practice paragraph writing, verb tenses, linking words, "
                "and expressing ideas clearly."
            ),
            "Proficient": (
                "Work on paragraph structure, precise vocabulary, "
                "complex sentences, and supporting your ideas."
            ),
            "Advanced": (
                "Focus on nuanced expression, style, clarity, "
                "and precise academic or professional writing."
            ),
        }

        attempt = AssessmentAttempt.objects.create(
            user=request.user,
            writing_score=round(writing_score, 2),
            ml_confidence=round(confidence, 2),
            final_score=round(writing_score, 2),
            predicted_level=predicted,
            writing_response=writing,
            recommendations=recommendations[predicted],
        )

        log_event(
            request.user,
            "assessment",
            "Writing Assessment",
            writing_score,
        )

        return redirect(
            "assessment_result",
            attempt_id=attempt.id,
        )

    return render(request, "assessment_writing.html")


@login_required
def assessment_result(request, attempt_id):
    attempt = get_object_or_404(
        AssessmentAttempt,
        id=attempt_id,
        user=request.user,
    )

    return render(
        request,
        "assessment_result.html",
        {"attempt": attempt},
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
    from urllib.parse import urlparse, parse_qs
    import re

    categories = [
        {
            "slug": "tenses",
            "title": "Tenses",
            "description": "Grammar, verb forms and sentence structure.",
            "icon": "Aa",
            "keywords": ["tense", "grammar", "verb"],
        },
        {
            "slug": "conversation",
            "title": "Conversation",
            "description": "Everyday English and practical dialogues.",
            "icon": "↔",
            "keywords": ["conversation", "dialogue", "daily talk"],
        },
        {
            "slug": "speaking-podcast",
            "title": "Speaking & Podcast",
            "description": "Listening, pronunciation and spoken English.",
            "icon": "♫",
            "keywords": ["speaking", "podcast", "pronunciation", "listening"],
        },
        {
            "slug": "confidence-building",
            "title": "Confidence Building",
            "description": "Speak naturally and communicate confidently.",
            "icon": "✦",
            "keywords": ["confidence", "communication", "personality"],
        },
    ]

    category_slug = request.GET.get("category", "")
    video_pk = request.GET.get("video", "")

    selected_category = next(
        (item for item in categories if item["slug"] == category_slug),
        None,
    )

    notes = []
    selected_video = None
    embed_url = ""

    if selected_category:
        keywords = selected_category["keywords"]

        for note in VideoNote.objects.filter(is_active=True).order_by("title"):
            topic = (note.topic or "").lower().replace("&", "and")

            if any(keyword in topic for keyword in keywords):
                notes.append(note)

        if video_pk.isdigit():
            selected_video = next(
                (note for note in notes if note.pk == int(video_pk)),
                None,
            )

        if selected_video:
            parsed = urlparse(selected_video.youtube_url.strip())
            host = parsed.netloc.lower()
            youtube_id = ""

            if host == "youtu.be" or host.endswith(".youtu.be"):
                youtube_id = parsed.path.strip("/").split("/")[0]

            elif host in ("youtube.com", "www.youtube.com",
                          "m.youtube.com", "youtube-nocookie.com",
                          "www.youtube-nocookie.com"):
                if parsed.path == "/watch":
                    youtube_id = parse_qs(parsed.query).get("v", [""])[0]
                else:
                    match = re.match(
                        r"^/(?:embed|shorts|live)/([^/?]+)",
                        parsed.path,
                    )
                    if match:
                        youtube_id = match.group(1)

            if re.fullmatch(r"[A-Za-z0-9_-]{11}", youtube_id):
                embed_url = (
                    "https://www.youtube-nocookie.com/embed/" + youtube_id
                )

    return render(
        request,
        "vnotes.html",
        {
            "categories": categories,
            "category": category_slug,
            "selected_category": selected_category,
            "notes": notes,
            "selected_video": selected_video,
            "embed_url": embed_url,
        },
    )




@login_required
def profile(request):
    profile = get_profile(request.user)

    achievements = UserAchievement.objects.filter(
        user=request.user
    ).select_related("achievement")

    recent = LearningEvent.objects.filter(
        user=request.user
    ).order_by("-created_at")[:10]

    return render(
        request,
        "profile.html",
        {
            "user": request.user,
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


        
        if action == "preferences":
            profile.notifications_enabled = (
                request.POST.get("notifications_enabled") == "on"
            )
            profile.save(update_fields=["notifications_enabled"])

            messages.success(
                request,
                "Learning notification preferences saved."
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
