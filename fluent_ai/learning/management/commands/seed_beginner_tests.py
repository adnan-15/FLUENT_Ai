from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from learning.models import Lesson, Quiz, Question


# Questions below are transcribed from the supplied
# Fluent_AI_Beginner_Professionally_Formatted.docx.
# Only the eight tests not yet entered are included:
# Stage 2 Levels 3-5 and Stage 3 Levels 1-5.

BEGINNER_TESTS = [{'stage': 2, 'topic': 3, 'title': 'Food & Drinks - Test', 'questions': [('Which one is a drink?', 'Rice', 'Bread', 'Milk', 'Salad', 'C', 'Milk is a drink.'), ('What does hungry mean?', 'Wanting food', 'Wanting sleep', 'Wanting to travel', 'Feeling cold', 'A', 'Hungry means wanting food.'), ('Choose the correct sentence.', 'I am hunger.', 'I am hungry.', 'I have hungry.', 'I hungry am.', 'B', "Hungry is an adjective, so use 'am hungry'."), ('Which sentence is a polite way to ask for water?', 'Give water.', 'Water now.', 'Can I have some water, please?', 'You give me water.', 'C', 'Can I have...? with please is a polite request.'), ('What does thirsty mean?', 'Wanting food', 'Wanting a drink', 'Feeling tired', 'Feeling happy', 'B', 'Thirsty means wanting a drink.'), ('Which meal is usually eaten in the morning?', 'Dinner', 'Lunch', 'Breakfast', 'Snack', 'C', 'Breakfast is usually the first meal of the day.'), ('Choose the correct sentence.', 'I like tea.', 'I tea like.', 'I liking tea.', 'I am like tea.', 'A', 'The correct word order is subject + verb + object.'), ('What is a menu?', 'A type of food', 'A list of food and drinks', 'A kitchen', 'A restaurant worker', 'B', 'A menu lists the food and drinks available.'), ('Complete the sentence: I would ___ a sandwich, please.', 'like', 'likes', 'liking', 'liked', 'A', "Use the base form 'like' after would."), ('What can you say when you have finished ordering?', 'Anything else?', "That's all, thank you.", 'Give me menu.', 'I am order.', 'B', "That's all, thank you indicates you have finished ordering.")]}, {'stage': 2, 'topic': 4, 'title': 'Likes & Dislikes - Test', 'questions': [('Choose the correct sentence.', 'I like music.', 'I liking music.', 'I likes music.', 'I am like music.', 'A', "Use the base verb 'like' with I."), ('Which sentence shows that you do not like something?', 'I love coffee.', 'I enjoy coffee.', "I don't like coffee.", 'I prefer coffee.', 'C', "I don't like expresses a dislike."), ('Complete the sentence: Do you ___ cricket?', 'likes', 'like', 'liking', 'liked', 'B', 'Use the base verb after do.'), ("What is the best answer to: 'Do you like pizza?'", 'Yes, I do.', 'Yes, I am.', 'Yes, I like.', 'Yes, I does.', 'A', 'The correct short answer to Do you...? is Yes, I do.'), ('Complete the sentence: My ___ food is biryani.', 'like', 'favourite', 'liking', 'enjoy', 'B', 'Favourite describes the thing you like most.'), ('Which word is used to give a reason?', 'But', 'Because', 'And', 'Or', 'B', 'Because introduces a reason.'), ('Choose the correct sentence.', 'I like English because it is interesting.', 'I like English because is interesting.', 'I English like because interesting.', 'I liking English because it interesting.', 'A', 'A complete clause follows because.'), ("Someone says, 'I love cricket.' What can you say if you also love cricket?", 'Not me.', 'Me too!', "I don't.", 'Never.', 'B', 'Me too shows that you share the same preference.'), ("Which word means 'to like one thing more than another'?", 'Hate', 'Prefer', 'Dislike', 'Order', 'B', 'Prefer means to like one option more than another.'), ('Which sentence expresses a strong dislike?', 'I like coffee.', 'I enjoy coffee.', 'I prefer coffee.', 'I hate coffee.', 'D', 'Hate expresses a strong dislike.')]}, {'stage': 2, 'topic': 5, 'title': 'Everyday Activities - Test', 'questions': [('Choose the correct sentence.', 'I studies every day.', 'I study every day.', 'I studying every day.', 'I am study every day.', 'B', 'Use the base verb with I.'), ('Complete the sentence: She ___ to college every day.', 'go', 'going', 'goes', 'gone', 'C', 'Use goes with she in the simple present.'), ("Which activity means 'to rest and feel comfortable'?", 'Study', 'Work', 'Relax', 'Travel', 'C', 'Relax means to rest and become comfortable.'), ('Complete the sentence: I exercise ___ the morning.', 'on', 'in', 'at', 'from', 'B', 'Use in with parts of the day, such as in the morning.'), ("Which word means 'most of the time'?", 'Never', 'Sometimes', 'Usually', 'Rarely', 'C', 'Usually means most of the time.'), ('Choose the correct sentence.', 'He play cricket.', 'He plays cricket.', 'He playing cricket.', 'He is play cricket.', 'B', 'Add -s to the verb with he in the simple present.'), ('Which sentence talks about free time?', 'I attend my class.', 'I work at 9 AM.', 'I watch movies in my free time.', 'I take an exam.', 'C', 'Free time is time when you are not busy with work or study.'), ('Complete the sentence: I ___ watch movies on weekends.', 'sometimes', 'sometime', 'some', 'any', 'A', 'Sometimes is an adverb of frequency.'), ('Which sentence is correct?', 'I read books at night.', 'I reads books at night.', 'I reading books at night.', 'I am read books at night.', 'A', 'Use the base verb with I.'), ('What does never mean?', 'Every day', 'Most of the time', 'Sometimes', 'Not at any time', 'D', 'Never means not at any time.')]}, {'stage': 3, 'topic': 1, 'title': 'Describing People - Test', 'questions': [('Which word describes height?', 'Friendly', 'Tall', 'Funny', 'Honest', 'B', "Tall describes a person's height."), ('Choose the correct sentence.', 'He tall.', 'He has tall.', 'He is tall.', 'He tall is.', 'C', 'Use is before an adjective describing a person.'), ('Complete the sentence: She ___ long black hair.', 'is', 'has', 'have', 'having', 'B', 'Use has with she to describe something she possesses.'), ('Which word describes personality?', 'Curly', 'Tall', 'Friendly', 'Brown', 'C', 'Friendly describes personality.'), ('Choose the correct sentence.', 'She is long hair.', 'She has long hair.', 'She have long hair.', 'She long hair has.', 'B', 'Use has to describe hair.'), ('What does confident mean?', 'Believing in yourself', 'Being very tired', 'Being very young', 'Having curly hair', 'A', 'Confident means believing in your abilities.'), ('Which sentence is correct?', 'He has friendly.', 'He is friendly.', 'He friendly has.', 'He friendly is.', 'B', 'Use is before the adjective friendly.'), ('Which word describes hair?', 'Helpful', 'Honest', 'Curly', 'Confident', 'C', 'Curly describes the shape or texture of hair.'), ('Complete the sentence: My brother is tall and ___.', 'black hair', 'friendly', 'has hair', 'hair', 'B', 'Friendly is an adjective that can describe a person.'), ('Which sentence gives a complete description?', 'He is.', 'He has.', 'He is tall and friendly.', 'He tall.', 'C', 'This sentence gives two complete descriptions.')]}, {'stage': 3, 'topic': 2, 'title': 'Describing Places - Test', 'questions': [('Which word means full of people?', 'Empty', 'Crowded', 'Quiet', 'Small', 'B', 'Crowded means full of people.'), ('Complete the sentence: There ___ a library in my college.', 'are', 'am', 'is', 'be', 'C', 'Use there is with a singular noun.'), ('Complete the sentence: There ___ many classrooms in the building.', 'is', 'are', 'am', 'be', 'B', 'Use there are with a plural noun.'), ('Which word means close to something?', 'Far', 'Behind', 'Near', 'Opposite', 'C', 'Near means close to something.'), ('Choose the correct sentence.', 'The park are beautiful.', 'The park is beautiful.', 'The park beautiful is.', 'The park be beautiful.', 'B', 'Use is with the singular subject the park.'), ('The café is ___ the bank and the hotel.', 'between', 'behind', 'near', 'under', 'A', 'Between describes a position separating two things.'), ('Which word describes a place with little or no noise?', 'Crowded', 'Noisy', 'Quiet', 'Dirty', 'C', 'Quiet means having little or no noise.'), ('Choose the correct sentence.', 'There is two bedrooms.', 'There are two bedrooms.', 'There am two bedrooms.', 'There be two bedrooms.', 'B', 'Use there are with the plural noun bedrooms.'), ('Which sentence correctly describes a place?', 'My college is large and modern.', 'My college large and modern.', 'My college are large.', 'My college has large.', 'A', 'Use is before adjectives describing a singular place.'), ('What does spacious mean?', 'Very noisy', 'Having plenty of space', 'Very old', 'Full of people', 'B', 'Spacious means having plenty of space.')]}, {'stage': 3, 'topic': 3, 'title': 'Making Requests - Test', 'questions': [('Which is the most polite request?', 'Give me water.', 'Water.', 'Could you give me some water, please?', 'I want water.', 'C', 'Could you...? with please makes a polite request.'), ('Complete the sentence: Can I ___ your pen, please?', 'use', 'uses', 'using', 'used', 'A', 'Use the base verb after can.'), ('Which sentence asks someone to help you?', 'Can you help me?', 'I help you.', 'You help me.', 'I can helping you.', 'A', 'Can you...? is used to make a request.'), ('Which is more formal?', 'Can I come in?', 'May I come in?', 'Come in?', 'I come in?', 'B', 'May I...? is a more formal way to ask permission.'), ('What does please do in a request?', 'Makes it longer', 'Makes it more polite', 'Makes it negative', 'Changes it into a question', 'B', 'Please makes a request more polite.'), ('Complete the sentence: Could you ___ that again, please?', 'repeat', 'repeats', 'repeating', 'repeated', 'A', 'Use the base verb after could.'), ("Someone asks, 'Can you help me?' Which is a suitable positive response?", 'Sure.', 'Never.', 'No, I am.', 'I help', 'A', 'Sure is a natural positive response.'), ('Which sentence asks for permission?', 'Can I use your phone?', 'Use your phone.', 'You use my phone.', 'I use your phone.', 'A', 'Can I...? asks for permission.'), ('Which sentence is correct?', 'Could you opening the door?', 'Could you open the door, please?', 'Could you opened the door?', 'Could you opens the door?', 'B', 'Use the base verb after could.'), ('What does permission mean?', 'A request for help', 'Approval to do something', 'A type of question', 'An explanation', 'B', 'Permission is approval to do something.')]}, {'stage': 3, 'topic': 4, 'title': 'Shopping and Prices - Test', 'questions': [('Which question asks about the price of one item?', 'How many is this?', 'How much is this?', 'How much are this?', 'What price this?', 'B', 'Use How much is...? to ask the price of one item.'), ('Complete the sentence: How much ___ these shoes?', 'is', 'am', 'are', 'be', 'C', 'Use are with the plural noun shoes.'), ('What does expensive mean?', 'Costing very little', 'Costing a lot of money', 'Having a small size', 'Having a low quantity', 'B', 'Expensive means costing a lot of money.'), ('Which sentence asks for another colour?', 'What size is this?', 'Do you have this in blue?', 'How much is this?', 'Can I pay by card?', 'B', 'This question asks whether another colour is available.'), ('Complete the sentence: I would like one ___ of apples.', 'pair', 'kilo', 'bottle', 'piece', 'B', 'A kilo is a common unit for buying apples.'), ('Which person buys something from a shop?', 'Customer', 'Shopkeeper', 'Teacher', 'Driver', 'A', 'A customer is a person who buys goods or services.'), ('What does change mean when shopping?', 'A different product', 'Money returned after payment', 'A new shop', 'A different size', 'B', 'Change is money returned when you pay more than the price.'), ('Choose the correct sentence.', 'How much is these shoes?', 'How much are these shoes?', 'How many are these shoes?', 'How price these shoes?', 'B', 'Use are with the plural noun shoes.'), ('Which sentence asks about payment?', 'What size is this?', 'Do you have another one?', 'Can I pay by card?', 'How much is this?', 'C', 'Can I pay by card asks about the payment method.'), ('What does cheap mean?', 'Costing a lot', 'Costing very little', 'Very large', 'Very heavy', 'B', 'Cheap means costing relatively little.')]}, {'stage': 3, 'topic': 5, 'title': 'Directions and Locations - Test', 'questions': [("Which phrase means 'continue in the same direction'?", 'Turn left', 'Go straight', 'Turn right', 'Go back', 'B', 'Go straight means continue in the same direction.'), ('Which is a polite way to ask for directions?', 'Where bank?', 'Give me the way.', 'Excuse me, where is the bank?', 'Bank where?', 'C', 'Excuse me is a polite way to begin asking for directions.'), ('What does turn left mean?', 'Continue straight', 'Change direction to the left', 'Go backwards', 'Stop walking', 'B', 'Turn left means change direction to the left.'), ('Complete the sentence: The café is ___ the bank and the hotel.', 'between', 'straight', 'turn', 'cross', 'A', 'Between describes a place in the middle of two places.'), ('Which place can be used as a landmark?', 'Hospital', 'Quickly', 'Happy', 'Tall', 'A', 'A hospital is a recognizable place that can help someone navigate.'), ('What does opposite mean?', 'Very far away', 'Directly across from something', 'Behind something', 'Inside something', 'B', 'Opposite means directly across from something.'), ("Choose the correct direction: 'Turn ___ at the traffic light.'", 'straight', 'left', 'nearby', 'between', 'B', 'Left completes the direction instruction.'), ('What does cross the road mean?', 'Walk along the same side', 'Move from one side of the road to the other', 'Stop near the road', 'Turn around', 'B', 'Cross the road means move from one side to the other.'), ('Complete the sentence: The school is ___ the park.', 'opposite', 'turn', 'straight', 'cross', 'A', "Opposite describes the school's location across from the park."), ('Which response is suitable after someone gives you directions?', "You're directions.", 'Thank you!', 'Where?', 'Turn right!', 'B', 'Thank you is a polite response after receiving help.')]}]


class Command(BaseCommand):
    help = "Seed the eight remaining Beginner lesson tests (80 MCQs)."

    @transaction.atomic
    def handle(self, *args, **options):
        created_quizzes = 0
        reused_quizzes = 0
        created_questions = 0
        existing_questions = 0

        for test_data in BEGINNER_TESTS:
            try:
                lesson = Lesson.objects.get(
                    level__iexact="beginner",
                    stage_number=test_data["stage"],
                    topic_number=test_data["topic"],
                )
            except Lesson.DoesNotExist:
                raise CommandError(
                    "Could not find Beginner lesson at "
                    f"Stage {test_data['stage']}, Level {test_data['topic']}. "
                    "Check the lesson's level, stage_number and topic_number in Admin."
                )
            except Lesson.MultipleObjectsReturned:
                raise CommandError(
                    "More than one Beginner lesson matches "
                    f"Stage {test_data['stage']}, Level {test_data['topic']}."
                )

            quizzes = Quiz.objects.filter(lesson=lesson)
            if quizzes.count() > 1:
                raise CommandError(
                    f"More than one quiz exists for '{lesson.title}'. "
                    "Please resolve this in Admin before running the seed command."
                )

            quiz = quizzes.first()
            if quiz is None:
                quiz = Quiz.objects.create(
                    lesson=lesson,
                    title=test_data["title"],
                    description=f"10-question test for {lesson.title}.",
                )
                created_quizzes += 1
            else:
                # Preserve an existing quiz and its content; only add missing
                # questions from this source document.
                reused_quizzes += 1

            for question in test_data["questions"]:
                question_text, option_a, option_b, option_c, option_d, answer, explanation = question

                if answer not in ("A", "B", "C", "D"):
                    raise CommandError(f"Invalid answer key: {answer}")

                _, was_created = Question.objects.get_or_create(
                    quiz=quiz,
                    question_text=question_text,
                    defaults={
                        "option_a": option_a,
                        "option_b": option_b,
                        "option_c": option_c,
                        "option_d": option_d,
                        "correct_answer": answer,
                        "explanation": explanation,
                    },
                )

                if was_created:
                    created_questions += 1
                else:
                    existing_questions += 1

        self.stdout.write(self.style.SUCCESS("Beginner Phase 1 seeding completed."))
        self.stdout.write(f"New quizzes created: {created_quizzes}")
        self.stdout.write(f"Existing quizzes reused: {reused_quizzes}")
        self.stdout.write(f"New questions created: {created_questions}")
        self.stdout.write(f"Matching questions already present: {existing_questions}")

        self.stdout.write("\\nBeginner test overview:")
        for test_data in BEGINNER_TESTS:
            lesson = Lesson.objects.get(
                level__iexact="beginner",
                stage_number=test_data["stage"],
                topic_number=test_data["topic"],
            )
            quiz = Quiz.objects.filter(lesson=lesson).first()
            count = quiz.questions.count() if quiz else 0
            self.stdout.write(
                f"Stage {test_data['stage']} Level {test_data['topic']} - "
                f"{lesson.title}: {count} questions"
            )
