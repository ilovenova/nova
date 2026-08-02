"""
conversation.py

Handles soft conversation expectations for NOVA.

An expectation helps NOVA understand what kind of reply
may come next, but it never traps the user in the old topic.
"""

import random
import re


class Conversation:

    def __init__(self, memory):

        self.memory = memory

    # -------------------------------------------------
    # Main router
    # -------------------------------------------------

    def respond(self, message, text):

        result = self.check_story_opening(text)

        if result:
            return result

        result = self.check_question_opening(text)

        if result:
            return result

        result = self.check_opinion_opening(text)

        if result:
            return result

        result = self.check_memory_opening(text)

        if result:
            return result

        result = self.check_tell_me_opening(text)

        if result:
            return result

        return None

    # -------------------------------------------------
    # Story or surprise openings
    # -------------------------------------------------

    def check_story_opening(self, text):

        phrases = [
            "guess what",
            "guess what?",
            "youll never believe what happened",
            "you'll never believe what happened",
            "you wont believe what happened",
            "you won't believe what happened",
            "something happened",
            "the weirdest thing happened",
            "the funniest thing happened",
            "you will never guess what happened"
        ]

        if text not in phrases:
            return None

        return self.make_result(
            random.choice([
                "What happened?",
                "Okay, you've got my attention.",
                "Go on — tell me.",
                "Now I'm curious. What happened?"
            ]),
            {
                "kind": "conversation",
                "question_type": "awaiting_story",
                "tone": "general"
            }
        )

    # -------------------------------------------------
    # Question openings
    # -------------------------------------------------

    def check_question_opening(self, text):

        phrases = [
            "i have a question",
            "i have a question for you",
            "can i ask you something",
            "could i ask you something",
            "i wanted to ask you something",
            "i want to ask you something"
        ]

        if text not in phrases:
            return None

        return self.make_result(
            random.choice([
                "Of course. Ask me.",
                "Go ahead.",
                "What would you like to ask?",
                "I'm listening."
            ]),
            {
                "kind": "conversation",
                "question_type": "awaiting_question"
            }
        )

    # -------------------------------------------------
    # Opinion or advice openings
    # -------------------------------------------------

    def check_opinion_opening(self, text):

        phrases = [
            "i need your opinion",
            "i want your opinion",
            "can i get your opinion",
            "could i get your opinion",
            "i need some advice",
            "can you give me some advice",
            "i want to know what you think"
        ]

        if text not in phrases:
            return None

        return self.make_result(
            random.choice([
                "Of course. What do you want my opinion on?",
                "Tell me what you're thinking about.",
                "Go on. I'll think it through with you.",
                "What would you like my view on?"
            ]),
            {
                "kind": "conversation",
                "question_type": "awaiting_opinion"
            }
        )

    # -------------------------------------------------
    # Remembered-thought openings
    # -------------------------------------------------

    def check_memory_opening(self, text):

        phrases = [
            "i just remembered something",
            "i remembered something",
            "that reminds me",
            "i forgot to tell you something",
            "i meant to tell you something"
        ]

        if text not in phrases:
            return None

        return self.make_result(
            random.choice([
                "What did you remember?",
                "Go on — what was it?",
                "Tell me before it disappears again.",
                "I'm listening."
            ]),
            {
                "kind": "conversation",
                "question_type": "awaiting_memory"
            }
        )

    # -------------------------------------------------
    # "I want to tell you something..."
    # -------------------------------------------------

    def check_tell_me_opening(self, text):

        opening_patterns = [
            r"^i want to tell you something(?: .+)?[.!]?$",
            r"^i wanted to tell you something(?: .+)?[.!]?$",
            r"^i have something(?: .+)? to tell you[.!]?$",
            r"^can i tell you something(?: .+)?[.!]?$",
            r"^could i tell you something(?: .+)?[.!]?$",
            r"^there is something(?: .+)? i want to tell you[.!]?$",
            r"^theres something(?: .+)? i want to tell you[.!]?$",
            r"^there's something(?: .+)? i want to tell you[.!]?$"
        ]

        if not any(
            re.match(pattern, text)
            for pattern in opening_patterns
        ):
            return None

        tone = self.detect_tone(text)

        replies = {
            "sad": [
                "Of course. Take your time — I'm listening.",
                "You can tell me. I'm here.",
                "Okay. Say it when you're ready."
            ],
            "serious": [
                "Okay. I'm listening carefully.",
                "Of course. Tell me.",
                "All right. You have my attention."
            ],
            "exciting": [
                "Ooh, tell me!",
                "Okay, now I'm curious — what happened?",
                "That sounds exciting. Go on!"
            ],
            "good": [
                "That sounds promising. Tell me!",
                "Ooh, good news? I'm listening.",
                "Go on — I want to hear it."
            ],
            "worrying": [
                "Okay. Tell me what's worrying you.",
                "I'm listening. Take your time.",
                "You can tell me. What happened?"
            ],
            "embarrassing": [
                "You can tell me. No judgement.",
                "That's okay. I'm listening.",
                "Go on — you don't need to make it sound perfect."
            ],
            "funny": [
                "Okay, you've got my attention. Tell me.",
                "Now I want to hear this.",
                "Go on — what happened?"
            ],
            "important": [
                "All right. I'm listening carefully.",
                "Tell me. That sounds important.",
                "You have my attention."
            ],
            "general": [
                "Of course. I'm listening.",
                "Tell me.",
                "Go on — what did you want to tell me?",
                "You can tell me."
            ]
        }

        return self.make_result(
            random.choice(replies[tone]),
            {
                "kind": "conversation",
                "question_type": "shared_news",
                "tone": tone
            }
        )

    # -------------------------------------------------
    # Answer an expected continuation
    # -------------------------------------------------

    def answer_follow_up(self, message, context):

        question_type = context.get(
            "question_type",
            ""
        )

        if question_type == "shared_news":

            tone = context.get(
                "tone",
                "general"
            )

            return self.answer_shared_news(
                message,
                tone
            )

        if question_type == "day_positive_reason":

            return self.answer_day_reason(message)

        if question_type == "awaiting_story":

            return self.answer_story(message)

        if question_type == "awaiting_memory":

            return self.answer_remembered_thought(message)

        if question_type == "awaiting_opinion":

            return self.answer_opinion_request(message)

        # A real question should continue through NOVA's normal
        # routing so the correct specialist can answer it.
        if question_type == "awaiting_question":

            return None

        return None

    def answer_shared_news(self, message, tone):

        detail = message.strip().rstrip(".!")
        detail_tone = self.detect_shared_tone(detail)

        if tone == "general":
            tone = detail_tone

        remembered_topic = self.find_remembered_topic(
            detail
        )

        if (
            tone == "worrying"
            and remembered_topic
        ):
            return random.choice([
                (
                    f"I remember you're learning {remembered_topic}. "
                    "It makes sense that you're worried about whether "
                    "you'll get where you want to be, but finding it hard "
                    "doesn't mean you won't."
                ),
                (
                    f"I remember {remembered_topic} matters to you. "
                    "Worrying about your progress doesn't mean you're "
                    "failing — it usually means you care about it."
                ),
                (
                    f"You've told me about learning {remembered_topic} before. "
                    "I understand why this is worrying you. You don't have "
                    "to master it all at once."
                )
            ])

        if tone == "sad":
            return random.choice([
                f"I'm sorry. {detail} sounds difficult.",
                f"Thank you for telling me. {detail} must be hard.",
                "I'm listening. That sounds genuinely upsetting."
            ])

        if tone == "serious":
            return random.choice([
                "I understand. Thank you for telling me.",
                f"Okay. I can see why {detail} felt important to share.",
                "I'm taking that seriously. What do you need from me right now?"
            ])

        if tone in ["exciting", "good"]:

            if detail.lower().startswith((
                "i'm ",
                "im ",
                "i am ",
                "i've ",
                "ive ",
                "i have "
            )):
                return random.choice([
                    f"That is exciting — {detail}! Tell me more.",
                    f"Ooh, {detail}. I can see why you wanted to tell me.",
                    f"That's really good news. {detail} sounds exciting."
                ])

            return random.choice([
                f"That's brilliant! {detail} sounds like really good news.",
                "Oh, that's lovely. I'm glad you told me.",
                "That is exciting! Tell me more."
            ])

        if tone == "worrying":
            return random.choice([
                f"I can see why {detail} is worrying you.",
                "That does sound worrying. I'm here with you.",
                "Okay. Let's take it one part at a time."
            ])

        if tone == "embarrassing":
            return random.choice([
                "Honestly, that sounds more human than terrible.",
                "It's okay. Thank you for trusting me with it.",
                "I understand. You don't need to feel judged here."
            ])

        if tone == "funny":
            return random.choice([
                "Okay, that is pretty funny.",
                "I can see why you wanted to tell me that.",
                "That gave me a little imaginary grin."
            ])

        if tone == "important":
            return random.choice([
                "I understand. Thank you for telling me.",
                "That does sound important.",
                "I've got it. I'm listening."
            ])

        return random.choice([
            "I'm glad you told me.",
            "I understand. Tell me more if you want to.",
            "Thank you for sharing that with me.",
            "I'm listening."
        ])

    def answer_day_reason(self, message):

        reason = message.strip().rstrip(".!")

        lower = reason.lower()

        if lower in [
            "the sun",
            "sun",
            "sunshine",
            "the sunshine"
        ]:
            return random.choice([
                "That makes sense. Sunshine can change the whole feel of a day.",
                "I get that. A sunny day can make everything feel lighter.",
                "The sun is a good reason. Sometimes that is enough."
            ])

        if lower in [
            "music",
            "the music"
        ]:
            return random.choice([
                "That makes sense. Good music can carry a whole day.",
                "I get that. Music can change the mood completely.",
                "Nice. The right music really can make a day better."
            ])

        if lower in [
            "my family",
            "family",
            "my friends",
            "friends"
        ]:
            return random.choice([
                f"That makes sense. Time with {reason} can make a day feel special.",
                f"I can see why {reason} made today better.",
                "That sounds like a good part of the day."
            ])

        return random.choice([
            f"That makes sense. {reason} sounds like it made the day better.",
            f"I can see why {reason} stood out.",
            "I like that. Sometimes one small thing is enough to improve a day."
        ])

    # -------------------------------------------------
    # Intent continuation replies
    # -------------------------------------------------

    def answer_story(self, message):

        detail = message.strip().rstrip(".!")
        tone = self.detect_shared_tone(detail)
        remembered_topic = self.find_remembered_topic(
            detail
        )

        if tone == "worrying":
            if remembered_topic:
                return (
                    f"I remember {remembered_topic} matters to you. "
                    f"I can see why this would worry you."
                )

            return random.choice([
                "I can see why that worried you.",
                "That does sound worrying.",
                "Okay. I understand why you wanted to tell me."
            ])

        if tone == "sad":
            return random.choice([
                "I'm sorry. That sounds difficult.",
                "I can see why that upset you.",
                "Thank you for telling me. That sounds painful."
            ])

        if tone == "exciting":
            return random.choice([
                "That is exciting! Tell me more.",
                "Oh, that's brilliant.",
                "I can see why you wanted to tell me."
            ])

        return random.choice([
            "Oh wow. What happened next?",
            "I can see why you wanted to tell me that.",
            "That's quite a story.",
            "I'm listening — tell me more."
        ])

    def answer_remembered_thought(self, message):

        detail = message.strip().rstrip(".!")

        return random.choice([
            f"Ah, {detail}. I'm glad you remembered.",
            "Good catch. Tell me more about it.",
            "I'm listening.",
            "That sounds worth bringing back into the conversation."
        ])

    def answer_opinion_request(self, message):

        topic = message.strip().rstrip(".!")

        return random.choice([
            f"Okay. Tell me a little more about {topic} so I can give you a thoughtful answer.",
            f"I've got the topic: {topic}. What part are you unsure about?",
            "I can help you think it through. What are the main options?",
            "Tell me what you already think first."
        ])

    # -------------------------------------------------
    # Soft expectation checks
    # -------------------------------------------------

    def should_use_expectation(self, text, context):

        if self.is_clear_new_topic(text):
            return False

        question_type = context.get(
            "question_type",
            ""
        )

        if question_type == "shared_news":

            return self.is_meaningful_share(text)

        if question_type == "day_positive_reason":

            return self.is_short_reason(text)

        if question_type in [
            "awaiting_story",
            "awaiting_memory",
            "awaiting_opinion"
        ]:

            if self.is_direct_request(text):
                return False

            return self.is_meaningful_share(text)

        if question_type == "awaiting_question":

            # Let normal routing answer the actual question.
            return False

        return True

    def is_direct_request(self, text):

        direct_starters = [
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
            "delete ",
            "/"
        ]

        return any(
            text.startswith(starter)
            for starter in direct_starters
        )

    def is_clear_new_topic(self, text):

        if not text:
            return True

        direct_starters = [
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
            "delete ",
            "/"
        ]

        if any(
            text.startswith(starter)
            for starter in direct_starters
        ):
            return True

        new_topic_starters = [
            "my name is ",
            "my birthday is ",
            "my favourite ",
            "my favorite ",
            "my hobbies are ",
            "my school is ",
            "i'm working on ",
            "im working on ",
            "i am working on ",
            "i'm learning ",
            "im learning ",
            "i am learning ",
            "i have a ",
            "i have an ",
            "i dont have ",
            "i don't have ",
            "i want to ",
            "i wish ",
            "remember ",
            "today i ",
            "i went ",
            "i bought ",
            "i got "
        ]

        return any(
            text.startswith(starter)
            for starter in new_topic_starters
        )

    def is_meaningful_share(self, text):

        cleaned = re.sub(
            r"[^a-z0-9\s']",
            "",
            text
        ).strip()

        return len(cleaned.split()) >= 2

    def is_short_reason(self, text):

        cleaned = re.sub(
            r"[^a-z0-9\s']",
            "",
            text
        ).strip()

        words = cleaned.split()

        return 1 <= len(words) <= 12

    # -------------------------------------------------
    # Personalised conversation understanding
    # -------------------------------------------------

    def detect_shared_tone(self, message):

        text = message.lower()

        if self.contains_any(text, [
            "worry",
            "worried",
            "afraid",
            "scared",
            "nervous",
            "anxious",
            "what if i never",
            "if i will ever",
            "might never"
        ]):
            return "worrying"

        if self.contains_any(text, [
            "sad",
            "upset",
            "hurt",
            "cried",
            "crying",
            "disappointed",
            "lonely"
        ]):
            return "sad"

        if self.contains_any(text, [
            "excited",
            "amazing",
            "finally",
            "great news",
            "really happy",
            "so happy"
        ]):
            return "exciting"

        if self.contains_any(text, [
            "serious",
            "important",
            "need to talk"
        ]):
            return "serious"

        return "general"

    def find_remembered_topic(self, message):

        text = message.lower()

        preferences = self.memory.profile.get(
            "preferences",
            {}
        )

        candidates = []

        candidates.extend(
            preferences.get("hobbies", [])
        )

        candidates.extend(
            preferences.get("likes", [])
        )

        for goal in self.memory.profile.get(
            "goals",
            []
        ):
            description = goal.get(
                "description",
                ""
            )

            if description:
                candidates.append(description)

        for key in self.memory.profile.get(
            "facts",
            {}
        ).keys():
            candidates.append(key)

        best_match = ""

        for candidate in candidates:

            candidate_text = str(
                candidate
            ).lower().strip()

            simplified = candidate_text

            for prefix in [
                "learn ",
                "learning ",
                "reason for learning ",
                "difficulty learning ",
                "progress learning "
            ]:
                if simplified.startswith(prefix):
                    simplified = simplified[
                        len(prefix):
                    ].strip()

            if (
                simplified
                and simplified in text
                and len(simplified) > len(best_match)
            ):
                best_match = simplified

        return best_match

    def contains_any(self, text, phrases):

        return any(
            phrase in text
            for phrase in phrases
        )

    # -------------------------------------------------
    # Tone
    # -------------------------------------------------

    def detect_tone(self, text):

        tone_phrases = [
            ("sad", [
                "something sad",
                "sad news"
            ]),
            ("serious", [
                "something serious",
                "serious news"
            ]),
            ("exciting", [
                "something exciting",
                "exciting news"
            ]),
            ("good", [
                "something really good",
                "really good news",
                "good news",
                "something good"
            ]),
            ("worrying", [
                "something worrying",
                "something scary",
                "something bad"
            ]),
            ("embarrassing", [
                "something embarrassing"
            ]),
            ("funny", [
                "something funny"
            ]),
            ("important", [
                "something important"
            ])
        ]

        for tone, phrases in tone_phrases:

            if any(
                phrase in text
                for phrase in phrases
            ):
                return tone

        return "general"

    def make_result(
        self,
        reply,
        follow_up=None
    ):

        return {
            "reply": reply,
            "follow_up": follow_up
        }
