"""
context.py

Manages NOVA's short-term conversation context.
"""

import random
import re


class Context:

    def __init__(self, memory):
        self.memory = memory
        self.current_learning_topic = ""

    def observe(self, message, text):

        prefixes = [
            "i've started learning ",
            "ive started learning ",
            "i started learning ",
            "i'm learning ",
            "im learning ",
            "i am learning "
        ]

        for prefix in prefixes:
            if text.startswith(prefix):
                topic = message[len(prefix):].strip().rstrip(".!")

                if topic and topic.lower() not in [
                    "it",
                    "this",
                    "that"
                ]:
                    self.current_learning_topic = topic

                return

    def respond(
        self,
        message,
        text,
        pending_follow_up,
        activity,
        social,
        relationships,
        world_learning,
        conversation
    ):

        if self.is_direct_new_request(text):
            return None

        if pending_follow_up:

            kind = pending_follow_up.get("kind", "")

            if kind == "activity":

                reply = activity.answer_follow_up(
                    message,
                    pending_follow_up
                )

                if reply:
                    return self.make_result(
                        reply,
                        clear_pending=True
                    )

            if kind == "conversation":

                if not conversation.should_use_expectation(
                    text,
                    pending_follow_up
                ):

                    return self.make_result(
                        "",
                        clear_pending=True,
                        continue_routing=True
                    )

                reply = conversation.answer_follow_up(
                    message,
                    pending_follow_up
                )

                if reply:
                    return self.make_result(
                        reply,
                        clear_pending=True
                    )

            if kind == "relationship":

                reply = relationships.answer_follow_up(
                    message,
                    pending_follow_up
                )

                if reply:
                    return self.make_result(
                        reply,
                        clear_pending=True
                    )

            if kind == "world_learning":

                result = world_learning.answer_follow_up(
                    message,
                    pending_follow_up
                )

                if isinstance(result, dict):

                    return self.make_result(
                        result.get("reply", ""),
                        clear_pending=True,
                        next_follow_up=result.get(
                            "follow_up"
                        )
                    )

                if result:
                    return self.make_result(
                        result,
                        clear_pending=True
                    )

            if kind == "social":

                if social.should_use_follow_up(
                    text,
                    pending_follow_up
                ):

                    result = social.answer_follow_up(
                        message,
                        pending_follow_up
                    )

                    if isinstance(result, dict):

                        return self.make_result(
                            result.get("reply", ""),
                            clear_pending=True,
                            next_follow_up=result.get(
                                "follow_up"
                            )
                        )

                    return self.make_result(
                        result,
                        clear_pending=True
                    )

                return self.make_result(
                    "",
                    clear_pending=True,
                    continue_routing=True
                )

            if kind == "feeling":

                reply = self.answer_feeling_reason(
                    message,
                    pending_follow_up
                )

                if reply:
                    return self.make_result(
                        reply,
                        clear_pending=True
                    )

            if kind == "learning":

                reply = self.answer_learning_context(
                    message,
                    text,
                    pending_follow_up
                )

                if reply:
                    return self.make_result(
                        reply,
                        clear_pending=True
                    )

        reply = self.resolve_learning_pronoun(
            message,
            text
        )

        if reply:
            return self.make_result(
                reply,
                clear_pending=True
            )

        return None

    def answer_feeling_reason(self, message, context):

        text = message.lower().strip()

        if not self.is_meaningful_statement(text):
            return None

        feeling = context.get("topic", "that way")
        reason = message.strip().rstrip(".!")

        self.memory.add_event(
            f"felt {feeling} because: {reason}",
            "today"
        )

        if feeling == "tired":
            return random.choice([
                f"That explains it. {reason} sounds like it has been taking energy out of you.",
                f"That makes sense. {reason} could definitely leave you feeling tired.",
                f"No wonder you're tired. {reason} sounds draining.",
                f"I understand now — {reason} is part of why you're tired."
            ])

        if feeling == "sad":
            return random.choice([
                f"I'm sorry. {reason} sounds genuinely upsetting.",
                f"That explains why you feel sad. {reason} sounds difficult.",
                f"I understand a little better now. {reason} would be hard to carry.",
                f"That makes sense. I'm sorry you're dealing with {reason}."
            ])

        if feeling == "stressed":
            return random.choice([
                f"That explains the stress. {reason} sounds like a lot to handle.",
                f"No wonder you're stressed. {reason} sounds demanding.",
                f"I understand now — {reason} has been putting pressure on you.",
                f"That makes sense. {reason} could easily feel overwhelming."
            ])

        if feeling == "happy":
            return random.choice([
                f"I can see why that made you happy. {reason} sounds lovely.",
                f"That explains it. {reason} sounds worth being happy about.",
                f"Nice — now I understand what made you happy.",
                f"That makes sense. I'm glad {reason} happened."
            ])

        if feeling == "bored":
            return random.choice([
                f"That explains the boredom. {reason} doesn't sound very engaging.",
                f"I get it. {reason} sounds like it has been dragging.",
                f"That makes sense. No wonder you wanted something different.",
                f"I understand now. {reason} has not exactly been thrilling."
            ])

        return f"That makes sense. Now I understand why you felt {feeling}."

    def answer_learning_context(
        self,
        message,
        text,
        context
    ):

        topic = context.get(
            "topic",
            self.current_learning_topic
        )

        if not topic:
            return None

        self.current_learning_topic = topic

        if self.is_difficulty_statement(text):

            self.memory.set_profile_fact(
                f"difficulty learning {topic.lower()}",
                message.strip()
            )

            return random.choice([
                f"I get that. Learning {topic} can be hard, especially that part.",
                f"That makes sense. It sounds like {topic} has been challenging.",
                f"Yeah, that part of learning {topic} can take time.",
                f"I understand. I'll remember that you're finding {topic} difficult."
            ])

        return None

    def resolve_learning_pronoun(self, message, text):

        if not self.current_learning_topic:
            return None

        if not self.is_difficulty_statement(text):
            return None

        topic = self.current_learning_topic

        self.memory.set_profile_fact(
            f"difficulty learning {topic.lower()}",
            message.strip()
        )

        return random.choice([
            f"I get that. Learning {topic} can be hard.",
            f"That makes sense. It sounds like {topic} has been challenging.",
            f"Yeah, learning {topic} can take a lot of patience.",
            f"I understand. I'll remember that you're finding {topic} difficult."
        ])

    def is_difficulty_statement(self, text):

        return text in [
            "it is hard",
            "it's hard",
            "its hard",
            "this is hard",
            "that is hard",
            "it is difficult",
            "it's difficult",
            "its difficult",
            "this is difficult",
            "that is difficult",
            "im finding it hard",
            "i'm finding it hard",
            "i am finding it hard"
        ]

    def looks_like_social_answer(self, text):

        return text in [
            "im good",
            "i'm good",
            "i am good",
            "im okay",
            "i'm okay",
            "i am okay",
            "im fine",
            "i'm fine",
            "i am fine",
            "not bad",
            "pretty good",
            "not good",
            "im not good",
            "i'm not good",
            "i am not good",
            "not great",
            "could be better"
        ]

    def is_direct_new_request(self, text):

        if text.startswith("/"):
            return True

        starters = [
            "what ",
            "when ",
            "where ",
            "who ",
            "which ",
            "how ",
            "can you ",
            "could you ",
            "will you ",
            "do you ",
            "are you ",
            "is there ",
            "forget ",
            "delete "
        ]

        return any(
            text.startswith(starter)
            for starter in starters
        )

    def is_meaningful_statement(self, text):

        cleaned = re.sub(
            r"[^a-z0-9\s']",
            "",
            text
        ).strip()

        words = cleaned.split()

        if not words:
            return False

        if len(words) == 1:
            return cleaned in [
                "yes",
                "no",
                "maybe",
                "sometimes"
            ]

        vowels = sum(
            1
            for character in cleaned
            if character in "aeiou"
        )

        return vowels >= 2

    def make_result(
        self,
        reply,
        clear_pending=False,
        continue_routing=False,
        next_follow_up=None
    ):

        return {
            "reply": reply,
            "clear_pending": clear_pending,
            "continue_routing": continue_routing,
            "next_follow_up": next_follow_up
        }
