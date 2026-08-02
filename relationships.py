"""
relationships.py

Helps NOVA understand the important people and pets
in the user's life.

It stores:
- siblings
- family members
- friends
- pets

It also creates related follow-up questions.
"""

import random
import re


class Relationships:

    def __init__(self, memory):

        self.memory = memory

        self.relationships = self.memory.profile.setdefault(
            "relationships",
            {
                "siblings": [],
                "family": [],
                "friends": [],
                "pets": []
            }
        )

        self.relationships.setdefault("siblings", [])
        self.relationships.setdefault("family", [])
        self.relationships.setdefault("friends", [])
        self.relationships.setdefault("pets", [])

        self.memory.save_all()

    # -------------------------------------------------
    # Main router
    # -------------------------------------------------

    def respond(self, message, text):

        result = self.learn_sibling(message, text)

        if result:
            return result

        result = self.learn_pet(message, text)

        if result:
            return result

        result = self.learn_named_person(message, text)

        if result:
            return result

        result = self.recall_relationship(text)

        if result:
            return result

        return None

    # -------------------------------------------------
    # Learn siblings
    # -------------------------------------------------

    def learn_sibling(self, message, text):

        patterns = [
            (r"^i have a sister[.!]?$", "sister"),
            (r"^i have one sister[.!]?$", "sister"),
            (r"^i have a brother[.!]?$", "brother"),
            (r"^i have one brother[.!]?$", "brother"),
            (r"^i have a sibling[.!]?$", "sibling"),
            (r"^i have one sibling[.!]?$", "sibling")
        ]

        for pattern, relation in patterns:

            if re.match(pattern, text):

                existing = self.find_relative(
                    "siblings",
                    relation
                )

                if not existing:

                    person = {
                        "relation": relation,
                        "name": "",
                        "details": {}
                    }

                    self.relationships["siblings"].append(
                        person
                    )

                    self.memory.save_all()

                ask_name = random.choice([
                    True,
                    True,
                    False
                ])

                if ask_name:

                    pronoun = self.pronoun_for(relation)

                    return self.make_result(
                        random.choice([
                            f"Oh, you have a {relation}. What's {pronoun} name?",
                            f"I didn't know you had a {relation}. What is {pronoun} name?",
                            f"A {relation} — I'll remember that. What's {pronoun} name?"
                        ]),
                        {
                            "kind": "relationship",
                            "group": "siblings",
                            "relation": relation,
                            "question_type": "name"
                        }
                    )

                return self.make_result(
                    random.choice([
                        f"Oh, you have a {relation}. I'll remember that.",
                        f"I didn't know you had a {relation}.",
                        f"A {relation} — that is worth keeping in mind."
                    ])
                )

        named_patterns = [
            (
                r"^i have a sister called (.+?)[.!]?$",
                "sister"
            ),
            (
                r"^i have a sister named (.+?)[.!]?$",
                "sister"
            ),
            (
                r"^i have a brother called (.+?)[.!]?$",
                "brother"
            ),
            (
                r"^i have a brother named (.+?)[.!]?$",
                "brother"
            )
        ]

        for pattern, relation in named_patterns:

            match = re.match(pattern, text)

            if match:

                name = message[
                    match.start(1):match.end(1)
                ].strip().rstrip(".!")

                self.save_relative(
                    "siblings",
                    relation,
                    name
                )

                return self.make_result(
                    random.choice([
                        f"Your {relation} is called {name}. I'll remember her.",
                        f"Got it — {name} is your {relation}.",
                        f"{name}. That gives me a name to connect to your {relation}."
                    ])
                )

        return None

    # -------------------------------------------------
    # Learn pets
    # -------------------------------------------------

    def learn_pet(self, message, text):

        patterns = [
            (r"^i have a dog[.!]?$", "dog"),
            (r"^i have a cat[.!]?$", "cat"),
            (r"^i have a rabbit[.!]?$", "rabbit"),
            (r"^i have a hamster[.!]?$", "hamster"),
            (r"^i have a fish[.!]?$", "fish"),
            (r"^i have a pet[.!]?$", "pet")
        ]

        for pattern, animal in patterns:

            if re.match(pattern, text):

                existing = self.find_relative(
                    "pets",
                    animal
                )

                if not existing:

                    pet = {
                        "relation": animal,
                        "name": "",
                        "details": {}
                    }

                    self.relationships["pets"].append(pet)
                    self.memory.save_all()

                return self.make_result(
                    random.choice([
                        f"You have a {animal}? What's their name?",
                        f"Oh, a {animal}. What are they called?",
                        f"I'll remember that you have a {animal}. Do they have a name?"
                    ]),
                    {
                        "kind": "relationship",
                        "group": "pets",
                        "relation": animal,
                        "question_type": "name"
                    }
                )

        named_patterns = [
            r"^i have a (dog|cat|rabbit|hamster|fish|pet) called (.+?)[.!]?$",
            r"^i have a (dog|cat|rabbit|hamster|fish|pet) named (.+?)[.!]?$"
        ]

        for pattern in named_patterns:

            match = re.match(pattern, text)

            if match:

                animal = match.group(1)
                name = message[
                    match.start(2):match.end(2)
                ].strip().rstrip(".!")

                self.save_relative(
                    "pets",
                    animal,
                    name
                )

                return self.make_result(
                    random.choice([
                        f"Your {animal} is called {name}. I'll remember that.",
                        f"Got it — {name} is your {animal}.",
                        f"{name}. That is a lovely detail to know."
                    ])
                )

        return None

    # -------------------------------------------------
    # Learn other named people
    # -------------------------------------------------

    def learn_named_person(self, message, text):

        patterns = [
            (
                r"^my mum(?:'s|s) name is (.+?)[.!]?$",
                "mum",
                "family"
            ),
            (
                r"^my mom(?:'s|s) name is (.+?)[.!]?$",
                "mum",
                "family"
            ),
            (
                r"^my dad(?:'s|s) name is (.+?)[.!]?$",
                "dad",
                "family"
            ),
            (
                r"^my friend(?:'s|s) name is (.+?)[.!]?$",
                "friend",
                "friends"
            )
        ]

        for pattern, relation, group in patterns:

            match = re.match(pattern, text)

            if match:

                name = message[
                    match.start(1):match.end(1)
                ].strip().rstrip(".!")

                self.save_relative(
                    group,
                    relation,
                    name
                )

                return self.make_result(
                    random.choice([
                        f"Got it — {name} is your {relation}.",
                        f"I'll remember that your {relation} is called {name}.",
                        f"{name}. I'll keep that name connected to your {relation}."
                    ])
                )

        return None

    # -------------------------------------------------
    # Answer follow-up questions
    # -------------------------------------------------

    def answer_follow_up(self, message, context):

        question_type = context.get(
            "question_type",
            ""
        )

        if question_type != "name":
            return None

        text = message.strip().rstrip(".!")

        name = self.extract_name(text)

        if not name:
            return (
                "I didn't quite catch the name. "
                "You can say something like, 'Her name is Annie.'"
            )

        group = context.get(
            "group",
            "family"
        )

        relation = context.get(
            "relation",
            "relative"
        )

        self.save_relative(
            group,
            relation,
            name
        )

        if group == "pets":

            return random.choice([
                f"{name} — got it. I'll remember that your {relation} is called {name}.",
                f"Aw, {name}. Now I know your {relation}'s name.",
                f"Your {relation} is called {name}. That feels much more personal now."
            ])

        return random.choice([
            f"{name} — got it. I'll remember that {name} is your {relation}.",
            f"Now I know your {relation}'s name is {name}.",
            f"{name}. I'll keep that connected to your {relation}."
        ])

    # -------------------------------------------------
    # Recall
    # -------------------------------------------------

    def recall_relationship(self, text):

        sibling_questions = {
            "do i have a sister": "sister",
            "do i have a brother": "brother",
            "do i have any siblings": "any",
            "do i have siblings": "any"
        }

        if text in sibling_questions:

            wanted = sibling_questions[text]

            if wanted == "any":

                siblings = self.relationships.get(
                    "siblings",
                    []
                )

                if siblings:
                    return self.make_result(
                        "Yes. You've told me about "
                        + self.describe_people(siblings)
                        + "."
                    )

                return self.make_result(
                    "You haven't told me about any siblings yet."
                )

            relative = self.find_relative(
                "siblings",
                wanted
            )

            if relative:
                name = relative.get("name", "")

                if name:
                    return self.make_result(
                        f"Yes. Your {wanted} is called {name}."
                    )

                return self.make_result(
                    f"Yes. You told me you have a {wanted}."
                )

            return self.make_result(
                f"You haven't told me that you have a {wanted}."
            )

        name_patterns = [
            (
                r"^what is my sister(?:'s|s) name[?]?$",
                "siblings",
                "sister"
            ),
            (
                r"^what is my brother(?:'s|s) name[?]?$",
                "siblings",
                "brother"
            ),
            (
                r"^what is my dog(?:'s|s) name[?]?$",
                "pets",
                "dog"
            ),
            (
                r"^what is my cat(?:'s|s) name[?]?$",
                "pets",
                "cat"
            )
        ]

        for pattern, group, relation in name_patterns:

            if re.match(pattern, text):

                relative = self.find_relative(
                    group,
                    relation
                )

                if not relative:
                    return self.make_result(
                        f"You haven't told me about your {relation} yet."
                    )

                name = relative.get("name", "")

                if name:
                    return self.make_result(
                        f"Your {relation} is called {name}."
                    )

                return self.make_result(
                    f"You told me you have a {relation}, but I don't know their name yet."
                )

        if text in [
            "what pets do i have",
            "do i have any pets",
            "do i have pets"
        ]:

            pets = self.relationships.get(
                "pets",
                []
            )

            if pets:
                return self.make_result(
                    "You've told me about "
                    + self.describe_people(pets)
                    + "."
                )

            return self.make_result(
                "You haven't told me about any pets yet."
            )

        return None

    # -------------------------------------------------
    # Storage helpers
    # -------------------------------------------------

    def save_relative(
        self,
        group,
        relation,
        name
    ):

        relative = self.find_relative(
            group,
            relation
        )

        if not relative:

            relative = {
                "relation": relation,
                "name": "",
                "details": {}
            }

            self.relationships[group].append(relative)

        relative["name"] = name
        self.memory.save_all()

    def find_relative(self, group, relation):

        for person in self.relationships.get(
            group,
            []
        ):
            if (
                person.get("relation", "").lower()
                == relation.lower()
            ):
                return person

        return None

    def extract_name(self, text):

        prefixes = [
            "her name is ",
            "his name is ",
            "their name is ",
            "its name is ",
            "she is called ",
            "he is called ",
            "they are called ",
            "it is called ",
            "she's called ",
            "he's called "
        ]

        lower_text = text.lower()

        for prefix in prefixes:

            if lower_text.startswith(prefix):
                return text[len(prefix):].strip()

        words = text.split()

        if 1 <= len(words) <= 3:
            return text.strip()

        return ""

    def pronoun_for(self, relation):

        if relation == "sister":
            return "her"

        if relation == "brother":
            return "his"

        return "their"

    def describe_people(self, people):

        descriptions = []

        for person in people:

            relation = person.get(
                "relation",
                "relative"
            )

            name = person.get("name", "")

            if name:
                descriptions.append(
                    f"a {relation} called {name}"
                )
            else:
                descriptions.append(
                    f"a {relation}"
                )

        if len(descriptions) == 1:
            return descriptions[0]

        if len(descriptions) == 2:
            return (
                descriptions[0]
                + " and "
                + descriptions[1]
            )

        return (
            ", ".join(descriptions[:-1])
            + ", and "
            + descriptions[-1]
        )

    def make_result(
        self,
        reply,
        follow_up=None
    ):

        return {
            "reply": reply,
            "follow_up": follow_up
        }
