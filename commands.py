"""
commands.py

Handles slash commands for NOVA.
"""


class CommandHandler:

    def __init__(self, memory):
        self.memory = memory

    def execute(self, command):

        command = command.strip().lower()

        # -----------------------------
        # HELP
        # -----------------------------

        if command == "/help":

            return (
                "\n"
                "==============================\n"
                "      NOVA COMMANDS\n"
                "==============================\n\n"
                "Conversation\n"
                "/help      Show this menu\n"
                "/history   View conversation statistics\n\n"
                "Memory\n"
                "/memory    View memory statistics\n\n"
                "System\n"
                "/clear     Clear conversation history\n"
                "/exit      Close NOVA\n\n"
                "Coming Soon\n"
                "/search\n"
                "/note\n"
                "/calc\n"
                "/personality\n"
                "/learn\n"
                "=============================="
            )

        # -----------------------------
        # MEMORY
        # -----------------------------

        if command == "/memory":

            name = self.memory.profile.get("name", "Unknown")

            profile_facts = len(self.memory.profile.get("facts", {}))
            knowledge = len(self.memory.knowledge)
            notes = len(self.memory.notes)
            history = len(self.memory.history)
            personality = self.memory.settings.get("personality", "friendly")

            total = (
                profile_facts
                + knowledge
                + notes
                + history
            )

            return (
                "\n"
                "==============================\n"
                "        NOVA MEMORY\n"
                "==============================\n\n"
                f"Name: {name}\n\n"
                f"Profile Facts: {profile_facts}\n"
                f"Knowledge Facts: {knowledge}\n"
                f"Notes: {notes}\n"
                f"Conversation History: {history}\n\n"
                f"Personality: {personality}\n\n"
                f"Total Memories: {total}\n"
                "=============================="
            )

        # -----------------------------
        # HISTORY
        # -----------------------------

        if command == "/history":

            return (
                f"NOVA has stored "
                f"{len(self.memory.history)} conversations."
            )

        # -----------------------------
        # CLEAR
        # -----------------------------

        if command == "/clear":

            self.memory.history.clear()
            self.memory.save_all()

            return "Conversation history cleared."

        return "Unknown command. Type /help."