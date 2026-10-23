
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fluent_ai.settings")
django.setup()

from learning.models import AssessmentQuestion

questions = [
    # Grammar (7)
    ("Grammar", "She ___ to school every day.", "go", "goes", "going", "gone", "B"),
    ("Grammar", "They ___ playing football now.", "is", "am", "are", "be", "C"),
    ("Grammar", "I have lived here ___ 2020.", "for", "since", "from", "by", "B"),
    ("Grammar", "If I ___ rich, I would travel.", "am", "was", "were", "be", "C"),
    ("Grammar", "He has already ___ his homework.", "finish", "finishes", "finished", "finishing", "C"),
    ("Grammar", "Neither of the answers ___ correct.", "are", "were", "is", "be", "C"),
    ("Grammar", "The letter ___ yesterday.", "sent", "was sent", "is send", "sending", "B"),

    # Vocabulary (7)
    ("Vocabulary", "Choose a synonym for 'rapid'.", "Slow", "Fast", "Weak", "Late", "B"),
    ("Vocabulary", "What does 'generous' mean?", "Selfish", "Kind and giving", "Angry", "Careless", "B"),
    ("Vocabulary", "Choose the opposite of 'ancient'.", "Old", "Historic", "Modern", "Past", "C"),
    ("Vocabulary", "A person who writes books is an ___.", "Author", "Actor", "Editor", "Artist", "A"),
    ("Vocabulary", "What does 'reluctant' mean?", "Unwilling", "Excited", "Certain", "Friendly", "A"),
    ("Vocabulary", "Choose a synonym for 'accurate'.", "Correct", "Vague", "False", "Ordinary", "A"),
    ("Vocabulary", "What does 'expand' mean?", "Reduce", "Enlarge", "Hide", "Divide", "B"),

    # Conversation (6)
    ("Conversation", "Someone says, 'How are you?' Choose a suitable reply.", "I am fine, thank you.", "I am 20 years.", "I fine.", "How you?", "A"),
    ("Conversation", "You want to ask someone to repeat. You say:", "Go again.", "Could you repeat that, please?", "What?", "Speak.", "B"),
    ("Conversation", "Someone thanks you. You reply:", "Never mind you.", "Welcome you.", "You're welcome.", "Thanks me.", "C"),
    ("Conversation", "You arrive late to a meeting. You say:", "I apologize for being late.", "You wait me.", "I late yesterday.", "No meeting.", "A"),
    ("Conversation", "You want to politely request help. You say:", "Help me now.", "Can you help me, please?", "You must help.", "Do help.", "B"),
    ("Conversation", "Someone says, 'Nice to meet you.' You reply:", "Nice to meet you too.", "Meet nice.", "Same meeting.", "I know.", "A"),
]

created = 0

for category, question, a, b, c, d, answer in questions:
    obj, was_created = AssessmentQuestion.objects.get_or_create(
        question=question,
        defaults={
            "category": category,
            "option_a": a,
            "option_b": b,
            "option_c": c,
            "option_d": d,
            "correct_answer": answer,
        },
    )
    if was_created:
        created += 1

print(f"Created {created} questions.")
print(f"Total questions: {AssessmentQuestion.objects.count()}")
