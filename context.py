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

        self.current_project = ""
        self.current_project_status = ""

        self.current_person = ""
        self.current_person_label = ""
        self.last_person_message = ""
        self.person_message_pending = False
        self.last_person_question = ""

        self.project_intro_pending = False
        self.last_project_question = ""

        self.last_nova_question = ""
        self.last_nova_question_topic = ""

        self.last_question_shape = ""
        self.last_question_subject = ""

        self.last_nova_statement = ""
        self.last_nova_statement_type = ""

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

        if self.observe_person(
            message,
            text
        ):
            return

        if self.observe_project(
            message,
            text
        ):
            return

        self.observe_emotion(
            message,
            text
        )

    def observe_person(
        self,
        message,
        text
    ):

        relationship_prefixes = {
            "my friend ": "your friend",
            "my best friend ": "your best friend",
            "my sister ": "your sister",
            "my brother ": "your brother",
            "my mum ": "your mum",
            "my mom ": "your mom",
            "my dad ": "your dad",
            "my cousin ": "your cousin",
            "my teacher ": "your teacher",
            "my classmate ": "your classmate"
        }

        for prefix, label in relationship_prefixes.items():

            if not text.startswith(prefix):
                continue

            remainder = message[
                len(prefix):
            ].strip().rstrip(".!")

            self.current_person_label = label

            possible_name = self.extract_person_name(
                remainder
            )

            if possible_name:
                self.current_person = possible_name
                self.last_active_topic = (
                    f"{label} {possible_name}"
                )
            else:
                self.current_person = ""
                self.last_active_topic = label

            self.last_person_message = message.strip()
            self.person_message_pending = True

            return True

        pronoun_starters = [
            "she ",
            "he ",
            "they ",
            "her ",
            "him ",
            "them "
        ]

        if any(
            text.startswith(starter)
            for starter in pronoun_starters
        ):

            if self.current_person_label:
                self.last_active_topic = (
                    self.person_topic_phrase()
                )

            return False

        return False

    def extract_person_name(self, remainder):

        if not remainder:
            return ""

        words = remainder.split()

        if not words:
            return ""

        first_word = words[0].strip(
            " ,.!?'\""
        )

        blocked_words = {
            "is",
            "was",
            "has",
            "had",
            "likes",
            "loves",
            "hates",
            "came",
            "went",
            "pulled",
            "said",
            "told",
            "helped",
            "called",
            "started"
        }

        if first_word.lower() in blocked_words:
            return ""

        if first_word.lower() in {
            "he",
            "she",
            "they",
            "who",
            "that"
        }:
            return ""

        if first_word[:1].isupper():
            return first_word

        return ""

    def person_topic_phrase(self):

        if self.current_person and self.current_person_label:
            return (
                f"{self.current_person_label} "
                f"{self.current_person}"
            )

        return self.current_person_label

    def observe_project(
        self,
        message,
        text
    ):

        project_prefixes = [
            "i'm working on ",
            "im working on ",
            "i am working on ",
            "i'm trying to ",
            "im trying to ",
            "i am trying to ",
            "i'm building ",
            "im building ",
            "i am building ",
            "i'm coding ",
            "im coding ",
            "i am coding ",
            "my project is ",
            "we're working on ",
            "were working on ",
            "we are working on "
        ]

        for prefix in project_prefixes:

            if not text.startswith(prefix):
                continue

            project = message[
                len(prefix):
            ].strip().rstrip(".!")

            if (
                project
                and project.lower() not in {
                    "it",
                    "this",
                    "that",
                    "something"
                }
            ):
                self.current_project = project
                self.current_project_status = "working"
                self.last_active_topic = project
                self.project_intro_pending = True

            return True

        return False

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

        acknowledgement_result = (
            self.handle_short_acknowledgement(
                text,
                pending_follow_up
            )
        )

        if acknowledgement_result:
            return acknowledgement_result

        ellipsis_result = self.handle_contextual_ellipsis(
            message,
            text
        )

        if ellipsis_result:
            return ellipsis_result

        description_result = (
            self.handle_experience_description(
                message,
                text
            )
        )

        if description_result:
            return description_result

        person_description_result = (
            self.handle_person_description(
                message,
                text
            )
        )

        if person_description_result:
            return person_description_result

        generic_continuation_result = (
            self.handle_generic_continuation(
                message,
                text
            )
        )

        if generic_continuation_result:
            return generic_continuation_result

        person_continuation_result = (
            self.handle_person_continuation(
                message,
                text
            )
        )

        if person_continuation_result:
            return person_continuation_result

        project_answer_result = (
            self.handle_project_answer(
                message,
                text
            )
        )

        if project_answer_result:
            return project_answer_result

        person_result = self.handle_person_statement(
            message,
            text
        )

        if person_result:
            return person_result

        project_intro_result = self.handle_project_intro(
            message,
            text
        )

        if project_intro_result:
            return project_intro_result

        project_result = self.handle_project_progress(
            message,
            text
        )

        if project_result:
            return project_result

        if self.is_direct_new_emotion_statement(
            text
        ):

            if pending_follow_up:
                return self.make_result(
                    "",
                    clear_pending=True,
                    continue_routing=True
                )

            return None

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

    # -------------------------------------------------
    # Active person continuity
    # -------------------------------------------------

    def resolve_simple_reference(
        self,
        text
    ):

        normalised = self.normalise_control_text(
            text
        )

        if normalised in {
            "it",
            "that",
            "this",
            "that one",
            "this one"
        }:

            if self.current_project:
                return self.current_project

            if self.last_active_topic:
                return self.last_active_topic

        if normalised in {
            "she",
            "her"
        }:

            if self.current_person_label:
                return self.person_topic_phrase()

        if normalised in {
            "he",
            "him"
        }:

            if self.current_person_label:
                return self.person_topic_phrase()

        if normalised in {
            "they",
            "them"
        }:

            if self.current_person_label:
                return self.person_topic_phrase()

        return ""

    # -------------------------------------------------
    # Contextual ellipsis
    # -------------------------------------------------

    # -------------------------------------------------
    # Person-description statements
    # -------------------------------------------------

    def handle_person_description(
        self,
        message,
        text
    ):

        normalised = self.normalise_control_text(
            text
        )

        patterns = [
            r"^my (friend|best friend|sister|brother|mum|mom|dad|"
            r"cousin|teacher|classmate) was (?:really )?(.+?)(?: today)?$",

            r"^my (friend|best friend|sister|brother|mum|mom|dad|"
            r"cousin|teacher|classmate) is (?:really )?(.+?)(?: today)?$",

            r"^(?:a|the) (stranger|teacher|classmate|friend) "
            r"was (?:really )?(.+?)(?: today)?$",

            r"^(?:a|the) (stranger|teacher|classmate|friend) "
            r"is (?:really )?(.+?)(?: today)?$"
        ]

        match = None

        for pattern in patterns:

            match = re.match(
                pattern,
                normalised
            )

            if match:
                break

        if not match:
            return None

        person_type = match.group(
            1
        ).strip()

        description = match.group(
            2
        ).strip()

        if not person_type or not description:
            return None

        if normalised.startswith("my "):
            person_label = f"your {person_type}"
        else:
            person_label = f"the {person_type}"

        self.current_person_label = person_label
        self.current_person = ""
        self.last_active_topic = (
            f"{person_label} being {description}"
        )

        negative_descriptions = {
            "mean",
            "annoying",
            "frustrating",
            "rude",
            "unkind",
            "difficult",
            "harsh",
            "upsetting"
        }

        positive_descriptions = {
            "kind",
            "nice",
            "helpful",
            "funny",
            "sweet",
            "friendly",
            "patient"
        }

        if description in negative_descriptions:

            replies = [
                f"Ahh, {person_label} was {description}? That doesn’t sound nice.",
                f"That sounds frustrating. {person_label.capitalize()} was {description}.",
                f"Ugh, {description} is hard to deal with."
            ]

            if random.random() < 0.35:
                replies.append(
                    f"What did {person_label} do?"
                )

            return self.make_result(
                random.choice(replies),
                clear_pending=False
            )

        if description in positive_descriptions:

            replies = [
                f"Aw, {person_label} sounds {description}.",
                f"That’s nice — {description} is a lovely quality.",
                f"Okay, so {person_label} was {description}."
            ]

            if random.random() < 0.3:
                replies.append(
                    f"What made {person_label} seem {description}?"
                )

            return self.make_result(
                random.choice(replies),
                clear_pending=False
            )

        return self.make_result(
            random.choice([
                f"Okay, so {person_label} was {description}.",
                f"Ahh, {person_label} seemed {description}.",
                f"I’m following — {person_label} was {description}."
            ]),
            clear_pending=False
        )

    # -------------------------------------------------
    # Experience-description statements
    # -------------------------------------------------

    def handle_experience_description(
        self,
        message,
        text
    ):

        normalised = self.normalise_control_text(
            text
        )

        patterns = [
            r"^the (.+?) was (.+)$",
            r"^the (.+?) is (.+)$",
            r"^my (.+?) was (.+)$",
            r"^my (.+?) is (.+)$",
            r"^that (.+?) was (.+)$",
            r"^that (.+?) is (.+)$"
        ]

        match = None

        for pattern in patterns:

            match = re.match(
                pattern,
                normalised
            )

            if match:
                break

        if not match:
            return None

        subject = match.group(
            1
        ).strip()

        description = match.group(
            2
        ).strip()

        if not subject or not description:
            return None

        self.last_active_topic = (
            f"the {subject} being {description}"
        )

        emotional_descriptions = {
            "scary": [
                f"Ohh, the {subject} was scary? That sounds intense.",
                f"Ahh, so the {subject} actually frightened you.",
                f"That must have been unsettling if the {subject} felt scary."
            ],
            "funny": [
                f"Okay, so the {subject} was actually funny 😭",
                f"That sounds like the {subject} gave you a good laugh.",
                f"Ahh, the {subject} was funny then."
            ],
            "hard": [
                f"That sounds difficult. What made the {subject} hard?",
                f"Ahh, the {subject} was hard. That can be frustrating.",
                f"Okay, so the {subject} was a challenge."
            ],
            "good": [
                f"Nice — the {subject} was good.",
                f"Okayyy, sounds like the {subject} went well.",
                f"Glad the {subject} was good."
            ],
            "bad": [
                f"Ahh, the {subject} was bad?",
                f"That doesn’t sound great.",
                f"Okay, so the {subject} really didn’t go well."
            ],
            "exhausting": [
                f"No wonder you’re tired if the {subject} was exhausting.",
                f"That sounds draining.",
                f"Ahh, the {subject} took a lot out of you."
            ],
            "annoying": [
                f"Yeah, that sounds annoying.",
                f"Ahh, the {subject} was frustrating then.",
                f"I can see why the {subject} annoyed you."
            ],
            "interesting": [
                f"Ooo, what made the {subject} interesting?",
                f"Nice — sounds like the {subject} caught your attention.",
                f"Ahh, the {subject} was interesting then."
            ]
        }

        replies = emotional_descriptions.get(
            description
        )

        if replies:
            return self.make_result(
                random.choice(
                    replies
                ),
                clear_pending=False
            )

        return self.make_result(
            random.choice([
                f"Okay, so the {subject} was {description}.",
                f"Ahh, the {subject} felt {description} to you.",
                f"I get it — you found the {subject} {description}."
            ]),
            clear_pending=False
        )

    def handle_contextual_ellipsis(
        self,
        message,
        text
    ):

        normalised = self.normalise_control_text(
            text
        )

        if not normalised:
            return None

        if str(message).strip().endswith("?"):
            return None

        # Example:
        # Nova: What do they like about the rain?
        # User: the cooling feeling on their skin
        if (
            self.current_person_label
            and self.last_question_shape == "preference_reason"
        ):

            if not self.starts_with_explicit_subject(
                normalised
            ):

                interpreted = (
                    f"they like {normalised}"
                )

                self.last_active_topic = (
                    f"{self.person_topic_phrase()} "
                    f"liking {normalised}"
                )

                self.last_question_shape = ""
                self.last_question_subject = ""

                return self.make_result(
                    random.choice([
                        (
                            f"Ahh, they like "
                            f"{normalised}. That makes sense."
                        ),
                        (
                            f"Ohh, so it’s "
                            f"{normalised} they like."
                        ),
                        (
                            f"Okay, I get it — "
                            f"{normalised} is what they enjoy."
                        )
                    ]),
                    clear_pending=False
                )

        # Example:
        # Nova: Why are you tired?
        # User: because of school
        if normalised.startswith(
            "because "
        ):

            if self.current_emotion:
                reason = normalised[
                    len("because "):
                ].strip()

                if reason:
                    self.current_emotion_topic = reason
                    self.last_active_topic = (
                        f"you feeling "
                        f"{self.current_emotion} because of "
                        f"{reason}"
                    )

                    return self.make_result(
                        random.choice([
                            (
                                f"That makes sense. "
                                f"{reason} could explain why "
                                f"you feel {self.current_emotion}."
                            ),
                            (
                                f"Ahh, so {reason} is part "
                                f"of why you’re "
                                f"{self.current_emotion}."
                            )
                        ]),
                        clear_pending=False
                    )

        # Example:
        # "she's kind" while the active person is the user's friend.
        if (
            self.current_person_label
            and re.match(
                r"^(she|he|they)(?:'s| is| are) .+",
                normalised
            )
        ):

            trait = re.sub(
                r"^(she|he|they)(?:'s| is| are)\s+",
                "",
                normalised
            ).strip()

            if trait:
                self.last_active_topic = (
                    f"{self.person_topic_phrase()} "
                    f"being {trait}"
                )

                return self.make_result(
                    random.choice([
                        f"Aw, {self.person_topic_phrase()} sounds {trait}.",
                        f"That’s nice — {trait} is a lovely quality.",
                        f"Okay, I’m following. {self.person_topic_phrase()} is {trait}."
                    ]),
                    clear_pending=False
                )

        return None

    def starts_with_explicit_subject(
        self,
        text
    ):

        starters = (
            "i ",
            "you ",
            "he ",
            "she ",
            "they ",
            "we ",
            "it ",
            "my ",
            "your ",
            "his ",
            "her ",
            "their "
        )

        return text.startswith(
            starters
        )

    def handle_generic_continuation(
        self,
        message,
        text
    ):

        if not self.last_nova_question:
            return None

        normalised = self.normalise_control_text(
            text
        )

        resolved_reference = self.resolve_simple_reference(
            normalised
        )

        if resolved_reference:
            normalised = resolved_reference

        if not normalised:
            return None

        if str(message).strip().endswith("?"):
            return None

        if normalised in {
            "never mind",
            "not now",
            "maybe later",
            "another time"
        }:
            return None

        if len(normalised.split()) > 20:
            return None

        if self.last_nova_question == "project_change":
            return None

        if self.last_nova_question == "rain_reaction":
            return None

        topic = self.last_nova_question_topic

        self.last_nova_question = ""
        self.last_nova_question_topic = ""

        if topic:
            return self.make_result(
                random.choice([
                    f"Okay, that makes sense about {topic}.",
                    f"Right, I'm following — this is about {topic}.",
                    f"Got it. That helps me understand {topic} better."
                ]),
                clear_pending=False
            )

        return self.make_result(
            random.choice([
                "Okay, that makes sense.",
                "Right, I'm following.",
                "Got it."
            ]),
            clear_pending=False
        )

    def handle_person_continuation(
        self,
        message,
        text
    ):

        normalised = self.normalise_control_text(
            text
        )

        if self.last_person_question == "rain_reaction":

            funny_phrases = {
                "it was funny",
                "i found it funny",
                "it was actually funny",
                "i thought it was funny",
                "funny",
                "i laughed"
            }

            annoyed_phrases = {
                "it was annoying",
                "i was annoyed",
                "it annoyed me",
                "annoying",
                "i didnt like it",
                "i didn't like it"
            }

            if normalised in funny_phrases:
                self.last_person_question = ""
                self.last_nova_question = ""
                self.last_nova_question_topic = ""

                return self.make_result(
                    random.choice([
                        "Okay, that makes it way better 😭",
                        "😭 Fair enough — at least you found it funny.",
                        "That actually sounds like one of those chaotic-funny moments.",
                        "Okayyy, that sounds more funny than annoying then 😭"
                    ]),
                    clear_pending=False
                )

            if normalised in annoyed_phrases:
                self.last_person_question = ""
                self.last_nova_question = ""
                self.last_nova_question_topic = ""

                return self.make_result(
                    random.choice([
                        "Yeah, I would understand being annoyed by that.",
                        "That makes sense. Being pulled into rain without warning would be irritating.",
                        "Fair enough — funny for your friend, less funny for you."
                    ]),
                    clear_pending=False
                )

        pronoun_starters = (
            "she ",
            "he ",
            "they "
        )

        if (
            self.current_person_label
            and normalised.startswith(
                pronoun_starters
            )
        ):

            self.last_active_topic = (
                self.person_topic_phrase()
            )

            if (
                "likes the rain" in normalised
                or "loves the rain" in normalised
            ):
                replies = [
                    "Ohhh, that explains why she pulled you into it 😭",
                    "Okay, now it makes sense 😭 She wanted you to enjoy the rain with her.",
                    "She really committed to sharing the rain experience with you then 😭"
                ]

                if random.random() < 0.35:
                    self.last_question_shape = "preference_reason"
                    self.last_question_subject = (
                        self.person_topic_phrase()
                    )

                    replies.append(
                        "What does she like about the rain so much?"
                    )

                return self.make_result(
                    random.choice(replies),
                    clear_pending=False
                )

            return self.make_result(
                random.choice([
                    f"Ohh, so this is still about {self.person_topic_phrase()}.",
                    f"Okay, tell me more about {self.person_topic_phrase()}.",
                    "Right, I'm following."
                ]),
                clear_pending=False
            )

        return None

    def interpret_project_answer(
        self,
        answer
    ):

        clean_answer = str(
            answer
        ).strip()

        lowered_project = self.current_project.lower()

        nova_project = (
            "nova" in lowered_project
            or "your " in lowered_project
            or "you " in lowered_project
        )

        if not nova_project:
            return clean_answer

        replacements = [
            (
                r"\bhow much you know\b",
                "how much I know"
            ),
            (
                r"\bwhat you know\b",
                "what I know"
            ),
            (
                r"\byour knowledge\b",
                "my knowledge"
            ),
            (
                r"\byour memory\b",
                "my memory"
            ),
            (
                r"\byour dictionary\b",
                "my dictionary"
            ),
            (
                r"\bhow you respond\b",
                "how I respond"
            ),
            (
                r"\bhow you understand\b",
                "how I understand"
            )
        ]

        interpreted = clean_answer

        for pattern, replacement in replacements:

            interpreted = re.sub(
                pattern,
                replacement,
                interpreted,
                flags=re.IGNORECASE
            )

        return interpreted

    def handle_project_answer(
        self,
        message,
        text
    ):

        if (
            not self.current_project
            or not self.last_project_question
        ):
            return None

        normalised = self.normalise_control_text(
            text
        )

        # A short answer to Nova's project question may begin
        # with words such as "how", "what", or "which".
        # Only treat it as a separate question when the user
        # actually includes question punctuation.
        if str(message).strip().endswith("?"):
            return None

        if normalised in {
            "its not working",
            "it's not working",
            "it works",
            "it works now",
            "i fixed it",
            "we fixed it"
        }:
            return None

        if len(normalised.split()) > 18:
            return None

        self.last_project_question = ""
        self.last_nova_question = ""
        self.last_nova_question_topic = ""
        self.last_active_topic = self.current_project

        interpreted_answer = self.interpret_project_answer(
            message
        )

        replies = [
            (
                f"Ooo, so you're changing "
                f"{interpreted_answer} in "
                f"{self.current_project}."
            ),
            (
                f"Ahh, you're working on "
                f"{interpreted_answer}. "
                "That sounds like an important part."
            ),
            (
                f"Okay, I get it — this part is about "
                f"{interpreted_answer}."
            )
        ]

        if random.random() < 0.35:
            replies.extend([
                (
                    f"Wait, so this is about "
                    f"{interpreted_answer}? "
                    "What are you hoping it will improve?"
                ),
                (
                    f"That sounds interesting — "
                    f"{interpreted_answer}. "
                    "How are you planning to change it?"
                )
            ])

        return self.make_result(
            random.choice(replies),
            clear_pending=False
        )

    def handle_person_statement(
        self,
        message,
        text
    ):

        if not self.person_message_pending:
            return None

        if message.strip() != self.last_person_message:
            return None

        self.person_message_pending = False

        lowered = self.normalise_control_text(
            text
        )

        if any(
            phrase in lowered
            for phrase in [
                "pulled me into the rain",
                "dragged me into the rain"
            ]
        ):
            self.last_person_question = "rain_reaction"
            self.last_nova_question = "rain_reaction"
            self.last_nova_question_topic = (
                self.person_topic_phrase()
            )
            self.last_question_shape = "reaction"
            self.last_question_subject = (
                self.person_topic_phrase()
            )

            return self.make_result(
                random.choice([
                    "Wait, your friend pulled you into the rain? 😭 Was it funny or were you annoyed?",
                    "Into the rain?? 😭 Did you find it funny, or was it annoying?",
                    "Your friend really said you're coming into the rain with me 😭 How did you feel about it?"
                ]),
                clear_pending=False
            )

        if "likes the rain" in lowered or "loves the rain" in lowered:
            self.last_question_shape = "preference_reason"
            self.last_question_subject = (
                self.person_topic_phrase()
            )

            return self.make_result(
                random.choice([
                    "Ohh, that explains it a little. What do they like about the rain?",
                    "Your friend really likes rain then 😭 Do you know why?",
                    "Okay, now I'm curious — what do they like about it?"
                ]),
                clear_pending=False
            )

        return self.make_result(
            random.choice([
                f"Ohh, what happened with {self.person_topic_phrase()}?",
                f"Okay, tell me more about {self.person_topic_phrase()}.",
                f"Wait, what did {self.person_topic_phrase()} do?"
            ]),
            clear_pending=False
        )

    # -------------------------------------------------
    # Active project introductions
    # -------------------------------------------------

    def handle_project_intro(
        self,
        message,
        text
    ):

        if not self.project_intro_pending:
            return None

        project_prefixes = [
            "i'm working on ",
            "im working on ",
            "i am working on ",
            "i'm trying to ",
            "im trying to ",
            "i am trying to ",
            "i'm building ",
            "im building ",
            "i am building ",
            "i'm coding ",
            "im coding ",
            "i am coding ",
            "my project is ",
            "we're working on ",
            "were working on ",
            "we are working on "
        ]

        if not any(
            text.startswith(prefix)
            for prefix in project_prefixes
        ):
            return None

        self.project_intro_pending = False
        self.last_project_question = "project_change"
        self.last_nova_question = "project_change"
        self.last_nova_question_topic = self.current_project
        self.last_question_shape = "project_detail"
        self.last_question_subject = self.current_project

        return self.make_result(
            random.choice([
                f"Ooo, you're working on {self.current_project} now? What are you changing?",
                f"Ahh, back to {self.current_project}. What are you adding this time?",
                f"Nice — {self.current_project}. Which part are you working on?"
            ]),
            clear_pending=False
        )

    # -------------------------------------------------
    # Active project and progress continuity
    # -------------------------------------------------

    def handle_project_progress(
        self,
        message,
        text
    ):

        normalised = self.normalise_control_text(
            text
        )

        working_phrases = {
            "im still working on it",
            "i'm still working on it",
            "i am still working on it",
            "im still trying",
            "i'm still trying",
            "i am still trying",
            "im still testing it",
            "i'm still testing it",
            "i am still testing it",
            "still testing it",
            "still working on it"
        }

        failing_phrases = {
            "its not working",
            "it's not working",
            "it isnt working",
            "it isn't working",
            "it doesnt work",
            "it doesn't work",
            "that didnt work",
            "that didn't work",
            "that broke it",
            "i broke it",
            "it broke",
            "it failed",
            "still not working"
        }

        success_phrases = {
            "it works",
            "it works now",
            "its working",
            "it's working",
            "its working now",
            "it's working now",
            "i fixed it",
            "we fixed it",
            "we finally fixed it",
            "we finally got it working",
            "i got it working",
            "it finally works",
            "it finally worked"
        }

        if normalised in working_phrases:

            if not self.current_project:
                return None

            self.current_project_status = "testing"
            self.last_active_topic = self.current_project

            return self.make_result(
                random.choice([
                    (
                        f"Okay — you're still working on "
                        f"{self.current_project}."
                    ),
                    (
                        f"Got it. You're still testing "
                        f"{self.current_project}."
                    ),
                    (
                        "Alright. Let me know what happens "
                        "with it."
                    )
                ]),
                clear_pending=False
            )

        if normalised in failing_phrases:

            if not self.current_project:
                return None

            self.current_project_status = "not working"
            self.last_active_topic = self.current_project

            return self.make_result(
                random.choice([
                    (
                        f"Ahh, that's annoying. "
                        f"{self.current_project} still "
                        "isn't working."
                    ),
                    (
                        f"Oh no — something went wrong with "
                        f"{self.current_project}. What part "
                        "is failing?"
                    ),
                    (
                        f"Still fighting with "
                        f"{self.current_project}? I hope "
                        "this is the last stubborn bug."
                    )
                ]),
                clear_pending=False
            )

        if normalised in success_phrases:

            if not self.current_project:
                return None

            self.current_project_status = "working"
            self.last_active_topic = self.current_project

            return self.make_result(
                random.choice([
                    (
                        f"Yesss — {self.current_project} "
                        "is working now!"
                    ),
                    (
                        f"You fixed {self.current_project}!"
                    ),
                    (
                        f"Finally! We got "
                        f"{self.current_project} working."
                    )
                ]),
                clear_pending=False
            )

        return None

    # -------------------------------------------------
    # NOVA reply continuity
    # -------------------------------------------------

    def observe_nova_reply(
        self,
        reply
    ):

        clean_reply = str(
            reply
        ).strip()

        if not clean_reply:
            return

        self.last_nova_statement = clean_reply
        self.last_nova_statement_type = (
            self.classify_nova_reply(
                clean_reply
            )
        )

    def classify_nova_reply(
        self,
        reply
    ):

        lowered = str(
            reply
        ).lower().strip()

        if not lowered:
            return ""

        if lowered.rstrip().endswith("?"):
            return "question"

        purpose_groups = {
            "celebration": [
                "yess",
                "you fixed",
                "we fixed",
                "it works",
                "working now",
                "finally",
                "you did it",
                "well done",
                "proud of"
            ],

            "sympathy": [
                "i'm sorry",
                "i’m sorry",
                "that sounds difficult",
                "that sounds hard",
                "that doesn't sound",
                "that doesn’t sound",
                "that sounds upsetting",
                "that sounds frustrating",
                "that sounds annoying",
                "that must have been",
                "you don't have to explain",
                "you don’t have to explain"
            ],

            "supportive_explanation": [
                "that makes sense",
                "i understand",
                "i get it",
                "i get you",
                "it can be hard",
                "you don't have to know",
                "you don’t have to know",
                "tiredness can",
                "that explains",
                "no wonder",
                "i'm following",
                "i’m following",
                "could explain",
                "is part of why",
                "hard to tell",
                "harder to untangle",
                "we don't have to force",
                "we don’t have to force"
            ],

            "reassurance": [
                "that's okay",
                "that’s okay",
                "that's alright",
                "that’s alright",
                "you can be unsure",
                "take your time",
                "no pressure",
                "we can leave",
                "i'm here",
                "i’m here"
            ],

            "agreement": [
                "exactly",
                "you're right",
                "you’re right",
                "that's true",
                "that’s true",
                "i agree",
                "right —",
                "right,"
            ],

            "positive_reaction": [
                "that's nice",
                "that’s nice",
                "sounds good",
                "glad",
                "lovely",
                "nice —",
                "aw,"
            ],

            "negative_reaction": [
                "oh no",
                "ahh,",
                "ugh",
                "annoying",
                "frustrating",
                "didn't go well",
                "didn’t go well"
            ]
        }

        for purpose, phrases in purpose_groups.items():

            if any(
                phrase in lowered
                for phrase in phrases
            ):
                return purpose

        return "statement"

    def acknowledgement_from_last_reply(
        self,
        normalised
    ):

        if not self.last_nova_statement:
            return None

        agreement_words = {
            "yeah",
            "yh",
            "yes",
            "right",
            "exactly",
            "true",
            "thats true",
            "that's true",
            "that is true",
            "mhm",
            "mm",
            "fr",
            "for real"
        }

        if normalised not in agreement_words:
            return None

        reply_type = self.last_nova_statement_type

        replies_by_type = {
            "supportive_explanation": [
                "Yeah.",
                "Right — that makes sense.",
                "Exactly.",
                "Mhm, I get you."
            ],

            "sympathy": [
                "Yeah, I get you.",
                "Mhm.",
                "Right.",
                "Yeah."
            ],

            "reassurance": [
                "Mhm. No pressure.",
                "Yeah.",
                "Exactly — take your time.",
                "Right."
            ],

            "celebration": [
                "Yesss 😭",
                "Exactlyyy.",
                "We actually did it.",
                "Yeahhh 🎉"
            ],

            "agreement": [
                "Exactly.",
                "Right.",
                "Yeah.",
                "Mhm."
            ],

            "positive_reaction": [
                "Yeah 😊",
                "Mhm, it is.",
                "Exactly.",
                "Right."
            ],

            "negative_reaction": [
                "Yeah, honestly.",
                "Right? 😭",
                "Mhm.",
                "Exactly."
            ],

            "statement": [
                "Yeah.",
                "Right.",
                "Exactly.",
                "Mhm."
            ]
        }

        replies = replies_by_type.get(
            reply_type
        )

        if not replies:
            return None

        return random.choice(
            replies
        )

    # -------------------------------------------------
    # Short acknowledgement continuity
    # -------------------------------------------------

    def handle_short_acknowledgement(
        self,
        text,
        pending_follow_up
    ):

        normalised = self.normalise_control_text(
            text
        )

        acknowledgement_phrases = {
            "yeah",
            "yh",
            "yes",
            "exactly",
            "right",
            "correct",
            "thats right",
            "that's right",
            "that is right",
            "true",
            "thats true",
            "that's true",
            "that is true",
            "youre right",
            "you're right",
            "you are right"
        }

        if normalised not in acknowledgement_phrases:
            return None

        last_reply_acknowledgement = (
            self.acknowledgement_from_last_reply(
                normalised
            )
        )

        if last_reply_acknowledgement:
            self.last_control_action = "acknowledged"

            return self.make_result(
                last_reply_acknowledgement,
                clear_pending=False
            )

        has_active_context = bool(
            pending_follow_up
            or self.last_active_topic
            or self.current_learning_topic
            or self.current_emotion_topic
        )

        if not has_active_context:
            return None

        if pending_follow_up:

            kind = str(
                pending_follow_up.get(
                    "kind",
                    ""
                )
            ).strip()

            question_type = str(
                pending_follow_up.get(
                    "question_type",
                    ""
                )
            ).strip()

            # A yes/no acknowledgement may genuinely answer
            # some questions, so let their own module handle it.
            if question_type in {
                "yes_no",
                "confirmation",
                "permission"
            }:
                return None

            if kind in {
                "reflection",
                "world_learning"
            }:
                return None

        self.last_control_action = "acknowledged"

        if normalised in {
            "exactly",
            "correct",
            "thats right",
            "that's right",
            "that is right",
            "youre right",
            "you're right",
            "you are right"
        }:
            reply = random.choice([
                "Exactly.",
                "Right — that makes sense.",
                "Got it. I understood you correctly."
            ])

        elif normalised in {
            "true",
            "thats true",
            "that's true",
            "that is true"
        }:
            reply = random.choice([
                "Yeah, that's true.",
                "Right.",
                "That makes sense."
            ])

        else:
            reply = random.choice([
                "Yeah, that makes sense.",
                "Right.",
                "I understand."
            ])

        return self.make_result(
            reply,
            clear_pending=False
        )

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
            return self.natural_topic_phrase(
                self.last_active_topic
            )

        if self.current_learning_topic:
            return (
                f"you learning "
                f"{self.current_learning_topic}"
            )

        if self.current_emotion_topic:
            if self.current_emotion:
                return (
                    f"you feeling "
                    f"{self.current_emotion} about "
                    f"{self.current_emotion_topic}"
                )

            return self.current_emotion_topic

        if self.current_project:
            return (
                f"you working on "
                f"{self.current_project}"
            )

        if self.current_person_label:
            return self.person_topic_phrase()

        return ""

    def natural_topic_phrase(self, topic):

        clean_topic = str(
            topic
        ).strip()

        lowered = clean_topic.lower()

        feeling_topics = {
            "tired",
            "sad",
            "stressed",
            "happy",
            "bored",
            "worried",
            "scared",
            "upset",
            "excited",
            "proud"
        }

        if lowered in feeling_topics:
            return f"you being {clean_topic}"

        if lowered.startswith(
            "you "
        ):
            return clean_topic

        return clean_topic

    def answer_feeling_reason(self, message, context):

        text = message.lower().strip()

        uncertainty_reply = self.answer_uncertain_feeling_reason(
            message,
            text,
            context
        )

        if uncertainty_reply:
            return uncertainty_reply

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

    def is_direct_new_emotion_statement(
        self,
        text
    ):

        patterns = [
            r"^i(?:'m| am|m) (?:feeling )?"
            r"(tired|sad|happy|stressed|worried|scared|upset|"
            r"excited|proud|bored|angry|annoyed)$",

            r"^i feel "
            r"(tired|sad|happy|stressed|worried|scared|upset|"
            r"excited|proud|bored|angry|annoyed)$",

            r"^i(?:'ve| have) been "
            r"(tired|sad|happy|stressed|worried|scared|upset|"
            r"excited|proud|bored|angry|annoyed)$",

            r"^i keep feeling "
            r"(tired|sad|happy|stressed|worried|scared|upset|"
            r"excited|proud|bored|angry|annoyed)$"
        ]

        return any(
            re.match(pattern, text)
            for pattern in patterns
        )

    def answer_uncertain_feeling_reason(
        self,
        message,
        text,
        context
    ):

        patterns = [
            r"^i don't know because (.+)$",
            r"^i dont know because (.+)$",
            r"^i'm not sure because (.+)$",
            r"^im not sure because (.+)$",
            r"^i don't really know(?: because (.+))?$",
            r"^i dont really know(?: because (.+))?$",
            r"^idk(?: because (.+))?$"
        ]

        reason = ""
        matched = False

        for pattern in patterns:

            match = re.match(
                pattern,
                text
            )

            if not match:
                continue

            matched = True

            if match.lastindex and match.group(1):
                reason = match.group(1).strip()

            break

        if not matched:
            return None

        feeling = str(
            context.get(
                "topic",
                ""
            )
        ).strip()

        if reason:
            self.memory.add_event(
                (
                    f"was unsure why they felt "
                    f"{feeling}; mentioned: {reason}"
                ),
                "today"
            )

        tired_reasons = {
            "i'm really tired",
            "im really tired",
            "i am really tired",
            "really tired",
            "tired"
        }

        if reason in tired_reasons:
            return random.choice([
                (
                    "That’s okay. Being really tired can "
                    "make feelings harder to untangle."
                ),
                (
                    "You don’t have to know exactly why "
                    "right now. Tiredness can blur everything."
                ),
                (
                    "That makes sense. When you’re really "
                    "tired, it can be hard to tell what’s "
                    "causing what."
                )
            ])

        if reason:
            return random.choice([
                (
                    f"That’s okay. You don’t have to be "
                    f"certain yet. {reason} might be part "
                    f"of it."
                ),
                (
                    f"I get that. You’re not sure of the "
                    f"reason, and {reason} may be affecting "
                    f"how everything feels."
                )
            ])

        return random.choice([
            (
                "That’s okay. You don’t have to know the "
                "reason straight away."
            ),
            (
                "You can be unsure. We don’t have to force "
                "an explanation."
            ),
            (
                "That’s alright. Sometimes the feeling "
                "comes before the explanation."
            )
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
                "sometimes",
                "everything",
                "nothing",
                "school",
                "work",
                "sleep",
                "homework",
                "people",
                "family",
                "friends",
                "stress",
                "life",
                "today",
                "yesterday"
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