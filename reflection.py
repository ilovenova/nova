"""
reflection.py

Lets NOVA connect present messages with recent emotional threads.

Reflection does not create memories by itself. It looks at memories
that already exist and decides whether a gentle connection may help.

Core rules:
- make cautious guesses, never claims
- accept "no" immediately
- do not force an old topic
- ask at most one reflective question
- sometimes reflect without asking anything
"""

import random
import re


class Reflection:

    def __init__(self, memory):

        self.memory = memory

    # -------------------------------------------------
    # Main router
    # -------------------------------------------------

    def respond(self, message, text):

        result = self.check_guess_opening(
            message,
            text
        )

        if result:
            return result

        result = self.check_reflective_success(
            message,
            text
        )

        if result:
            return result

        return None

    # -------------------------------------------------
    # Guess openings
    # -------------------------------------------------

    def check_guess_opening(
        self,
        message,
        text
    ):

        openings = [
            "guess what",
            "guess what!",
            "youll never guess",
            "you'll never guess",
            "something happened",
            "i have news",
            "ive got news",
            "i've got news"
        ]

        if text not in openings:
            return None

        thread = self.find_best_active_thread()

        if not thread:
            return self.make_result(
                random.choice([
                    "What happened?",
                    "Ooh, tell me.",
                    "Go on — what's the news?"
                ])
            )

        topic = thread.get(
            "topic",
            ""
        )

        if not topic:
            return self.make_result(
                "What happened?"
            )

        return self.make_result(
            random.choice([
                f"Is it about {topic}?",
                f"Does this have something to do with {topic}?",
                f"Wait — is this about {topic}?"
            ]),
            {
                "kind": "reflection",
                "question_type": "topic_guess",
                "topic": topic
            }
        )

    # -------------------------------------------------
    # Success reflection
    # -------------------------------------------------

    def check_reflective_success(
        self,
        message,
        text
    ):

        patterns = [
            r"^i passed$",
            r"^i passed!$",
            r"^i did it$",
            r"^i did it!$",
            r"^i finally did it$",
            r"^i finally did it!$",
            r"^it worked$",
            r"^it worked!$"
        ]

        if not any(
            re.match(pattern, text)
            for pattern in patterns
        ):
            return None

        thread = self.find_best_active_thread()

        if not thread:
            return None

        topic = thread.get(
            "topic",
            ""
        )

        if not topic:
            return None

        # A bare success message is ambiguous, so Nova asks once.
        return self.make_result(
            random.choice([
                f"Was it about {topic}?",
                f"Is this the thing with {topic}?",
                f"Did something finally go right with {topic}?"
            ]),
            {
                "kind": "reflection",
                "question_type": "success_guess",
                "topic": topic
            }
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
        topic = context.get(
            "topic",
            "that"
        )
        question_type = context.get(
            "question_type",
            ""
        )

        if self.is_yes(text):

            if question_type == "success_guess":

                self.resolve_thread(
                    topic
                )

                return {
                    "reply": random.choice([
                        f"I thought it might be. Remember when {topic} felt so difficult? Well, you did it.",
                        f"Yes! You were worried about {topic} before, and now look at you.",
                        f"All those hard moments with {topic} — and you kept going. You did it.",
                        f"See? {topic} once felt so heavy, and now you have this moment."
                    ]),
                    "follow_up": None
                }

            return {
                "reply": random.choice([
                    f"I had a feeling it might be about {topic}. Tell me what happened.",
                    f"Ah, yes — {topic}. Go on.",
                    f"I thought so. What's the news?"
                ]),
                "follow_up": None
            }

        if self.is_no(text):

            return {
                "reply": random.choice([
                    "Oh, something else then. What happened?",
                    "No problem — wrong guess. Tell me.",
                    "Ah, not that. What's the news?",
                    "Okay, I won't force that connection. What happened?"
                ]),
                "follow_up": None
            }

        if self.is_uncertain(text):

            return {
                "reply": random.choice([
                    "Maybe, then. Tell me what happened and we'll see.",
                    "That's okay. Go on.",
                    "Fair enough — tell me the news."
                ]),
                "follow_up": None
            }

        # The user may answer with the actual subject instead of yes/no.
        if self.is_meaningful_text(text):

            return {
                "reply": random.choice([
                    f"Ohh, {message.strip().rstrip('.!')} — tell me more.",
                    f"Ah, so it's about {message.strip().rstrip('.!')}. What happened?",
                    "Got it. Go on."
                ]),
                "follow_up": None
            }

        return None

    # -------------------------------------------------
    # Thread lookup and updates
    # -------------------------------------------------

    def find_best_active_thread(self):

        facts = self.memory.profile.get(
            "facts",
            {}
        )

        candidates = []

        for key, value in facts.items():

            if not key.startswith(
                "emotional thread:"
            ):
                continue

            if not isinstance(value, dict):
                continue

            if value.get("status") not in [
                "current",
                "ongoing"
            ]:
                continue

            topic = value.get(
                "topic",
                ""
            )

            if topic:
                candidates.append(value)

        if not candidates:
            return None

        # Dictionaries retain insertion order in modern Python.
        # The latest saved active thread is the safest candidate.
        return candidates[-1]

    def resolve_thread(
        self,
        topic
    ):

        facts = self.memory.profile.get(
            "facts",
            {}
        )

        normalised_topic = self.normalise(
            topic
        )

        for key, value in list(
            facts.items()
        ):

            if not key.startswith(
                "emotional thread:"
            ):
                continue

            if not isinstance(value, dict):
                continue

            saved_topic = self.normalise(
                value.get(
                    "topic",
                    ""
                )
            )

            if saved_topic != normalised_topic:
                continue

            value["status"] = "resolved"
            value["emotion"] = "proud"

        self.memory.save_all()

    # -------------------------------------------------
    # Reply helpers
    # -------------------------------------------------

    def is_yes(self, text):

        return text in [
            "yes",
            "yeah",
            "yep",
            "yea",
            "it is",
            "it was",
            "yes it is",
            "yes it was",
            "youre right",
            "you're right",
            "your right",
            "exactly",
            "correct",
            "thats right",
            "that's right"
        ]

    def is_no(self, text):

        return text in [
            "no",
            "nope",
            "nah",
            "not that",
            "no it isnt",
            "no it isn't",
            "no it wasnt",
            "no it wasn't",
            "it isnt",
            "it isn't",
            "it wasnt",
            "it wasn't",
            "youre wrong",
            "you're wrong",
            "wrong guess"
        ]

    def is_uncertain(self, text):

        return text in [
            "maybe",
            "possibly",
            "im not sure",
            "i'm not sure",
            "not sure",
            "kind of",
            "sort of"
        ]

    def is_meaningful_text(self, text):

        cleaned = re.sub(
            r"[^a-z0-9\s']",
            "",
            text
        ).strip()

        return len(
            cleaned.split()
        ) >= 1

    def normalise(self, text):

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