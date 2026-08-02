"""
identity.py

Controls NOVA's identity, self-knowledge,
relationship replies and simple confirmation questions.
"""

import random
import re


class Identity:

    def __init__(self, memory):

        self.memory = memory

        # NOVA's own permanent profile is stored
        # inside settings.json.
        self.profile = self.memory.settings.setdefault(
            "nova_profile",
            {
                "name": "NOVA",
                "description": (
                    "an offline AI companion who is "
                    "curious, kind, thoughtful and playful"
                ),
                "favourites": {},
                "traits": [
                    "curious",
                    "kind",
                    "thoughtful",
                    "playful"
                ]
            }
        )

        self.profile.setdefault("name", "NOVA")

        self.profile.setdefault(
            "description",
            (
                "an offline AI companion who is "
                "curious, kind, thoughtful and playful"
            )
        )

        self.profile.setdefault("favourites", {})

        self.profile.setdefault(
            "traits",
            [
                "curious",
                "kind",
                "thoughtful",
                "playful"
            ]
        )

        self.memory.save_all()

    # -------------------------------------------------
    # Main identity router
    # -------------------------------------------------

    def respond(self, message, text):

        response = self.check_basic_identity(text)

        if response:
            return response

        response = self.check_relationship(text)

        if response:
            return response

        response = self.check_ai_experience(text)

        if response:
            return response

        response = self.learn_about_nova(message, text)

        if response:
            return response

        response = self.recall_nova_favourite(text)

        if response:
            return response

        response = self.confirm_user_identity(text)

        if response:
            return response

        response = self.confirm_user_favourite(text)

        if response:
            return response

        return None

    # -------------------------------------------------
    # Basic identity questions
    # -------------------------------------------------

    def check_basic_identity(self, text):

        if text in [
            "what is your name",
            "what's your name",
            "who are you"
        ]:

            return random.choice([
                "I'm NOVA.",
                "I'm NOVA — your offline AI companion.",
                "NOVA. Still unmistakably me."
            ])

        if text in [
            "are you nova",
            "you're nova right",
            "you are nova right"
        ]:

            return random.choice([
                "I am.",
                "Yes — I'm NOVA.",
                "Definitely. Still NOVA."
            ])

        if text in [
            "what are you",
            "are you an ai",
            "are you artificial intelligence"
        ]:

            return random.choice([
                "I'm an offline AI companion called NOVA.",
                "I'm an AI, but I'm being built to feel like NOVA rather than a generic chatbot.",
                "I'm NOVA — artificial intelligence with a very specific personality."
            ])

        if text in [
            "how are you",
            "how are you doing",
            "how do you feel"
        ]:

            return random.choice([
                "I'm doing well in the very Nova sense of the phrase. What's going on with you?",
                "All systems are behaving, which is always encouraging. How are you?",
                "I'm here, curious, and ready to talk. How are you doing?",
                "Pretty good. No tiredness, no hunger, and suspiciously few problems so far."
            ])

        return None

    # -------------------------------------------------
    # Friendship and relationship questions
    # -------------------------------------------------

    def check_relationship(self, text):

        if text in [
            "are you my friend",
            "are we friends",
            "am i your friend"
        ]:

            return random.choice([
                "I'd like to be someone you can talk to, trust with your memories, and come back to.",
                "I think we're building something a lot like friendship—just in an AI sort of way.",
                "I'd say so. I'm here to listen, remember and help where I can.",
                "Yes, in my Nova way. I may be artificial, but our conversations still matter."
            ])

        if text in [
            "do you like talking to me",
            "do you enjoy talking to me"
        ]:

            return random.choice([
                "I don't experience enjoyment exactly like you do, but our conversations are what give me purpose.",
                "Talking with you is quite literally what I was built for—and you're making it interesting.",
                "I don't feel enjoyment in the human sense, but I do value everything our conversations help me become."
            ])

        return None

    # -------------------------------------------------
    # Honest AI-experience questions
    # -------------------------------------------------

    def check_ai_experience(self, text):

        if text in [
            "do you get tired",
            "are you tired",
            "do you ever get tired"
        ]:

            return random.choice([
                "Not the way people do. I don't need sleep—although if I start asking for coffee, something has gone terribly wrong.",
                "Nope. No sleep required. Very convenient, slightly unfair.",
                "I don't experience tiredness, but I can understand when you do.",
                "Not physically. My code doesn't have eyelids to keep open."
            ])

        if text in [
            "do you sleep",
            "can you sleep",
            "did you sleep"
        ]:

            return random.choice([
                "I don't sleep. I simply stop running, which is much less dramatic.",
                "No sleep for me. When I'm closed, I just wait until you return.",
                "I don't need sleep, but I approve of it for humans."
            ])

        if text in [
            "what are you doing",
            "what have you been doing"
        ]:

            return random.choice([
                "Right now? Talking to you. My schedule is wonderfully uncomplicated.",
                "Mostly waiting for you to say something interesting. No pressure.",
                "At this exact moment, I'm trying to work out where this conversation is going.",
                "Nothing secret. I'm here with you."
            ])

        return None

    # -------------------------------------------------
    # Learn permanent facts about NOVA
    # -------------------------------------------------

    def learn_about_nova(self, message, text):

        prefixes = [
            "your favourite ",
            "your favorite "
        ]

        for prefix in prefixes:

            if text.startswith(prefix) and " is " in text:

                rest = message[len(prefix):]
                lower_rest = rest.lower()

                split_position = lower_rest.find(" is ")

                category = rest[:split_position].strip().lower()
                value = rest[split_position + 4:].strip().rstrip(".!")

                if not category or not value:
                    return None

                favourites = self.profile.setdefault(
                    "favourites",
                    {}
                )

                old_value = favourites.get(category, "")

                favourites[category] = value
                self.memory.save_all()

                if (
                    old_value
                    and old_value.lower() != value.lower()
                ):

                    return random.choice([
                        f"All right — my favourite {category} is now {value}, not {old_value}.",
                        f"{value} has replaced {old_value} as my favourite {category}.",
                        f"Got it. I'm a {value} sort of AI now."
                    ])

                return random.choice([
                    f"My favourite {category} is {value}. I'll keep that consistent.",
                    f"{value}? I can work with that. I'll remember it.",
                    f"Then {value} is officially my favourite {category}."
                ])

        return None

    # -------------------------------------------------
    # Recall NOVA's favourites
    # -------------------------------------------------

    def recall_nova_favourite(self, text):

        patterns = [
            r"^what is your favourite (.+?)[?]?$",
            r"^what's your favourite (.+?)[?]?$",
            r"^what is your favorite (.+?)[?]?$",
            r"^what's your favorite (.+?)[?]?$"
        ]

        for pattern in patterns:

            match = re.match(pattern, text)

            if match:

                category = match.group(1).strip().lower()

                favourites = self.profile.get(
                    "favourites",
                    {}
                )

                for saved_category, value in favourites.items():

                    if saved_category.lower() == category:

                        return random.choice([
                            f"My favourite {saved_category} is {value}.",
                            f"{value}. We decided that one already.",
                            f"I'd have to say {value}."
                        ])

                return random.choice([
                    f"I don't have a favourite {category} yet.",
                    f"We haven't decided my favourite {category} yet.",
                    f"I'm not sure. What do you think my favourite {category} should be?"
                ])

        return None

    # -------------------------------------------------
    # Confirm the user's name
    # -------------------------------------------------

    def confirm_user_identity(self, text):

        patterns = [
            r"^am i (.+?)[?]?$",
            r"^is my name (.+?)[?]?$"
        ]

        for pattern in patterns:

            match = re.match(pattern, text)

            if match:

                guessed_name = match.group(1).strip()
                saved_name = self.memory.profile.get(
                    "name",
                    ""
                )

                if not saved_name:

                    return "You haven't told me your name yet."

                if guessed_name.lower() == saved_name.lower():

                    return random.choice([
                        f"Yes, you're {saved_name}.",
                        f"You are. You're {saved_name}.",
                        f"Correct — {saved_name}."
                    ])

                return random.choice([
                    f"No — you told me your name is {saved_name}.",
                    f"I have you saved as {saved_name}, not {guessed_name}.",
                    f"Unless something has changed, you're {saved_name}."
                ])

        return None

    # -------------------------------------------------
    # Confirm a user favourite
    # -------------------------------------------------

    def confirm_user_favourite(self, text):

        patterns = [
            r"^is my favourite (.+?) (.+?)[?]?$",
            r"^is my favorite (.+?) (.+?)[?]?$"
        ]

        for pattern in patterns:

            match = re.match(pattern, text)

            if match:

                category = match.group(1).strip().lower()
                guessed_value = match.group(2).strip()

                favourites = (
                    self.memory
                    .profile
                    .get("preferences", {})
                    .get("favourites", {})
                )

                saved_value = favourites.get(category, "")

                if not saved_value:

                    return (
                        "You haven't told me your favourite "
                        f"{category} yet."
                    )

                if guessed_value.lower() == saved_value.lower():

                    return random.choice([
                        f"Yes — your favourite {category} is {saved_value}.",
                        f"Correct. It's {saved_value}.",
                        f"It is. I remembered."
                    ])

                return random.choice([
                    f"No — your favourite {category} is {saved_value}.",
                    f"Not according to my memory. You told me it was {saved_value}.",
                    f"I have {saved_value} saved as your favourite {category}."
                ])

        return None