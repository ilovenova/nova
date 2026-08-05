import unittest

from brain import Brain
from memory import Memory


class ReferenceSelectionTests(unittest.TestCase):

    def setUp(self):
        self.memory = Memory()
        self.brain = Brain(self.memory)

    def test_pending_reference_selection_resolves_my_sister(self):
        self.brain.respond(
            "my friend and my sister were at the park"
        )

        clarification = self.brain.respond(
            "she was annoyed"
        )

        self.assertIsNotNone(
            self.brain.pending_follow_up,
            "Expected a pending reference selection follow-up"
        )

        self.assertEqual(
            self.brain.pending_follow_up.get("kind"),
            "reference_selection"
        )

        self.assertIn(
            "your friend",
            self.brain.pending_follow_up.get("options", [])
        )
        self.assertIn(
            "your sister",
            self.brain.pending_follow_up.get("options", [])
        )

        reply = self.brain.respond("my sister")

        self.assertIsNone(
            self.brain.pending_follow_up,
            "Reference selection should clear pending follow-up"
        )

        self.assertIn(
            "sister",
            reply.lower()
        )

    def test_pending_reference_selection_resolves_first_one(self):
        self.brain.respond(
            "my friend and my sister were at the park"
        )

        self.brain.respond("she was annoyed")

        reply = self.brain.respond("the first one")

        self.assertIsNone(
            self.brain.pending_follow_up,
            "First-one selection should clear pending follow-up"
        )

        self.assertIn(
            "friend",
            reply.lower()
        )


if __name__ == "__main__":
    unittest.main()
