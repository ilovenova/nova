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
        self.current_emotion = ""
        self.current_emotion_topic = ""

        self.last_active_topic = ""
        self.last_control_action = ""

        self.paused_follow_up = None
        self.paused_topic = ""

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
                    self.last_active_topic = topic

                return

        self.observe_emotion(
            message,
            text
        )

    def observe_emotion(
        self,
        message,
        text
    ):

        emotion_patterns = [
            (
                "worried",
                [
                    r"^i(?:'m| am|m) worried about (.+)$",
                    r"^i(?:'m| am|m) worried (?:that|if) (.+)$"
                ]
            ),
            (
                "scared",
                [
                    r"^i(?:'m| am|m) scared about (.+)$",
                    r"^i(?:'m| am|m) scared (?:that|of) (.+)$"
                ]
            ),
            (
                "upset",
                [
                    r"^i(?:'m| am|m) upset about (.+)$",
                    r"^i(?:'m| am|m) upset (?:that|because) (.+)$"
                ]
            ),
            (
                "excited",
                [
                    r"^i(?:'m| am|m) excited about (.+)$",
                    r"^i(?:'m| am|m) excited (?:that|because) (.+)$"
                ]
            ),
            (
                "proud",
                [
                    r"^i(?:'m| am|m) proud of (.+)$",
                    r"^i(?:'m| am|m) proud (?:that|because) (.+)$"
                ]
            ),
            (
                "sad",
                [
                    r"^i(?:'m| am|m) sad about (.+)$",
                    r"^i(?:'m| am|m) sad (?:that|because) (.+)$"
                ]
            ),
            (
                "happy",
                [
                    r"^i(?:'m| am|m) happy about (.+)$",
                    r"^i(?:'m| am|m) happy (?:that|because) (.+)$"
                ]
            )
        ]

        for emotion, patterns in emotion_patterns:

            for pattern in patterns:

                match = re.match(
                    pattern,
                    text
                )

                if not match:
                    continue

                topic = match.group(1).strip().rstrip(".!")

                if not topic:
                    return

                self.current_emotion = emotion
                self.current_emotion_topic = topic
                self.last_active_topic = topic

                self.memory.set_profile_fact(
                    f"recent emotion: {emotion}",
                    topic
                )

                self.memory.add_event(
                    f"felt {emotion} about: {topic}",
                    "recent"
                )

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

        control_result = self.handle_conversation_control(
            message,
            text,
            pending_follow_up
        )

        if control_result:
            return control_result

        if self.is_direct_new_request(text):

            if pending_follow_up:
                return self.make_result(
                    "",
                    clear_pending=True,
                    continue_routing=True
                )

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

                result = conversation.answer_follow_up(
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

    # -------------------------------------------------
    # Universal Conversation Control
    # -------------------------------------------------

    def handle_conversation_control(
        self,
        message,
        text,
        pending_follow_up
    ):

        normalised = self.normalise_control_text(
            text
        )

        cancel_phrases = {
            "never mind",
            "nevermind",
            "forget that question",
            "forget the question",
            "leave it",
            "leave that",
            "drop it",
            "ignore that question",
            "i dont want to answer",
            "i don't want to answer",
            "i do not want to answer",
            "id rather not answer",
            "i'd rather not answer",
            "dont ask me that",
            "don't ask me that",
            "stop asking that"
        }

        pause_phrases = {
            "not now",
            "maybe later",
            "another time",
            "ask me later",
            "we can talk about it later",
            "lets talk about it later",
            "let's talk about it later",
            "i dont want to talk about it now",
            "i don't want to talk about it now"
        }

        subject_change_phrases = {
            "change the subject",
            "can we change the subject",
            "lets change the subject",
            "let's change the subject",
            "talk about something else",
            "can we talk about something else",
            "something else",
            "new topic"
        }

        recall_phrases = {
            "what were we talking about",
            "what were we talking about again",
            "what was i talking about",
            "what was the topic",
            "where were we"
        }

        return_phrases = {
            "go back",
            "go back to what i said",
            "go back to what i said earlier",
            "go back to the last topic",
            "continue the last topic",
            "carry on from before",
            "continue from before"
        }

        resume_question_phrases = {
            "ask me now",
            "you can ask me now",
            "you can ask me anything now",
            "you can ask me anything rn",
            "you can ask me anything right now",
            "we can talk about it now",
            "lets talk about it now",
            "let's talk about it now",
            "go back to that question",
            "ask that question again",
            "continue that question",
            "carry on with the question",
            "im ready to answer now",
            "i'm ready to answer now",
            "im ready to talk",
            "i'm ready to talk",
            "im ready to talk now",
            "i'm ready to talk now",
            "im ready to talk about it",
            "i'm ready to talk about it",
            "i feel ready to talk",
            "im feeling ready to talk",
            "i'm feeling ready to talk",
            "im feeling open to talk",
            "i'm feeling open to talk",
            "i feel open to talk"
        }

        if normalised in cancel_phrases:

            self.last_control_action = "cancelled"
            self.clear_paused_follow_up()

            if pending_follow_up:
                self.remember_follow_up_topic(
                    pending_follow_up
                )

                return self.make_result(
                    random.choice([
                        "Okay. We can leave that.",
                        "That's okay. You don't have to answer.",
                        "Alright. I'll drop that question.",
                        "No problem. We can move on."
                    ]),
                    clear_pending=True
                )

            return self.make_result(
                random.choice([
                    "Okay. We can leave it.",
                    "No problem.",
                    "Alright, we can move on."
                ]),
                clear_pending=True
            )

        if normalised in pause_phrases:

            self.last_control_action = "paused"

            if pending_follow_up:
                self.pause_follow_up(
                    pending_follow_up
                )

            return self.make_result(
                random.choice([
                    "Okay. We can come back to it another time.",
                    "That's fine. We'll leave it for now.",
                    "Alright. No pressure.",
                    "Okay, not now."
                ]),
                clear_pending=True
            )

        if normalised in subject_change_phrases:

            self.last_control_action = "changed_subject"
            self.clear_paused_follow_up()

            if pending_follow_up:
                self.remember_follow_up_topic(
                    pending_follow_up
                )

            return self.make_result(
                random.choice([
                    "Of course. What do you want to talk about instead?",
                    "Sure. We can change the subject.",
                    "Okay. What should we talk about now?",
                    "Absolutely. New topic."
                ]),
                clear_pending=True
            )

        resume_topic = self.extract_resume_topic(
            normalised
        )

        if (
            normalised in resume_question_phrases
            or resume_topic
        ):

            if not self.paused_follow_up:
                return self.make_result(
                    (
                        "I don't have a paused question "
                        "to return to."
                    ),
                    clear_pending=False
                )

            resumed_follow_up = dict(
                self.paused_follow_up
            )

            question = self.follow_up_question_text(
                resumed_follow_up
            )

            self.last_control_action = "resumed"
            self.clear_paused_follow_up()

            if question:
                return self.make_result(
                    question,
                    clear_pending=True,
                    next_follow_up=resumed_follow_up
                )

            return self.make_result(
                "Okay. We can return to that now.",
                clear_pending=True,
                next_follow_up=resumed_follow_up
            )

        if normalised in recall_phrases:

            topic = self.describe_current_topic(
                pending_follow_up
            )

            if topic:
                return self.make_result(
                    f"We were talking about {topic}.",
                    clear_pending=False
                )

            return self.make_result(
                "I'm not completely sure what the last topic was.",
                clear_pending=False
            )

        if normalised in return_phrases:

            topic = self.describe_current_topic(
                pending_follow_up
            )

            if topic:
                return self.make_result(
                    f"Okay. Let's go back to {topic}.",
                    clear_pending=False
                )

            return self.make_result(
                "I'm not sure which earlier topic you want to return to.",
                clear_pending=False
            )

        return None

    def extract_resume_topic(self, text):

        patterns = [
            r"^you can ask me about (.+?) now$",
            r"^you can ask me about (.+?) rn$",
            r"^you can ask me about (.+?) right now$",
            r"^im ready to talk about (.+?)$",
            r"^i'm ready to talk about (.+?)$",
            r"^i feel ready to talk about (.+?)$",
            r"^im feeling open to talk about (.+?)$",
            r"^i'm feeling open to talk about (.+?)$"
        ]

        for pattern in patterns:

            match = re.match(
                pattern,
                text
            )

            if match:
                return match.group(
                    1
                ).strip()

        return ""

    def pause_follow_up(self, follow_up):

        if not isinstance(
            follow_up,
            dict
        ):
            return

        self.paused_follow_up = dict(
            follow_up
        )

        self.remember_follow_up_topic(
            follow_up
        )

        self.paused_topic = self.last_active_topic

    def clear_paused_follow_up(self):

        self.paused_follow_up = None
        self.paused_topic = ""

    def follow_up_question_text(
        self,
        follow_up
    ):

        if not isinstance(
            follow_up,
            dict
        ):
            return ""

        for key in [
            "question",
            "prompt",
            "original_question"
        ]:

            value = follow_up.get(
                key
            )

            if value:
                return str(value).strip()

        kind = str(
            follow_up.get(
                "kind",
                ""
            )
        ).strip()

        topic = str(
            follow_up.get(
                "topic",
                ""
            )
        ).strip()

        if kind == "feeling":

            if topic:
                return f"What made you feel {topic}?"

            return "What made you feel that way?"

        if kind == "learning":

            if topic:
                return (
                    f"What part of {topic} are you "
                    "finding difficult?"
                )

            return "What part are you finding difficult?"

        if kind == "understanding":

            word = str(
                follow_up.get(
                    "word",
                    ""
                )
            ).strip()

            if word:
                return f"What does '{word}' mean there?"

        if kind == "relationship":

            person = str(
                follow_up.get(
                    "person",
                    ""
                )
            ).strip()

            if person:
                return (
                    f"What did you want to tell me "
                    f"about {person}?"
                )

        if kind == "activity":

            activity = str(
                follow_up.get(
                    "activity",
                    ""
                )
            ).strip()

            if activity:
                return f"What happened with {activity}?"

        return "Can you answer the question from before?"

    def normalise_control_text(self, text):

        normalised = str(
            text
        ).lower().strip()

        normalised = re.sub(
            r"[.!?,]+$",
            "",
            normalised
        )

        normalised = re.sub(
            r"\s+",
            " ",
            normalised
        )

        return normalised

    def remember_follow_up_topic(self, follow_up):

        if not isinstance(
            follow_up,
            dict
        ):
            return

        possible_keys = [
            "topic",
            "subject",
            "activity",
            "person",
            "word",
            "question"
        ]

        for key in possible_keys:

            value = follow_up.get(
                key
            )

            if not value:
                continue

            clean_value = str(
                value
            ).strip()

            if clean_value:
                self.last_active_topic = clean_value
                return

        kind = str(
            follow_up.get(
                "kind",
                ""
            )
        ).strip()

        if kind:
            self.last_active_topic = kind

    def describe_current_topic(
        self,
        pending_follow_up
    ):

        if pending_follow_up:
            self.remember_follow_up_topic(
                pending_follow_up
            )

        if self.last_active_topic:
            return self.last_active_topic

        if self.current_learning_topic:
            return self.current_learning_topic

        if self.current_emotion_topic:
            return self.current_emotion_topic

        return ""

    def answer_feeling_reason(self, message, context):

        text = message.lower().strip()

        if not self.is_meaningful_statement(text):
            return None

        feeling = context.get("topic", "that way")
        reason = message.strip().rstrip(".!")

        self.current_emotion = feeling
        self.current_emotion_topic = reason

        self.memory.set_profile_fact(
            f"recent emotion: {feeling}",
            reason
        )

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
            "i am finding it hard",
            "im struggling with it",
            "i'm struggling with it",
            "i am struggling with it",
            "its taking me a long time",
            "it's taking me a long time",
            "i dont think im getting it",
            "i don't think i'm getting it"
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