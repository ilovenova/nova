"""
emotions.py

Handles NOVA's emotional understanding and continuity.

NOVA uses this module to:
- understand emotions and what they are about
- remember emotional threads
- recognise hopes, worries, pride and excitement
- connect later successes to earlier struggles
- respond warmly without asking too many questions
"""

import random
import re


class Emotions:

    def __init__(self, memory):

        self.memory = memory

    # -------------------------------------------------
    # Main router
    # -------------------------------------------------

    def respond(self, message, text):

        result = self.check_emotional_statement(
            message,
            text
        )

        if result:
            return result

        result = self.check_success_statement(
            message,
            text
        )

        if result:
            return result

        result = self.check_discovery_statement(
            message,
            text
        )

        if result:
            return result

        result = self.check_happy_follow_up(
            message,
            text
        )

        if result:
            return result

        return None

    # -------------------------------------------------
    # Emotional statements
    # -------------------------------------------------

    def check_emotional_statement(
        self,
        message,
        text
    ):

        emotion_patterns = [
            (
                "happy",
                [
                    r"^i(?:'m| am|m) (?:really |so |very )?happy about (.+)$",
                    r"^i(?:'m| am|m) (?:really |so |very )?happy (?:that|because) (.+)$"
                ]
            ),
            (
                "proud",
                [
                    r"^i(?:'m| am|m) (?:really |so |very )?proud of (.+)$",
                    r"^i(?:'m| am|m) (?:really |so |very )?proud (?:that|because) (.+)$"
                ]
            ),
            (
                "excited",
                [
                    r"^i(?:'m| am|m) (?:really |so |very )?excited about (.+)$",
                    r"^i(?:'m| am|m) (?:really |so |very )?excited (?:that|because) (.+)$",
                    r"^i cant wait for (.+)$",
                    r"^i can't wait for (.+)$"
                ]
            ),
            (
                "worried",
                [
                    r"^i(?:'m| am|m) (?:really |so |very )?worried about (.+)$",
                    r"^i(?:'m| am|m) (?:really |so |very )?worried (?:that|if) (.+)$"
                ]
            ),
            (
                "scared",
                [
                    r"^i(?:'m| am|m) (?:really |so |very )?scared (?:about|of) (.+)$",
                    r"^i(?:'m| am|m) (?:really |so |very )?scared (?:that|because) (.+)$"
                ]
            ),
            (
                "nervous",
                [
                    r"^i(?:'m| am|m) (?:really |so |very )?nervous about (.+)$",
                    r"^i(?:'m| am|m) (?:really |so |very )?nervous (?:that|because) (.+)$"
                ]
            ),
            (
                "upset",
                [
                    r"^i(?:'m| am|m) (?:really |so |very )?upset about (.+)$",
                    r"^i(?:'m| am|m) (?:really |so |very )?upset (?:that|because) (.+)$"
                ]
            ),
            (
                "sad",
                [
                    r"^i(?:'m| am|m) (?:really |so |very )?sad about (.+)$",
                    r"^i(?:'m| am|m) (?:really |so |very )?sad (?:that|because) (.+)$"
                ]
            )
        ]

        for emotion, patterns in emotion_patterns:

            for pattern in patterns:

                match = re.match(
                    pattern,
                    text
                )

                if not match:
                    continue

                topic = match.group(1).strip().rstrip(".!")

                if not topic:
                    return None

                self.save_emotional_thread(
                    emotion,
                    topic
                )

                return self.make_result(
                    self.emotional_reply(
                        emotion,
                        topic
                    )
                )

        return None

    def emotional_reply(
        self,
        emotion,
        topic
    ):

        replies = {
            "happy": [
                f"I'm glad. {topic} clearly means a lot to you.",
                f"That sounds worth being happy about.",
                f"I can see why {topic} made you happy.",
                f"That's lovely. Enjoy that feeling."
            ],
            "proud": [
                f"You deserve to feel proud of {topic}.",
                f"That sounds like something you worked for.",
                f"I'm glad you can see your own progress.",
                f"You should let yourself enjoy that pride."
            ],
            "excited": [
                f"I can see why you're excited about {topic}.",
                f"That sounds like something to look forward to.",
                f"Ooh, that does sound exciting.",
                f"I hope it turns out even better than you're imagining."
            ],
            "worried": [
                f"I understand why {topic} is worrying you.",
                f"That sounds like something that's been sitting on your mind.",
                f"I can see why you'd feel worried about that.",
                f"You don't have to solve all of {topic} at once."
            ],
            "scared": [
                f"I can understand why {topic} feels scary.",
                f"That sounds difficult to carry alone.",
                f"It's okay to be scared of something that matters to you.",
                f"I'm listening."
            ],
            "nervous": [
                f"That makes sense. {topic} sounds important to you.",
                f"Nerves usually show that you care about how it goes.",
                f"I can understand why you'd feel nervous.",
                f"Take it one step at a time."
            ],
            "upset": [
                f"I can see why {topic} upset you.",
                f"That sounds genuinely difficult.",
                f"I'm sorry. That sounds like it hurt.",
                f"Thank you for telling me."
            ],
            "sad": [
                f"I'm sorry. {topic} sounds painful.",
                f"I can understand why that made you sad.",
                f"That sounds hard to sit with.",
                f"I'm here with you."
            ]
        }

        choices = replies.get(
            emotion,
            ["I understand."]
        )

        # Curiosity stays restrained:
        # most replies contain no follow-up question.
        return random.choice(choices)

    # -------------------------------------------------
    # Success and reflection
    # -------------------------------------------------

    def check_success_statement(
        self,
        message,
        text
    ):

        patterns = [
            r"^i passed(?: my)? (.+)$",
            r"^i passed$",
            r"^i did it$",
            r"^i finally did it$",
            r"^i succeeded$",
            r"^i made it$"
        ]

        for pattern in patterns:

            match = re.match(
                pattern,
                text
            )

            if not match:
                continue

            detail = ""

            if match.lastindex:
                detail = match.group(1).strip().rstrip(".!")

            thread = self.find_relevant_thread(
                detail
            )

            if thread:

                topic = thread.get(
                    "topic",
                    detail or "it"
                )
                old_emotion = thread.get(
                    "emotion",
                    ""
                )

                self.update_thread(
                    topic,
                    "proud",
                    "resolved"
                )

                return self.make_result(
                    random.choice([
                        f"Remember when {topic} felt so hard? Well, you did it.",
                        f"You were {old_emotion} about {topic} before — and now look at you.",
                        f"All those difficult moments with {topic}, and you kept going. You did it.",
                        f"I remember {topic} being hard for you. You should be proud now."
                    ])
                )

            if detail:
                return self.make_result(
                    random.choice([
                        f"You passed {detail}! That's brilliant.",
                        f"That's wonderful — well done on {detail}.",
                        f"You did it. You should be proud of yourself."
                    ])
                )

            return self.make_result(
                random.choice([
                    "You did it! That's brilliant.",
                    "That's wonderful — well done.",
                    "You should be proud of yourself."
                ])
            )

        return None

    # -------------------------------------------------
    # Personal curiosity and discovery
    # -------------------------------------------------

    def check_discovery_statement(
        self,
        message,
        text
    ):

        curiosity_patterns = [
            r"^i(?:'ve| have|ve) been wondering about (.+)$",
            r"^i wonder about (.+)$",
            r"^i(?:'m| am|m) curious about (.+)$"
        ]

        for pattern in curiosity_patterns:

            match = re.match(
                pattern,
                text
            )

            if not match:
                continue

            topic = match.group(1).strip().rstrip(".!")

            if not topic:
                return None

            self.save_personal_curiosity(
                topic
            )

            return self.make_result(
                random.choice([
                    f"I'll remember that you've been wondering about {topic}.",
                    f"That's an interesting thing to wonder about.",
                    f"I'll keep {topic} in mind with you."
                ])
            )

        discovery_phrases = [
            "i found out",
            "i found out!",
            "i figured it out",
            "i figured it out!",
            "i know now",
            "i learned the answer"
        ]

        if text not in discovery_phrases:
            return None

        topic = self.find_open_personal_curiosity()

        if not topic:
            return self.make_result(
                random.choice([
                    "Oh, what did you find out?",
                    "Tell me — what was the answer?",
                    "Now I'm curious too. What did you learn?"
                ])
            )

        self.resolve_personal_curiosity(
            topic
        )

        return self.make_result(
            random.choice([
                f"Was it about {topic}?",
                f"Did you finally find out about {topic}?",
                f"Is this the thing you were wondering about — {topic}?"
            ]),
            {
                "kind": "emotion_thread",
                "question_type": "discovery_confirmation",
                "topic": topic
            }
        )

    # -------------------------------------------------
    # Happy follow-up after success
    # -------------------------------------------------

    def check_happy_follow_up(
        self,
        message,
        text
    ):

        happy_phrases = [
            "im so happy",
            "i'm so happy",
            "i am so happy",
            "im really happy",
            "i'm really happy",
            "i am really happy",
            "im sooo happy",
            "i'm sooo happy"
        ]

        if text not in happy_phrases:
            return None

        thread = self.find_recent_resolved_thread()

        if not thread:
            return self.make_result(
                random.choice([
                    "I'm really glad.",
                    "You deserve to enjoy that feeling.",
                    "That makes me happy for you."
                ])
            )

        topic = thread.get(
            "topic",
            "it"
        )

        return self.make_result(
            random.choice([
                f"You deserve to be. You worked through so much with {topic}.",
                f"You should be happy. Remember when {topic} felt impossible?",
                f"I'm really happy for you. You kept going with {topic}.",
                f"Enjoy it. You earned this moment."
            ])
        )

    # -------------------------------------------------
    # Follow-up answers
    # -------------------------------------------------

    def answer_follow_up(
        self,
        message,
        context
    ):

        text = message.lower().strip()

        question_type = context.get(
            "question_type",
            ""
        )

        if question_type == "discovery_confirmation":

            topic = context.get(
                "topic",
                "that"
            )

            if text in [
                "yes",
                "yeah",
                "yep",
                "yes it was",
                "it was",
                "exactly",
                "thats right",
                "that's right"
            ]:
                return {
                    "reply": random.choice([
                        f"I thought it might be. What did you find out about {topic}?",
                        f"Ah, yes — {topic}. Tell me what you learned.",
                        f"That makes sense. So what was the answer?"
                    ]),
                    "follow_up": None
                }

            if text in [
                "no",
                "nope",
                "no it wasnt",
                "no it wasn't",
                "not that"
            ]:
                return {
                    "reply": random.choice([
                        "Oh, something else then. What did you find out?",
                        "Got it. Tell me what it was.",
                        "Okay — what was the thing you learned?"
                    ]),
                    "follow_up": None
                }

        return None

    # -------------------------------------------------
    # Thread storage
    # -------------------------------------------------

    def save_emotional_thread(
        self,
        emotion,
        topic
    ):

        key = (
            "emotional thread: "
            + self.thread_key(topic)
        )

        self.memory.set_profile_fact(
            key,
            {
                "emotion": emotion,
                "topic": topic,
                "status": "current"
            }
        )

        self.memory.add_event(
            f"felt {emotion} about: {topic}",
            "recent"
        )

    def update_thread(
        self,
        topic,
        emotion,
        status
    ):

        key = (
            "emotional thread: "
            + self.thread_key(topic)
        )

        self.memory.set_profile_fact(
            key,
            {
                "emotion": emotion,
                "topic": topic,
                "status": status
            }
        )

    def save_personal_curiosity(
        self,
        topic
    ):

        key = (
            "personal curiosity: "
            + self.thread_key(topic)
        )

        self.memory.set_profile_fact(
            key,
            {
                "topic": topic,
                "status": "open"
            }
        )

        self.memory.add_event(
            f"wondered about: {topic}",
            "recent"
        )

    def resolve_personal_curiosity(
        self,
        topic
    ):

        key = (
            "personal curiosity: "
            + self.thread_key(topic)
        )

        self.memory.set_profile_fact(
            key,
            {
                "topic": topic,
                "status": "resolved"
            }
        )

    # -------------------------------------------------
    # Thread lookup
    # -------------------------------------------------

    def find_relevant_thread(
        self,
        detail=""
    ):

        threads = self.get_emotional_threads(
            statuses=[
                "current",
                "ongoing"
            ]
        )

        if not threads:
            return None

        detail_words = set(
            self.normalise(detail).split()
        )

        if detail_words:

            best_thread = None
            best_score = 0

            for thread in threads:

                topic_words = set(
                    self.normalise(
                        thread.get(
                            "topic",
                            ""
                        )
                    ).split()
                )

                score = len(
                    detail_words.intersection(
                        topic_words
                    )
                )

                if score > best_score:
                    best_score = score
                    best_thread = thread

            if best_thread:
                return best_thread

        # Cautious fallback: only use the latest active thread.
        return threads[-1]

    def find_recent_resolved_thread(self):

        threads = self.get_emotional_threads(
            statuses=[
                "resolved"
            ]
        )

        if threads:
            return threads[-1]

        return None

    def find_open_personal_curiosity(self):

        facts = self.memory.profile.get(
            "facts",
            {}
        )

        topics = []

        for key, value in facts.items():

            if not key.startswith(
                "personal curiosity:"
            ):
                continue

            if not isinstance(value, dict):
                continue

            if value.get("status") != "open":
                continue

            topic = value.get(
                "topic",
                ""
            )

            if topic:
                topics.append(topic)

        if topics:
            return topics[-1]

        return ""

    def get_emotional_threads(
        self,
        statuses
    ):

        facts = self.memory.profile.get(
            "facts",
            {}
        )

        threads = []

        for key, value in facts.items():

            if not key.startswith(
                "emotional thread:"
            ):
                continue

            if not isinstance(value, dict):
                continue

            if value.get("status") in statuses:
                threads.append(value)

        return threads

    # -------------------------------------------------
    # Helpers
    # -------------------------------------------------

    def thread_key(
        self,
        text
    ):

        cleaned = self.normalise(text)
        words = cleaned.split()

        return " ".join(words[:8])

    def normalise(
        self,
        text
    ):

        cleaned = re.sub(
            r"[^a-z0-9\s]",
            "",
            str(text).lower()
        )

        return " ".join(
            cleaned.split()
        )

    def make_result(
        self,
        reply,
        follow_up=None
    ):

        return {
            "reply": reply,
            "follow_up": follow_up
        }