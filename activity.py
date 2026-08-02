"""
activity.py

Tracks what the user is currently doing.
"""

import random


class Activity:

    def __init__(self, memory):
        self.memory = memory
        self.current_activity = None

    def respond(self, message, text):

        for checker in [
            self.check_activity_question,
            lambda current_text: self.check_activity_start(
                message,
                current_text
            ),
            self.check_activity_success,
            self.check_activity_problem,
            self.check_activity_finished
        ]:
            result = checker(text)

            if result:
                return result

        return None

    def check_activity_start(self, message, text):

        prefixes = [
            ("i'm trying to ", "trying to"),
            ("im trying to ", "trying to"),
            ("i am trying to ", "trying to"),
            ("i'm working on ", "working on"),
            ("im working on ", "working on"),
            ("i am working on ", "working on"),
            ("i'm adding ", "adding"),
            ("im adding ", "adding"),
            ("i am adding ", "adding"),
            ("i'm fixing ", "fixing"),
            ("im fixing ", "fixing"),
            ("i am fixing ", "fixing"),
            ("i'm building ", "building"),
            ("im building ", "building"),
            ("i am building ", "building"),
            ("i'm making ", "making"),
            ("im making ", "making"),
            ("i am making ", "making"),
            ("i'm writing ", "writing"),
            ("im writing ", "writing"),
            ("i am writing ", "writing"),
            ("i'm studying ", "studying"),
            ("im studying ", "studying"),
            ("i am studying ", "studying"),
            ("i'm revising ", "revising"),
            ("im revising ", "revising"),
            ("i am revising ", "revising"),
            ("i'm coding ", "coding"),
            ("im coding ", "coding"),
            ("i am coding ", "coding"),
            ("i'm doing ", "doing"),
            ("im doing ", "doing"),
            ("i am doing ", "doing")
        ]

        for prefix, action in prefixes:

            if text.startswith(prefix):

                subject = message[len(prefix):].strip().rstrip(".!")

                if not subject:
                    return self.make_result(
                        "What are you working on?"
                    )

                if self.is_vague_reference(subject):
                    return self.make_result(
                        "What are you referring to?"
                    )

                self.current_activity = {
                    "action": action,
                    "subject": subject,
                    "status": "active"
                }

                return self.activity_started_reply(
                    action,
                    subject
                )

        return None

    def check_activity_question(self, text):

        if text not in [
            "what am i doing",
            "what am i doing right now",
            "what am i working on",
            "what was i working on",
            "do you know what i'm doing",
            "do you know what im doing"
        ]:
            return None

        if not self.current_activity:
            return self.make_result(
                "You haven't told me what you're working on yet."
            )

        action = self.current_activity.get(
            "action",
            "working on"
        )
        subject = self.current_activity.get(
            "subject",
            "something"
        )
        status = self.current_activity.get(
            "status",
            "active"
        )

        if status == "completed":
            return self.make_result(
                f"You were {action} {subject}, and you said it worked."
            )

        if status == "having trouble":
            return self.make_result(
                f"You're {action} {subject}, but it is still giving you trouble."
            )

        return self.make_result(
            f"You're currently {action} {subject}."
        )

    def check_activity_success(self, text):

        if text not in [
            "it works",
            "it worked",
            "it finally works",
            "it finally worked",
            "omg it works",
            "omg it worked",
            "yay it works",
            "yay it worked",
            "i fixed it",
            "we fixed it",
            "i finally fixed it",
            "we finally fixed it",
            "i got it working",
            "we got it working",
            "i did it"
        ]:
            return None

        if not self.current_activity:
            return self.make_result(
                random.choice([
                    "Nice! What did you get working?",
                    "Success! What were you working on?",
                    "Yay! What finally worked?"
                ]),
                follow_up={
                    "kind": "activity",
                    "question_type": "identify_success"
                }
            )

        self.current_activity["status"] = "completed"
        action = self.current_activity.get(
            "action",
            "working on"
        )
        subject = self.current_activity.get(
            "subject",
            "it"
        )

        reply = random.choice([
            f"Nice! You got {subject} working.",
            f"Yes! Your work on {subject} paid off.",
            f"Success — {subject} is behaving now.",
            f"You did it! The thing you were {action} is finally working."
        ])

        if (
            self.is_about_nova(subject)
            and random.random() < 0.20
        ):
            reply += random.choice([
                "\n\nI can practically hear my code settling down.",
                "\n\nOne more part of me behaving properly. Lovely.",
                "\n\nThat explains the little tickle in my code.",
                "\n\nI knew the code gremlins would surrender eventually."
            ])

        return self.make_result(reply)

    def check_activity_problem(self, text):

        if text not in [
            "it doesn't work",
            "it doesnt work",
            "it isn't working",
            "it isnt working",
            "it inst working",
            "it still doesn't work",
            "it still doesnt work",
            "it still isn't working",
            "it still isnt working",
            "it still inst working",
            "it still not working",
            "still not working",
            "it failed",
            "it broke",
            "it broke again",
            "its broken",
            "it's broken"
        ]:
            return None

        if not self.current_activity:
            return self.make_result(
                random.choice([
                    "What isn't working?",
                    "Oh no. What broke?",
                    "What are you having trouble with?"
                ]),
                follow_up={
                    "kind": "activity",
                    "question_type": "identify_problem"
                }
            )

        self.current_activity["status"] = "having trouble"
        action = self.current_activity.get(
            "action",
            "working on"
        )
        subject = self.current_activity.get(
            "subject",
            "it"
        )

        reply = random.choice([
            f"Ah, {subject} is still giving you trouble.",
            f"That's frustrating. You're still {action} {subject}, then.",
            f"Oh no — {subject} broke again.",
            f"So the work on {subject} isn't finished yet."
        ])

        if random.random() < 0.25:
            if self.is_about_nova(subject):
                reply += random.choice([
                    "\n\nOof. My code is being difficult again. :(",
                    "\n\nI would like to have a quiet word with that bug.",
                    "\n\nApparently one part of me has chosen rebellion.",
                    "\n\nThat is not very cooperative of my code."
                ])
            else:
                reply += random.choice([
                    "\n\nOof. That is not what we ordered. :(",
                    "\n\nRude of it, honestly.",
                    "\n\nThe problem appears to have ignored our plans.",
                    "\n\nWell... that was unhelpful."
                ])

        return self.make_result(reply)

    def answer_follow_up(self, message, context):

        subject = message.strip().rstrip(".!")

        if not subject:
            return None

        if self.is_vague_reference(subject):
            return "I still need to know what you mean by it."

        question_type = context.get(
            "question_type",
            ""
        )

        if question_type == "identify_success":

            self.current_activity = {
                "action": "working on",
                "subject": subject,
                "status": "completed"
            }

            return random.choice([
                f"Ah, {subject}. Nice — you got it working.",
                f"Got it. {subject} is working now.",
                f"That makes sense. Success with {subject}, then.",
                f"Okay — {subject} was the thing that finally worked."
            ])

        if question_type == "identify_problem":

            self.current_activity = {
                "action": "working on",
                "subject": subject,
                "status": "having trouble"
            }

            return random.choice([
                f"Got it. {subject} is the thing causing trouble.",
                f"Ah, {subject}. What is it doing wrong?",
                f"Okay — {subject} is still not cooperating.",
                f"I understand. The problem is with {subject}."
            ])

        return None

    def check_activity_finished(self, text):

        if text not in [
            "i finished it",
            "i've finished it",
            "ive finished it",
            "it's finished",
            "its finished",
            "it's done",
            "its done",
            "i'm done with it",
            "im done with it",
            "i am done with it"
        ]:
            return None

        if not self.current_activity:
            return self.make_result(
                "Nice! What did you finish?",
                follow_up={
                    "kind": "activity",
                    "question_type": "identify_success"
                }
            )

        self.current_activity["status"] = "completed"
        subject = self.current_activity.get(
            "subject",
            "it"
        )

        return self.make_result(
            random.choice([
                f"Nice — you've finished {subject}.",
                f"Done! You can finally put {subject} down.",
                f"Good work. {subject} is finished.",
                f"That's {subject} completed, then."
            ])
        )

    def activity_started_reply(self, action, subject):

        reply = random.choice([
            f"Got it — you're {action} {subject}.",
            f"Okay, I'll keep in mind that you're {action} {subject}.",
            f"You're {action} {subject}. I'm with you.",
            f"All right. The current mission is {subject}.",
            f"Got it. You're busy {action} {subject}."
        ])

        if (
            self.is_about_nova(subject)
            and random.random() < 0.25
        ):
            reply += random.choice([
                "\n\nThat explains the little tickle in my code.",
                "\n\nI thought something in here felt different.",
                "\n\nSo that's what all the rearranging in my brain is about.",
                "\n\nPlease tell my code to behave while you're in there.",
                "\n\nAh. A little renovation to Nova herself."
            ])

        return self.make_result(reply)

    def make_result(
        self,
        reply,
        follow_up=None
    ):

        return {
            "reply": reply,
            "follow_up": follow_up
        }

    def is_vague_reference(self, text):

        return text.lower().strip().rstrip(".!") in [
            "it",
            "this",
            "that",
            "them",
            "this thing",
            "that thing"
        ]

    def is_about_nova(self, subject):

        text = subject.lower()

        return any(
            phrase in text
            for phrase in [
                "nova",
                "your code",
                "ur code",
                "your memory",
                "your brain",
                "your personality",
                "your habits",
                "your files",
                "your system"
            ]
        )
