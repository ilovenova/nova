"""
main.py

Entry point for NOVA.
"""

from memory import Memory
from brain import Brain
from commands import CommandHandler


def main():

    memory = Memory()

    brain = Brain(memory)

    commands = CommandHandler(memory)

    print("NOVA started.")
    print("Type /help")
    print()

    while True:

        user = input("You: ").strip()

        if not user:
            continue

        if user == "/exit":

            memory.save_all()

            print("Goodbye!")

            break

        if user.startswith("/"):

            print(commands.execute(user))

            continue

        reply = brain.respond(user)

        print("NOVA:", reply)

        memory.add_history(user, reply)


if __name__ == "__main__":
    main()