"""
language_adapter.py

NOVA 1.7.8 — Flexible Conversation Understanding

Provides cautious language normalisation before routing.
"""

import json
import re
from pathlib import Path


class LanguageAdapter:

    def __init__(self):

        self.abbreviations = {
            "rn": "right now",
            "bc": "because",
            "bcs": "because",
            "cuz": "because",
            "cos": "because",
            "idk": "i don't know",
            "ik": "i know",
            "imo": "in my opinion",
            "tbh": "to be honest",
            "ngl": "not going to lie",
            "btw": "by the way",
            "fr": "for real",
            "irl": "in real life",
            "atm": "at the moment",
            "nvm": "never mind",
            "yh": "yeah",
            "yep": "yes",
            "nope": "no",
            "pls": "please",
            "plz": "please",
            "thx": "thanks",
            "ty": "thank you",
            "abt": "about",
            "smth": "something",
            "somth": "something",
            "tho": "though",
            "rly": "really",
            "rlly": "really",
            "u": "you"
        }

        self.contractions = {
            "im": "i'm",
            "ive": "i've",
            "ill": "i'll",
            "id": "i'd",
            "dont": "don't",
            "doesnt": "doesn't",
            "didnt": "didn't",
            "cant": "can't",
            "couldnt": "couldn't",
            "wouldnt": "wouldn't",
            "wont": "won't",
            "isnt": "isn't",
            "arent": "aren't",
            "wasnt": "wasn't",
            "werent": "weren't",
            "hasnt": "hasn't",
            "havent": "haven't",
            "hadnt": "hadn't",
            "thats": "that's",
            "whats": "what's",
            "hows": "how's",
            "heres": "here's",
            "theres": "there's",
            "youre": "you're",
            "youve": "you've",
            "youll": "you'll",
            "shes": "she's",
            "hes": "he's",
            "theyre": "they're",
            "theyve": "they've",
            "theyll": "they'll",
            "weve": "we've",
            "whos": "who's"
        }

        self.user_phrase_path = Path(
            "language_patterns.json"
        )

        self.user_phrases = self.load_user_phrases()

        self.pending_unknown_word = ""
        self.pending_original_message = ""
        self.pending_suggested_word = ""

        self.common_word_suggestions = {
            "skary": "scary",
            "tierd": "tired",
            "tirred": "tired",
            "hapy": "happy",
            "stresed": "stressed",
            "woryed": "worried",
            "freind": "friend",
            "frend": "friend",
            "becuse": "because",
            "becuase": "because",
            "somthing": "something",
            "someting": "something",
            "alot": "a lot"
        }

        self.safe_phrase_repairs = [
            (
                r"^just wondering[, ]+",
                "",
                "high"
            ),
            (
                r"^i was just wondering[, ]+",
                "",
                "high"
            ),
            (
                r"^i'm just wondering[, ]+",
                "",
                "high"
            ),
            (
                r"^im just wondering[, ]+",
                "",
                "high"
            ),
            (
                r"^did you know[, ]+",
                "",
                "high"
            ),
            (
                r"^apparently[, ]+",
                "",
                "high"
            ),
            (
                r"^turns out[, ]+",
                "",
                "high"
            ),
            (
                r"^it turns out[, ]+",
                "",
                "high"
            ),
            (
                r"^i ended up (.+)$",
                r"i \1",
                "high"
            ),
            (
                r"^i was just (.+)$",
                r"i \1",
                "high"
            ),
            (
                r"^i started to (.+)$",
                r"i started \1",
                "high"
            ),
            (
                r"^i keep on (.+)$",
                r"i keep \1",
                "high"
            ),
            (
                r"\bi(?:'m| am) feeling "
                r"(tired|sad|happy|stressed|worried|scared|upset|"
                r"excited|proud|bored|angry|annoyed)\b",
                r"i feel \1",
                "high"
            ),
            (
                r"\bi(?:'ve| have) been feeling "
                r"(tired|sad|happy|stressed|worried|scared|upset|"
                r"excited|proud|bored|angry|annoyed)\b",
                r"i feel \1",
                "high"
            ),
            (
                r"\bi(?:'ve| have) been "
                r"(tired|sad|happy|stressed|worried|scared|upset|"
                r"excited|proud|bored|angry|annoyed)\b",
                r"i'm \1",
                "high"
            ),
            (
                r"\bi keep feeling "
                r"(tired|sad|happy|stressed|worried|scared|upset|"
                r"excited|proud|bored|angry|annoyed)\b",
                r"i feel \1",
                "high"
            ),
            (
                r"\b(i(?:'m| am) (?:tired|sad|happy|stressed|worried|"
                r"scared|upset|excited|proud|bored|angry|annoyed)) "
                r"(?:right now|at the moment)\b",
                r"\1",
                "high"
            ),
            (
                r"\b(i feel (?:tired|sad|happy|stressed|worried|"
                r"scared|upset|excited|proud|bored|angry|annoyed)) "
                r"(?:right now|at the moment)\b",
                r"\1",
                "high"
            ),
            (r"\bits was\b", "it was", "high"),
            (
                r"\bwhat did i told you\b",
                "what did i tell you",
                "high"
            ),
            (
                r"\bwhat did you asked me\b",
                "what did you ask me",
                "high"
            ),
            (r"\bi am agree\b", "i agree", "high"),
            (
                r"\bi didnt slept\b",
                "i didn't sleep",
                "high"
            ),
            (
                r"\bi dont knew\b",
                "i don't know",
                "high"
            )
        ]

    def adapt(self, message):

        original = str(message)

        normalised = self.normalise_spacing(
            original
        ).lower()

        normalised = re.sub(
            r"^(?:you|nova)\s*:\s*",
            "",
            normalised
        )

        frame = self.detect_conversation_frame(
            normalised
        )

        changes = []

        if self.is_phrase_management_command(
            normalised
        ):
            return {
                "original": original,
                "text": normalised,
                "changes": [],
                "changed": False,
                "confidence": "unchanged",
                "frame": frame
            }

        normalised, user_phrase_changes = (
            self.apply_user_phrases(
                normalised
            )
        )

        changes.extend(
            user_phrase_changes
        )

        normalised, word_changes = self.expand_known_words(
            normalised
        )

        changes.extend(word_changes)

        normalised, phrase_changes = self.repair_safe_phrases(
            normalised
        )

        changes.extend(phrase_changes)

        normalised = self.normalise_spacing(
            normalised
        )

        return {
            "original": original,
            "text": normalised,
            "changes": changes,
            "changed": bool(changes),
            "confidence": self.overall_confidence(
                changes
            ),
            "frame": frame
        }

    def detect_conversation_frame(
        self,
        text
    ):

        frames = [
            (
                "wondering",
                [
                    "just wondering ",
                    "i was just wondering ",
                    "i'm just wondering ",
                    "im just wondering "
                ]
            ),
            (
                "did_you_know",
                [
                    "did you know "
                ]
            ),
            (
                "unexpected_result",
                [
                    "turns out ",
                    "it turns out ",
                    "apparently "
                ]
            ),
            (
                "ended_up",
                [
                    "i ended up "
                ]
            ),
            (
                "background",
                [
                    "i was just "
                ]
            )
        ]

        for frame_name, starters in frames:

            if any(
                text.startswith(starter)
                for starter in starters
            ):
                return frame_name

        return ""

    def is_phrase_management_command(
        self,
        text
    ):

        command_starters = [
            "when i say ",
            "when i use ",
            "for me ",
            "forget the phrase ",
            "forget that phrase ",
            "forget that ",
            "delete the phrase ",
            "remove the phrase "
        ]

        return any(
            text.startswith(starter)
            for starter in command_starters
        )

    # -------------------------------------------------
    # Unknown-word clarification
    # -------------------------------------------------

    def detect_unknown_language(
        self,
        message
    ):

        if self.pending_unknown_word:
            return None

        normalised = self.normalise_spacing(
            message
        ).lower()

        normalised = re.sub(
            r"^(?:you|nova)\s*:\s*",
            "",
            normalised
        )

        tokens = re.findall(
            r"[a-z']+",
            normalised
        )

        for token in tokens:

            suggestion = self.common_word_suggestions.get(
                token
            )

            if not suggestion:
                continue

            self.pending_unknown_word = token
            self.pending_original_message = normalised
            self.pending_suggested_word = suggestion

            return {
                "word": token,
                "suggestion": suggestion,
                "original": normalised,
                "reply": (
                    f"Did you mean '{suggestion}' when you "
                    f"said '{token}', or is '{token}' an "
                    "intentional word with its own meaning?"
                )
            }

        return None

    def handle_unknown_word_reply(
        self,
        message
    ):

        if not self.pending_unknown_word:
            return {
                "handled": False
            }

        text = self.normalise_spacing(
            message
        ).lower().rstrip(".!")

        unknown = self.pending_unknown_word
        suggestion = self.pending_suggested_word
        original = self.pending_original_message

        correction_patterns = [
            rf"^i meant {re.escape(suggestion)}$",
            rf"^i meant to say {re.escape(suggestion)}$",
            rf"^yes i meant {re.escape(suggestion)}$",
            rf"^yeah i meant {re.escape(suggestion)}$",
            rf"^yh i meant {re.escape(suggestion)}$",
            r"^yes$",
            r"^yeah$",
            r"^yh$"
        ]

        if any(
            re.match(pattern, text)
            for pattern in correction_patterns
        ):

            interpreted = self.replace_pending_word(
                original,
                unknown,
                suggestion
            )

            self.clear_unknown_word_state()

            return {
                "handled": True,
                "reply": (
                    f"Got it — you meant '{suggestion}'."
                ),
                "interpreted_message": interpreted,
                "learned": False
            }

        correction_with_meaning = re.match(
            (
                rf"^i meant(?: to say)? {re.escape(suggestion)}"
                r"(?:,| and)? it means (.+)$"
            ),
            text
        )

        if correction_with_meaning:

            meaning = correction_with_meaning.group(
                1
            ).strip()

            self.learn_phrase(
                unknown,
                suggestion,
                category="correction"
            )

            interpreted = self.replace_pending_word(
                original,
                unknown,
                suggestion
            )

            self.clear_unknown_word_state()

            return {
                "handled": True,
                "reply": (
                    f"Got it — '{unknown}' was meant to be "
                    f"'{suggestion}', meaning {meaning}."
                ),
                "interpreted_message": interpreted,
                "learned": True
            }

        intentional_word_patterns = [
            rf"^no[, ]+{re.escape(unknown)} means (.+)$",
            rf"^{re.escape(unknown)} has its own meaning[, ]+it means (.+)$",
            rf"^i meant {re.escape(unknown)}[,; ]+it means (.+)$",
            rf"^i meant to say {re.escape(unknown)}[,; ]+it means (.+)$",
            rf"^yes i meant {re.escape(unknown)}[,; ]+it means (.+)$",
            rf"^yeah i meant {re.escape(unknown)}[,; ]+it means (.+)$"
        ]

        for pattern in intentional_word_patterns:

            match = re.match(
                pattern,
                text
            )

            if not match:
                continue

            meaning = match.group(
                1
            ).strip()

            if not meaning:
                continue

            self.learn_phrase(
                unknown,
                meaning,
                category="intentional_word"
            )

            interpreted = self.replace_pending_word(
                original,
                unknown,
                meaning
            )

            self.clear_unknown_word_state()

            return {
                "handled": True,
                "reply": (
                    f"Got it — '{unknown}' is its own word "
                    f"for you, meaning {meaning}."
                ),
                "interpreted_message": interpreted,
                "learned": True
            }

        if text in {
            f"{unknown} has its own meaning",
            f"i meant {unknown}",
            f"yes i meant {unknown}",
            f"yeah i meant {unknown}",
            f"yh i meant {unknown}"
        }:
            return {
                "handled": True,
                "reply": (
                    f"Okay — what does '{unknown}' mean?"
                ),
                "interpreted_message": "",
                "learned": False
            }

        meaning_patterns = [
            rf"^{re.escape(unknown)} means (.+)$",
            r"^it means (.+)$",
            r"^i mean (.+)$",
            r"^it is when (.+)$"
        ]

        for pattern in meaning_patterns:

            match = re.match(
                pattern,
                text
            )

            if not match:
                continue

            meaning = match.group(
                1
            ).strip()

            if not meaning:
                continue

            self.learn_phrase(
                unknown,
                meaning,
                category="learned_word"
            )

            interpreted = self.replace_pending_word(
                original,
                unknown,
                meaning
            )

            self.clear_unknown_word_state()

            return {
                "handled": True,
                "reply": (
                    f"Okay, I understand '{unknown}' now."
                ),
                "interpreted_message": interpreted,
                "learned": True
            }

        if text in {
            "neither",
            "no",
            "nope",
            "not that",
            "i dont know",
            "i don't know"
        }:
            self.clear_unknown_word_state()

            return {
                "handled": True,
                "reply": (
                    "Okay. I won't guess what it means."
                ),
                "interpreted_message": "",
                "learned": False
            }

        return {
            "handled": True,
            "reply": (
                f"I'm still not sure what '{unknown}' means. "
                "Can you explain it another way?"
            ),
            "interpreted_message": "",
            "learned": False
        }

    def replace_pending_word(
        self,
        message,
        old_word,
        new_text
    ):

        pattern = (
            r"(?<![a-z0-9'])"
            + re.escape(old_word)
            + r"(?![a-z0-9'])"
        )

        return re.sub(
            pattern,
            new_text,
            message,
            flags=re.IGNORECASE
        )

    def clear_unknown_word_state(self):

        self.pending_unknown_word = ""
        self.pending_original_message = ""
        self.pending_suggested_word = ""

    # -------------------------------------------------
    # Personal phrase learning
    # -------------------------------------------------

    def handle_learning_statement(
        self,
        message
    ):

        text = self.normalise_spacing(
            message
        ).lower().rstrip(".!")

        patterns = [
            (
                r"^when i say (.+?) i mean (.+)$",
                "phrase"
            ),
            (
                r"^when i use (.+?) i mean (.+)$",
                "phrase"
            ),
            (
                r"^for me (.+?) means (.+)$",
                "phrase"
            )
        ]

        for pattern, category in patterns:

            match = re.match(
                pattern,
                text
            )

            if not match:
                continue

            phrase = self.clean_learned_phrase(
                match.group(1)
            )

            meaning = self.clean_learned_phrase(
                match.group(2)
            )

            if not phrase or not meaning:
                return {
                    "handled": True,
                    "reply": (
                        "I understood that you were teaching "
                        "me a phrase, but I couldn't separate "
                        "the phrase from its meaning."
                    )
                }

            if phrase == meaning:
                return {
                    "handled": True,
                    "reply": (
                        "Those look like the same phrase to me. "
                        "Can you explain the meaning differently?"
                    )
                }

            self.learn_phrase(
                phrase,
                meaning,
                category=category
            )

            return {
                "handled": True,
                "reply": (
                    f"Got it. When you say '{phrase}', "
                    f"I'll understand it as '{meaning}'."
                ),
                "phrase": phrase,
                "meaning": meaning
            }

        forget_patterns = [
            r"^forget that (.+?) means (.+)$",
            r"^forget the phrase (.+)$",
            r"^forget that phrase (.+)$",
            r"^delete the phrase (.+)$",
            r"^remove the phrase (.+)$"
        ]

        for pattern in forget_patterns:

            match = re.match(
                pattern,
                text
            )

            if not match:
                continue

            phrase = self.clean_learned_phrase(
                match.group(1)
            )

            if self.forget_phrase(
                phrase
            ):
                return {
                    "handled": True,
                    "reply": (
                        f"Okay. I've forgotten the personal "
                        f"meaning of '{phrase}'."
                    )
                }

            return {
                "handled": True,
                "reply": (
                    f"I don't have a personal meaning saved "
                    f"for '{phrase}'."
                )
            }

        return {
            "handled": False
        }

    def learn_phrase(
        self,
        phrase,
        meaning,
        category="user"
    ):

        clean_phrase = self.clean_learned_phrase(
            phrase
        )

        clean_meaning = self.clean_learned_phrase(
            meaning
        )

        if not clean_phrase or not clean_meaning:
            return False

        self.user_phrases[
            clean_phrase
        ] = {
            "meaning": clean_meaning,
            "category": str(
                category
            ).strip() or "user"
        }

        self.save_user_phrases()
        return True

    def forget_phrase(
        self,
        phrase
    ):

        clean_phrase = self.clean_learned_phrase(
            phrase
        )

        if clean_phrase not in self.user_phrases:
            return False

        del self.user_phrases[
            clean_phrase
        ]

        self.save_user_phrases()
        return True

    def apply_user_phrases(
        self,
        text
    ):

        adapted = text
        changes = []

        phrases = sorted(
            self.user_phrases.keys(),
            key=len,
            reverse=True
        )

        for phrase in phrases:

            entry = self.user_phrases.get(
                phrase,
                {}
            )

            meaning = str(
                entry.get(
                    "meaning",
                    ""
                )
            ).strip()

            if not meaning:
                continue

            pattern = (
                r"(?<![a-z0-9'])"
                + re.escape(phrase)
                + r"(?![a-z0-9'])"
            )

            if not re.search(
                pattern,
                adapted
            ):
                continue

            adapted = re.sub(
                pattern,
                meaning,
                adapted
            )

            changes.append({
                "from": phrase,
                "to": meaning,
                "type": "personal_phrase",
                "confidence": "high"
            })

        return adapted, changes

    def load_user_phrases(self):

        if not self.user_phrase_path.exists():
            return {}

        try:
            data = json.loads(
                self.user_phrase_path.read_text(
                    encoding="utf-8"
                )
            )

        except (
            OSError,
            json.JSONDecodeError
        ):
            return {}

        if not isinstance(
            data,
            dict
        ):
            return {}

        cleaned = {}

        for phrase, entry in data.items():

            clean_phrase = self.clean_learned_phrase(
                phrase
            )

            if not clean_phrase:
                continue

            if isinstance(
                entry,
                str
            ):
                meaning = self.clean_learned_phrase(
                    entry
                )

                category = "user"

            elif isinstance(
                entry,
                dict
            ):
                meaning = self.clean_learned_phrase(
                    entry.get(
                        "meaning",
                        ""
                    )
                )

                category = str(
                    entry.get(
                        "category",
                        "user"
                    )
                ).strip() or "user"

            else:
                continue

            if not meaning:
                continue

            cleaned[
                clean_phrase
            ] = {
                "meaning": meaning,
                "category": category
            }

        return cleaned

    def save_user_phrases(self):

        try:
            self.user_phrase_path.write_text(
                json.dumps(
                    self.user_phrases,
                    indent=2,
                    ensure_ascii=False
                ),
                encoding="utf-8"
            )

        except OSError:
            return False

        return True

    def clean_learned_phrase(
        self,
        value
    ):

        cleaned = self.normalise_spacing(
            value
        ).lower()

        cleaned = cleaned.strip(
            " \"'`"
        )

        return cleaned

    def expand_known_words(self, text):

        tokens = re.findall(
            r"[a-z0-9']+|[^a-z0-9']+",
            text
        )

        changes = []
        output = []

        for token in tokens:

            lowered = token.lower()

            replacement = None
            category = ""

            if lowered in self.abbreviations:
                replacement = self.abbreviations[
                    lowered
                ]
                category = "abbreviation"

            elif lowered in self.contractions:
                replacement = self.contractions[
                    lowered
                ]
                category = "contraction"

            if replacement is None:
                output.append(token)
                continue

            output.append(replacement)

            changes.append({
                "from": token,
                "to": replacement,
                "type": category,
                "confidence": "high"
            })

        return "".join(output), changes

    def repair_safe_phrases(self, text):

        changes = []
        repaired = text

        for pattern, replacement, confidence in (
            self.safe_phrase_repairs
        ):

            if not re.search(
                pattern,
                repaired
            ):
                continue

            before = repaired

            repaired = re.sub(
                pattern,
                replacement,
                repaired
            )

            changes.append({
                "from": before,
                "to": repaired,
                "type": "phrase_repair",
                "confidence": confidence
            })

        return repaired, changes

    def likely_keyboard_smash(self, message):

        text = str(
            message
        ).strip().lower()

        if not text:
            return False

        words = re.findall(
            r"[a-z]+",
            text
        )

        if not words:
            return False

        compact = "".join(
            words
        )

        if len(compact) < 6:
            return False

        known_short_words = {
            "yeah",
            "yes",
            "nope",
            "okay",
            "hello",
            "thanks",
            "please",
            "tired",
            "happy",
            "sad",
            "right",
            "really"
        }

        if (
            len(words) == 1
            and words[0] in known_short_words
        ):
            return False

        repeated_run = bool(
            re.search(
                r"(.)\1{4,}",
                compact
            )
        )

        no_vowels = not any(
            character in "aeiou"
            for character in compact
        )

        longest_consonant_run = 0
        current_run = 0

        for character in compact:

            if character not in "aeiou":

                current_run += 1

                longest_consonant_run = max(
                    longest_consonant_run,
                    current_run
                )

            else:
                current_run = 0

        unusual_pairs = [
            "jh",
            "hg",
            "gf",
            "fd",
            "kj",
            "lk",
            "zx",
            "xq",
            "qv",
            "vj"
        ]

        unusual_pair_count = sum(
            compact.count(pair)
            for pair in unusual_pairs
        )

        single_long_unknown_word = (
            len(words) == 1
            and len(compact) >= 11
            and longest_consonant_run >= 4
            and unusual_pair_count >= 2
        )

        return (
            repeated_run
            or no_vowels
            or single_long_unknown_word
        )

    def should_ask_for_clarification(
        self,
        message,
        adapted
    ):

        if self.likely_keyboard_smash(
            message
        ):
            return True

        if not adapted.get(
            "text",
            ""
        ).strip():
            return True

        return False

    def normalise_spacing(self, text):

        return re.sub(
            r"\s+",
            " ",
            str(text).strip()
        )

    def overall_confidence(self, changes):

        if not changes:
            return "unchanged"

        levels = {
            change.get(
                "confidence",
                "medium"
            )
            for change in changes
        }

        if levels == {"high"}:
            return "high"

        if "low" in levels:
            return "low"

        return "medium"