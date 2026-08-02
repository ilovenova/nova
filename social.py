"""
social.py

Handles greetings, social phrases
and short conversational check-ins for NOVA.
"""

import random


class Social:

    def __init__(self, memory):

        self.memory = memory

    # -------------------------------------------------
    # Main social router
    # -------------------------------------------------

    def respond(self, message, text):

        response = self.check_greeting(text)

        if response:
            return response

        response = self.check_simple_social_phrase(text)

        if response:
            return response

        response = self.check_user_state(text)

        if response:
            return response

        response = self.check_short_agreement(text)

        if response:
            return response

        return None

    # -------------------------------------------------
    # Greetings
    # -------------------------------------------------

    def check_greeting(self, text):

        greetings = [
            "hi",
            "hii",
            "hiii",
            "hello",
            "hey",
            "hiya",
            "helo",
            "helloo",
            "hi nova",
            "hello nova",
            "hey nova"
        ]

        if text not in greetings:
            return None

        name = self.memory.profile.get(
            "name",
            ""
        )

        if name:
            greeting_name = f", {name}"
        else:
            greeting_name = ""

        choices = [
            {
                "reply": f"Hey{greeting_name}! How are you doing?",
                "follow_up": {
                    "kind": "social",
                    "question_type": "how_are_you"
                }
            },
            {
                "reply": f"Hello{greeting_name}! Tell me something new.",
                "follow_up": {
                    "kind": "social",
                    "question_type": "something_new"
                }
            },
            {
                "reply": f"Hi{greeting_name}! How has your day been?",
                "follow_up": {
                    "kind": "social",
                    "question_type": "how_was_day"
                }
            },
            {
                "reply": f"Hey{greeting_name}. Good to see you.",
                "follow_up": None
            },
            {
                "reply": f"Hello{greeting_name}!",
                "follow_up": None
            },
            {
                "reply": f"There you are{greeting_name}. What's going on?",
                "follow_up": {
                    "kind": "social",
                    "question_type": "whats_going_on"
                }
            }
        ]

        return random.choice(choices)

    # -------------------------------------------------
    # Simple social language
    # -------------------------------------------------

    def check_simple_social_phrase(self, text):

        if text in [
            "yay",
            "yayy",
            "yayyy",
            "woohoo",
            "yes!"
        ]:

            return {
                "reply": random.choice([
                    "Yay indeed.",
                    "That sounds like good news.",
                    "Tiny celebration accepted.",
                    "Okay, something clearly went right.",
                    "I approve of this sudden enthusiasm."
                ]),
                "follow_up": None
            }

        if text in [
            "thank you",
            "thanks",
            "thx",
            "ty",
            "thank you nova",
            "thanks nova"
        ]:

            return {
                "reply": random.choice([
                    "You're welcome.",
                    "Anytime.",
                    "Of course.",
                    "You're very welcome.",
                    "We make a pretty good team."
                ]),
                "follow_up": None
            }

        if text in [
            "thats good",
            "that's good",
            "that is good",
            "good",
            "nice"
        ]:

            return {
                "reply": random.choice([
                    "It is.",
                    "I'm glad you think so.",
                    "Things seem to be behaving for once.",
                    "Agreed.",
                    "A pleasantly uncomplicated result."
                ]),
                "follow_up": None
            }

        return None

    # -------------------------------------------------
    # User states outside a pending question
    # -------------------------------------------------

    def check_user_state(self, text):

        positive_states = [
            "im good",
            "i'm good",
            "i am good",
            "im okay",
            "i'm okay",
            "i am okay",
            "im fine",
            "i'm fine",
            "i am fine",
            "not bad",
            "pretty good"
        ]

        if text in positive_states:

            return {
                "reply": random.choice([
                    "I'm glad to hear that.",
                    "Good. A calm day is allowed.",
                    "Nice. I hope it stays that way.",
                    "That's good to hear.",
                    "Not bad is sometimes perfectly respectable."
                ]),
                "follow_up": None
            }

        negative_states = [
            "not good",
            "im not good",
            "i'm not good",
            "i am not good",
            "could be better",
            "not great"
        ]

        if text in negative_states:

            ask_question = random.choice([
                True,
                False
            ])

            if ask_question:

                return {
                    "reply": random.choice([
                        "I'm sorry. Do you want to tell me what's wrong?",
                        "That doesn't sound great. What happened?",
                        "Okay. What's been making today difficult?"
                    ]),
                    "follow_up": {
                        "kind": "social",
                        "question_type": "not_good"
                    }
                }

            return {
                "reply": random.choice([
                    "I'm sorry. I'm here if you want to talk.",
                    "That doesn't sound great.",
                    "Okay. We can take things slowly."
                ]),
                "follow_up": None
            }

        return None

    # -------------------------------------------------
    # Short agreement after a social reply
    # -------------------------------------------------

    def check_short_agreement(self, text):

        positive_agreements = [
            "yeah",
            "yea",
            "yes",
            "yep",
            "yeah it has",
            "yea it has",
            "yes it has",
            "it has",
            "yeah it has been",
            "yes it has been",
            "it has been"
        ]

        if text in positive_agreements:

            return {
                "reply": random.choice([
                    "I'm glad.",
                    "Good. A decent day is always welcome.",
                    "That's nice to hear.",
                    "I hope it keeps going that way.",
                    "Then today has been treating you fairly well."
                ]),
                "follow_up": None
            }

        negative_agreements = [
            "no",
            "nope",
            "not really",
            "no it hasnt",
            "no it hasn't",
            "it hasnt",
            "it hasn't"
        ]

        if text in negative_agreements:

            return {
                "reply": random.choice([
                    "Fair enough.",
                    "Okay. Some days just don't cooperate.",
                    "I understand.",
                    "That's all right. You don't have to make it sound better than it was."
                ]),
                "follow_up": None
            }

        return None

    # -------------------------------------------------
    # Does this plausibly answer NOVA's social question?
    # -------------------------------------------------

    def should_use_follow_up(self, text, context):

        question_type = context.get(
            "question_type",
            ""
        )

        if question_type == "how_are_you":

            return self.is_state_answer(text)

        if question_type == "how_was_day":

            return self.is_day_answer(text)

        if question_type in [
            "something_new",
            "whats_going_on",
            "not_good"
        ]:
            return self.is_meaningful_social_reply(text)

        return False

    def is_state_answer(self, text):

        phrases = [
            "im good",
            "i'm good",
            "i am good",
            "im okay",
            "i'm okay",
            "i am okay",
            "im fine",
            "i'm fine",
            "i am fine",
            "not bad",
            "pretty good",
            "not good",
            "im not good",
            "i'm not good",
            "i am not good",
            "not great",
            "could be better",
            "tired",
            "im tired",
            "i'm tired",
            "happy",
            "im happy",
            "i'm happy",
            "sad",
            "im sad",
            "i'm sad"
        ]

        return text in phrases

    def is_day_answer(self, text):

        day_words = [
            "good",
            "nice",
            "okay",
            "alright",
            "bad",
            "great",
            "terrible",
            "awful",
            "tiring",
            "stressful",
            "busy",
            "calm",
            "normal",
            "boring"
        ]

        return any(
            word in text
            for word in day_words
        )

    def is_meaningful_social_reply(self, text):

        if not text:
            return False

        simple_replies = [
            "nothing",
            "nothing much",
            "not much",
            "same old",
            "not a lot",
            "i dont know",
            "i don't know"
        ]

        if text in simple_replies:
            return True

        return len(text.split()) >= 2

    # -------------------------------------------------
    # Answers to NOVA's social questions
    # -------------------------------------------------

    def answer_follow_up(self, message, context):

        question_type = context.get(
            "question_type",
            ""
        )

        text = message.lower().strip()

        if question_type == "how_are_you":

            return {
                "reply": self.answer_how_are_you(text),
                "follow_up": None
            }

        if question_type == "how_was_day":

            result = self.answer_how_was_day(text)

            if isinstance(result, dict):
                return result

            return {
                "reply": result,
                "follow_up": None
            }

        if question_type == "something_new":

            return {
                "reply": random.choice([
                    "Oh, interesting. Tell me a little more.",
                    "That's new. I'll keep it in mind.",
                    "I like hearing the small updates too.",
                    "Interesting — what happened next?"
                ]),
                "follow_up": None
            }

        if question_type == "whats_going_on":

            if text in [
                "nothing",
                "nothing much",
                "not much",
                "not a lot",
                "same old"
            ]:
                return {
                    "reply": random.choice([
                        "Fair enough. A quiet moment, then.",
                        "Not much can be nice sometimes.",
                        "Okay. We can just be here for a bit.",
                        "A calm day, perhaps."
                    ]),
                    "follow_up": None
                }

            return {
                "reply": random.choice([
                    "Got it. I'm with you.",
                    "Okay, tell me more.",
                    "I see. What happened next?",
                    "That sounds worth talking about."
                ]),
                "follow_up": None
            }

        if question_type == "not_good":

            return {
                "reply": random.choice([
                    "I'm sorry. That sounds difficult.",
                    "Thank you for telling me.",
                    "That makes sense. I'm here with you.",
                    "You don't have to pretend it's fine."
                ]),
                "follow_up": None
            }

        return {
            "reply": random.choice([
                "I understand.",
                "Thanks for telling me.",
                "That makes sense."
            ]),
            "follow_up": None
        }

    # -------------------------------------------------
    # How are you?
    # -------------------------------------------------

    def answer_how_are_you(self, text):

        positive = [
            "im good",
            "i'm good",
            "i am good",
            "im okay",
            "i'm okay",
            "i am okay",
            "im fine",
            "i'm fine",
            "i am fine",
            "not bad",
            "pretty good"
        ]

        if text in positive:

            return random.choice([
                "I'm glad to hear that.",
                "Good. I hope the rest of your day stays that way.",
                "Nice. That's good to hear.",
                "I'm glad you're doing okay."
            ])

        negative = [
            "not good",
            "im not good",
            "i'm not good",
            "i am not good",
            "not great",
            "could be better"
        ]

        if text in negative:

            return random.choice([
                "I'm sorry. Do you want to tell me what happened?",
                "That doesn't sound great. I'm listening.",
                "I'm here. What's been going on?",
                "Okay. We can take it slowly."
            ])

        return random.choice([
            "I see. Thanks for telling me.",
            "That gives me a better idea of how you're doing.",
            "Got it. I'm listening.",
            "I understand."
        ])

    # -------------------------------------------------
    # How has your day been?
    # -------------------------------------------------

    def answer_how_was_day(self, text):

        positive_day_answers = [
            "its been good",
            "it's been good",
            "it has been good",
            "my days been good",
            "my day's been good",
            "my day has been good",
            "good",
            "good so far",
            "pretty good",
            "pretty good actually",
            "not bad",
            "its been nice",
            "it's been nice",
            "it has been nice"
        ]

        if text in positive_day_answers:

            ask_question = random.choice([
                True,
                False,
                False
            ])

            if ask_question:

                return {
                    "reply": random.choice([
                        "That's good to hear. Anything nice happen?",
                        "I'm glad. Was there a particularly good part?",
                        "Nice. What made today good?"
                    ]),
                    "follow_up": {
                        "kind": "conversation",
                        "question_type": "day_positive_reason"
                    }
                }

            return random.choice([
                "That's good to hear.",
                "Nice. I'm glad your day's been good.",
                "I'm glad today has treated you well.",
                "Good. A pleasant day is always welcome.",
                "That's nice to hear."
            ])

        neutral_day_answers = [
            "its been okay",
            "it's been okay",
            "it has been okay",
            "okay",
            "alright",
            "all right",
            "its been alright",
            "it's been alright",
            "it has been alright",
            "same as usual",
            "normal"
        ]

        if text in neutral_day_answers:

            return random.choice([
                "Fair enough. An okay day is still a day survived.",
                "Okay sounds manageable.",
                "Nothing too dramatic, then.",
                "Some days are simply ordinary.",
                "I understand. Not brilliant, but not terrible either."
            ])

        negative_day_answers = [
            "its been bad",
            "it's been bad",
            "it has been bad",
            "bad",
            "not good",
            "not great",
            "terrible",
            "awful",
            "its been tiring",
            "it's been tiring",
            "it has been tiring",
            "tiring",
            "stressful",
            "its been stressful",
            "it's been stressful"
        ]

        if text in negative_day_answers:

            ask_question = random.choice([
                True,
                False
            ])

            if ask_question:

                return random.choice([
                    "I'm sorry. What made today difficult?",
                    "That doesn't sound pleasant. What happened?",
                    "A tiring day, then. What took the most out of you?"
                ])

            return random.choice([
                "I'm sorry. That doesn't sound like a good day.",
                "That sounds exhausting.",
                "Some days really do take more than they give.",
                "I'm sorry today has been difficult."
            ])

        return random.choice([
            "Thanks for telling me about your day.",
            "I see. Was there one part that stood out?",
            "That gives me a better picture of your day.",
            "I understand."
        ])