"""
recent_memory.py

NOVA 1.7.7 — Active Memory Search

Stores a small searchable window of recent conversation.
This is short-term context, not permanent memory.
"""

import re
from collections import deque


class RecentMemory:

    def __init__(self, max_turns=40):
        self.max_turns = max(10, int(max_turns))
        self.turns = deque(maxlen=self.max_turns)
        self.facts = deque(maxlen=self.max_turns * 3)

        self.last_user_message = ""
        self.last_nova_reply = ""
        self.last_nova_question = ""

        self.last_recalled_fact = None
        self.last_user_fact = None

    # -------------------------------------------------
    # Recording
    # -------------------------------------------------

    def record_user(self, message):
        clean = self.clean_text(message)

        if not clean:
            return

        self.last_user_message = clean
        self.turns.append({
            "speaker": "user",
            "message": clean
        })

        self.extract_user_facts(clean)

    def record_nova(self, reply):
        clean = self.clean_text(reply)

        if not clean:
            return

        self.last_nova_reply = clean
        self.turns.append({
            "speaker": "nova",
            "message": clean
        })

        if clean.rstrip().endswith("?"):
            self.last_nova_question = clean

    # -------------------------------------------------
    # Fact extraction
    # -------------------------------------------------

    def extract_user_facts(self, message):
        lowered = message.lower()

        self.extract_person_action(message, lowered)
        self.extract_project(message, lowered)
        self.extract_feeling(message, lowered)
        self.extract_event(message, lowered)

    def extract_person_action(self, message, lowered):
        pattern = (
            r"^my (friend|best friend|sister|brother|mum|mom|dad|"
            r"cousin|teacher|classmate)\s+(.+)$"
        )

        match = re.match(pattern, lowered)

        if match:
            relationship = match.group(1).strip()
            action = message[
                match.start(2):
            ].strip().rstrip(".!")

            if action:
                self.add_fact(
                    kind="person_action",
                    subject=f"your {relationship}",
                    detail=action,
                    source=message
                )

    def extract_project(self, message, lowered):
        prefixes = [
            "i'm working on ",
            "im working on ",
            "i am working on ",
            "i'm building ",
            "im building ",
            "i am building ",
            "i'm coding ",
            "im coding ",
            "i am coding ",
            "i'm trying to ",
            "im trying to ",
            "i am trying to ",
            "we're working on ",
            "were working on ",
            "we are working on "
        ]

        for prefix in prefixes:
            if not lowered.startswith(prefix):
                continue

            project = message[len(prefix):].strip().rstrip(".!")

            if project:
                self.add_fact(
                    kind="project",
                    subject="user",
                    detail=project,
                    source=message
                )

            return

        statuses = {
            "it works": "working",
            "it works now": "working",
            "it's working": "working",
            "its working": "working",
            "i fixed it": "fixed",
            "we fixed it": "fixed",
            "it's not working": "not working",
            "its not working": "not working",
            "it isn't working": "not working",
            "it isnt working": "not working",
            "it broke": "broken",
            "that broke it": "broken",
            "i'm still testing it": "testing",
            "im still testing it": "testing"
        }

        if lowered in statuses:
            latest = self.latest_fact(kind="project")

            if latest:
                self.add_fact(
                    kind="project_status",
                    subject=latest.get("detail", "the project"),
                    detail=statuses[lowered],
                    source=message
                )

    def extract_feeling(self, message, lowered):
        patterns = [
            r"^i(?:'m| am|m) feeling ([a-z]+)(?:\s+(.+))?$",
            r"^i feel ([a-z]+)(?:\s+(.+))?$",
            r"^i(?:'m| am|m) ([a-z]+)(?:\s+(.+))?$"
        ]

        feelings = {
            "tired", "sad", "happy", "stressed", "worried",
            "scared", "upset", "excited", "proud", "bored",
            "angry", "annoyed"
        }

        for pattern in patterns:
            match = re.match(pattern, lowered)

            if not match:
                continue

            feeling = match.group(1).strip()

            if feeling not in feelings:
                continue

            context = ""

            if match.lastindex and match.lastindex >= 2 and match.group(2):
                context = match.group(2).strip()

            self.add_fact(
                kind="feeling",
                subject="user",
                detail=feeling,
                source=message,
                extra={"context": context}
            )
            return

    def extract_event(self, message, lowered):
        prefixes = [
            "i went ",
            "today i went ",
            "i visited ",
            "i met ",
            "i bought ",
            "i got ",
            "i started ",
            "i finished "
        ]

        for prefix in prefixes:
            if lowered.startswith(prefix):
                self.add_fact(
                    kind="event",
                    subject="user",
                    detail=message.strip().rstrip(".!"),
                    source=message
                )
                return

    def add_fact(
        self,
        kind,
        subject,
        detail,
        source="",
        extra=None
    ):
        fact = {
            "kind": str(kind).strip(),
            "subject": str(subject).strip(),
            "detail": str(detail).strip(),
            "source": str(source).strip()
        }

        if not fact["kind"] or not fact["detail"]:
            return

        if isinstance(extra, dict):
            fact.update(extra)

        for existing in reversed(self.facts):
            if (
                existing.get("kind") == fact["kind"]
                and existing.get("subject") == fact["subject"]
                and existing.get("detail") == fact["detail"]
            ):
                return

        self.facts.append(fact)
        self.last_user_fact = fact

    # -------------------------------------------------
    # Search
    # -------------------------------------------------

    def latest_fact(self, kind=None, subject=None):
        wanted_subject = str(subject).strip().lower() if subject else ""

        for fact in reversed(self.facts):
            if kind and fact.get("kind") != kind:
                continue

            if wanted_subject:
                saved_subject = fact.get("subject", "").lower()

                if wanted_subject not in saved_subject:
                    continue

            return fact

        return None

    def search(self, query, kind=None, limit=5):
        wanted = self.tokenise(query)

        if not wanted:
            return []

        results = []

        for index, fact in enumerate(reversed(self.facts)):
            if kind and fact.get("kind") != kind:
                continue

            searchable = " ".join([
                fact.get("kind", ""),
                fact.get("subject", ""),
                fact.get("detail", ""),
                fact.get("source", "")
            ])

            tokens = self.tokenise(searchable)
            overlap = wanted.intersection(tokens)

            if not overlap:
                continue

            score = len(overlap) * 10 + max(0, 5 - index)

            results.append({
                "score": score,
                "fact": fact
            })

        results.sort(key=lambda item: -item["score"])

        return [
            item["fact"]
            for item in results[:max(1, int(limit))]
        ]

    # -------------------------------------------------
    # Direct recent-memory answers
    # -------------------------------------------------

    def answer_recent_question(self, message, text):
        normalised = self.normalise_question(text)

        person_match = re.match(
            (
                r"^what did my "
                r"(friend|best friend|sister|brother|mum|mom|dad|"
                r"cousin|teacher|classmate) do$"
            ),
            normalised
        )

        if person_match:
            relationship = person_match.group(1)

            fact = self.latest_fact(
                kind="person_action",
                subject=f"your {relationship}"
            )

            if not fact:
                return (
                    f"I don't remember what your "
                    f"{relationship} did."
                )

            self.last_recalled_fact = fact

            return (
                f"Your {relationship} "
                f"{self.shift_user_perspective(fact.get('detail', ''))}."
            )

        if normalised in {
            "what was i working on",
            "what am i working on",
            "what project was i working on",
            "what project am i working on"
        }:
            fact = self.latest_fact(kind="project")

            if not fact:
                return (
                    "I don't remember a recent project "
                    "you were working on."
                )

            self.last_recalled_fact = fact

            return f"You were working on {fact.get('detail', '')}."

        if normalised in {
            "what did you ask me",
            "what was your question",
            "what question did you ask",
            "what did you just ask me"
        }:
            if self.last_nova_question:
                return f"I asked: '{self.last_nova_question}'"

            return "I don't remember asking a recent question."

        forget_reply = self.answer_forget_recent(
            normalised
        )

        if forget_reply:
            return forget_reply

        search_reply = self.answer_search_question(
            message,
            normalised
        )

        if search_reply:
            return search_reply

        return None

    # -------------------------------------------------
    # Flexible recent-memory questions
    # -------------------------------------------------

    def answer_search_question(
        self,
        message,
        normalised
    ):

        query = self.extract_memory_query(
            normalised
        )

        if not query:
            return None

        results = self.search(
            query,
            limit=3
        )

        if not results:
            return (
                f"I don't remember anything recent "
                f"about {query}."
            )

        best = results[0]

        self.last_recalled_fact = best

        return self.fact_to_reply(
            best,
            query
        )

    def extract_memory_query(
        self,
        normalised
    ):

        patterns = [
            r"^what happened with (.+)$",
            r"^what happened about (.+)$",
            r"^what do you remember about (.+)$",
            r"^do you remember anything about (.+)$",
            r"^what did i say about (.+)$",
            r"^what did i tell you about (.+)$",
            r"^what have i said about (.+)$",
            r"^what have i told you about (.+)$",
            r"^tell me what you remember about (.+)$",
            r"^search your recent memory for (.+)$",
            r"^search recent memory for (.+)$"
        ]

        for pattern in patterns:

            match = re.match(
                pattern,
                normalised
            )

            if match:

                query = match.group(
                    1
                ).strip()

                if query:
                    return query

        return ""

    def fact_to_reply(
        self,
        fact,
        query=""
    ):

        kind = fact.get(
            "kind",
            ""
        )

        subject = fact.get(
            "subject",
            ""
        )

        detail = fact.get(
            "detail",
            ""
        )

        if kind == "person_action":

            shifted_detail = self.shift_user_perspective(
                detail
            )

            if subject:
                return (
                    f"{subject.capitalize()} "
                    f"{shifted_detail}."
                )

            return (
                f"I remember that "
                f"{shifted_detail}."
            )

        if kind == "project":

            return (
                f"You were working on {detail}."
            )

        if kind == "project_status":

            return (
                f"The latest update was that "
                f"{subject} was {detail}."
            )

        if kind == "feeling":

            context = fact.get(
                "context",
                ""
            )

            if context:
                return (
                    f"You said you were feeling "
                    f"{detail} {context}."
                )

            return (
                f"You said you were feeling "
                f"{detail}."
            )

        if kind == "event":

            return (
                f"You told me: {detail}."
            )

        if detail:
            return (
                f"I remember that {detail}."
            )

        return (
            f"I found something recent about "
            f"{query}, but I couldn't explain it clearly."
        )

    # -------------------------------------------------
    # Recent-memory forgetting and perspective
    # -------------------------------------------------

    def answer_forget_recent(
        self,
        normalised
    ):

        forget_last_message_phrases = {
            "forget what i just said",
            "forget my last message",
            "forget the last thing i said",
            "delete what i just said",
            "remove what i just said"
        }

        if normalised in forget_last_message_phrases:

            if not self.last_user_fact:
                return (
                    "I'm not sure which recent statement "
                    "you want me to forget."
                )

            removed = self.remove_fact(
                self.last_user_fact
            )

            self.last_user_fact = None

            if removed:
                return (
                    "Okay. I've forgotten what you just said."
                )

            return (
                "I couldn't find that recent statement anymore."
            )

        explicit_match = re.match(
            r"^forget that i said (.+)$",
            normalised
        )

        if not explicit_match:
            explicit_match = re.match(
                r"^forget that (.+)$",
                normalised
            )

        if explicit_match:

            wanted = explicit_match.group(
                1
            ).strip()

            match = self.find_matching_recent_fact(
                wanted
            )

            if not match:
                return (
                    "I couldn't find a recent memory "
                    "matching that."
                )

            removed = self.remove_fact(
                match
            )

            if removed:
                return (
                    "Okay. I've forgotten that recent memory."
                )

            return (
                "I couldn't remove that recent memory."
            )

        forget_phrases = {
            "forget that",
            "forget that happened",
            "forget it",
            "delete that",
            "remove that memory"
        }

        if normalised not in forget_phrases:
            return None

        target = (
            self.last_recalled_fact
            or self.last_user_fact
        )

        if not target:
            return (
                "I'm not sure which recent memory "
                "you want me to forget."
            )

        removed = self.remove_fact(
            target
        )

        self.last_recalled_fact = None

        if target is self.last_user_fact:
            self.last_user_fact = None

        if removed:
            return (
                "Okay. I've forgotten that recent memory."
            )

        return (
            "I couldn't find that recent memory anymore."
        )

    def remove_fact(
        self,
        target
    ):

        if not isinstance(
            target,
            dict
        ):
            return False

        for index in range(
            len(self.facts) - 1,
            -1,
            -1
        ):

            current = self.facts[index]

            if (
                current.get("kind")
                == target.get("kind")
                and current.get("subject")
                == target.get("subject")
                and current.get("detail")
                == target.get("detail")
                and current.get("source")
                == target.get("source")
            ):
                del self.facts[index]
                return True

        return False

    def find_matching_recent_fact(
        self,
        wanted
    ):

        wanted_tokens = self.tokenise(
            wanted
        )

        if not wanted_tokens:
            return None

        best = None
        best_score = 0

        for fact in reversed(
            self.facts
        ):

            searchable = " ".join([
                fact.get("subject", ""),
                fact.get("detail", ""),
                fact.get("source", "")
            ])

            fact_tokens = self.tokenise(
                searchable
            )

            score = len(
                wanted_tokens.intersection(
                    fact_tokens
                )
            )

            if score > best_score:
                best = fact
                best_score = score

        return best if best_score > 0 else None

    def shift_user_perspective(
        self,
        value
    ):

        text = str(
            value
        ).strip()

        replacements = [
            (
                r"\bmyself\b",
                "yourself"
            ),
            (
                r"\bme\b",
                "you"
            ),
            (
                r"\bmy\b",
                "your"
            ),
            (
                r"\bmine\b",
                "yours"
            ),
            (
                r"\bi am\b",
                "you are"
            ),
            (
                r"\bi'm\b",
                "you're"
            ),
            (
                r"\bi\b",
                "you"
            )
        ]

        shifted = text

        for pattern, replacement in replacements:

            shifted = re.sub(
                pattern,
                replacement,
                shifted,
                flags=re.IGNORECASE
            )

        return shifted

    # -------------------------------------------------
    # Helpers
    # -------------------------------------------------

    def clean_text(self, value):
        return re.sub(
            r"\s+",
            " ",
            str(value).strip()
        )

    def normalise_question(self, value):
        return self.clean_text(value).lower().rstrip("?.!")

    def tokenise(self, value):
        stop_words = {
            "a", "an", "the", "is", "are", "was", "were",
            "do", "did", "does", "my", "your", "i", "you",
            "me", "about", "what", "with", "anything",
            "recent", "remember"
        }

        cleaned = str(
            value
        ).lower()

        cleaned = cleaned.replace(
            "'s",
            ""
        )

        tokens = set(
            re.findall(
                r"[a-z0-9']+",
                cleaned
            )
        )

        return {
            token
            for token in tokens
            if token not in stop_words
        }