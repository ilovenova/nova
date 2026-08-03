"""
understanding.py

NOVA 1.7.4 personal language-learning layer.

This version:
- uses NOVA's PersonalDictionary
- learns unfamiliar slang and expressions
- remembers the user's explanation
- recognises learned expressions later
- continues from the original message after learning
- supports multiple saved meanings
- occasionally tries using learned language herself
"""

import random
import re

from dictionary import PersonalDictionary


class Understanding:

    def __init__(self, memory):

        self.memory = memory
        self.dictionary = PersonalDictionary(
            "vocabulary.json"
        )

        self.last_dictionary_subject = ""
        self.last_dictionary_meaning = ""
        self.last_dictionary_action = ""

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

    # -------------------------------------------------
    # Main router
    # -------------------------------------------------

    def respond(self, message, text):

        self.dictionary.refresh()

        result = self.answer_pending_definition(
            message,
            text
        )

        if result:
            return result

        result = self.check_dictionary_request(
            message,
            text
        )

        if result:
            return result

        result = self.check_definition_correction(
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

        pending = self.dictionary.get_pending()

        if not pending:
            return None

        if self.looks_like_new_topic(text):

            self.dictionary.clear_pending()
            return None

        meaning = self.extract_meaning(
            message
        )

        if not meaning:
            return {
                "reply": (
                    f"I'm still not sure what "
                    f"'{pending['word']}' means there."
                ),
                "follow_up": {
                    "kind": "understanding",
                    "question_type": "word_meaning",
                    "word": pending["word"]
                }
            }

        word = pending["word"]
        original_message = pending.get(
            "example",
            ""
        )

        kind = self.infer_meaning_kind(
            word,
            original_message,
            meaning
        )

        self.dictionary.add_meaning(
            word=word,
            meaning=meaning,
            kind=kind,
            source="user",
            confidence="high",
            example=original_message
        )

        self.dictionary.clear_pending()

        self.remember_dictionary_reference(
            word,
            meaning,
            "learned"
        )

        continued_reply = self.continue_original_message(
            original_message,
            word,
            meaning
        )

        if continued_reply:
            return {
                "reply": continued_reply,
                "follow_up": None
            }

        return {
            "reply": random.choice([
                (
                    f"Oh, I understand now. "
                    f"'{word}' means {meaning}."
                ),
                (
                    f"Got it. When you say "
                    f"'{word}', you mean {meaning}."
                ),
                (
                    f"That makes sense. I'll remember "
                    f"how you use '{word}'."
                )
            ]),
            "follow_up": None
        }

    # -------------------------------------------------
    # Dictionary requests
    # -------------------------------------------------

    def check_dictionary_request(
        self,
        message,
        text
    ):

        reference_result = self.check_reference_forgetting(
            text
        )

        if reference_result:
            return reference_result

        list_requests = {
            "show me your dictionary",
            "show your dictionary",
            "what words do you know",
            "show me the words you know",
            "list your words",
            "list your dictionary"
        }

        if text in list_requests:

            words = self.dictionary.list_words()

            if not words:
                return {
                    "reply": (
                        "My personal dictionary is empty "
                        "right now."
                    ),
                    "follow_up": None
                }

            return {
                "reply": (
                    "These are the words and expressions "
                    "in my personal dictionary:\n\n"
                    + "\n".join(
                        f"- {word}"
                        for word in words
                    )
                ),
                "follow_up": None
            }

        search_patterns = [
            r"^what does (.+?) mean in your dictionary[?.!]*$",
            r"^what does (.+?) mean[?.!]*$",
            r"^what do you think (.+?) means[?.!]*$",
            r"^search your dictionary for (.+?)[?.!]*$",
            r"^search for (.+?)[?.!]*$",
            r"^look up (.+?) in your dictionary[?.!]*$",
            r"^look up (.+?)[?.!]*$",
            r"^define (.+?)[?.!]*$"
        ]

        for pattern in search_patterns:

            match = re.match(
                pattern,
                text
            )

            if not match:
                continue

            query = message[
                match.start(1):match.end(1)
            ].strip().strip("'\"?.!,")

            results = self.dictionary.search(
                query
            )

            if not results:
                return {
                    "reply": (
                        f"I don't have '{query}' in my "
                        "personal dictionary yet."
                    ),
                    "follow_up": None
                }

            best = results[0]
            word = best["word"]
            meanings = best["entry"].get(
                "meanings",
                []
            )

            meaning_lines = []

            for index, meaning_data in enumerate(
                meanings,
                start=1
            ):
                meaning = meaning_data.get(
                    "meaning",
                    ""
                )

                kind = meaning_data.get(
                    "kind",
                    "unknown"
                )

                meaning_lines.append(
                    f"{index}. {meaning} ({kind})"
                )

            self.remember_dictionary_reference(
                word,
                meanings[0].get("meaning", "") if meanings else "",
                "looked_up"
            )

            return {
                "reply": (
                    f"In my personal dictionary, "
                    f"'{word}' means:\n\n"
                    + "\n".join(meaning_lines)
                ),
                "follow_up": None
            }

        profile_patterns = [
            r"^tell me everything you know about (.+?)[?.!]*$",
            r"^show me everything you know about (.+?)[?.!]*$",
            r"^what do you know about (.+?)[?.!]*$",
            r"^tell me about (.+?)[?.!]*$",
            r"^show me (.+?) in your dictionary[?.!]*$",
            r"^do you know (.+?)[?.!]*$",
            r"^have you learned (.+?)[?.!]*$"
        ]

        for pattern in profile_patterns:

            match = re.match(
                pattern,
                text
            )

            if not match:
                continue

            expression = message[
                match.start(1):match.end(1)
            ].strip().strip("'\"?.!,")

            entry = self.dictionary.get_entry(
                expression
            )

            if not entry:
                return {
                    "reply": (
                        f"I don't have '{expression}' in my "
                        "personal dictionary yet."
                    ),
                    "follow_up": None
                }

            meanings = entry.get(
                "meanings",
                []
            )

            meaning_lines = []

            all_examples = []

            for index, meaning_data in enumerate(
                meanings,
                start=1
            ):

                meaning = meaning_data.get(
                    "meaning",
                    ""
                )

                kind = meaning_data.get(
                    "kind",
                    "unknown"
                )

                confidence = meaning_data.get(
                    "confidence",
                    "unknown"
                )

                meaning_lines.append(
                    f"{index}. {meaning}\n"
                    f"   Type: {kind}\n"
                    f"   Confidence: {confidence}"
                )

                for example in meaning_data.get(
                    "examples",
                    []
                ):

                    if example not in all_examples:
                        all_examples.append(example)

            heard = entry.get(
                "times_heard",
                0
            )

            used = entry.get(
                "times_used",
                0
            )

            reply_parts = [
                (
                    f"Here's everything I know about "
                    f"'{expression}'."
                ),
                "",
                "Meanings",
                "",
                "\n\n".join(meaning_lines),
                "",
                (
                    f"I've heard it {heard} time"
                    + ("" if heard == 1 else "s")
                    + "."
                ),
                (
                    f"I've used it {used} time"
                    + ("" if used == 1 else "s")
                    + "."
                )
            ]

            if all_examples:

                reply_parts.extend([
                    "",
                    "Examples",
                    "",
                    "\n".join(
                        f"- {example}"
                        for example in all_examples
                    )
                ])

            self.remember_dictionary_reference(
                expression,
                meanings[0].get("meaning", "") if meanings else "",
                "showed"
            )

            return {
                "reply": "\n".join(reply_parts),
                "follow_up": None
            }

        detail_patterns = [
            r"^show me examples of (.+?)[?.!]*$",
            r"^show examples for (.+?)[?.!]*$",
            r"^how have i used (.+?)[?.!]*$",
            r"^what examples do you have for (.+?)[?.!]*$"
        ]

        for pattern in detail_patterns:

            match = re.match(
                pattern,
                text
            )

            if not match:
                continue

            expression = message[
                match.start(1):match.end(1)
            ].strip().strip("'\"?.!,")

            entry = self.dictionary.get_entry(
                expression
            )

            if not entry:
                return {
                    "reply": (
                        f"I don't have '{expression}' in my "
                        "personal dictionary yet."
                    ),
                    "follow_up": None
                }

            examples = []

            for meaning_data in entry.get(
                "meanings",
                []
            ):
                for example in meaning_data.get(
                    "examples",
                    []
                ):
                    if example not in examples:
                        examples.append(example)

            if not examples:
                reply = (
                    f"I know '{expression}', but I don't have "
                    "any saved examples for it yet."
                )
            else:
                reply = (
                    f"These are the examples I have for "
                    f"'{expression}':\n\n"
                    + "\n".join(
                        f"- {example}"
                        for example in examples
                    )
                )

            return {
                "reply": reply,
                "follow_up": None
            }

        usage_patterns = [
            r"^how many times have you heard (.+?)[?.!]*$",
            r"^how often have you heard (.+?)[?.!]*$",
            r"^how many times have you used (.+?)[?.!]*$"
        ]

        for pattern in usage_patterns:

            match = re.match(
                pattern,
                text
            )

            if not match:
                continue

            expression = message[
                match.start(1):match.end(1)
            ].strip().strip("'\"?.!,")

            entry = self.dictionary.get_entry(
                expression
            )

            if not entry:
                return {
                    "reply": (
                        f"I don't have '{expression}' in my "
                        "personal dictionary yet."
                    ),
                    "follow_up": None
                }

            if "used" in text:
                count = entry.get(
                    "times_used",
                    0
                )

                reply = (
                    f"I've used '{expression}' "
                    f"{count} time"
                    + ("" if count == 1 else "s")
                    + "."
                )
            else:
                count = entry.get(
                    "times_heard",
                    0
                )

                reply = (
                    f"I've heard '{expression}' "
                    f"{count} time"
                    + ("" if count == 1 else "s")
                    + "."
                )

            return {
                "reply": reply,
                "follow_up": None
            }

        remove_meaning_patterns = [
            r"^forget that (.+?) means (.+?)[.!?]*$",
            r"^remove the meaning (.+?) from (.+?)[.!?]*$",
            r"^delete the meaning (.+?) from (.+?)[.!?]*$"
        ]

        for pattern in remove_meaning_patterns:

            match = re.match(
                pattern,
                text
            )

            if not match:
                continue

            if text.startswith("forget that "):
                expression = message[
                    match.start(1):match.end(1)
                ].strip().strip("'\"")

                meaning = message[
                    match.start(2):match.end(2)
                ].strip().strip("'\"?.!,")
            else:
                meaning = message[
                    match.start(1):match.end(1)
                ].strip().strip("'\"")

                expression = message[
                    match.start(2):match.end(2)
                ].strip().strip("'\"?.!,")

            removed = self.dictionary.remove_meaning(
                expression,
                meaning
            )

            if removed:
                reply = (
                    f"Okay. I've removed the meaning "
                    f"'{meaning}' from '{expression}'."
                )
            else:
                reply = (
                    f"I couldn't find that exact meaning "
                    f"for '{expression}'."
                )

            return {
                "reply": reply,
                "follow_up": None
            }

        forget_patterns = [
            r"^forget the word (.+?)[.!]?$",
            r"^forget what (.+?) means[.!]?$",
            r"^delete (.+?) from your dictionary[.!]?$"
        ]

        for pattern in forget_patterns:

            match = re.match(
                pattern,
                text
            )

            if not match:
                continue

            word = message[
                match.start(1):match.end(1)
            ].strip().strip("'\"?.!")

            forgotten = self.dictionary.forget_word(
                word
            )

            if forgotten:
                reply = (
                    f"Okay. I've forgotten what "
                    f"'{word}' means."
                )
            else:
                reply = (
                    f"I couldn't find '{word}' in my "
                    "personal dictionary."
                )

            return {
                "reply": reply,
                "follow_up": None
            }

        return None

    # -------------------------------------------------
    # Correct or add dictionary meanings
    # -------------------------------------------------

    def check_definition_correction(
        self,
        message,
        text
    ):

        replace_patterns = [
            (
                r"^change what (.+?) means to (.+)$",
                1,
                2
            ),
            (
                r"^actually,? (.+?) means (.+)$",
                1,
                2
            ),
            (
                r"^i meant (.+?) means (.+)$",
                1,
                2
            )
        ]

        for pattern, word_group, meaning_group in replace_patterns:

            match = re.match(
                pattern,
                text
            )

            if not match:
                continue

            expression = message[
                match.start(word_group):match.end(word_group)
            ].strip().strip("'\"")

            new_meaning = message[
                match.start(meaning_group):match.end(meaning_group)
            ].strip().rstrip(".!")

            entry = self.dictionary.get_entry(
                expression
            )

            if not entry:
                self.dictionary.add_meaning(
                    word=expression,
                    meaning=new_meaning,
                    kind=self.infer_meaning_kind(
                        expression,
                        message,
                        new_meaning
                    ),
                    source="user",
                    confidence="high",
                    example=message
                )

                return {
                    "reply": (
                        f"I didn't already have '{expression}', "
                        f"so I've added it with the meaning "
                        f"{new_meaning}."
                    ),
                    "follow_up": None
                }

            meanings = entry.get(
                "meanings",
                []
            )

            if len(meanings) == 1:

                old_meaning = meanings[0].get(
                    "meaning",
                    ""
                )

                changed = self.dictionary.edit_meaning(
                    expression,
                    old_meaning,
                    new_meaning,
                    self.infer_meaning_kind(
                        expression,
                        message,
                        new_meaning
                    )
                )

                if changed:
                    return {
                        "reply": (
                            f"Okay. I've changed '{expression}' "
                            f"from meaning {old_meaning} to "
                            f"{new_meaning}."
                        ),
                        "follow_up": None
                    }

            self.dictionary.add_meaning(
                word=expression,
                meaning=new_meaning,
                kind=self.infer_meaning_kind(
                    expression,
                    message,
                    new_meaning
                ),
                source="user",
                confidence="high",
                example=message
            )

            return {
                "reply": (
                    f"Got it. I've added {new_meaning} as "
                    f"another meaning of '{expression}'."
                ),
                "follow_up": None
            }

        explicit_replace = re.match(
            r"^(.+?) doesn't mean (.+?),? it means (.+)$",
            text
        )

        if explicit_replace:

            expression = message[
                explicit_replace.start(1):
                explicit_replace.end(1)
            ].strip().strip("'\"")

            old_meaning = message[
                explicit_replace.start(2):
                explicit_replace.end(2)
            ].strip().strip("'\"")

            new_meaning = message[
                explicit_replace.start(3):
                explicit_replace.end(3)
            ].strip().rstrip(".!")

            changed = self.dictionary.edit_meaning(
                expression,
                old_meaning,
                new_meaning,
                self.infer_meaning_kind(
                    expression,
                    message,
                    new_meaning
                )
            )

            if changed:
                return {
                    "reply": (
                        f"Thanks for correcting me. "
                        f"I've changed '{expression}' to mean "
                        f"{new_meaning}."
                    ),
                    "follow_up": None
                }

            return {
                "reply": (
                    f"I couldn't find that exact old meaning "
                    f"for '{expression}'."
                ),
                "follow_up": None
            }

        additional_patterns = [
            r"^(.+?) can also mean (.+)$",
            r"^another meaning of (.+?) is (.+)$",
            r"^when i say (.+?),? it can also mean (.+)$"
        ]

        for pattern in additional_patterns:

            match = re.match(
                pattern,
                text
            )

            if not match:
                continue

            expression = message[
                match.start(1):match.end(1)
            ].strip().strip("'\"")

            new_meaning = message[
                match.start(2):match.end(2)
            ].strip().rstrip(".!")

            self.dictionary.add_meaning(
                word=expression,
                meaning=new_meaning,
                kind=self.infer_meaning_kind(
                    expression,
                    message,
                    new_meaning
                ),
                source="user",
                confidence="high",
                example=message
            )

            return {
                "reply": (
                    f"Got it. I've added {new_meaning} as "
                    f"another meaning of '{expression}'."
                ),
                "follow_up": None
            }

        return None

    # -------------------------------------------------
    # Direct teaching
    # -------------------------------------------------

    def check_direct_definition(
        self,
        message,
        text
    ):

        patterns = [
            (
                r"^when i say (.+?)(?:,?\s+)"
                r"(?:i mean|it means|that means)\s+(.+?)[.!?]*$"
            ),
            r"^by (.+?),?\s*i mean (.+?)[.!?]*$",
            r"^(.+?) means (.+?)[.!?]*$"
        ]

        for pattern in patterns:

            match = re.match(
                pattern,
                text
            )

            if not match:
                continue

            word = message[
                match.start(1):match.end(1)
            ].strip().strip("'\"")

            meaning = message[
                match.start(2):match.end(2)
            ].strip().rstrip(".!")

            if not word or not meaning:
                return None

            kind = self.infer_meaning_kind(
                word,
                message,
                meaning
            )

            self.dictionary.add_meaning(
                word=word,
                meaning=meaning,
                kind=kind,
                source="user",
                confidence="high",
                example=message
            )

            self.remember_dictionary_reference(
                word,
                meaning,
                "learned"
            )

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

        matches = self.find_known_expressions(
            text
        )

        if not matches:
            return None

        word = matches[0]
        meaning_data = self.choose_meaning(
            word,
            text
        )

        if not meaning_data:
            return None

        meaning = meaning_data.get(
            "meaning",
            ""
        ).strip()

        if not meaning:
            return None

        self.dictionary.record_heard(
            word,
            message
        )

        self.remember_dictionary_reference(
            word,
            meaning,
            "heard"
        )

        entry = self.dictionary.get_entry(
            word
        ) or {}

        times_heard = entry.get(
            "times_heard",
            0
        )

        if (
            times_heard >= 4
            and random.random() < 0.20
        ):

            self.dictionary.record_used(
                word
            )

            return {
                "reply": random.choice([
                    f"Yeah, that does sound {word}.",
                    f"That sounds pretty {word}, actually.",
                    (
                        f"Okay, I think I can use it here — "
                        f"that sounds {word}."
                    )
                ]),
                "follow_up": None
            }

        reply = self.continue_original_message(
            message,
            word,
            meaning
        )

        if reply:
            return {
                "reply": reply,
                "follow_up": None
            }

        return {
            "reply": random.choice([
                f"Oh, so you mean {meaning}.",
                f"Got it — {meaning}.",
                f"I understand. You mean {meaning}.",
                f"That sounds {meaning}."
            ]),
            "follow_up": None
        }

    def find_known_expressions(self, text):

        entries = self.dictionary.data.get(
            "entries",
            {}
        )

        found = []

        for expression in entries:

            pattern = (
                r"(?<![a-zA-Z'])"
                + re.escape(expression)
                + r"(?![a-zA-Z'])"
            )

            if re.search(pattern, text):
                found.append(expression)

        found.sort(
            key=lambda item: (
                -len(item.split()),
                -len(item)
            )
        )

        return found

    def choose_meaning(
        self,
        word,
        text
    ):

        meanings = self.dictionary.get_meanings(
            word
        )

        if not meanings:
            return None

        if len(meanings) == 1:
            return meanings[0]

        informal_clues = {
            "that",
            "this",
            "so",
            "really",
            "pretty",
            "actually",
            "game",
            "film",
            "movie",
            "song"
        }

        words = set(
            re.findall(
                r"[a-zA-Z']+",
                text
            )
        )

        if words.intersection(
            informal_clues
        ):

            for meaning in meanings:

                kind = meaning.get(
                    "kind",
                    ""
                ).lower()

                if kind in {
                    "slang",
                    "informal"
                }:
                    return meaning

        return meanings[0]

    # -------------------------------------------------
    # Unknown expressions
    # -------------------------------------------------

    def notice_unknown_expression(
        self,
        message,
        text
    ):

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

            if self.dictionary.knows(
                word
            ):
                continue

            if word not in self.likely_slang:
                continue

            self.dictionary.set_pending(
                word,
                message
            )

            return {
                "reply": random.choice([
                    f"What does '{word}' mean there?",
                    (
                        f"Does '{word}' have a special "
                        "meaning the way you're using it?"
                    ),
                    (
                        f"I'm not completely sure how you "
                        f"mean '{word}'. Can you teach me?"
                    )
                ]),
                "follow_up": {
                    "kind": "understanding",
                    "question_type": "word_meaning",
                    "word": word
                }
            }

        return None

    # -------------------------------------------------
    # Continue the original message
    # -------------------------------------------------

    def continue_original_message(
        self,
        original_message,
        word,
        meaning
    ):

        if not original_message:
            return ""

        original_text = original_message.lower().strip()

        replaced = re.sub(
            r"(?<![a-zA-Z'])"
            + re.escape(word)
            + r"(?![a-zA-Z'])",
            meaning,
            original_message,
            flags=re.IGNORECASE
        )

        if original_text.endswith("?"):

            return (
                f"Oh, I understand your question now: "
                f"'{replaced}'"
            )

        description_patterns = [
            r"^(?:that|this|the|my|your|our|his|her) .+ "
            r"(?:was|is|looks|sounds|felt|feels) .+[.!]?$",
            r"^.+ (?:was|is|looks|sounds|felt|feels) .+[.!]?$"
        ]

        if any(
            re.match(pattern, original_text)
            for pattern in description_patterns
        ):

            return random.choice([
                f"Oh, so you thought it was {meaning}.",
                f"I understand — you mean it was {meaning}.",
                f"Got it. That sounds {meaning}."
            ])

        return (
            f"Oh, I understand what you meant now: "
            f"'{replaced}'"
        )

    # -------------------------------------------------
    # Dictionary reference memory
    # -------------------------------------------------

    def remember_dictionary_reference(
        self,
        subject,
        meaning="",
        action=""
    ):

        self.last_dictionary_subject = str(
            subject
        ).strip().lower()

        self.last_dictionary_meaning = str(
            meaning
        ).strip()

        self.last_dictionary_action = str(
            action
        ).strip()

    def clear_dictionary_reference(self):

        self.last_dictionary_subject = ""
        self.last_dictionary_meaning = ""
        self.last_dictionary_action = ""

    def check_reference_forgetting(
        self,
        text
    ):

        whole_item_requests = {
            "forget that word",
            "forget that phrase",
            "delete that word",
            "delete that phrase",
            "forget that expression",
            "delete that expression",
            "never mind dont learn that",
            "never mind don't learn that"
        }

        meaning_requests = {
            "forget that meaning",
            "delete that meaning",
            "remove that meaning"
        }

        general_requests = {
            "actually forget it",
            "forget it"
        }

        if text in whole_item_requests:

            if not self.last_dictionary_subject:
                return {
                    "reply": (
                        "I'm not sure which word or phrase "
                        "you mean."
                    ),
                    "follow_up": None
                }

            subject = self.last_dictionary_subject

            forgotten = self.dictionary.forget_word(
                subject
            )

            if forgotten:
                self.clear_dictionary_reference()

                return {
                    "reply": (
                        f"Okay. I've forgotten "
                        f"'{subject}'."
                    ),
                    "follow_up": None
                }

            return {
                "reply": (
                    f"I couldn't find '{subject}' in my "
                    "personal dictionary."
                ),
                "follow_up": None
            }

        if text in meaning_requests:

            if not self.last_dictionary_subject:
                return {
                    "reply": (
                        "I'm not sure which word or phrase "
                        "you mean."
                    ),
                    "follow_up": None
                }

            if not self.last_dictionary_meaning:
                return {
                    "reply": (
                        f"I know you mean "
                        f"'{self.last_dictionary_subject}', "
                        "but I'm not sure which meaning "
                        "you want me to remove."
                    ),
                    "follow_up": None
                }

            subject = self.last_dictionary_subject
            meaning = self.last_dictionary_meaning

            removed = self.dictionary.remove_meaning(
                subject,
                meaning
            )

            if removed:
                remaining = self.dictionary.get_meanings(
                    subject
                )

                if remaining:
                    self.remember_dictionary_reference(
                        subject,
                        remaining[0].get(
                            "meaning",
                            ""
                        ),
                        "meaning_removed"
                    )
                else:
                    self.clear_dictionary_reference()

                return {
                    "reply": (
                        f"Okay. I've removed the meaning "
                        f"'{meaning}' from '{subject}'."
                    ),
                    "follow_up": None
                }

            return {
                "reply": (
                    f"I couldn't find that exact meaning "
                    f"for '{subject}'."
                ),
                "follow_up": None
            }

        if text in general_requests:

            if not self.last_dictionary_subject:
                return None

            if self.last_dictionary_action in {
                "learned",
                "added",
                "corrected"
            }:

                subject = self.last_dictionary_subject

                forgotten = self.dictionary.forget_word(
                    subject
                )

                if forgotten:
                    self.clear_dictionary_reference()

                    return {
                        "reply": (
                            f"Okay. I've forgotten "
                            f"'{subject}'."
                        ),
                        "follow_up": None
                    }

        return None

    # -------------------------------------------------
    # Helpers
    # -------------------------------------------------

    def infer_meaning_kind(
        self,
        word,
        example,
        meaning
    ):

        lowered_word = str(
            word
        ).lower()

        lowered_example = str(
            example
        ).lower()

        if (
            lowered_word in self.likely_slang
            or "when i say" in lowered_example
            or "the way i'm using it" in lowered_example
        ):
            return "slang"

        if "informal" in str(
            meaning
        ).lower():
            return "informal"

        return "unknown"

    def extract_meaning(self, message):

        clean_text = message.strip().rstrip(".!")
        lowered = clean_text.lower()

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
                return clean_text[
                    match.start(1):match.end(1)
                ].strip()

        if 1 <= len(clean_text.split()) <= 20:
            return clean_text

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