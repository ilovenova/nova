"""
brain.py

NOVA's response engine.

Handles:
- conversation routing
- feelings
- structured follow-up context
- memory recall
- memory forgetting
- conversation context
- time and date
"""

from datetime import datetime
import random
import re

from personality import Personality
from learning import Learning
from identity import Identity
from habits import Habits
from social import Social
from activity import Activity
from context import Context
from relationships import Relationships
from world_learning import WorldLearning
from conversation import Conversation
from emotions import Emotions
from memory_editor import MemoryEditor
from reflection import Reflection
from understanding import Understanding
from recent_memory import RecentMemory


class Brain:

    def __init__(self, memory):

        self.memory = memory
        self.personality = Personality(memory)
        self.learning = Learning(memory)
        self.identity = Identity(memory)
        self.habits = Habits(memory)
        self.social = Social(memory)
        self.activity = Activity(memory)
        self.context = Context(memory)
        self.relationships = Relationships(memory)
        self.world_learning = WorldLearning(memory)
        self.conversation = Conversation(memory)
        self.emotions = Emotions(memory)
        self.memory_editor = MemoryEditor(memory)
        self.reflection = Reflection(memory)
        self.understanding = Understanding(memory)
        self.recent_memory = RecentMemory()

        self.last_user_message = ""
        self.last_nova_reply = ""

        self.pending_follow_up = None

    # -------------------------------------------------
    # Main response router
    # -------------------------------------------------
    
    def respond(self, message):

        text = message.lower().strip()

        self.recent_memory.record_user(
            message
        )

        recent_memory_reply = (
            self.recent_memory.answer_recent_question(
                message,
                text
            )
        )

        if recent_memory_reply:

            return self.finish(
                message,
                recent_memory_reply
            )

        self.context.observe(message, text)

        context_result = self.context.respond(
            message,
            text,
            self.pending_follow_up,
            self.activity,
            self.social,
            self.relationships,
            self.world_learning,
            self.conversation
        )

        if context_result:

            if context_result.get(
                "clear_pending",
                False
            ):
                self.pending_follow_up = None

            next_follow_up = context_result.get(
                "next_follow_up"
            )

            if next_follow_up is not None:
                self.pending_follow_up = next_follow_up

            if not context_result.get(
                "continue_routing",
                False
            ):
                return self.finish(
                    message,
                    context_result.get("reply", "")
                )

        understanding_result = self.understanding.respond(
            message,
            text
        )

        if understanding_result:

            self.pending_follow_up = understanding_result.get(
                "follow_up"
            )

            return self.finish(
                message,
                understanding_result.get("reply", "")
            )

        if (
            self.pending_follow_up
            and self.pending_follow_up.get("kind")
            == "reflection"
        ):

            result = self.reflection.answer_follow_up(
                message,
                self.pending_follow_up
            )

            if result:

                self.pending_follow_up = result.get(
                    "follow_up"
                )

                return self.finish(
                    message,
                    result.get("reply", "")
                )

        reflection_result = self.reflection.respond(
            message,
            text
        )

        if reflection_result:

            self.pending_follow_up = reflection_result.get(
                "follow_up"
            )

            return self.finish(
                message,
                reflection_result.get("reply", "")
            )

        memory_edit_result = self.memory_editor.respond(
            message,
            text
        )

        if memory_edit_result:

            self.pending_follow_up = memory_edit_result.get(
                "follow_up"
            )

            return self.finish(
                message,
                memory_edit_result.get("reply", "")
            )

        if (
            self.pending_follow_up
            and self.pending_follow_up.get("kind")
            == "emotion_thread"
        ):

            result = self.emotions.answer_follow_up(
                message,
                self.pending_follow_up
            )

            if result:

                self.pending_follow_up = result.get(
                    "follow_up"
                )

                return self.finish(
                    message,
                    result.get("reply", "")
                )

        emotion_result = self.emotions.respond(
            message,
            text
        )

        if emotion_result:

            self.pending_follow_up = emotion_result.get(
                "follow_up"
            )

            return self.finish(
                message,
                emotion_result.get("reply", "")
            )

        relationship_result = self.relationships.respond(
            message,
            text
        )

        if relationship_result:

            reply = relationship_result.get(
                "reply",
                ""
            )

            self.pending_follow_up = relationship_result.get(
                "follow_up"
            )

            return self.finish(message, reply)

        conversation_result = self.conversation.respond(
            message,
            text
        )

        if conversation_result:

            reply = conversation_result.get(
                "reply",
                ""
            )

            self.pending_follow_up = conversation_result.get(
                "follow_up"
            )

            return self.finish(message, reply)

        social_result = self.social.respond(
            message,
            text
        )

        if social_result:

            reply = social_result.get(
                "reply",
                ""
            )

            self.pending_follow_up = social_result.get(
                "follow_up"
            )

            return self.finish(message, reply)

        activity_result = self.activity.respond(
            message,
            text
        )

        if activity_result:

            reply = activity_result.get(
                "reply",
                ""
            )

            self.pending_follow_up = activity_result.get(
                "follow_up"
            )

            return self.finish(message, reply)

        response = self.identity.respond(
            message,
            text
        )

        if response:
            self.pending_follow_up = None
            return self.finish(message, response)

        response = self.check_greeting(text)

        if response:
            return self.finish(message, response)

        response = self.check_direct_requests(text)

        if response:
            self.pending_follow_up = None
            return self.finish(message, response)

        response = self.check_forget_request(
            message,
            text
        )

        if response:
            self.pending_follow_up = None
            return self.finish(message, response)

        response = self.check_specific_memory_question(
            text
        )

        if response:
            self.pending_follow_up = None
            return self.finish(message, response)

        response = self.check_feeling(text)

        if response:
            return self.finish(message, response)

        response = self.check_success(text)

        if response:
            return self.finish(message, response)

        if self.pending_follow_up:

            if self.is_clear_new_topic(text):

                self.pending_follow_up = None

            elif self.is_meaningful_answer(text):

                response = self.check_follow_up_answer(
                    message
                )

                if response:
                    return self.finish(message, response)

            else:

                self.pending_follow_up = None

                response = random.choice([
                    "I'm not sure I understood that. You can say it another way, or we can leave it there.",
                    "I didn't quite catch what you meant.",
                    "That one lost me a little. Try saying it differently?",
                    "I'm not sure that answered what I asked, but that's okay."
                ])

                return self.finish(message, response)

        world_result = self.world_learning.respond(
            message,
            text
        )

        if world_result:

            reply = world_result.get(
                "reply",
                ""
            )

            self.pending_follow_up = world_result.get(
                "follow_up"
            )

            return self.finish(message, reply)

        learning_result = self.learning.learn(message)

        if learning_result:

            reply = learning_result.get(
                "reply",
                ""
            )

            self.pending_follow_up = learning_result.get(
                "follow_up"
            )

            return self.finish(message, reply)

        response = self.check_memory_summary(text)

        if response:
            return self.finish(message, response)

        response = self.check_conversation_context(text)

        if response:
            return self.finish(message, response)

        response = random.choice([
            "I'm not completely sure how to respond to that yet, but I'm listening.",
            "I understand some of that, but I haven't learned the best response yet.",
            "Hmm... I'm still figuring out messages like that.",
            "I'm not sure what you need from me there, but you can tell me more."
        ])

        return self.finish(message, response)

    # -------------------------------------------------
    # Save current conversation context
    # -------------------------------------------------

    def finish(self, message, reply):

        reply = self.habits.apply(
            message,
            reply
        )

        self.last_user_message = message
        self.last_nova_reply = reply

        self.recent_memory.record_nova(
            reply
        )

        return reply

    # -------------------------------------------------
    # Greetings
    # -------------------------------------------------

    def check_greeting(self, text):

        greetings = [
            "hi",
            "hello",
            "hey",
            "hiya",
            "helo",
            "helloo",
            "hii"
        ]

        if text in greetings:
            return self.personality.greeting()

        return None

    # -------------------------------------------------
    # Direct requests
    # -------------------------------------------------

    def check_direct_requests(self, text):

        if text in [
            "what is your name",
            "what's your name",
            "who are you"
        ]:
            return "I'm NOVA."

        if text in [
            "what is my name",
            "what's my name"
        ]:

            name = self.memory.profile.get(
                "name",
                ""
            )

            if name:
                return f"Your name is {name}."

            return "You haven't told me your name yet."

        if text in [
            "what time is it",
            "tell me the time",
            "current time"
        ]:
            return datetime.now().strftime("%H:%M:%S")

        if text in [
            "what is the date",
            "what's the date",
            "tell me the date",
            "current date"
        ]:
            return datetime.now().strftime("%Y-%m-%d")

        return None

    # -------------------------------------------------
    # Specific memory questions
    # -------------------------------------------------

    def check_specific_memory_question(self, text):

        personal = self.memory.profile.get(
            "personal",
            {}
        )

        preferences = self.memory.profile.get(
            "preferences",
            {}
        )

        favourites = preferences.get(
            "favourites",
            {}
        )

        likes = preferences.get(
            "likes",
            []
        )

        dislikes = preferences.get(
            "dislikes",
            []
        )

        hobbies = preferences.get(
            "hobbies",
            []
        )

        if text in [
            "how old am i",
            "what is my age",
            "what's my age"
        ]:

            age = personal.get("age", "")

            if age:
                return f"You're {age} years old."

            return "You haven't told me your age yet."

        if text in [
            "when is my birthday",
            "what is my birthday",
            "what's my birthday"
        ]:

            birthday = personal.get(
                "birthday",
                ""
            )

            if birthday:
                return f"Your birthday is {birthday}."

            return "You haven't told me your birthday yet."

        if text in [
            "what is my school",
            "what's my school",
            "where do i go to school",
            "what school do i go to"
        ]:

            school = personal.get(
                "school",
                ""
            )

            if school:
                return f"You go to {school}."

            return "You haven't told me which school you go to."

        favourite_patterns = [
            r"^what is my favourite (.+?)[?]?$",
            r"^what's my favourite (.+?)[?]?$",
            r"^what is my favorite (.+?)[?]?$",
            r"^what's my favorite (.+?)[?]?$"
        ]

        for pattern in favourite_patterns:

            match = re.match(pattern, text)

            if match:

                category = match.group(1).strip()

                for saved_category, value in favourites.items():

                    if (
                        saved_category.lower()
                        == category.lower()
                    ):

                        return (
                            f"Your favourite {saved_category} "
                            f"is {value}."
                        )

                return (
                    "I don't remember your favourite "
                    f"{category} yet."
                )

        if text in [
            "what do i like",
            "what things do i like",
            "tell me what i like"
        ]:

            if likes:
                return (
                    "You like "
                    + self.natural_list(likes)
                    + "."
                )

            return "You haven't told me many things you like yet."

        if text in [
            "what do i dislike",
            "what don't i like",
            "what do i not like",
            "tell me what i dislike"
        ]:

            if dislikes:
                return (
                    "You don't like "
                    + self.natural_list(dislikes)
                    + "."
                )

            return "You haven't told me many things you dislike yet."

        if text in [
            "what are my hobbies",
            "what hobbies do i have",
            "tell me my hobbies"
        ]:

            if hobbies:
                return (
                    "Your hobbies include "
                    + self.natural_list(hobbies)
                    + "."
                )

            return "You haven't told me your hobbies yet."

        like_patterns = [
            r"^do i like (.+?)[?]?$",
            r"^did i say i like (.+?)[?]?$"
        ]

        for pattern in like_patterns:

            match = re.match(pattern, text)

            if match:

                item = match.group(1).strip()

                saved_like = self.find_in_list(
                    likes,
                    item
                )

                saved_dislike = self.find_in_list(
                    dislikes,
                    item
                )

                if saved_like:

                    return random.choice([
                        f"Yes — you told me you like {saved_like}.",
                        f"You do. {saved_like} is on your likes list.",
                        f"Yes, I remember that you enjoy {saved_like}."
                    ])

                if saved_dislike:

                    return random.choice([
                        f"No — you told me you don't like {saved_dislike}.",
                        f"Quite the opposite. {saved_dislike} is on your dislike list.",
                        f"No. I remember that {saved_dislike} isn't for you."
                    ])

                return (
                    "You haven't told me how you feel about "
                    f"{item} yet."
                )

        dislike_patterns = [
            r"^do i dislike (.+?)[?]?$",
            r"^do i hate (.+?)[?]?$",
            r"^did i say i dislike (.+?)[?]?$"
        ]

        for pattern in dislike_patterns:

            match = re.match(pattern, text)

            if match:

                item = match.group(1).strip()

                saved_dislike = self.find_in_list(
                    dislikes,
                    item
                )

                saved_like = self.find_in_list(
                    likes,
                    item
                )

                if saved_dislike:

                    return random.choice([
                        f"Yes — you told me you don't like {saved_dislike}.",
                        f"You do. {saved_dislike} is on your no-thank-you list.",
                        f"Yes, I remember that {saved_dislike} isn't for you."
                    ])

                if saved_like:

                    return random.choice([
                        f"No — you actually told me you like {saved_like}.",
                        f"No. {saved_like} is one of the things you enjoy.",
                        f"Quite the opposite — you said you like {saved_like}."
                    ])

                return (
                    "You haven't told me how you feel about "
                    f"{item} yet."
                )

        return None

    # -------------------------------------------------
    # Forget requests
    # -------------------------------------------------

    def check_forget_request(self, message, text):

        if text in [
            "forget my name",
            "delete my name"
        ]:

            forgotten = self.memory.forget("name")

            if forgotten:
                return "Okay. I've forgotten your name."

            return "I wasn't storing your name."

        personal_categories = {
            "forget my age": "age",
            "delete my age": "age",
            "forget my birthday": "birthday",
            "delete my birthday": "birthday",
            "forget my gender": "gender",
            "delete my gender": "gender",
            "forget my school": "school",
            "delete my school": "school"
        }

        if text in personal_categories:

            category = personal_categories[text]

            forgotten = self.memory.forget(category)

            if forgotten:
                return f"Okay. I've forgotten your {category}."

            return f"I wasn't storing your {category}."

        favourite_patterns = [
            r"^forget my favourite (.+?)[.!]?$",
            r"^forget my favorite (.+?)[.!]?$",
            r"^delete my favourite (.+?)[.!]?$",
            r"^delete my favorite (.+?)[.!]?$"
        ]

        for pattern in favourite_patterns:

            match = re.match(pattern, text)

            if match:

                category = match.group(1).strip()

                forgotten = self.memory.forget(
                    "favourite",
                    category
                )

                if forgotten:
                    return f"Okay. I've forgotten your favourite {category}."

                return (
                    "I couldn't find a saved favourite "
                    f"{category}."
                )

        like_patterns = [
            r"^forget that i like (.+?)[.!]?$",
            r"^forget i like (.+?)[.!]?$",
            r"^delete (.+?) from my likes[.!]?$"
        ]

        for pattern in like_patterns:

            match = re.match(pattern, text)

            if match:

                item = message[
                    match.start(1):match.end(1)
                ].strip().rstrip(".!")

                forgotten = self.memory.forget(
                    "like",
                    item
                )

                if forgotten:
                    return f"I've forgotten that you like {item}."

                return f"I couldn't find {item} in your likes."

        dislike_patterns = [
            r"^forget that i dislike (.+?)[.!]?$",
            r"^forget that i hate (.+?)[.!]?$",
            r"^forget i dislike (.+?)[.!]?$",
            r"^delete (.+?) from my dislikes[.!]?$"
        ]

        for pattern in dislike_patterns:

            match = re.match(pattern, text)

            if match:

                item = message[
                    match.start(1):match.end(1)
                ].strip().rstrip(".!")

                forgotten = self.memory.forget(
                    "dislike",
                    item
                )

                if forgotten:
                    return f"I've forgotten that you dislike {item}."

                return f"I couldn't find {item} in your dislikes."

        hobby_patterns = [
            r"^forget that my hobby is (.+?)[.!]?$",
            r"^forget my hobby (.+?)[.!]?$",
            r"^delete (.+?) from my hobbies[.!]?$"
        ]

        for pattern in hobby_patterns:

            match = re.match(pattern, text)

            if match:

                hobby = message[
                    match.start(1):match.end(1)
                ].strip().rstrip(".!")

                forgotten = self.memory.forget(
                    "hobby",
                    hobby
                )

                if forgotten:
                    return f"I've forgotten that {hobby} is one of your hobbies."

                return f"I couldn't find {hobby} in your hobbies."

        return None

    # -------------------------------------------------
    # Feelings
    # -------------------------------------------------

    def check_feeling(self, text):

        feeling_groups = {
            "tired": [
                "i'm tired",
                "im tired",
                "i am tired",
                "i feel tired",
                "i'm exhausted",
                "im exhausted",
                "i am exhausted"
            ],
            "sad": [
                "i'm sad",
                "im sad",
                "i am sad",
                "i feel sad",
                "i'm upset",
                "im upset",
                "i am upset"
            ],
            "stressed": [
                "i'm stressed",
                "im stressed",
                "i am stressed",
                "i feel stressed",
                "i'm overwhelmed",
                "im overwhelmed",
                "i am overwhelmed"
            ],
            "happy": [
                "i'm happy",
                "im happy",
                "i am happy",
                "i feel happy",
                "i'm excited",
                "im excited",
                "i am excited"
            ],
            "bored": [
                "i'm bored",
                "im bored",
                "i am bored",
                "i feel bored"
            ]
        }

        for feeling, phrases in feeling_groups.items():

            if text in phrases:

                response_data = self.feeling_response(
                    feeling
                )

                self.pending_follow_up = response_data.get(
                    "follow_up"
                )

                return response_data.get("reply")

        return None

    def feeling_response(self, feeling):

        responses = {
            "tired": [
                "You sound worn out. Long day, or did you not sleep well?",
                "Tired tired, or just mentally finished with today?",
                "That doesn't sound fun. What's been draining your energy?"
            ],
            "sad": [
                "I'm sorry. Do you want to tell me what happened?",
                "That sounds difficult. What's made you feel like that?",
                "You don't have to explain, but I'm here if you want to."
            ],
            "stressed": [
                "That sounds like a lot. What's putting the most pressure on you?",
                "Let's slow it down a little. What's making you feel overwhelmed?",
                "Is it one large problem or lots of smaller things?"
            ],
            "happy": [
                "I like hearing that. What happened?",
                "Ooh, good news? What's made you happy?",
                "Nice. What's got you feeling like that?"
            ],
            "bored": [
                "Bored, huh? Do you want something creative, relaxing, or slightly ridiculous to do?",
                "We can't have that. What kind of mood are you in?",
                "Do you want an idea or just some company?"
            ]
        }

        reply = random.choice(
            responses.get(
                feeling,
                ["Tell me more."]
            )
        )

        follow_up = {
            "kind": "feeling",
            "topic": feeling,
            "question_type": "reason"
        }

        return {
            "reply": reply,
            "follow_up": follow_up
        }
    # -------------------------------------------------
    # Success and progress
    # -------------------------------------------------

    def check_success(self, text):

        success_phrases = [
            "it works",
            "it worked",
            "omg it works",
            "omg it worked",
            "yay it works",
            "yay it worked",
            "we fixed it",
            "i fixed it",
            "i did it"
        ]

        if text in success_phrases:

            return random.choice([
                "It works! Nice — another little piece of Nova behaving properly.",
                "Yes! We got it working.",
                "That is exactly what I wanted to hear.",
                "Success. I was beginning to take that bug personally.",
                "Nice! Another problem officially defeated."
            ])

        return None
    # -------------------------------------------------
    # Topic change detection
    # -------------------------------------------------

    def is_clear_new_topic(self, text):

        if not text:
            return True

        question_starters = [
            "what ",
            "when ",
            "where ",
            "who ",
            "which ",
            "how ",
            "can you ",
            "could you ",
            "will you ",
            "do you ",
            "are you ",
            "is there "
        ]

        for starter in question_starters:

            if text.startswith(starter):
                return True

        new_topic_starters = [
            "my name is ",
            "call me ",
            "my birthday is ",
            "my favourite ",
            "my favorite ",
            "actually my favourite ",
            "actually my favorite ",
            "my hobbies are ",
            "my hobbies include ",
            "my school is ",
            "i go to ",
            "i study at ",
            "i went ",
            "today i went ",
            "i got ",
            "i bought ",
            "i visited ",
            "i met ",
            "i started ",
            "i'm working on ",
            "im working on ",
            "i am working on ",
            "my project is ",
            "remember ",
            "forget ",
            "delete "
        ]

        for starter in new_topic_starters:

            if text.startswith(starter):
                return True

        return text in [
            "hi",
            "hello",
            "hey",
            "hiya",
            "hii"
        ]

    # -------------------------------------------------
    # Meaningful-answer check
    # -------------------------------------------------

    def is_meaningful_answer(self, text):

        cleaned = re.sub(
            r"[^a-z0-9\s']",
            "",
            text.lower()
        ).strip()

        words = cleaned.split()

        if not words:
            return False

        if len(words) == 1:

            return cleaned in [
                "yes",
                "no",
                "maybe",
                "sometimes",
                "probably"
            ]

        vowel_count = sum(
            1
            for character in cleaned
            if character in "aeiou"
        )

        if vowel_count < 2:
            return False

        long_random_words = [
            word
            for word in words
            if len(word) >= 12
        ]

        if len(long_random_words) >= 2:
            return False

        return True

    # -------------------------------------------------
    # Follow-up answers
    # -------------------------------------------------

    def check_follow_up_answer(self, message):

        context = self.pending_follow_up
        self.pending_follow_up = None

        if not context:
            return None

        kind = context.get("kind", "")
        topic = context.get("topic", "that")
        question_type = context.get(
            "question_type",
            "general"
        )
        if kind == "social":

            result = self.social.answer_follow_up(
                message,
                context
            )

            if isinstance(result, dict):

                self.pending_follow_up = result.get(
                    "follow_up"
                )

                return result.get(
                    "reply",
                    ""
                )

            return result
        if kind == "learning":

            return self.learning_follow_up(
                topic,
                question_type,
                message
            )

        if kind == "like":

            self.memory.set_profile_fact(
                f"reason for liking {topic.lower()}",
                message.strip()
            )

            return random.choice([
                f"That makes sense. I can see why you like {topic}.",
                f"Fair enough — that tells me more about what you enjoy about {topic}.",
                "I understand. I'll keep that reason in mind too."
            ])

        if kind == "dislike":

            self.memory.set_profile_fact(
                f"reason for disliking {topic.lower()}",
                message.strip()
            )

            return random.choice([
                f"That makes sense. I can see why {topic} isn't for you.",
                "Fair enough — now I understand the reason behind that dislike.",
                "I get that. I'll keep the reason in mind as well."
            ])

        if kind == "favourite":

            category = context.get(
                "category",
                "thing"
            )

            self.memory.set_profile_fact(
                f"reason {topic} is favourite {category}",
                message.strip()
            )

            return random.choice([
                f"That makes sense. I can see why {topic} is your favourite.",
                "Fair enough. That explains it nicely.",
                "I get that. I'll keep that reason in mind too."
            ])

        if kind == "event":

            return random.choice([
                "That gives me a better picture of how your day went.",
                "That sounds like a memorable part of it.",
                "I can see why that stood out."
            ])

        if kind == "school":

            self.memory.set_profile_fact(
                f"thoughts about {topic.lower()}",
                message.strip()
            )

            return random.choice([
                f"That gives me a better idea of how you feel about {topic}.",
                "That makes sense. I'll keep that in mind.",
                "I understand a little better now."
            ])

        if kind == "hobby":

            return random.choice([
                "That gives me a better idea of which hobbies matter most to you.",
                "Nice. I'll keep that in mind.",
                "That makes sense."
            ])

        if kind == "goal":

            self.memory.set_profile_fact(
                f"reason for goal {topic.lower()}",
                message.strip()
            )

            return random.choice([
                "That makes sense. It sounds like a meaningful goal.",
                "I understand why that matters to you.",
                "That's a good reason to keep working toward it."
            ])

        if kind == "project":

            self.memory.set_profile_fact(
                f"project update {topic.lower()}",
                message.strip()
            )

            return random.choice([
                f"That gives me a better idea of how {topic} is going.",
                "I understand. I'll keep that project update in mind.",
                "That makes sense. It sounds like you're making progress."
            ])

        if kind == "feeling":

            return self.feeling_follow_up(
                topic,
                message
            )

        return random.choice([
            "That makes sense.",
            "I understand what you mean.",
            "Thanks for explaining that."
        ])

    def learning_follow_up(
        self,
        topic,
        question_type,
        message
    ):

        if question_type == "reason":

            self.memory.set_profile_fact(
                f"reason for learning {topic.lower()}",
                message.strip()
            )

            return random.choice([
                f"That makes sense. I can see why that drew you to {topic}.",
                f"That's a good reason to learn {topic}.",
                "I get that. The reason makes sense."
            ])

        if question_type == "difficulty":

            self.memory.set_profile_fact(
                f"difficulty learning {topic.lower()}",
                message.strip()
            )

            return random.choice([
                f"I get that. That sounds like one of the harder parts of learning {topic}.",
                "Yeah, that can be tricky. Hopefully practice makes it easier.",
                "That makes sense. That part can take time."
            ])

        if question_type == "progress":

            self.memory.set_profile_fact(
                f"progress learning {topic.lower()}",
                message.strip()
            )

            return random.choice([
                f"That gives me a better idea of how learning {topic} is going.",
                "Progress can feel uneven when you're learning something new.",
                "I understand. I'll keep in mind how it's going."
            ])

        return random.choice([
            f"That tells me a little more about your experience learning {topic}.",
            "I understand. I'll keep that in mind.",
            "That makes sense."
        ])

    def feeling_follow_up(self, feeling, message):

        self.memory.add_event(
            f"felt {feeling}: {message.strip()}",
            "today"
        )

        responses = {
            "tired": [
                "That explains it. I hope you get a proper chance to rest soon.",
                "Ah, that makes sense. Be kind to yourself tonight.",
                "No wonder you're tired."
            ],
            "sad": [
                "I'm sorry. That sounds difficult to carry.",
                "Thank you for telling me what was behind it.",
                "That sounds genuinely upsetting."
            ],
            "stressed": [
                "That explains the stress. It sounds like a lot to hold at once.",
                "I understand. That kind of pressure can build quickly.",
                "No wonder you're stressed."
            ],
            "happy": [
                "I can see why that made you happy.",
                "That sounds like a moment worth enjoying.",
                "I'm glad you told me."
            ],
            "bored": [
                "Fair enough. Sometimes the day just needs something different.",
                "We should find something that actually fits your mood.",
                "I get that."
            ]
        }

        return random.choice(
            responses.get(
                feeling,
                ["That makes sense. Thanks for telling me."]
            )
        )

    # -------------------------------------------------
    # Full memory summary
    # -------------------------------------------------

    def check_memory_summary(self, text):

        if text != "what do you know about me":
            return None

        lines = []

        name = self.memory.profile.get(
            "name",
            ""
        )

        if name:
            lines.append("Name: " + name)

        personal = self.memory.profile.get(
            "personal",
            {}
        )

        for key, value in personal.items():

            if value:
                lines.append(
                    f"{key.capitalize()}: {value}"
                )

        preferences = self.memory.profile.get(
            "preferences",
            {}
        )

        for category in [
            "likes",
            "dislikes",
            "hobbies"
        ]:

            items = preferences.get(
                category,
                []
            )

            if items:

                lines.append(
                    category.capitalize()
                    + ": "
                    + ", ".join(items)
                )

        favourites = preferences.get(
            "favourites",
            {}
        )

        for key, value in favourites.items():

            lines.append(
                f"Favourite {key}: {value}"
            )

        if not lines:
            return "I don't know much about you yet."

        return (
            "Here's what I know:\n\n"
            + "\n".join(lines)
        )

    # -------------------------------------------------
    # Recent conversation context
    # -------------------------------------------------

    def check_conversation_context(self, text):

        if text in [
            "what did i just say",
            "what was my last message"
        ]:

            if self.last_user_message:

                return (
                    "You just said: "
                    f"'{self.last_user_message}'"
                )

            return "You haven't said anything yet."

        if text in [
            "what did you just say",
            "what was your last reply"
        ]:

            if self.last_nova_reply:

                return (
                    "I just said: "
                    f"'{self.last_nova_reply}'"
                )

            return "I haven't replied yet."

        return None

    # -------------------------------------------------
    # Helpers
    # -------------------------------------------------

    def find_in_list(self, items, wanted_item):

        wanted_item = wanted_item.lower().strip()

        for item in items:

            if item.lower().strip() == wanted_item:
                return item

        return None

    def natural_list(self, items):

        if not items:
            return ""

        if len(items) == 1:
            return items[0]

        if len(items) == 2:
            return items[0] + " and " + items[1]

        return (
            ", ".join(items[:-1])
            + ", and "
            + items[-1]
        )