"""
Fluent AI Practice Hub seed data (90 starter questions).

Save this file as:
    learning/management/commands/seed_practicehub.py

Create __init__.py in both management/ and commands/ if they do not exist.
Then run from the folder containing manage.py:
    python manage.py seed_practicehub

Safe to rerun: matching questions are updated instead of duplicated.
These are practice examples, not real-student training data.
"""
from django.core.management.base import BaseCommand
from learning.models import PracticeQuestion

# Each entry:
# (category, question_type, question_text, option_a, option_b,
#  option_c, option_d, correct_answer, explanation)
QUESTION_BANK = [
    # GRAMMAR — SPOT THE ERROR
    ("grammar","spot_error","Correct: She go to college every day.","","","","","She goes to college every day.","Use -s/-es with he, she, or it in the simple present."),
    ("grammar","spot_error","Correct: They was playing football.","","","","","They were playing football.","Use 'were' with they."),
    ("grammar","spot_error","Correct: I have saw that movie.","","","","","I have seen that movie.","Use the past participle after have."),
    ("grammar","spot_error","Correct: He is senior than me.","","","","","He is senior to me.","Senior is followed by 'to'."),
    ("grammar","spot_error","Correct: She did not went to class.","","","","","She did not go to class.","Use the base verb after did not."),
    ("grammar","spot_error","Correct: There are a book on the table.","","","","","There is a book on the table.","Use 'is' with a singular noun."),
    ("grammar","spot_error","Correct: Each student have a notebook.","","","","","Each student has a notebook.","Each takes a singular verb."),
    ("grammar","spot_error","Correct: I am living here since 2020.","","","","","I have been living here since 2020.","Use present perfect continuous for an action continuing since a past time."),
    ("grammar","spot_error","Correct: She is more taller than her sister.","","","","","She is taller than her sister.","Do not use 'more' with 'taller'."),
    ("grammar","spot_error","Correct: If I will see him, I will tell him.","","","","","If I see him, I will tell him.","Use present simple in the first conditional if-clause."),
    # GRAMMAR — MCQ
    ("grammar","mcq","Choose the correct sentence.","She don't like tea.","She doesn't likes tea.","She doesn't like tea.","She not like tea.","C","Doesn't is followed by the base verb."),
    ("grammar","mcq","They _____ finished their homework.","has","have","is","was","B","Use 'have' with they."),
    ("grammar","mcq","I have lived here _____ five years.","since","from","for","during","C","'For' is used with a duration."),
    ("grammar","mcq","She ate _____ apple.","a","an","the","no article","B","Use 'an' before a vowel sound."),
    ("grammar","mcq","Neither of the answers _____ correct.","are","were","is","be","C","'Neither' is singular in this construction."),
    ("grammar","mcq","If it rains, we _____ at home.","stayed","will stay","would stayed","staying","B","First conditional: if + present, will + verb."),
    ("grammar","mcq","She is interested _____ learning French.","on","at","in","for","C","The phrase is 'interested in'."),
    ("grammar","mcq","By the time we arrived, the film _____.","starts","has started","had started","will start","C","Past perfect marks the earlier past action."),
    ("grammar","mcq","This gift is for you and _____.","I","me","my","mine","B","Use the object pronoun after 'for'."),
    ("grammar","mcq","There isn't _____ milk left.","many","few","much","several","C","Milk is uncountable."),
    # GRAMMAR — ONE WORD
    ("grammar","one_word","Give the adverb meaning 'in a careful manner'.","","","","","carefully","Carefully describes how an action is done."),
    ("grammar","one_word","What is the past tense of teach?","","","","","taught","Teach, taught, taught."),
    ("grammar","one_word","What is the past participle of write?","","","","","written","Write, wrote, written."),
    ("grammar","one_word","Give the comparative form of good.","","","","","better","Good has the irregular comparative 'better'."),
    ("grammar","one_word","Give the superlative form of bad.","","","","","worst","Bad has the irregular superlative 'worst'."),
    ("grammar","one_word","What is the plural of child?","","","","","children","Child has the irregular plural 'children'."),
    ("grammar","one_word","What is the noun form of decide?","","","","","decision","Decision is the noun form."),
    ("grammar","one_word","What is the adjective form of beauty?","","","","","beautiful","Beautiful is the adjective form."),
    ("grammar","one_word","What is the contraction of they are?","","","","","they're","They're means they are."),
    ("grammar","one_word","What is the past tense of bring?","","","","","brought","Bring, brought, brought."),
    # VOCABULARY — SPOT THE ERROR
    ("vocabulary","spot_error","Replace the wrong word: The medicine had a positive affect on her health.","","","","","The medicine had a positive effect on her health.","Effect is a noun; affect is usually a verb."),
    ("vocabulary","spot_error","Replace the wrong word: Please give me some advise.","","","","","Please give me some advice.","Advice is a noun; advise is a verb."),
    ("vocabulary","spot_error","Replace the wrong word: The rule will not effect my schedule.","","","","","The rule will not affect my schedule.","Affect is the verb meaning influence."),
    ("vocabulary","spot_error","Replace the wrong word: Their going to arrive at noon.","","","","","They're going to arrive at noon.","They're means they are."),
    ("vocabulary","spot_error","Replace the wrong word: I bought stationary for my notebook.","","","","","I bought stationery for my notebook.","Stationery means writing materials."),
    ("vocabulary","spot_error","Replace the wrong word: Honesty is an important principal.","","","","","Honesty is an important principle.","Principle means a rule or belief."),
    ("vocabulary","spot_error","Replace the wrong word: The weather had a great affect on travel.","","","","","The weather had a great effect on travel.","Effect is the noun."),
    ("vocabulary","spot_error","Replace the wrong word: The scarf compliments her outfit well.","","","","","The scarf complements her outfit well.","Complement means to go well with."),
    ("vocabulary","spot_error","Replace the wrong word: We must insure that everyone gets a copy.","","","","","We must ensure that everyone gets a copy.","Ensure means make certain."),
    ("vocabulary","spot_error","Replace the wrong word: He was stationary about the private information.","","","","","He was discreet about the private information.","Discreet means careful about keeping information private."),
    # VOCABULARY — MCQ
    ("vocabulary","mcq","Choose the synonym of rapid.","Slow","Quick","Weak","Quiet","B","Rapid means fast or quick."),
    ("vocabulary","mcq","Choose the antonym of generous.","Kind","Giving","Selfish","Helpful","C","Selfish is an antonym of generous."),
    ("vocabulary","mcq","What does reluctant mean?","Very excited","Unwilling or hesitant","Extremely tired","Highly skilled","B","Reluctant means unwilling or hesitant."),
    ("vocabulary","mcq","Choose the closest meaning of concise.","Brief","Confusing","Lengthy","Careless","A","Concise means brief but clear."),
    ("vocabulary","mcq","What does fragile mean?","Easily broken","Very expensive","Extremely large","Hard to find","A","Fragile means easily damaged."),
    ("vocabulary","mcq","Choose the antonym of ancient.","Historic","Old","Modern","Traditional","C","Modern is the opposite of ancient."),
    ("vocabulary","mcq","A person who writes poems is a _____.","Novelist","Poet","Editor","Reporter","B","A poet writes poems."),
    ("vocabulary","mcq","What does meticulous mean?","Careless","Very careful about details","Often late","Easily angered","B","Meticulous means precise and detail-oriented."),
    ("vocabulary","mcq","Choose the synonym of assist.","Help","Avoid","Delay","Refuse","A","Assist means help."),
    ("vocabulary","mcq","If a task is mandatory, it is _____.","Optional","Forbidden","Required","Unusual","C","Mandatory means required."),
    # VOCABULARY — ONE WORD
    ("vocabulary","one_word","One word for a person who speaks two languages.","","","","","bilingual","Bilingual means able to use two languages."),
    ("vocabulary","one_word","One word for a person who loves books.","","","","","bibliophile","A bibliophile loves books."),
    ("vocabulary","one_word","A word with the opposite meaning of another word.","","","","","antonym","An antonym has an opposite meaning."),
    ("vocabulary","one_word","A word with the same or similar meaning as another word.","","","","","synonym","A synonym has a similar meaning."),
    ("vocabulary","one_word","Something suitable to be eaten.","","","","","edible","Edible means suitable to eat."),
    ("vocabulary","one_word","Unable to read or write.","","","","","illiterate","Illiterate means unable to read and write."),
    ("vocabulary","one_word","Something that happens every year.","","","","","annual","Annual means yearly."),
    ("vocabulary","one_word","A building where aircraft are kept.","","","","","hangar","A hangar houses aircraft."),
    ("vocabulary","one_word","A person who studies stars and planets.","","","","","astronomer","An astronomer studies celestial objects."),
    ("vocabulary","one_word","A word meaning done without preparation.","","","","","impromptu","Impromptu means without preparation."),
    # CONVERSATIONS — SPOT THE ERROR
    ("conversations","spot_error","Correct this polite request: Can you to help me, please?","","","","","Can you help me, please?","Use the base verb after can."),
    ("conversations","spot_error","Correct: I am agree with your suggestion.","","","","","I agree with your suggestion.","Agree is a verb; do not add am."),
    ("conversations","spot_error","Correct: Could you tell me where is the station?","","","","","Could you tell me where the station is?","Indirect questions use statement word order."),
    ("conversations","spot_error","Correct: I look forward to meet you.","","","","","I look forward to meeting you.","Look forward to is followed by a noun or -ing form."),
    ("conversations","spot_error","Correct: Thank you for invite me.","","","","","Thank you for inviting me.","Use the -ing form after the preposition for."),
    ("conversations","spot_error","Correct: Would you mind to open the window?","","","","","Would you mind opening the window?","Would you mind is followed by -ing."),
    ("conversations","spot_error","Correct: I didn't understood what you said.","","","","","I didn't understand what you said.","Use the base verb after didn't."),
    ("conversations","spot_error","Correct: Could you repeat again, please?","","","","","Could you repeat that, please?","Repeat already means say again."),
    ("conversations","spot_error","Correct: I am looking forward to hear from you.","","","","","I am looking forward to hearing from you.","Use -ing after look forward to."),
    ("conversations","spot_error","Correct: May I know what time does the meeting start?","","","","","May I know what time the meeting starts?","Indirect questions use statement word order."),
    # CONVERSATIONS — MCQ
    ("conversations","mcq","Someone says 'How are you?' Choose a natural reply.","I am fine, thank you. How about you?","I am 20 years.","Yes, I do.","At the station.","A","A polite reply answers and may ask back."),
    ("conversations","mcq","How can you politely ask someone to repeat something?","Say it again now.","Could you repeat that, please?","What?","You spoke wrong.","B","Could you ... please is a polite request."),
    ("conversations","mcq","Choose the most appropriate way to ask for directions.","Tell me road.","Where road?","Excuse me, could you tell me how to get to the library?","You must show library.","C","Begin politely and ask a complete question."),
    ("conversations","mcq","A colleague helps you. What should you say?","Never mind you.","Thanks for your help; I appreciate it.","You have to help.","No, thanks you.","B","Express gratitude politely."),
    ("conversations","mcq","You did not hear a name clearly. Best response?","Your name is unclear.","Speak louder!","Sorry, could you tell me your name again?","I don't care.","C","A brief apology and polite request are appropriate."),
    ("conversations","mcq","How should you politely disagree?","You are stupid.","I see your point, but I have a different view.","That is nonsense.","Stop talking.","B","Acknowledge the other view respectfully."),
    ("conversations","mcq","Choose a suitable formal email sign-off.","Later!","Bye bye dude.","Yours sincerely,","See ya maybe.","C","Yours sincerely is suitable for formal correspondence."),
    ("conversations","mcq","You arrive late to a meeting. What is appropriate?","Sorry I'm late; thank you for waiting.","You started too early.","It doesn't matter.","Why are you here?","A","Acknowledge the delay and thank others."),
    ("conversations","mcq","How can you ask for clarification in a meeting?","That makes no sense.","Could you clarify what you mean by that?","I refuse to listen.","Talk properly.","B","Ask a neutral, polite clarification question."),
    ("conversations","mcq","You cannot attend an invitation. Choose a polite reply.","Don't ask again.","I won't come, obviously.","Thank you for inviting me, but I can't make it this time.","Your plan is bad.","C","Thank the person and decline respectfully."),
    # CONVERSATIONS — ONE WORD
    ("conversations","one_word","A word used to express gratitude.","","","","","thanks","Thanks is a common expression of gratitude."),
    ("conversations","one_word","A formal expression of regret for a mistake.","","","","","apology","An apology expresses regret."),
    ("conversations","one_word","A suggestion or recommendation.","","","","","advice","Advice is a recommendation."),
    ("conversations","one_word","A spoken exchange between two or more people.","","","","","dialogue","Dialogue is a conversation between people."),
    ("conversations","one_word","Describes respectful and considerate language.","","","","","polite","Polite means respectful."),
    ("conversations","one_word","A meeting arranged for a particular time.","","","","","appointment","An appointment is an arranged meeting."),
    ("conversations","one_word","A response to a question.","","","","","answer","An answer responds to a question."),
    ("conversations","one_word","A courteous act of asking someone to do something.","","","","","request","A request asks for something."),
    ("conversations","one_word","The act of presenting one person to another.","","","","","introduction","An introduction presents someone or something."),
    ("conversations","one_word","A person's opportunity to speak in a conversation.","","","","","turn","Conversation partners take turns."),
]


class Command(BaseCommand):
    help = "Add or update the 90 Fluent AI Practice Hub starter questions"

    def handle(self, *args, **options):
        created = 0
        updated = 0

        for row in QUESTION_BANK:
            (category, question_type, question_text, option_a, option_b,
             option_c, option_d, correct_answer, explanation) = row

            _, was_created = PracticeQuestion.objects.update_or_create(
                category=category,
                question_type=question_type,
                question_text=question_text,
                defaults={
                    "option_a": option_a,
                    "option_b": option_b,
                    "option_c": option_c,
                    "option_d": option_d,
                    "correct_answer": correct_answer,
                    "explanation": explanation,
                    "is_active": True,
                },
            )
            if was_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(self.style.SUCCESS(
            f"Practice Hub seed complete. Created: {created}; updated: {updated}."
        ))
        self.stdout.write(f"Questions in seed: {len(QUESTION_BANK)}")
        for category in ("grammar", "vocabulary", "conversations"):
            for question_type in ("spot_error", "mcq", "one_word"):
                count = PracticeQuestion.objects.filter(
                    category=category,
                    question_type=question_type,
                    is_active=True,
                ).count()
                self.stdout.write(f"{category} / {question_type}: {count} active question(s)")
