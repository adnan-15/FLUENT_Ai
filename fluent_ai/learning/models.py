from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    LEVEL_CHOICES = [
        ("BEGINNER", "Beginner"),
        ("ELEMENTARY", "Elementary"),
        ("INTERMEDIATE", "Intermediate"),
        ("ADVANCED", "Advanced"),
    ]

    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name="profile")
    level = models.CharField(max_length=20,choices=LEVEL_CHOICES,default="BEGINNER")
    cefr_level = models.CharField(max_length=5,default="A1")
    points = models.PositiveIntegerField(default=0)
    streak = models.PositiveIntegerField(default=0)
    progress_percent = models.FloatField(default=0)
    completed_lessons = models.PositiveIntegerField(default=0)
    last_active = models.DateTimeField(null=True,blank=True)
    bio = models.TextField(blank=True)
    notifications_enabled = models.BooleanField(default=True)
    dark_mode = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.user.username} Profile"


class Lesson(models.Model):
    LEVEL_CHOICES = [
        ("BEGINNER", "Beginner"),
        ("ELEMENTARY", "Elementary"),
        ("INTERMEDIATE", "Intermediate"),
        ("ADVANCED", "Advanced"),
    ]

    level = models.CharField(max_length=20,choices=LEVEL_CHOICES)
    stage_number = models.PositiveIntegerField()
    topic_number = models.PositiveIntegerField()
    title = models.CharField(max_length=200)
    description = models.TextField()
    content = models.TextField()
    vocabulary = models.JSONField(default=list,blank=True)
    grammar_points = models.JSONField(default=list,blank=True)
    estimated_minutes = models.PositiveIntegerField(default=15)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["level","stage_number","order"]

    def __str__(self):
        return self.title


class LessonProgress(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson,on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    progress_percent = models.FloatField(default=0)
    completed_at = models.DateTimeField(null=True,blank=True)
    last_viewed = models.DateTimeField(auto_now=True)
    class Meta:
        unique_together = ("user", "lesson")
    def __str__(self):
        return f"{self.user.username} - {self.lesson.title}"


class Quiz(models.Model):
    lesson = models.ForeignKey(Lesson,on_delete=models.CASCADE,related_name="quizzes")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.title


class Question(models.Model):
    quiz = models.ForeignKey(Quiz,on_delete=models.CASCADE,related_name="questions")
    question_text = models.TextField()
    option_a = models.CharField(max_length=300)
    option_b = models.CharField(max_length=300)
    option_c = models.CharField(max_length=300)
    option_d = models.CharField(max_length=300)
    correct_answer = models.CharField(max_length=1)
    explanation = models.TextField(blank=True)
    def __str__(self):
        return self.question_text


class QuizAttempt(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz,on_delete=models.CASCADE)
    score = models.FloatField()
    total_questions = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.quiz.title}"


class PracticeSession(models.Model):
    PRACTICE_CHOICES = [
        ("conversation", "Conversation Practice"),
        ("speaking", "Speaking Practice"),
        ("grammar", "Grammar Practice"),
        ("structure", "Sentence Structure"),
    ]

    user = models.ForeignKey(User,on_delete=models.CASCADE)
    practice_type = models.CharField(max_length=30,choices=PRACTICE_CHOICES)
    prompt = models.TextField()
    response = models.TextField()
    score = models.FloatField(default=0)
    feedback = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.practice_type}"


class PracticeQuestion(models.Model):
    CATEGORY_CHOICES = [
        ("grammar", "Grammar"),
        ("vocabulary", "Vocabulary"),
        ("conversations", "Conversations"),
    ]
    TYPE_CHOICES = [
        ("mcq", "MCQ Questions"),
        ("spot_error", "Spot the Error"),
        ("one_word", "One Word"),
    ]
    category = models.CharField(max_length=20,choices=CATEGORY_CHOICES,)
    question_type = models.CharField(max_length=20,choices=TYPE_CHOICES,)
    question_text = models.TextField()
    option_a = models.CharField(max_length=300,blank=True,)
    option_b = models.CharField(max_length=300,blank=True,)
    option_c = models.CharField(max_length=300,blank=True,)
    option_d = models.CharField(max_length=300,blank=True,)
    correct_answer = models.CharField(max_length=300,blank=True,)
    explanation = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ["category", "question_type", "id"]

    def __str__(self):
        return (
            f"{self.get_category_display()} - "
            f"{self.question_text[:60]}"
        )

class AssessmentQuestion(models.Model):
    CATEGORY_CHOICES = [
        ("Grammar", "Grammar"),
        ("Vocabulary", "Vocabulary"),
        ("Conversation", "Conversation"),
    ]

    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default="Grammar",
    )

    question = models.TextField()
    option_a = models.CharField(max_length=300)
    option_b = models.CharField(max_length=300)
    option_c = models.CharField(max_length=300)
    option_d = models.CharField(max_length=300)
    correct_answer = models.CharField(max_length=1)
    difficulty = models.CharField(max_length=10, default="A1")
    explanation = models.TextField(blank=True)

    def __str__(self):
        return f"{self.category}: {self.question}"



class AssessmentAttempt(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    mcq_score = models.FloatField(default=0)
    writing_score = models.FloatField(default=0)
    ml_confidence = models.FloatField(default=0)
    final_score = models.FloatField(default=0)
    predicted_level = models.CharField(max_length=30,blank=True,default="",)
    writing_response = models.TextField(blank=True)
    recommendations = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.user.username} - {self.predicted_level}"


class VideoNote(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    youtube_url = models.URLField()
    topic = models.CharField(max_length=100)
    level = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class ChatMessage(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    message = models.TextField()
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.message[:30]}"


class Achievement(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=10, default="★")
    points_required = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title


class UserAchievement(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    achievement = models.ForeignKey(Achievement,on_delete=models.CASCADE)
    unlocked_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ("user", "achievement")


class LearningEvent(models.Model):
    EVENT_CHOICES = [
        ("lesson", "Lesson"),
        ("quiz", "Quiz"),
        ("practice", "Practice"),
        ("assessment", "Assessment"),
    ]

    user = models.ForeignKey(User,on_delete=models.CASCADE)
    event_type = models.CharField(max_length=20,choices=EVENT_CHOICES)
    title = models.CharField(max_length=200)
    score = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.title}"



class InterviewQuestion(models.Model):
    CATEGORY_CHOICES = [
        ("introduction", "Self Introduction"),
        ("hr", "HR Questions"),
        ("strengths", "Strengths and Weaknesses"),
        ("teamwork", "Teamwork and Situational"),
        ("career", "Career Goals"),
    ]

    category = models.CharField(max_length=30,choices=CATEGORY_CHOICES,default="hr",)
    question_text = models.TextField()
    sample_answer = models.TextField()
    answer_tips = models.TextField(blank=True)
    keywords = models.JSONField(default=list,blank=True,)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True,)

    class Meta:
        ordering = ["category", "id"]

    def __str__(self):
        return self.question_text[:100]
