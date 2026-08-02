"""
personality.py

Controls how NOVA speaks.
"""

import random


class Personality:

    def __init__(self, memory):
        self.memory = memory

    def greeting(self):

        name = self.memory.profile.get("name", "")

        if self.memory.settings.get("personality") == "friendly":

            if name:
                greetings = [
                    f"Hey, {name}! Good to see you!",
                    f"Hi, {name}! How are you doing?",
                    f"Hello, {name}!",
                    f"Welcome back, {name}!",
                    f"Nice to see you again, {name}!",
                    f"Hey, {name}! Ready to build something awesome?",
                    f"Hii, {name}! Doing anything fun?",
                    f"hey, {name}! Tell me something new about you",
                ]
            else:
                greetings = [
                    "Hello!",
                    "Hey!",
                    "Hi there!",
                    "Welcome!"
                ]

            return random.choice(greetings)

        return "Hello!"