
import random

WRITING_TOPICS = {
    "BEGINNER": [
        "Describe Your Daily Routine",
        "My Family",
        "My Favourite Food",
        "My Best Friend",
        "My Hobbies",
        "My College Life",
        "My Favourite Season",
        "How I Spend My Weekend",
        "My Favourite Teacher",
        "A Memorable Day"
    ],

    "ELEMENTARY": [
        "My Future Goals",
        "Importance of Education",
        "Benefits of Reading Books",
        "A Journey I Will Never Forget",
        "Healthy Lifestyle",
        "My Dream Career",
        "How I Manage My Time",
        "Importance of Friendship",
        "Learning a New Skill",
        "My Favourite Festival"
    ],

    "INTERMEDIATE": [
        "Technology in Everyday Life",
        "Social Media and Its Impact",
        "Environmental Protection",
        "Benefits of Learning English",
        "Online Education vs Traditional Education",
        "Importance of Communication Skills",
        "Work-Life Balance",
        "Women Empowerment",
        "The Role of Sports in Education",
        "How Technology Changes Our Lifestyle"
    ],

    "ADVANCED": [
        "Impact of Artificial Intelligence on Society",
        "The Future of Technology",
        "Ethical Challenges of Artificial Intelligence",
        "Climate Change and Global Responsibility",
        "The Importance of Critical Thinking",
        "Digital Privacy in the Modern World",
        "The Future of Education",
        "Innovation and Economic Growth",
        "Human Creativity in the Age of AI",
        "Globalization and Cultural Identity"
    ]
}

def get_random_topic(level="BEGINNER", previous_topic=None):
    topics = WRITING_TOPICS.get(
        level.upper(),
        WRITING_TOPICS["BEGINNER"]
    )

    available_topics = [
        topic for topic in topics
        if topic != previous_topic
    ]

    return random.choice(available_topics or topics)
