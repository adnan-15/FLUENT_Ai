
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fluent_ai.settings")
django.setup()

from learning.models import VideoNote

VIDEOS = [
    {
        "title": "Learn English Grammar: Easy Tenses",
        "description": "Learn present simple and present continuous tenses.",
        "youtube_url": "https://www.youtube.com/watch?v=ELLCFbomiio",
        "topic": "Tenses",
        "level": "Beginner",
    },
    {
        "title": "English Conversation Practice",
        "description": "Practise everyday English conversations.",
        "youtube_url": "https://www.youtube.com/watch?v=1PGgf8fHXkY",
        "topic": "Conversation",
        "level": "Beginner",
    },
    {
        "title": "Speaking and Listening Practice",
        "description": "Practise real-life conversations and listening.",
        "youtube_url": "https://www.youtube.com/watch?v=MKln91sQYFQ",
        "topic": "Speaking",
        "level": "Beginner",
    },
    {
        "title": "Speak English with Confidence",
        "description": "Learn techniques to speak more confidently.",
        "youtube_url": "https://www.youtube.com/watch?v=T15_JtNQdFo",
        "topic": "Confidence",
        "level": "Beginner",
    },
]

for video in VIDEOS:
    note, created = VideoNote.objects.update_or_create(
        title=video["title"],
        defaults={
            **video,
            "is_active": True,
        },
    )

    action = "Added" if created else "Updated"
    print(f"{action}: {note.title}")

print("V-Notes seeding completed!")
