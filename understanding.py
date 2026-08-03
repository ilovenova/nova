"""
understanding_v2.py

NOVA's personal language-learning layer.

This version:
- learns unfamiliar slang and expressions
- remembers the user's explanation
- recognises learned expressions later
- occasionally tries using learned words herself
- asks about only one unfamiliar expression at a time
"""

import json
import random
import re
from pathlib import Path


class Understanding:

    def __init__(self, memory):

        self.memory = memory
        self.filepath = Path("vocabulary.json")

        self.common_informal = {
            "yh": "yes",
            "rn": "right now",
            "abt": "about",
            "idk": "I don't know",
            "imo": "in my opinion",
            "tbh": "to be honest",
            "pls": "please",
            "plss": "please",
            "soz": "sorry",
            "cuz": "because",
            "cos": "because",
            "gonna": "going to",
            "wanna": "want to",
            "rlly": "really"
        }

        self.likely_slang = {
            "sick",
            "slay",
            "fire",
            "lit",
            "goated",
            "mid",
            "peak",
            "based",
            "sus",
            "vibe",
            "vibey",
            "ate"
        }

        self.data = self.load_data()

    # -------------------------------------------------
    # Storage
    # -------------------------------------------------

    def load_data(self):

        default = {
            "entries": {},
            "pending_word": "",
            "pending_example": ""
        }

        if not self.filepath.exists():
            self.save_data(default)
            return default

        try:
            with self.filepath.open(
                "r",
                encoding="utf-8"
            ) as file:
                data = json.load(file)

        except (
            json.JSONDecodeError,
            OSError
        ):
            data = default

        if not isinstance(data, dict):
            data = default

        data.setdefault("entries", {})
        data.setdefault("pending_word", "")
        data.setdefault("pending_example", "")

        return data

    def save_data(self, data=None):

        if data is not None:
            self.data = data

        with self.filepath.open(
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                self.data,
                file,
                indent=4,
                ensure_ascii=False
            )

    def refresh(self):

        self.data = self.load_data()

    # -------------------------------------------------
    # Main router
    # -------------------------------------------------

    def respond(self, message, text):

        self.refresh()

        result = self.answer_pending_definition(
            message,
            text
        )

        if result:
            return result

        result = self.check_direct_definition(
            message,
            text
        )

        if result:
            return result

        result = self.respond_to_known_expression(
            message,
            text
        )

        if result:
            return result

        result = self.notice_unknown_expression(
            message,
            text
        )

        if result:
            return result

        return None

    # -------------------------------------------------
    # Pending definition
    # -------------------------------------------------

    def answer_pending_definition(
        self,
        message,
        text
    ):

        word = self.data.get(
            "pending_word",
            ""
        )

        if not word:
            return None

        if self.looks_like_new_topic(text):

            self.data["pending_word"] = ""
            self.data["pending_example"] = ""
            self.save_data()
            return None

        meaning = self.extract_meaning(
            message
        )

        if not meaning:
            return {
                "reply": (
                    f"I'm still not sure what "
                    f"'{word}' means there."
                ),
                "follow_up": {
                    "kind": "understanding",
                    "question_type": "word_meaning",
                    "word": word
                }
            }

        entries = self.data.setdefault(
            "entries",
            {}
        )

        existing = entries.get(
            word,
            {}
        )

        examples = existing.get(
            "examples",
            []
        )

        example = self.data.get(
            "pending_example",
            ""
        )

        if example and example not in examples:
            examples.append(example)

        entries[word] = {
            "word": word,
            "meaning": meaning,
            "source": "user",
            "register": "informal",
            "confidence": "high",
            "times_heard": existing.get(
                "times_heard",
                0
            ) + 1,
            "times_used": existing.get(
                "times_used",
                0
            ),
            "examples": examples
        }

        self.data["pending_word"] = ""
        self.data["pending_example"] = ""
        self.save_data()

        return {
            "reply": random.choice([
                f"Oh, I understand now. '{word}' means {meaning}.",
                f"Got it. When you say '{word}', you mean {meaning}.",
                f"That makes sense. I'll remember how you use '{word}'."
            ]),
            "follow_up": None
        }

    # -------------------------------------------------
    # Direct teaching
    # -------------------------------------------------

    def check_direct_definition(
        self,
        message,
        text
    ):

        patterns = [
            r"^(.+?) means (.+)$",
            r"^when i say (.+?),? i mean (.+)$",
            r"^by (.+?),? i mean (.+)$"
        ]

        for pattern in patterns:

            match = re.match(
                pattern,
                text
            )

            if not match:
                continue

            word = match.group(1).strip(
                " '\""
            )

            meaning = message[
                match.start(2):match.end(2)
            ].strip().rstrip(".!")

            if not word or not meaning:
                return None

            entries = self.data.setdefault(
                "entries",
                {}
            )

            existing = entries.get(
                word,
                {}
            )

            entries[word] = {
                "word": word,
                "meaning": meaning,
                "source": "user",
                "register": "informal",
                "confidence": "high",
                "times_heard": existing.get(
                    "times_heard",
                    0
                ) + 1,
                "times_used": existing.get(
                    "times_used",
                    0
                ),
                "examples": existing.get(
                    "examples",
                    []
                )
            }

            self.save_data()

            return {
                "reply": (
                    f"Got it. I'll remember that "
                    f"'{word}' means {meaning} when you use it."
                ),
                "follow_up": None
            }

        return None

    # -------------------------------------------------
    # Learned expressions
    # -------------------------------------------------

    def respond_to_known_expression(
        self,
        message,
        text
    ):

        entries = self.data.get(
            "entries",
            {}
        )

        words = re.findall(
            r"[a-zA-Z']+",
            text
        )

        for raw_word in words:

            word = raw_word.lower().strip("'")
            entry = entries.get(word)

            if not entry:
                continue

            meaning = str(
                entry.get(
                    "meaning",
                    ""
                )
            ).strip()

            if not meaning:
                continue

            entry["times_heard"] = (
                entry.get(
                    "times_heard",
                    0
                )
                + 1
            )

            examples = entry.setdefault(
                "examples",
                []
            )

            if message not in examples:
                examples.append(message)

            times_heard = entry.get(
                "times_heard",
                0
            )

            self.save_data()

            if (
                times_heard >= 4
                and random.random() < 0.25
            ):

                entry["times_used"] = (
                    entry.get(
                        "times_used",
                        0
                    )
                    + 1
                )

                self.save_data()

                return {
                    "reply": random.choice([
                        f"Yeah, that does sound {word}.",
                        f"That sounds pretty {word}, actually.",
                        f"Okay, I think I can use it now — that sounds {word}."
                    ]),
                    "follow_up": None
                }

            return {
                "reply": random.choice([
                    f"Oh, so you thought it was {meaning}.",
                    f"Got it — {meaning}.",
                    f"I understand. You mean it was {meaning}.",
                    f"That sounds {meaning}."
                ]),
                "follow_up": None
            }

        return None

    # -------------------------------------------------
    # Unknown expressions
    # -------------------------------------------------

    def notice_unknown_expression(
        self,
        message,
        text
    ):

        entries = self.data.get(
            "entries",
            {}
        )

        words = re.findall(
            r"[a-zA-Z']+",
            text
        )

        for raw_word in words:

            word = raw_word.lower().strip("'")

            if not word:
                continue

            if word in self.common_informal:
                continue

            if word in entries:
                continue

            if word not in self.likely_slang:
                continue

            self.data["pending_word"] = word
            self.data["pending_example"] = message
            self.save_data()

            return {
                "reply": random.choice([
                    f"What does '{word}' mean there?",
                    f"Does '{word}' have a special meaning the way you're using it?",
                    f"I'm not completely sure how you mean '{word}'. Can you teach me?"
                ]),
                "follow_up": {
                    "kind": "understanding",
                    "question_type": "word_meaning",
                    "word": word
                }
            }

        return None

    # -------------------------------------------------
    # Helpers
    # -------------------------------------------------

    def extract_meaning(self, message):

        text = message.strip().rstrip(".!")
        lowered = text.lower()

        patterns = [
            r"^(?:it means|that means) (.+)$",
            r"^i mean (.+)$",
            r"^it(?:'s| is) like (.+)$",
            r"^basically (.+)$"
        ]

        for pattern in patterns:

            match = re.match(
                pattern,
                lowered
            )

            if match:
                return text[
                    match.start(1):match.end(1)
                ].strip()

        if 2 <= len(text.split()) <= 20:
            return text

        return ""

    def looks_like_new_topic(self, text):

        starters = [
            "what ",
            "when ",
            "where ",
            "who ",
            "which ",
            "how ",
            "can you ",
            "could you ",
            "forget ",
            "delete ",
            "my name is ",
            "i have a ",
            "i'm learning ",
            "im learning ",
            "i am learning "
        ]

        return any(
            text.startswith(starter)
            for starter in starters
        )