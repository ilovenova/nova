import random
import unittest

from brain import Brain
from memory import Memory


class StoryAndOrdinaryLanguageTests(unittest.TestCase):

    def setUp(self):
        random.seed(0)
        self.memory = Memory()
        self.brain = Brain(self.memory)

    def test_person_description_with_my_mum_sets_current_person_label(self):
        reply = self.brain.respond("my mum was kind")

        self.assertIsNotNone(reply)
        self.assertEqual(
            self.brain.context.current_person_label,
            "your mum"
        )
        self.assertIn(
            "your mum",
            self.brain.context.active_proposition
        )

    def test_story_sequence_with_and_then_updates_active_proposition(self):
        self.brain.respond("i went to the park")

        reply = self.brain.respond("and then it started raining")

        self.assertIsNotNone(reply)
        self.assertIn(
            "raining",
            self.brain.context.active_proposition.lower()
        )
        self.assertEqual(
            self.brain.context.active_proposition,
            "it started raining"
        )

    def test_ordinary_statement_finished_homework_sets_active_proposition(self):
        reply = self.brain.respond("I've finished my homework")

        self.assertIsNotNone(reply)
        self.assertIn(
            "you finishing my homework",
            self.brain.context.active_proposition
        )
        self.assertTrue(
            reply,
            "Expected a reply for a finished homework statement"
        )

    def test_new_experience_match_handles_i_got_a_message(self):
        reply = self.brain.respond("i got a message")

        self.assertIsNotNone(reply)
        self.assertEqual(
            self.brain.context.active_proposition,
            "you got a message"
        )

    def test_pending_reference_selection_resolves_the_other_one(self):
        self.brain.respond("my friend and my sister were at the park")
        self.brain.respond("she was annoyed")

        reply = self.brain.respond("the other one")

        self.assertIsNone(
            self.brain.pending_follow_up,
            "Other-one selection should clear pending follow-up"
        )
        self.assertIn(
            "sister",
            reply.lower()
        )


if __name__ == "__main__":
    unittest.main()
