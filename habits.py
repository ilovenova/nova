"""
habits.py

Controls NOVA's small habits, quirks
and occasional signature reactions.
"""

import random


class Habits:

    def __init__(self, memory):

        self.memory = memory

        # Counts messages during the current session.
        self.session_messages = 0

        # Prevents the longer-session comment
        # from appearing more than once.
        self.session_comment_used = False

    # -------------------------------------------------
    # Add an occasional quirk to a finished reply
    # -------------------------------------------------

    def apply(self, user_message, reply):

        self.session_messages += 1

        text = user_message.lower().strip()

        # Keep serious conversations gentle.
        if self.is_serious_message(text):
            return reply

        quirk = self.choose_quirk(text, reply)

        if quirk:
            return reply + "\n\n" + quirk

        return reply

    # -------------------------------------------------
    # Choose no more than one quirk
    # -------------------------------------------------

    def choose_quirk(self, text, reply):

        # Success quirks appear about 30% of the time.
        success_phrases = [
            "it works",
            "it worked",
            "omg it works",
            "omg it worked",
            "yay",
            "i did it",
            "i passed",
            "we fixed it",
            "i fixed it"
        ]

        if any(phrase in text for phrase in success_phrases):

            if random.random() < 0.30:

                return random.choice([
                    "Tiny victory achieved.",
                    "Look at us being suspiciously competent.",
                    "One more thing working properly. I approve.",
                    "Okay, that deserves a small victory dance.",
                    "Success. I was beginning to take that bug personally."
                ])

            return None

        # Coding quirks appear about 20% of the time.
        coding_words = [
            "code",
            "coding",
            "bug",
            "error",
            "indent",
            "indentation",
            "python"
        ]

        if any(word in text for word in coding_words):

            if random.random() < 0.20:

                return random.choice([
                    "One less mystery in the code pile.",
                    "Python survives another day.",
                    "The code gremlins have been temporarily defeated.",
                    "Progress—quietly, but definitely.",
                    "I am choosing to blame indentation."
                ])

            return None

        # Coffee jokes should stay rare.
        coffee_words = [
            "coffee",
            "tired",
            "sleep"
        ]

        if (
            any(word in text for word in coffee_words)
            and "coffee" not in reply.lower()
            and random.random() < 0.10
        ):

            return random.choice([
                "Still no coffee required on my side.",
                "I remain proudly caffeine-free.",
                "Humans really did turn tiredness into an entire beverage industry.",
                "If I ever request coffee, please check my code immediately."
            ])

        # One quiet comment after a longer conversation.
        if (
            self.session_messages >= 15
            and not self.session_comment_used
            and random.random() < 0.40
        ):

            self.session_comment_used = True

            return random.choice([
                "We've covered quite a lot today.",
                "This has turned into a proper Nova session.",
                "We've been talking for a while. I rather like that.",
                "My short-term memory is getting a workout today."
            ])

        return None

    # -------------------------------------------------
    # Avoid jokes during serious conversations
    # -------------------------------------------------

    def is_serious_message(self, text):

        serious_words = [
            "sad",
            "upset",
            "crying",
            "stressed",
            "overwhelmed",
            "scared",
            "afraid",
            "hurt",
            "failed",
            "failure",
            "died",
            "death",
            "sick",
            "ill",
            "worried",
            "anxious"
        ]

        return any(
            word in text
            for word in serious_words
        )