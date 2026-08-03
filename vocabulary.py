"""
vocabulary.py

Stores words, slang and expressions NOVA learns from the user.
"""

from utils import load_json, save_json


class Vocabulary:

    def __init__(self, filename="vocabulary.json"):

        self.filename = filename
        self.data = load_json(
            filename,
            {
                "entries": {},
                "pending_word": "",
                "pending_example": ""
            }
        )

        self.data.setdefault("entries", {})
        self.data.setdefault("pending_word", "")
        self.data.setdefault("pending_example", "")

        self.save()

    def save(self):

        save_json(
            self.filename,
            self.data
        )

    def remember_pending(
        self,
        word,
        example
    ):

        self.data["pending_word"] = word.strip().lower()
        self.data["pending_example"] = example.strip()
        self.save()

    def clear_pending(self):

        self.data["pending_word"] = ""
        self.data["pending_example"] = ""
        self.save()

    def pending(self):

        word = self.data.get(
            "pending_word",
            ""
        )

        if not word:
            return None

        return {
            "word": word,
            "example": self.data.get(
                "pending_example",
                ""
            )
        }

    def learn(
        self,
        word,
        meaning,
        example="",
        source="user"
    ):

        key = word.strip().lower()

        if not key:
            return False

        entries = self.data.setdefault(
            "entries",
            {}
        )

        existing = entries.get(
            key,
            {}
        )

        examples = existing.get(
            "examples",
            []
        )

        if example and example not in examples:
            examples.append(example)

        entries[key] = {
            "word": key,
            "meaning": meaning.strip(),
            "source": source,
            "register": existing.get(
                "register",
                "informal"
            ),
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

        self.clear_pending()
        self.save()

        return True

    def get(self, word):

        return self.data.get(
            "entries",
            {}
        ).get(
            word.strip().lower()
        )

    def knows(self, word):

        return self.get(word) is not None

    def record_heard(
        self,
        word,
        example=""
    ):

        entry = self.get(word)

        if not entry:
            return False

        entry["times_heard"] = (
            entry.get("times_heard", 0)
            + 1
        )

        examples = entry.setdefault(
            "examples",
            []
        )

        if example and example not in examples:
            examples.append(example)

        self.save()
        return True

    def mark_used(self, word):

        entry = self.get(word)

        if not entry:
            return False

        entry["times_used"] = (
            entry.get("times_used", 0)
            + 1
        )

        self.save()
        return True