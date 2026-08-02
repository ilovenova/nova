"""
learning.py

Handles learning from natural conversation.

This module returns structured results containing:
- Nova's reply
- optional follow-up context
"""

import random
import re


class Learning:

    def __init__(self, memory):

        self.memory = memory

        # Short-term topic memory.
        # This is not saved permanently.
        self.last_learning_topic = ""

    # -------------------------------------------------
    # Main learning router
    # -------------------------------------------------

    def learn(self, message):

        text = message.lower().strip()

        learners = [
            self.learn_name,
            self.learn_age,
            self.learn_birthday,
            self.learn_school,
            self.learn_favourite,
            self.learn_hobbies,
            self.learn_likes,
            self.learn_dislikes,
            self.learn_goal,
            self.learn_project,
            self.learn_new_activity,
            self.learn_event,
            self.learn_explicit_memory
        ]

        for learner in learners:

            result = learner(message, text)

            if result:
                return result

        return None

    # -------------------------------------------------
    # Result helper
    # -------------------------------------------------

    def result(self, reply, follow_up=None):

        return {
            "reply": reply,
            "follow_up": follow_up
        }

    # -------------------------------------------------
    # Name
    # -------------------------------------------------

    def learn_name(self, message, text):

        prefixes = [
            "my name is ",
            "call me ",
            "i am called ",
            "i'm called ",
            "im called "
        ]

        for prefix in prefixes:

            if text.startswith(prefix):

                name = message[len(prefix):].strip().rstrip(".!")

                if not name:

                    return self.result(
                        "What name would you like me to call you?"
                    )

                old_name = self.memory.set_name(name)

                if (
                    old_name
                    and old_name.lower() != name.lower()
                ):

                    reply = random.choice([
                        f"Got it — I'll call you {name} from now on.",
                        f"Okay, {name}. I'll remember the change.",
                        f"{name} it is."
                    ])

                    return self.result(reply)

                reply = random.choice([
                    f"Nice to meet you, {name}. I'll remember that.",
                    f"Got it — you're {name}.",
                    f"Hello, {name}. That name is staying with me."
                ])

                return self.result(reply)

        return None

    # -------------------------------------------------
    # Age
    # -------------------------------------------------

    def learn_age(self, message, text):

        patterns = [
            r"^i am (\d{1,3}) years? old[.!]?$",
            r"^i'm (\d{1,3}) years? old[.!]?$",
            r"^im (\d{1,3}) years? old[.!]?$",
            r"^my age is (\d{1,3})[.!]?$"
        ]

        for pattern in patterns:

            match = re.match(pattern, text)

            if match:

                age = int(match.group(1))

                if age < 1 or age > 130:

                    return self.result(
                        "That age doesn't look quite right. Could you check it?"
                    )

                old_age = self.memory.set_personal(
                    "age",
                    str(age)
                )

                if old_age and old_age != str(age):

                    reply = random.choice([
                        f"Got it — I've updated your age from {old_age} to {age}.",
                        f"You're {age} now. I'll keep that up to date.",
                        f"Age updated: {age}."
                    ])

                    return self.result(reply)

                reply = random.choice([
                    f"You're {age}. I'll keep that in mind.",
                    f"Got it — {age} years old.",
                    f"I'll remember that you're {age}."
                ])

                return self.result(reply)

        return None

    # -------------------------------------------------
    # Birthday
    # -------------------------------------------------

    def learn_birthday(self, message, text):

        prefixes = [
            "my birthday is ",
            "i was born on "
        ]

        for prefix in prefixes:

            if text.startswith(prefix):

                birthday = message[len(prefix):].strip().rstrip(".!")

                if not birthday:
                    return self.result("When is your birthday?")

                old_birthday = self.memory.set_personal(
                    "birthday",
                    birthday
                )

                if (
                    old_birthday
                    and old_birthday.lower() != birthday.lower()
                ):

                    reply = random.choice([
                        f"I've updated your birthday to {birthday}.",
                        f"Okay — {birthday} is the date I'll remember now.",
                        f"Birthday corrected. I'll keep {birthday} in mind."
                    ])

                    return self.result(reply)

                reply = random.choice([
                    f"{birthday} — I'll remember that.",
                    "Birthday noted, in a very un-robotic way.",
                    f"I'll keep {birthday} somewhere safe in my memory."
                ])

                return self.result(reply)

        return None

    # -------------------------------------------------
    # School
    # -------------------------------------------------

    def learn_school(self, message, text):

        prefixes = [
            "i go to ",
            "my school is ",
            "i study at "
        ]

        for prefix in prefixes:

            if text.startswith(prefix):

                school = message[len(prefix):].strip().rstrip(".!")

                if not school:
                    return None

                old_school = self.memory.set_personal(
                    "school",
                    school
                )

                if (
                    old_school
                    and old_school.lower() != school.lower()
                ):

                    reply = random.choice([
                        f"Got it — you now go to {school}.",
                        f"I've updated your school from {old_school} to {school}.",
                        f"{school}. I'll remember the change."
                    ])

                    return self.result(reply)

                if random.choice([True, False]):

                    reply = random.choice([
                        f"I'll remember that you go to {school}. How do you like it there?",
                        f"{school} — got it. What's your favourite thing about it?",
                        f"I'll keep {school} in mind. What subject do you enjoy most?"
                    ])

                    follow_up = {
                        "kind": "school",
                        "topic": school,
                        "question_type": "opinion"
                    }

                    return self.result(reply, follow_up)

                reply = random.choice([
                    f"I'll remember that you go to {school}.",
                    f"{school} — got it.",
                    f"Okay, I'll keep {school} in mind."
                ])

                return self.result(reply)

        return None

    # -------------------------------------------------
    # Favourites
    # -------------------------------------------------

    def learn_favourite(self, message, text):

        prefixes = [
            "actually my favourite ",
            "actually my favorite ",
            "my favourite ",
            "my favorite "
        ]

        for prefix in prefixes:

            if text.startswith(prefix) and " is " in text:

                rest = message[len(prefix):]

                lower_rest = rest.lower()
                split_position = lower_rest.find(" is ")

                category = rest[:split_position].strip().lower()
                value = rest[split_position + 4:].strip().rstrip(".!")

                value = self.clean_update_words(value)

                if not category or not value:
                    return None

                old_value = self.memory.set_favourite(
                    category,
                    value
                )

                if (
                    old_value
                    and old_value.lower() != value.lower()
                ):

                    reply = random.choice([
                        f"Got it — your favourite {category} is now {value}, not {old_value}.",
                        f"I'll replace {old_value} with {value} as your favourite {category}.",
                        f"{value} has officially taken over from {old_value}."
                    ])

                    return self.result(reply)

                if random.choice([True, False, False]):

                    question = self.favourite_question(
                        category,
                        value
                    )

                    reply = random.choice([
                        f"{value} — good choice. I'll remember that. {question}",
                        f"Your favourite {category} is {value}. That's staying with me. {question}",
                        f"{value}? Noted. {question}"
                    ])

                    follow_up = {
                        "kind": "favourite",
                        "topic": value,
                        "category": category,
                        "question_type": "reason"
                    }

                    return self.result(reply, follow_up)

                reply = random.choice([
                    f"{value} — good choice. I'll remember that.",
                    f"Your favourite {category} is {value}.",
                    f"{value}? Noted."
                ])

                return self.result(reply)

        return None

    # -------------------------------------------------
    # Hobbies
    # -------------------------------------------------

    def learn_hobbies(self, message, text):

        prefixes = [
            "my hobbies are ",
            "my hobbies include ",
            "my hobby is "
        ]

        for prefix in prefixes:

            if text.startswith(prefix):

                raw_hobbies = message[len(prefix):].strip().rstrip(".!")

                hobbies = self.split_items(raw_hobbies)

                if not hobbies:
                    return None

                new_hobbies = []

                for hobby in hobbies:

                    if self.is_vague_pronoun(hobby):
                        continue

                    if self.memory.add_hobby(hobby):
                        new_hobbies.append(hobby)

                if not new_hobbies:

                    reply = random.choice([
                        "I remember those hobbies already.",
                        "You told me that before — they're still remembered.",
                        "Already stored. My memory isn't completely hopeless."
                    ])

                    return self.result(reply)

                hobby_text = self.natural_list(new_hobbies)

                if random.choice([True, False]):

                    reply = random.choice([
                        f"I'll remember that your hobbies include {hobby_text}. Which one do you enjoy most?",
                        f"{hobby_text} — those are staying with me. Which one have you done most recently?",
                        f"Nice. I've got {hobby_text} in mind now. How did you get into them?"
                    ])

                    follow_up = {
                        "kind": "hobby",
                        "topic": hobby_text,
                        "question_type": "opinion"
                    }

                    return self.result(reply, follow_up)

                reply = random.choice([
                    f"I'll remember that your hobbies include {hobby_text}.",
                    f"{hobby_text} — those are staying with me.",
                    f"Nice. I've got {hobby_text} in mind now."
                ])

                return self.result(reply)

        return None

    # -------------------------------------------------
    # Likes
    # -------------------------------------------------

    def learn_likes(self, message, text):

        prefixes = [
            "i really like ",
            "i really love ",
            "i'm a fan of ",
            "im a fan of ",
            "i enjoy ",
            "i love ",
            "i like "
        ]

        for prefix in prefixes:

            if text.startswith(prefix):

                item = message[len(prefix):].strip().rstrip(".!")

                if not item:
                    return None

                if self.is_vague_pronoun(item):

                    return self.result(
                        "What are you referring to?"
                    )

                added = self.memory.add_like(item)

                if not added:

                    reply = random.choice([
                        f"I remember — you like {item}.",
                        f"{item} again? Yes, I remember that.",
                        f"I know that one. You're definitely a fan of {item}."
                    ])

                    return self.result(reply)

                if random.choice([True, False, False]):

                    reply = random.choice([
                        f"{item}? Nice. I'll keep that in mind. What do you like most about it?",
                        f"I'll remember that you enjoy {item}. How did you get into it?",
                        f"That one's staying with me: you like {item}. What makes it special to you?"
                    ])

                    follow_up = {
                        "kind": "like",
                        "topic": item,
                        "question_type": "reason"
                    }

                    return self.result(reply, follow_up)

                reply = random.choice([
                    f"{item}? Nice. I'll keep that in mind.",
                    f"I'll remember that you enjoy {item}.",
                    f"That one's staying with me: you like {item}."
                ])

                return self.result(reply)

        return None

    # -------------------------------------------------
    # Dislikes
    # -------------------------------------------------

    def learn_dislikes(self, message, text):

        prefixes = [
            "i'm not a fan of ",
            "im not a fan of ",
            "i cannot stand ",
            "i can't stand ",
            "i do not like ",
            "i don't like ",
            "i dislike ",
            "i hate "
        ]

        for prefix in prefixes:

            if text.startswith(prefix):

                item = message[len(prefix):].strip().rstrip(".!")

                if not item:
                    return None

                if self.is_vague_pronoun(item):

                    return self.result(
                        "What are you referring to?"
                    )

                added = self.memory.add_dislike(item)

                if not added:

                    reply = random.choice([
                        f"I remember — {item} isn't exactly your favourite.",
                        f"Yes, I know you don't like {item}.",
                        f"{item} remains firmly on your no-thank-you list."
                    ])

                    return self.result(reply)

                if random.choice([True, False, False]):

                    reply = random.choice([
                        f"I'll remember that {item} isn't for you. Was there a particular reason?",
                        f"{item} has made it onto your dislike list. What put you off it?",
                        f"Got it — no {item}. Has that always been the case?"
                    ])

                    follow_up = {
                        "kind": "dislike",
                        "topic": item,
                        "question_type": "reason"
                    }

                    return self.result(reply, follow_up)

                reply = random.choice([
                    f"I'll remember that {item} isn't for you.",
                    f"{item} has made it onto your dislike list.",
                    f"Got it — no {item}."
                ])

                return self.result(reply)

        return None

    # -------------------------------------------------
    # Goals
    # -------------------------------------------------

    def learn_goal(self, message, text):

        prefixes = [
            "one of my goals is to ",
            "my goal is to ",
            "i hope to ",
            "i want to become ",
            "i want to learn "
        ]

        for prefix in prefixes:

            if text.startswith(prefix):

                goal_text = message[len(prefix):].strip().rstrip(".!")

                if not goal_text:
                    return None

                if self.is_vague_pronoun(goal_text):

                    return self.result(
                        "What goal are you referring to?"
                    )

                if prefix == "i want to become ":
                    description = "Become " + goal_text

                elif prefix == "i want to learn ":
                    description = "Learn " + goal_text

                else:
                    description = goal_text

                self.memory.add_goal(description)

                if random.choice([True, False]):

                    reply = random.choice([
                        f"That's a goal worth keeping: {description}. What made you choose it?",
                        f"I'll remember that goal. What's your first step?",
                        f"{description} — I like that goal. How long have you wanted it?"
                    ])

                    follow_up = {
                        "kind": "goal",
                        "topic": description,
                        "question_type": "reason"
                    }

                    return self.result(reply, follow_up)

                reply = random.choice([
                    f"That's a goal worth keeping: {description}.",
                    f"I'll remember that goal.",
                    f"{description} — that's staying with me."
                ])

                return self.result(reply)

        return None

    # -------------------------------------------------
    # Projects
    # -------------------------------------------------

    def learn_project(self, message, text):

        prefixes = [
            "i'm working on ",
            "im working on ",
            "i am working on ",
            "my project is ",
            "i started a project called "
        ]

        for prefix in prefixes:

            if text.startswith(prefix):

                project_name = message[len(prefix):].strip().rstrip(".!")

                if not project_name:
                    return None

                if self.is_vague_pronoun(project_name):

                    return self.result(
                        "Which project are you referring to?"
                    )

                self.memory.add_project(project_name)

                if random.choice([True, False]):

                    reply = random.choice([
                        f"{project_name} — I'll remember that project. What are you working on first?",
                        f"That project is staying on my radar. What is {project_name} about?",
                        f"I've got {project_name} in mind now. How is it going so far?"
                    ])

                    follow_up = {
                        "kind": "project",
                        "topic": project_name,
                        "question_type": "progress"
                    }

                    return self.result(reply, follow_up)

                reply = random.choice([
                    f"{project_name} — I'll remember that project.",
                    f"That project is staying on my radar.",
                    f"I've got {project_name} in mind now."
                ])

                return self.result(reply)

        return None

    # -------------------------------------------------
    # New activities and skills
    # -------------------------------------------------

    def learn_new_activity(self, message, text):

        prefixes = [
            "i've started learning ",
            "ive started learning ",
            "i started learning ",
            "i'm learning ",
            "im learning ",
            "i am learning ",
            "i've started ",
            "ive started ",
            "i started "
        ]

        for prefix in prefixes:

            if text.startswith(prefix):

                activity = message[len(prefix):].strip().rstrip(".!")

                if not activity:
                    return self.result(
                        "What are you learning?"
                    )

                activity = self.resolve_learning_reference(activity)

                if not activity:

                    return self.result(
                        "What are you referring to? Tell me what you're learning."
                    )

                self.last_learning_topic = activity

                added = self.memory.add_hobby(activity)

                if not added:

                    return self.revisit_learning_topic(activity)

                question_choices = [
                    (
                        f"{self.display_topic(activity)}? That's exciting. What made you start?",
                        "reason"
                    ),
                    (
                        f"You're learning {self.display_topic(activity)} now. How is it going?",
                        "progress"
                    ),
                    (
                        f"Nice. What has been the hardest part so far?",
                        "difficulty"
                    ),
                    (
                        f"I'll keep {self.display_topic(activity)} in mind.",
                        None
                    ),
                    (
                        f"You're learning {self.display_topic(activity)} now — that's staying with me.",
                        None
                    )
                ]

                reply, question_type = random.choice(
                    question_choices
                )

                if question_type:

                    follow_up = {
                        "kind": "learning",
                        "topic": activity,
                        "question_type": question_type
                    }

                    return self.result(reply, follow_up)

                return self.result(reply)

        return None

    def revisit_learning_topic(self, activity):

        display_topic = self.display_topic(activity)

        choices = [
            (
                f"I remember you're learning {display_topic}. How has it been going lately?",
                "progress"
            ),
            (
                f"Yes, I remember {display_topic}. What's been the hardest part recently?",
                "difficulty"
            ),
            (
                f"I remember that one. Are you still enjoying {display_topic}?",
                "progress"
            ),
            (
                f"{display_topic} — yes, I remember.",
                None
            ),
            (
                f"I've still got {display_topic} in mind.",
                None
            )
        ]

        reply, question_type = random.choice(choices)

        if question_type:

            follow_up = {
                "kind": "learning",
                "topic": activity,
                "question_type": question_type
            }

            return self.result(reply, follow_up)

        return self.result(reply)

    def resolve_learning_reference(self, activity):

        cleaned = activity.strip()

        if not self.is_vague_pronoun(cleaned):
            return cleaned

        if self.last_learning_topic:
            return self.last_learning_topic

        return ""

    # -------------------------------------------------
    # Events and recent experiences
    # -------------------------------------------------

    def learn_event(self, message, text):

        event_patterns = [
            (
                r"^i went (.+?) today[.!]?$",
                "went {value} today",
                "activity"
            ),
            (
                r"^today i went (.+?)[.!]?$",
                "went {value} today",
                "activity"
            ),
            (
                r"^i got (.+?) today[.!]?$",
                "got {value} today",
                "new_thing"
            ),
            (
                r"^i bought (.+?) today[.!]?$",
                "bought {value} today",
                "new_thing"
            ),
            (
                r"^i visited (.+?) today[.!]?$",
                "visited {value} today",
                "visit"
            ),
            (
                r"^i met (.+?) today[.!]?$",
                "met {value} today",
                "person"
            )
        ]

        for pattern, template, event_type in event_patterns:

            match = re.match(pattern, text)

            if match:

                value = message[
                    match.start(1):match.end(1)
                ].strip()

                if self.is_vague_pronoun(value):

                    return self.result(
                        "What are you referring to?"
                    )

                description = template.format(value=value)

                self.memory.add_event(
                    description,
                    "today"
                )

                if random.choice([True, False]):

                    reply = self.event_question_reply(
                        event_type,
                        value
                    )

                    follow_up = {
                        "kind": "event",
                        "topic": value,
                        "question_type": "experience"
                    }

                    return self.result(reply, follow_up)

                reply = random.choice([
                    f"I'll keep today's {value} in mind.",
                    "That sounds worth remembering.",
                    f"Today's {value} is staying with me."
                ])

                return self.result(reply)

        return None

    # -------------------------------------------------
    # Explicit remembered information
    # -------------------------------------------------

    def learn_explicit_memory(self, message, text):

        prefixes = [
            "remember that ",
            "remember "
        ]

        for prefix in prefixes:

            if text.startswith(prefix):

                fact = message[len(prefix):].strip().rstrip(".!")

                if not fact:

                    return self.result(
                        "What would you like me to remember?"
                    )

                lower_fact = fact.lower()

                if lower_fact.startswith("my "):

                    cleaned_fact = fact[3:].strip()
                    key, value = self.split_fact(cleaned_fact)

                    self.memory.set_profile_fact(
                        key,
                        value
                    )

                    reply = random.choice([
                        "I'll keep that with the things I know about you.",
                        "That feels worth remembering.",
                        "Got it — that one's staying with me."
                    ])

                    return self.result(reply)

                key, value = self.split_fact(fact)

                self.memory.set_knowledge(
                    key,
                    value
                )

                reply = random.choice([
                    "I'll add that to what I know.",
                    "Got it. I'll keep that piece of knowledge in mind.",
                    "That's staying in my knowledge now."
                ])

                return self.result(reply)

        return None

    # -------------------------------------------------
    # Response helpers
    # -------------------------------------------------

    def event_question_reply(self, event_type, value):

        if event_type == "activity":

            return random.choice([
                f"{value.capitalize()} today? Nice. What was the best part?",
                f"I'll keep today's {value} in mind. Did you enjoy it?",
                "That sounds like a decent day. How did it go?"
            ])

        if event_type == "new_thing":

            return random.choice([
                f"You got {value} today? Tell me more about it.",
                f"New {value}? Nice. What made you choose it?",
                "That sounds exciting. What is it like?"
            ])

        if event_type == "visit":

            return random.choice([
                f"You visited {value} today? What was it like?",
                f"{value} is part of today's story, then. What was the best part?",
                f"Had you been to {value} before?"
            ])

        if event_type == "person":

            return random.choice([
                f"You met {value} today? What were they like?",
                f"{value} is a new name for me to remember. How did you meet?",
                "Interesting. Did you get along?"
            ])

        return "That sounds worth remembering. How did it go?"

    def favourite_question(self, category, value):

        questions = {
            "colour": [
                "What do you like about that colour?",
                "Has it always been your favourite?"
            ],
            "food": [
                "What makes it your favourite?",
                "When did you last have it?"
            ],
            "animal": [
                "What do you like most about them?",
                "Would you ever want one as a pet?"
            ],
            "country": [
                "What do you like most about it?",
                "Would you like to visit one day?"
            ],
            "subject": [
                "What makes that subject interesting to you?",
                "Which part do you enjoy most?"
            ]
        }

        category_questions = questions.get(
            category,
            []
        )

        if category_questions:
            return random.choice(category_questions)

        return random.choice([
            f"What makes {value} your favourite?",
            "Has it always been your favourite?"
        ])

    # -------------------------------------------------
    # Text helpers
    # -------------------------------------------------

    def is_vague_pronoun(self, text):

        cleaned = text.lower().strip().rstrip(".!")

        return cleaned in [
            "it",
            "this",
            "that",
            "them",
            "that one",
            "this one"
        ]

    def display_topic(self, topic):

        if not topic:
            return topic

        return topic[0].upper() + topic[1:]

    def clean_update_words(self, value):

        unwanted_starts = [
            "now ",
            "currently ",
            "actually "
        ]

        cleaned = value.strip()

        for unwanted in unwanted_starts:

            if cleaned.lower().startswith(unwanted):

                cleaned = cleaned[
                    len(unwanted):
                ].strip()

        return cleaned

    def split_items(self, text):

        parts = re.split(
            r",|\band\b",
            text,
            flags=re.IGNORECASE
        )

        return [
            part.strip()
            for part in parts
            if part.strip()
        ]

    def split_fact(self, fact):

        lower_fact = fact.lower()

        if " is " in lower_fact:

            position = lower_fact.find(" is ")

            key = fact[:position].strip()
            value = fact[position + 4:].strip()

            return key, value

        return fact.strip(), True

    def natural_list(self, items):

        if not items:
            return ""

        if len(items) == 1:
            return items[0]

        if len(items) == 2:
            return items[0] + " and " + items[1]

        return (
            ", ".join(items[:-1])
            + ", and "
            + items[-1]
        )