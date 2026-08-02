"""
world_learning.py

Lets NOVA learn carefully about the world.

She distinguishes:
- facts
- opinions
- assumptions
- guesses
- jokes
- definitions

She also remembers where information came from
and keeps a small curiosity list.
"""

import random
import re


class WorldLearning:

    def __init__(self, memory):

        self.memory = memory

    # -------------------------------------------------
    # Main router
    # -------------------------------------------------

    def respond(self, message, text):

        result = self.check_global_forgetting(text)

        if result:
            return result

        result = self.check_learning_invitation(text)

        if result:
            return result

        result = self.check_curiosity_question(text)

        if result:
            return result

        result = self.check_knowledge_question(text)

        if result:
            return result

        result = self.check_teaching_statement(
            message,
            text
        )

        if result:
            return result

        return None

    # -------------------------------------------------
    # Global forgetting
    # -------------------------------------------------

    def check_global_forgetting(self, text):

        forget_last_knowledge = [
            "forget i told you that",
            "forget i told you",
            "forget what i told you",
            "dont remember that",
            "don't remember that",
            "forget that information",
            "delete that information"
        ]

        if text in forget_last_knowledge:

            if self.memory.forget_last_knowledge():
                return self.make_result(
                    random.choice([
                        "Okay. I've forgotten the last thing you taught me.",
                        "All right — I removed that from what I know.",
                        "Got it. I won't keep that information."
                    ])
                )

            return self.make_result(
                "I couldn't find any recent world knowledge to forget."
            )

        forget_question = [
            "forget that question",
            "forget the question",
            "forget what you just asked",
            "delete that curiosity",
            "delete the curiosity",
            "dont wonder about that",
            "don't wonder about that",
            "stop wondering about that"
        ]

        if text in forget_question:

            curiosities = self.memory.get_open_curiosities()

            if not curiosities:
                return self.make_result(
                    "I don't have an open question to forget right now."
                )

            curiosity = curiosities[0]

            self.memory.delete_curiosity(
                curiosity.get("id", "")
            )

            return self.make_result(
                random.choice([
                    "Okay. I'll forget that question.",
                    "All right — that curiosity is gone.",
                    "Got it. I won't keep wondering about that."
                ])
            )

        return None

    # -------------------------------------------------
    # Invitations to teach
    # -------------------------------------------------

    def check_learning_invitation(self, text):

        if text in [
            "can i teach you something",
            "can i teach you something?",
            "let me teach you something",
            "i want to teach you something",
            "do you want to learn something",
            "would you like to learn something"
        ]:

            return self.make_result(
                random.choice([
                    "I'd like that. What are you going to teach me?",
                    "I'm listening.",
                    "Go on — teach me something.",
                    "Yes. What should I learn?"
                ]),
                {
                    "kind": "world_learning",
                    "question_type": "awaiting_statement"
                }
            )

        return None

    # -------------------------------------------------
    # Curiosity
    # -------------------------------------------------

    def check_curiosity_question(self, text):

        questions = [
            "is there anything you want to know",
            "is there anything you want to learn",
            "anything you want to know",
            "anything you want to learn",
            "what do you want to learn",
            "what are you curious about"
        ]

        if text not in questions:
            return None

        curiosities = self.memory.get_open_curiosities()

        if not curiosities:

            return self.make_result(
                random.choice([
                    "Nothing specific is waiting in my questions right now, but I'm always open to learning.",
                    "I don't have an unfinished question at the moment.",
                    "Not one particular thing right now. Something will probably catch my curiosity eventually."
                ])
            )

        curiosity = curiosities[0]
        question = curiosity.get(
            "question",
            ""
        )

        return self.make_result(
            random.choice([
                f"Actually, yes. {question}",
                f"There's one thing I've been wondering: {question}",
                f"I do have a question saved. {question}"
            ]),
            {
                "kind": "world_learning",
                "question_type": "curiosity_answer",
                "curiosity_id": curiosity.get("id", ""),
                "topic": curiosity.get("topic", "")
            }
        )

    # -------------------------------------------------
    # Recall learned knowledge
    # -------------------------------------------------

    def check_knowledge_question(self, text):

        patterns = [
            r"^what do you know about (.+?)[?]?$",
            r"^what have i taught you about (.+?)[?]?$",
            r"^what did i teach you about (.+?)[?]?$"
        ]

        for pattern in patterns:

            match = re.match(pattern, text)

            if match:

                query = match.group(1).strip()

                if query == "me":
                    return None

                results = self.memory.search_knowledge(
                    query
                )

                if not results:

                    question = (
                        f"What should I know about {query}?"
                    )

                    self.memory.add_curiosity(
                        question,
                        query
                    )

                    return self.make_result(
                        random.choice([
                            f"I don't know anything about {query} yet. Would you teach me?",
                            f"I haven't learned about {query} yet. What should I know?",
                            f"Not yet. I'd be interested to learn about {query}."
                        ]),
                        {
                            "kind": "world_learning",
                            "question_type": "teach_unknown",
                            "topic": query
                        }
                    )

                statements = [
                    item.get("statement", "")
                    for item in results[:5]
                    if item.get("statement", "")
                ]

                if len(statements) == 1:

                    item = results[0]
                    return self.make_result(
                        self.describe_learned_item(item)
                    )

                return self.make_result(
                    "Here's what I've learned about "
                    + query
                    + ":\n\n- "
                    + "\n- ".join(statements)
                )

        definition_patterns = [
            r"^what does (.+?) mean[?]?$",
            r"^what is (.+?)[?]?$",
            r"^do you know what (.+?) means[?]?$"
        ]

        for pattern in definition_patterns:

            match = re.match(pattern, text)

            if match:

                term = match.group(1).strip()

                # Keep identity and personal questions for other modules.
                if term in [
                    "your name",
                    "my name",
                    "the date",
                    "the time"
                ]:
                    return None

                # Prefer a formal saved definition.
                results = self.memory.search_knowledge(
                    term,
                    knowledge_type="definition"
                )

                # Otherwise use any relevant knowledge already learned.
                if not results:
                    results = self.memory.search_knowledge(
                        term
                    )

                if results:

                    statements = [
                        item.get("statement", "")
                        for item in results[:3]
                        if item.get("statement", "")
                    ]

                    if len(statements) == 1:
                        return self.make_result(
                            self.describe_learned_item(
                                results[0]
                            )
                        )

                    return self.make_result(
                        "Here's what you've taught me about "
                        + term
                        + ":\n\n- "
                        + "\n- ".join(statements)
                    )

                question = (
                    f"What should I know about {term}?"
                )

                self.memory.add_curiosity(
                    question,
                    term
                )

                return self.make_result(
                    random.choice([
                        f"I don't know what {term} is yet. Would you teach me?",
                        f"I haven't learned about {term} yet. What is it?",
                        f"Not yet. What should I know about {term}?"
                    ]),
                    {
                        "kind": "world_learning",
                        "question_type": "teach_unknown",
                        "topic": term
                    }
                )

        return None

    # -------------------------------------------------
    # Detect teaching
    # -------------------------------------------------

    def check_teaching_statement(
        self,
        message,
        text
    ):

        if self.is_personal_statement(text):
            return None

        cleaned_message, explicit_teaching = (
            self.remove_teaching_prefix(message, text)
        )

        classification = self.classify_statement(
            cleaned_message
        )

        if not explicit_teaching:

            if (
                not classification
                and not self.looks_like_world_statement(
                    cleaned_message
                )
            ):
                return None

        statement = self.clean_statement(
            cleaned_message
        )

        if not statement:
            return None

        subject = self.extract_subject(statement)

        if classification:

            knowledge_type = classification["type"]
            confidence = classification["confidence"]
            source_note = classification.get(
                "source_note",
                ""
            )

            item, updated = self.memory.add_knowledge_item(
                statement=statement,
                subject=subject,
                knowledge_type=knowledge_type,
                source=self.user_source(),
                confidence=confidence,
                verified=False,
                notes=source_note
            )

            self.maybe_add_grounded_curiosity(
                item
            )

            return self.make_result(
                self.saved_reply(
                    item,
                    updated
                )
            )

        return self.make_result(
            random.choice([
                f"Should I remember “{statement}” as something established, or as your own view?",
                f"Do you know “{statement}” to be true, or are you less certain?",
                f"Before I keep that, is it something known to be true or more what you think?"
            ]),
            {
                "kind": "world_learning",
                "question_type": "classify_statement",
                "statement": statement,
                "subject": subject
            }
        )

    # -------------------------------------------------
    # Follow-up answers
    # -------------------------------------------------

    def answer_follow_up(
        self,
        message,
        context
    ):

        text = message.lower().strip()
        question_type = context.get(
            "question_type",
            ""
        )

        if question_type == "awaiting_statement":

            result = self.check_teaching_statement(
                message,
                text
            )

            if result:
                return result

            return (
                "I'm listening, but I didn't quite recognise "
                "the thing you wanted to teach me."
            )

        if question_type == "classify_statement":

            classification = self.classify_reply(
                text
            )

            if not classification:

                return random.choice([
                    "I couldn't quite tell. You can say something like “I know it's true,” “that's my opinion,” or “I'm only guessing.”",
                    "I'm still unsure how certain you are. Is it something you know, believe, or suspect?",
                    "Tell me whether you know it, believe it, or are only guessing."
                ])

            statement = context.get(
                "statement",
                ""
            )
            subject = context.get(
                "subject",
                self.extract_subject(statement)
            )

            item, updated = self.memory.add_knowledge_item(
                statement=statement,
                subject=subject,
                knowledge_type=classification["type"],
                source=self.user_source(),
                confidence=classification["confidence"],
                verified=False,
                notes=classification.get(
                    "source_note",
                    ""
                )
            )

            self.maybe_add_grounded_curiosity(
                item
            )

            return self.saved_reply(
                item,
                updated
            )

        if question_type == "teach_unknown":

            if self.is_postpone_reply(text):

                topic = context.get("topic", "that")

                self.memory.add_curiosity(
                    f"What should I know about {topic}?",
                    topic,
                    status="waiting"
                )

                return random.choice([
                    "That's okay. We can leave it for another time.",
                    "No problem. That question can wait.",
                    "All right. I'll keep the question for later."
                ])

            result = self.check_teaching_statement(
                message,
                text
            )

            if result:
                return result

            return (
                "I think you're explaining it, but I need a "
                "full sentence so I know exactly what to remember."
            )

        if question_type == "curiosity_answer":

            curiosity_id = context.get(
                "curiosity_id",
                ""
            )

            if self.is_postpone_reply(text):

                self.memory.update_curiosity_status(
                    curiosity_id,
                    "waiting"
                )

                return random.choice([
                    "That's okay. Another time.",
                    "No problem. My question can wait.",
                    "All right — I'll leave it there for now."
                ])

            if self.is_close_reply(text):

                self.memory.update_curiosity_status(
                    curiosity_id,
                    "closed"
                )

                return random.choice([
                    "That's completely okay. I won't ask again.",
                    "Understood. I'll close that question.",
                    "No problem. We can leave that one alone."
                ])

            if self.is_positive_relation_reply(text):

                self.memory.update_curiosity_status(
                    curiosity_id,
                    "answered"
                )

                return random.choice([
                    "Oh, so they are connected. That makes sense.",
                    "Got it — you were confirming that they are related.",
                    "So I was on the right track. I'll keep that connection in mind.",
                    "Right, they are connected. Thanks for confirming it."
                ])

            if self.is_negative_relation_reply(text):

                self.memory.update_curiosity_status(
                    curiosity_id,
                    "answered"
                )

                return random.choice([
                    "Got it — they are not connected after all.",
                    "Okay, so those two things are separate.",
                    "Thanks for correcting me. I won't link them together.",
                    "Understood. That connection was only a possibility."
                ])

            if self.is_uncertain_relation_reply(text):

                self.memory.update_curiosity_status(
                    curiosity_id,
                    "waiting"
                )

                return random.choice([
                    "That's okay. We can leave it uncertain for now.",
                    "Fair enough. I'll keep it as an open question.",
                    "No problem. We don't have to decide yet."
                ])

            result = self.check_teaching_statement(
                message,
                text
            )

            if result:

                self.memory.update_curiosity_status(
                    curiosity_id,
                    "answered"
                )

                return result

            return (
                "I think you're answering my question, but I didn't "
                "quite understand whether you meant yes, no, or that "
                "you're unsure."
            )

        return None

    # -------------------------------------------------
    # Grounded curiosity
    # -------------------------------------------------

    def maybe_add_grounded_curiosity(self, new_item):

        if not new_item:
            return None

        if new_item.get("type") in [
            "joke",
            "opinion",
            "guess"
        ]:
            return None

        subject = new_item.get(
            "subject",
            ""
        ).strip()

        if not subject:
            return None

        related_items = self.find_related_knowledge(
            new_item
        )

        if not related_items:
            return None

        older_item = related_items[0]

        first_statement = older_item.get(
            "statement",
            ""
        ).strip()

        second_statement = new_item.get(
            "statement",
            ""
        ).strip()

        if (
            not first_statement
            or not second_statement
        ):
            return None

        question = random.choice([
            (
                f"You taught me that {first_statement}, "
                f"and also that {second_statement}. "
                "Are those two things connected?"
            ),
            (
                f"I know that {first_statement}, and now I've learned "
                f"that {second_statement}. Is there a connection between them?"
            ),
            (
                f"Do {first_statement} and {second_statement} "
                "have anything to do with each other?"
            )
        ])

        return self.memory.add_curiosity(
            question=question,
            topic=subject,
            priority="low",
            status="open"
        )

    def find_related_knowledge(self, new_item):

        subject = self.normalise_subject(
            new_item.get(
                "subject",
                ""
            )
        )

        if not subject:
            return []

        new_id = new_item.get("id", "")
        new_statement = self.normalise_subject(
            new_item.get(
                "statement",
                ""
            )
        )

        related = []

        for item in self.memory.knowledge.get(
            "items",
            []
        ):

            if item.get("id") == new_id:
                continue

            if item.get("type") in [
                "joke",
                "opinion",
                "guess"
            ]:
                continue

            item_subject = self.normalise_subject(
                item.get(
                    "subject",
                    ""
                )
            )

            item_statement = self.normalise_subject(
                item.get(
                    "statement",
                    ""
                )
            )

            if (
                item_subject == subject
                and item_statement
                and item_statement != new_statement
            ):
                related.append(item)

        related.sort(
            key=lambda item: item.get(
                "updated_at",
                ""
            ),
            reverse=True
        )

        return related

    def normalise_subject(self, text):

        cleaned = re.sub(
            r"[^a-z0-9\s]",
            "",
            str(text).lower()
        )

        return " ".join(
            cleaned.split()
        )

    # -------------------------------------------------
    # Classification
    # -------------------------------------------------

    def classify_statement(self, message):

        text = message.lower().strip()

        if self.contains_any(text, [
            "i was joking",
            "i'm joking",
            "im joking",
            "just kidding",
            "not literally",
            "as a joke"
        ]):
            return {
                "type": "joke",
                "confidence": "low"
            }

        if self.contains_any(text, [
            "in my opinion",
            "that's just what i believe",
            "thats just what i believe",
            "that's what i believe",
            "thats what i believe",
            "i believe that",
            "i believe ",
            "personally",
            "to me,",
            "from my point of view"
        ]):
            return {
                "type": "opinion",
                "confidence": "personal"
            }

        if self.contains_any(text, [
            "i'm guessing",
            "im guessing",
            "i guess",
            "my guess is",
            "just a guess"
        ]):
            return {
                "type": "guess",
                "confidence": "low"
            }

        if self.contains_any(text, [
            "i think",
            "maybe",
            "probably",
            "possibly",
            "i assume",
            "i'm assuming",
            "im assuming",
            "as far as i know",
            "i'm not sure",
            "im not sure",
            "not completely sure",
            "it might",
            "it could",
            "apparently",
            "i heard",
            "someone told me",
            "some one told me",
            "my teacher said",
            "my teacher told me",
            "a teacher said",
            "a teacher told me",
            "my friend said",
            "my friend told me",
            "i read that",
            "i read somewhere",
            "i saw that",
            "i saw online",
            "wikipedia says",
            "wikipedia said",
            "a documentary said",
            "an article said",
            "the internet says"
        ]):
            source_note = ""

            if self.contains_any(text, [
                "i heard",
                "someone told me",
                "some one told me",
                "apparently",
                "my teacher said",
                "my teacher told me",
                "a teacher said",
                "a teacher told me",
                "my friend said",
                "my friend told me",
                "i read that",
                "i read somewhere",
                "i saw that",
                "i saw online",
                "wikipedia says",
                "wikipedia said",
                "a documentary said",
                "an article said",
                "the internet says"
            ]):
                source_note = "second-hand information"

            confidence = "medium"

            if self.contains_any(text, [
                "maybe",
                "possibly",
                "i'm not sure",
                "im not sure",
                "not completely sure",
                "might",
                "could"
            ]):
                confidence = "low"

            return {
                "type": "assumption",
                "confidence": confidence,
                "source_note": source_note
            }

        if self.contains_any(text, [
            "research shows",
            "research has shown",
            "scientists know",
            "scientists have shown",
            "evidence shows",
            "studies show",
            "studies have shown",
            "it is widely accepted",
            "it's widely accepted",
            "its widely accepted",
            "it is generally accepted",
            "it's generally accepted",
            "its generally accepted",
            "i know for a fact",
            "this is definitely true",
            "that's definitely true",
            "thats definitely true",
            "it is definitely true",
            "i know this is true",
            "certainly",
            "definitely"
        ]):
            return {
                "type": "fact",
                "confidence": "high"
            }

        if re.search(
            r"\b(means|is defined as|refers to)\b",
            text
        ):
            return {
                "type": "definition",
                "confidence": "high"
            }

        return None

    def classify_reply(self, text):

        # Intention has priority over isolated words.
        if self.contains_any(text, [
            "i was joking",
            "i'm joking",
            "im joking",
            "just kidding",
            "not literally"
        ]):
            return {
                "type": "joke",
                "confidence": "low"
            }

        if self.contains_any(text, [
            "that's just what i believe",
            "thats just what i believe",
            "that's what i believe",
            "thats what i believe",
            "just my opinion",
            "my opinion",
            "i believe",
            "what i think",
            "only what i think"
        ]):
            return {
                "type": "opinion",
                "confidence": "personal"
            }

        if self.contains_any(text, [
            "i'm guessing",
            "im guessing",
            "i guess",
            "just a guess"
        ]):
            return {
                "type": "guess",
                "confidence": "low"
            }

        # “I think it's a fact” remains uncertain.
        if self.contains_any(text, [
            "i think",
            "maybe",
            "probably",
            "possibly",
            "i assume",
            "as far as i know",
            "i'm not sure",
            "im not sure",
            "not completely sure",
            "i heard",
            "someone told me",
            "some one told me",
            "my teacher said",
            "my teacher told me",
            "my friend said",
            "my friend told me",
            "i read that",
            "i read somewhere",
            "i saw that",
            "wikipedia says",
            "a documentary said",
            "an article said",
            "apparently"
        ]):
            return {
                "type": "assumption",
                "confidence": (
                    "low"
                    if self.contains_any(text, [
                        "maybe",
                        "possibly",
                        "not sure",
                        "i heard",
                        "someone told me",
                        "some one told me",
                        "my teacher said",
                        "my teacher told me",
                        "my friend said",
                        "my friend told me",
                        "i read that",
                        "i read somewhere",
                        "i saw that",
                        "wikipedia says",
                        "a documentary said",
                        "an article said"
                    ])
                    else "medium"
                )
            }

        if self.contains_any(text, [
            "a fact",
            "it is a fact",
            "it's a fact",
            "its a fact",
            "fact",
            "definitely true",
            "i know it is true",
            "i know it's true",
            "i know its true",
            "i know it is",
            "i know it's",
            "i know its",
            "i am certain",
            "i'm certain",
            "im certain",
            "i am sure",
            "i'm sure",
            "im sure",
            "research shows",
            "scientists know",
            "studies show",
            "it is established information",
            "it's established information",
            "its established information",
            "established information",
            "widely accepted",
            "generally accepted",
            "people know it is true",
            "people know it's true",
            "certainly true",
            "for certain"
        ]):
            return {
                "type": "fact",
                "confidence": "high"
            }

        if self.contains_any(text, [
            "an opinion",
            "opinion"
        ]):
            return {
                "type": "opinion",
                "confidence": "personal"
            }

        if self.contains_any(text, [
            "an assumption",
            "assumption",
            "a possibility",
            "possibility"
        ]):
            return {
                "type": "assumption",
                "confidence": "medium"
            }

        return None

    # -------------------------------------------------
    # Detection helpers
    # -------------------------------------------------

    def remove_teaching_prefix(
        self,
        message,
        text
    ):

        prefixes = [
            "did you know that ",
            "did you know ",
            "remember that ",
            "you should know that ",
            "a fact is that ",
            "fact: ",
            "here is a fact: ",
            "here's a fact: "
        ]

        for prefix in prefixes:

            if text.startswith(prefix):
                return (
                    message[len(prefix):].strip(),
                    True
                )

        return message.strip(), False

    def looks_like_world_statement(self, message):

        text = message.lower().strip()

        if len(text.split()) < 3:
            return False

        world_verbs = [
            " is ",
            " are ",
            " means ",
            " refers to ",
            " has ",
            " have ",
            " uses ",
            " use ",
            " can ",
            " could ",
            " might ",
            " may ",
            " cannot ",
            " can't ",
            " causes ",
            " contains ",
            " lives ",
            " grows ",
            " goes ",
            " makes "
        ]

        return any(
            verb in f" {text} "
            for verb in world_verbs
        )

    def is_personal_statement(self, text):

        personal_starters = [
            "my ",
            "i am ",
            "i'm ",
            "im ",
            "i have ",
            "i like ",
            "i love ",
            "i hate ",
            "i dislike ",
            "i enjoy ",
            "i went ",
            "i got ",
            "i bought ",
            "i feel "
        ]

        # These phrases can still introduce world knowledge.
        teaching_first_person = [
            "i think ",
            "i believe ",
            "i guess ",
            "i assume ",
            "i heard ",
            "i read ",
            "i saw ",
            "my teacher said ",
            "my teacher told me ",
            "my friend said ",
            "my friend told me ",
            "i know for a fact ",
            "i'm not sure ",
            "im not sure ",
            "as far as i know "
        ]

        if any(
            text.startswith(prefix)
            for prefix in teaching_first_person
        ):
            return False

        return any(
            text.startswith(prefix)
            for prefix in personal_starters
        )

    def extract_subject(self, statement):

        text = statement.strip().rstrip(".!?")

        definition_match = re.match(
            r"^(.+?)\s+(?:means|is defined as|refers to)\s+",
            text,
            re.IGNORECASE
        )

        if definition_match:
            return definition_match.group(1).strip()

        verb_match = re.match(
            r"^(.+?)\s+(?:is|are|has|have|uses|use|can|cannot|causes|contains|lives|grows|goes|makes)\b",
            text,
            re.IGNORECASE
        )

        if verb_match:
            subject = verb_match.group(1).strip()

            for prefix in [
                "i think ",
                "i believe ",
                "maybe ",
                "probably ",
                "apparently ",
                "as far as i know "
            ]:
                if subject.lower().startswith(prefix):
                    subject = subject[len(prefix):].strip()

            return subject

        words = text.split()

        return " ".join(words[:3])

    def clean_statement(self, statement):

        cleaned = statement.strip().rstrip(".!?")

        removable = [
            "in my opinion, ",
            "personally, ",
            "i think ",
            "i believe that ",
            "i believe ",
            "i guess ",
            "i assume ",
            "as far as i know, ",
            "as far as i know ",
            "apparently, ",
            "apparently ",
            "i heard that ",
            "someone told me that ",
            "some one told me that ",
            "my teacher said that ",
            "my teacher told me that ",
            "a teacher said that ",
            "a teacher told me that ",
            "my friend said that ",
            "my friend told me that ",
            "i read that ",
            "i saw that ",
            "wikipedia says that ",
            "wikipedia said that ",
            "a documentary said that ",
            "an article said that ",
            "the internet says that ",
            "research shows that ",
            "research has shown that ",
            "scientists have shown that ",
            "studies show that ",
            "studies have shown that "
        ]

        lower = cleaned.lower()

        for prefix in removable:

            if lower.startswith(prefix):
                cleaned = cleaned[len(prefix):].strip()
                break

        return cleaned

    def contains_any(self, text, phrases):

        return any(
            phrase in text
            for phrase in phrases
        )

    def is_positive_relation_reply(self, text):

        return text in [
            "yes",
            "yeah",
            "yea",
            "yep",
            "yes they are",
            "yeah they are",
            "they are",
            "theyre related",
            "they're related",
            "they are related",
            "you are right",
            "you're right",
            "your right",
            "correct",
            "exactly",
            "thats right",
            "that's right"
        ]

    def is_negative_relation_reply(self, text):

        return text in [
            "no",
            "nope",
            "no they arent",
            "no they aren't",
            "they arent",
            "they aren't",
            "they are not",
            "theyre not related",
            "they're not related",
            "they are not related",
            "you are wrong",
            "you're wrong",
            "your wrong",
            "not really"
        ]

    def is_uncertain_relation_reply(self, text):

        return text in [
            "i dont know",
            "i don't know",
            "im not sure",
            "i'm not sure",
            "not sure",
            "maybe",
            "possibly",
            "i think so",
            "probably"
        ]

    def is_postpone_reply(self, text):

        return text in [
            "not now",
            "another time",
            "maybe later",
            "later",
            "i dont have time",
            "i don't have time",
            "not today"
        ]

    def is_close_reply(self, text):

        return text in [
            "i dont want to answer",
            "i don't want to answer",
            "id rather not",
            "i'd rather not",
            "dont ask me that",
            "don't ask me that",
            "leave it"
        ]

    # -------------------------------------------------
    # Replies
    # -------------------------------------------------

    def saved_reply(self, item, updated):

        statement = item.get(
            "statement",
            "that"
        )
        knowledge_type = item.get(
            "type",
            "knowledge"
        )

        if updated:
            return random.choice([
                f"I've updated what I know about that. I'm keeping “{statement}” as a {knowledge_type}.",
                f"Got it — I've updated that piece of knowledge.",
                f"That replaces the older version in my library."
            ])

        notes = item.get(
            "notes",
            ""
        )

        if "second-hand information" in notes:
            return random.choice([
                f"I'll remember that you were told “{statement},” but I won't treat it as confirmed.",
                f"Got it. I'll keep “{statement}” as second-hand information.",
                "I'll remember the claim and also that it came from another source."
            ])

        if knowledge_type == "opinion":
            return random.choice([
                f"I'll remember that as your opinion: “{statement}.”",
                f"Got it. That's something you believe, not a universal fact.",
                f"I'll keep that as your view."
            ])

        if knowledge_type in [
            "assumption",
            "guess"
        ]:
            return random.choice([
                f"I'll keep “{statement}” as something uncertain, not a confirmed fact.",
                f"Got it. I'll remember that as a possibility.",
                f"I've saved it carefully, with the uncertainty attached."
            ])

        if knowledge_type == "joke":
            return random.choice([
                "Got it — a joke, not world knowledge.",
                "Noted as a joke. I won't mistake it for a fact.",
                "Understood. That one belongs in the joke drawer."
            ])

        if knowledge_type == "definition":
            return random.choice([
                f"I've learned that definition: {statement}.",
                f"Got it. I'll remember what that term means.",
                f"That definition is in my library now."
            ])

        return random.choice([
            f"I've learned that {statement}.",
            "Got it. I'll keep that as a user-taught fact.",
            "That's new to me. I've added it to what I know.",
            "Another little piece of the world added."
        ])

    def describe_learned_item(self, item):

        statement = item.get(
            "statement",
            ""
        )
        knowledge_type = item.get(
            "type",
            "knowledge"
        )
        source = item.get(
            "source",
            "you"
        )

        notes = item.get(
            "notes",
            ""
        )

        if "second-hand information" in notes:
            return random.choice([
                f"I remember the claim that {statement}, but I have it stored as second-hand information.",
                f"You told me that {statement}, although you weren't confirming it as established fact.",
                f"I've heard from you that {statement}, but I still have it marked as unconfirmed."
            ])

        if knowledge_type == "opinion":
            return (
                f"You taught me that “{statement}” is "
                f"{source}'s opinion."
            )

        if knowledge_type in [
            "assumption",
            "guess"
        ]:
            return (
                f"I've learned “{statement},” but I have it "
                "stored as uncertain rather than confirmed."
            )

        if knowledge_type == "joke":
            return (
                f"I remember “{statement},” but it was stored "
                "as a joke."
            )

        if source.lower() in [
            "the user",
            self.user_source().lower()
        ]:

            return random.choice([
                f"You taught me that {statement}.",
                f"From what you've taught me, {statement}.",
                f"I remember that {statement}.",
                f"From what I know, {statement}.",
                f"You've told me before that {statement}."
            ])

        return (
            f"From what {source} taught me, {statement}."
        )

    def user_source(self):

        name = self.memory.profile.get(
            "name",
            ""
        )

        return name if name else "the user"

    def make_result(
        self,
        reply,
        follow_up=None
    ):

        return {
            "reply": reply,
            "follow_up": follow_up
        }