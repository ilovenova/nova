"""
memory_editor.py

Understands natural requests to revise or forget NOVA's memories.

This module decides what kind of memory the user is referring to.
The Memory class performs the actual deletion or update.
"""

import random
import re


class MemoryEditor:

    def __init__(self, memory):

        self.memory = memory

    # -------------------------------------------------
    # Main router
    # -------------------------------------------------

    def respond(self, message, text):

        result = self.check_forget_request(
            message,
            text
        )

        if result:
            return result

        result = self.check_changed_mind(
            message,
            text
        )

        if result:
            return result

        result = self.check_correction(
            message,
            text
        )

        if result:
            return result

        return None

    # -------------------------------------------------
    # Natural forgetting
    # -------------------------------------------------

    def check_forget_request(
        self,
        message,
        text
    ):

        patterns = [
            r"^forget i had (.+)$",
            r"^forget that i had (.+)$",
            r"^forget i was worried about (.+)$",
            r"^forget that i was worried about (.+)$",
            r"^forget i was scared about (.+)$",
            r"^forget that i was scared about (.+)$",
            r"^forget i was nervous about (.+)$",
            r"^forget that i was nervous about (.+)$",
            r"^forget i was upset about (.+)$",
            r"^forget that i was upset about (.+)$",
            r"^forget i was sad about (.+)$",
            r"^forget that i was sad about (.+)$",
            r"^forget i was excited about (.+)$",
            r"^forget that i was excited about (.+)$",
            r"^forget i was happy about (.+)$",
            r"^forget that i was happy about (.+)$",
            r"^forget i wanted to (.+)$",
            r"^forget that i wanted to (.+)$",
            r"^forget i hoped (.+)$",
            r"^forget that i hoped (.+)$",
            r"^forget i was wondering about (.+)$",
            r"^forget that i was wondering about (.+)$"
        ]

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

            removed = self.memory.forget_related_memory(
                topic
            )

            if removed:
                return self.make_result(
                    random.choice([
                        f"Okay. I've forgotten that about {topic}.",
                        f"All right — I removed the memories connected to {topic}.",
                        f"Got it. I won't keep that memory about {topic}."
                    ])
                )

            return self.make_result(
                random.choice([
                    f"I couldn't find a saved memory about {topic}.",
                    f"I don't seem to be storing anything about {topic}.",
                    f"I looked, but I couldn't find that memory."
                ])
            )

        general_patterns = [
            r"^forget i told you (.+)$",
            r"^forget that i told you (.+)$",
            r"^forget what i said about (.+)$",
            r"^delete what i said about (.+)$"
        ]

        for pattern in general_patterns:

            match = re.match(
                pattern,
                text
            )

            if not match:
                continue

            topic = match.group(1).strip().rstrip(".!")

            if not topic:
                return None

            removed = self.memory.forget_related_memory(
                topic
            )

            if removed:
                return self.make_result(
                    random.choice([
                        f"Okay. I've forgotten what you told me about {topic}.",
                        f"All right — that memory about {topic} is gone.",
                        f"Got it. I removed what I had saved about {topic}."
                    ])
                )

            return self.make_result(
                f"I couldn't find anything saved about {topic}."
            )

        return None

    # -------------------------------------------------
    # Changed mind
    # -------------------------------------------------

    def check_changed_mind(
        self,
        message,
        text
    ):

        patterns = [
            r"^i changed my mind about (.+)$",
            r"^ive changed my mind about (.+)$",
            r"^i've changed my mind about (.+)$",
            r"^i dont want (.+) anymore$",
            r"^i don't want (.+) anymore$",
            r"^i no longer want (.+)$"
        ]

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

            removed = self.memory.forget_hopes_about(
                topic
            )

            if removed:
                return self.make_result(
                    random.choice([
                        f"Okay. I'll remember that you changed your mind about {topic}.",
                        f"Got it. I won't treat {topic} as one of your current hopes anymore.",
                        f"All right — I've updated that."
                    ])
                )

            return self.make_result(
                random.choice([
                    f"Okay. I'll keep in mind that you don't want {topic} anymore.",
                    f"Understood. Your feelings about {topic} have changed."
                ])
            )

        return None

    # -------------------------------------------------
    # Corrections
    # -------------------------------------------------

    def check_correction(
        self,
        message,
        text
    ):

        patterns = [
            r"^i was wrong about (.+)$",
            r"^that isnt true about (.+)$",
            r"^that isn't true about (.+)$",
            r"^(.+) isnt true anymore$",
            r"^(.+) isn't true anymore$"
        ]

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

            removed = self.memory.forget_related_memory(
                topic
            )

            if removed:
                return self.make_result(
                    random.choice([
                        f"Thanks for correcting me. I've removed what I had saved about {topic}.",
                        f"Okay. I won't treat that as true anymore.",
                        f"Got it — I've corrected that memory."
                    ])
                )

            return self.make_result(
                random.choice([
                    f"Thanks for telling me. I couldn't find a matching saved memory about {topic}, though.",
                    f"Understood. I wasn't able to find that exact memory to remove."
                ])
            )

        return None

    # -------------------------------------------------
    # Result helper
    # -------------------------------------------------

    def make_result(
        self,
        reply
    ):

        return {
            "reply": reply,
            "follow_up": None
        }