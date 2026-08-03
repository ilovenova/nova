"""
dictionary.py

NOVA's personal dictionary.

Stores words and expressions NOVA already knows, is taught,
or learns naturally through conversation.
"""

import json
from pathlib import Path


class PersonalDictionary:

    def __init__(self, filename="vocabulary.json"):
        self.filepath = Path(filename)
        self.data = self.load_data()

    def default_data(self):
        return {
            "entries": {},
            "pending_word": "",
            "pending_example": ""
        }

    def load_data(self):
        default = self.default_data()

        if not self.filepath.exists():
            self.save_data(default)
            return default

        try:
            with self.filepath.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except (json.JSONDecodeError, OSError):
            data = default

        if not isinstance(data, dict):
            data = default

        data.setdefault("entries", {})
        data.setdefault("pending_word", "")
        data.setdefault("pending_example", "")

        self._normalise_all_entries(data)
        return data

    def save_data(self, data=None):
        if data is not None:
            self.data = data

        with self.filepath.open("w", encoding="utf-8") as file:
            json.dump(
                self.data,
                file,
                indent=4,
                ensure_ascii=False
            )

    def refresh(self):
        self.data = self.load_data()

    def _normalise_key(self, word):
        return str(word).strip().lower()

    def _normalise_all_entries(self, data):
        entries = data.setdefault("entries", {})
        normalised = {}

        for raw_key, raw_entry in entries.items():
            key = self._normalise_key(raw_key)

            if not key:
                continue

            normalised[key] = self._normalise_entry(
                key,
                raw_entry
            )

        data["entries"] = normalised

    def _normalise_entry(self, word, raw_entry):
        if not isinstance(raw_entry, dict):
            raw_entry = {}

        meanings = raw_entry.get("meanings")

        if not isinstance(meanings, list):
            old_meaning = str(
                raw_entry.get("meaning", "")
            ).strip()

            meanings = []

            if old_meaning:
                meanings.append({
                    "meaning": old_meaning,
                    "kind": raw_entry.get(
                        "register",
                        "unknown"
                    ),
                    "confidence": raw_entry.get(
                        "confidence",
                        "high"
                    ),
                    "source": raw_entry.get(
                        "source",
                        "user"
                    ),
                    "examples": list(
                        raw_entry.get(
                            "examples",
                            []
                        )
                    )
                })

        cleaned = []

        for meaning_data in meanings:
            if not isinstance(meaning_data, dict):
                continue

            meaning = str(
                meaning_data.get("meaning", "")
            ).strip()

            if not meaning:
                continue

            examples = meaning_data.get("examples", [])

            if not isinstance(examples, list):
                examples = []

            cleaned.append({
                "meaning": meaning,
                "kind": str(
                    meaning_data.get(
                        "kind",
                        "unknown"
                    )
                ).strip() or "unknown",
                "confidence": str(
                    meaning_data.get(
                        "confidence",
                        "high"
                    )
                ).strip() or "high",
                "source": str(
                    meaning_data.get(
                        "source",
                        "user"
                    )
                ).strip() or "user",
                "examples": examples
            })

        return {
            "word": word,
            "meanings": cleaned,
            "times_heard": int(
                raw_entry.get(
                    "times_heard",
                    0
                )
            ),
            "times_used": int(
                raw_entry.get(
                    "times_used",
                    0
                )
            )
        }

    def set_pending(self, word, example=""):
        self.data["pending_word"] = self._normalise_key(word)
        self.data["pending_example"] = str(example).strip()
        self.save_data()

    def get_pending(self):
        word = self.data.get("pending_word", "")

        if not word:
            return None

        return {
            "word": word,
            "example": self.data.get(
                "pending_example",
                ""
            )
        }

    def clear_pending(self):
        self.data["pending_word"] = ""
        self.data["pending_example"] = ""
        self.save_data()

    def knows(self, word):
        key = self._normalise_key(word)
        return key in self.data.get("entries", {})

    def get_entry(self, word):
        key = self._normalise_key(word)
        return self.data.get("entries", {}).get(key)

    def get_meanings(self, word):
        entry = self.get_entry(word)

        if not entry:
            return []

        return list(entry.get("meanings", []))

    def get_best_meaning(self, word, preferred_kind=None):
        meanings = self.get_meanings(word)

        if not meanings:
            return None

        if preferred_kind:
            wanted = str(preferred_kind).strip().lower()

            for meaning in meanings:
                if (
                    str(meaning.get("kind", ""))
                    .strip()
                    .lower()
                    == wanted
                ):
                    return meaning

        return meanings[0]

    def add_meaning(
        self,
        word,
        meaning,
        kind="unknown",
        source="user",
        confidence="high",
        example=""
    ):
        key = self._normalise_key(word)
        clean_meaning = str(meaning).strip()

        if not key or not clean_meaning:
            return False

        entries = self.data.setdefault("entries", {})
        entry = entries.setdefault(
            key,
            {
                "word": key,
                "meanings": [],
                "times_heard": 0,
                "times_used": 0
            }
        )

        meanings = entry.setdefault("meanings", [])

        for existing in meanings:
            if (
                existing.get("meaning", "")
                .strip()
                .lower()
                == clean_meaning.lower()
            ):
                if example:
                    examples = existing.setdefault(
                        "examples",
                        []
                    )

                    if example not in examples:
                        examples.append(example)

                existing["kind"] = str(kind).strip() or "unknown"
                existing["source"] = str(source).strip() or "user"
                existing["confidence"] = (
                    str(confidence).strip() or "high"
                )

                entry["times_heard"] = (
                    entry.get("times_heard", 0) + 1
                )

                self.save_data()
                return True

        examples = []

        if example:
            examples.append(str(example).strip())

        meanings.append({
            "meaning": clean_meaning,
            "kind": str(kind).strip() or "unknown",
            "confidence": str(confidence).strip() or "high",
            "source": str(source).strip() or "user",
            "examples": examples
        })

        entry["times_heard"] = (
            entry.get("times_heard", 0) + 1
        )

        self.save_data()
        return True

    def edit_meaning(
        self,
        word,
        old_meaning,
        new_meaning,
        new_kind=None
    ):
        entry = self.get_entry(word)

        if not entry:
            return False

        old_clean = str(old_meaning).strip().lower()
        new_clean = str(new_meaning).strip()

        if not new_clean:
            return False

        for meaning_data in entry.get("meanings", []):
            if (
                meaning_data.get("meaning", "")
                .strip()
                .lower()
                != old_clean
            ):
                continue

            meaning_data["meaning"] = new_clean

            if new_kind is not None:
                meaning_data["kind"] = (
                    str(new_kind).strip() or "unknown"
                )

            self.save_data()
            return True

        return False

    def remove_meaning(self, word, meaning):
        key = self._normalise_key(word)
        entry = self.get_entry(key)

        if not entry:
            return False

        wanted = str(meaning).strip().lower()
        meanings = entry.get("meanings", [])

        remaining = [
            item
            for item in meanings
            if (
                item.get("meaning", "")
                .strip()
                .lower()
                != wanted
            )
        ]

        if len(remaining) == len(meanings):
            return False

        if remaining:
            entry["meanings"] = remaining
        else:
            self.data["entries"].pop(key, None)

        self.save_data()
        return True

    def forget_word(self, word):
        key = self._normalise_key(word)
        entries = self.data.get("entries", {})

        if key not in entries:
            return False

        del entries[key]
        self.save_data()
        return True

    def record_heard(self, word, example=""):
        entry = self.get_entry(word)

        if not entry:
            return False

        entry["times_heard"] = (
            entry.get("times_heard", 0) + 1
        )

        if example and entry.get("meanings"):
            examples = entry["meanings"][0].setdefault(
                "examples",
                []
            )

            if example not in examples:
                examples.append(example)

        self.save_data()
        return True

    def record_used(self, word):
        entry = self.get_entry(word)

        if not entry:
            return False

        entry["times_used"] = (
            entry.get("times_used", 0) + 1
        )

        self.save_data()
        return True

    def search(self, query):
        wanted = self._normalise_key(query)

        if not wanted:
            return []

        results = []

        for word, entry in self.data.get(
            "entries",
            {}
        ).items():
            score = 0

            if wanted == word:
                score += 100
            elif wanted in word:
                score += 50

            for meaning_data in entry.get("meanings", []):
                meaning_text = meaning_data.get(
                    "meaning",
                    ""
                ).lower()

                if wanted in meaning_text:
                    score += 20

                for example in meaning_data.get(
                    "examples",
                    []
                ):
                    if wanted in str(example).lower():
                        score += 5

            if score > 0:
                results.append({
                    "word": word,
                    "score": score,
                    "entry": entry
                })

        results.sort(
            key=lambda item: (
                -item["score"],
                item["word"]
            )
        )

        return results

    def list_words(self):
        return sorted(
            self.data.get("entries", {}).keys()
        )