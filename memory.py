"""
memory.py

Handles loading, saving, searching and editing NOVA's memory.
"""

from datetime import datetime
from utils import load_json, save_json


class Memory:

    def __init__(self):

        # -----------------------------
        # Main data files
        # -----------------------------

        self.knowledge = load_json("knowledge.json", {})
        self.history = load_json("history.json", [])
        self.profile = load_json("profile.json", {})
        self.notes = load_json("notes.json", [])

        self.settings = load_json(
            "settings.json",
            {
                "name": "NOVA",
                "personality": "friendly",
                "autosave": True
            }
        )

        self._upgrade_profile()
        self._upgrade_settings()
        self._upgrade_knowledge()

    # -------------------------------------------------
    # Upgrade profile.json safely
    # -------------------------------------------------

    def _upgrade_profile(self):

        self.profile.setdefault("name", "")

        personal = self.profile.setdefault("personal", {})
        personal.setdefault("age", "")
        personal.setdefault("birthday", "")
        personal.setdefault("gender", "")
        personal.setdefault("school", "")

        preferences = self.profile.setdefault("preferences", {})
        preferences.setdefault("likes", [])
        preferences.setdefault("dislikes", [])
        preferences.setdefault("favourites", {})
        preferences.setdefault("hobbies", [])

        self.profile.setdefault("habits", {})
        self.profile.setdefault("facts", {})
        self.profile.setdefault("events", [])
        self.profile.setdefault("goals", [])
        self.profile.setdefault("projects", [])

        self.save_all()


    # -------------------------------------------------
    # Upgrade knowledge.json safely
    # -------------------------------------------------

    def _upgrade_knowledge(self):

        if not isinstance(self.knowledge, dict):
            self.knowledge = {}

        legacy_items = []

        reserved_keys = {
            "items",
            "curiosities",
            "next_item_id",
            "next_curiosity_id"
        }

        for key, value in list(self.knowledge.items()):

            if key in reserved_keys:
                continue

            if value is True:
                statement = str(key)
            else:
                statement = f"{key} is {value}"

            legacy_items.append(
                {
                    "id": "",
                    "statement": statement,
                    "subject": str(key),
                    "type": "legacy",
                    "source": "older Nova memory",
                    "confidence": "unknown",
                    "verified": False,
                    "notes": "Automatically upgraded from the old knowledge format.",
                    "created_at": self.current_timestamp(),
                    "updated_at": self.current_timestamp(),
                    "times_recalled": 0
                }
            )

            del self.knowledge[key]

        items = self.knowledge.setdefault(
            "items",
            []
        )

        curiosities = self.knowledge.setdefault(
            "curiosities",
            []
        )

        self.knowledge.setdefault(
            "next_item_id",
            1
        )

        self.knowledge.setdefault(
            "next_curiosity_id",
            1
        )

        for item in legacy_items:
            item["id"] = self._next_knowledge_id()
            items.append(item)

        if not isinstance(items, list):
            self.knowledge["items"] = []

        if not isinstance(curiosities, list):
            self.knowledge["curiosities"] = []

        self.save_all()

    # -------------------------------------------------
    # Upgrade settings.json safely
    # -------------------------------------------------

    def _upgrade_settings(self):

        self.settings.setdefault("name", "NOVA")
        self.settings.setdefault("personality", "friendly")
        self.settings.setdefault("autosave", True)
        self.settings.setdefault("mood", "calm")
        self.settings.setdefault("debug", False)

        self.save_all()

    # -------------------------------------------------
    # Save everything
    # -------------------------------------------------

    def save_all(self):

        save_json("knowledge.json", self.knowledge)
        save_json("history.json", self.history)
        save_json("profile.json", self.profile)
        save_json("notes.json", self.notes)
        save_json("settings.json", self.settings)

    # -------------------------------------------------
    # Dates and timestamps
    # -------------------------------------------------

    def current_timestamp(self):

        return datetime.now().isoformat(timespec="seconds")

    # -------------------------------------------------
    # Conversation history
    # -------------------------------------------------

    def add_history(self, user, bot):

        self.history.append(
            {
                "timestamp": self.current_timestamp(),
                "user": user,
                "nova": bot
            }
        )

        if self.settings.get("autosave", True):
            self.save_all()

    # -------------------------------------------------
    # Basic personal information
    # -------------------------------------------------

    def set_name(self, name):

        old_value = self.profile.get("name", "")
        self.profile["name"] = name
        self.save_all()

        return old_value

    def set_personal(self, key, value):

        personal = self.profile.setdefault("personal", {})
        old_value = personal.get(key, "")
        personal[key] = value
        self.save_all()

        return old_value

    # -------------------------------------------------
    # Favourites
    # -------------------------------------------------

    def set_favourite(self, category, value):

        favourites = self.profile["preferences"]["favourites"]

        category = category.strip().lower()
        old_value = favourites.get(category, "")

        favourites[category] = value.strip()
        self.save_all()

        return old_value

    # -------------------------------------------------
    # Likes and dislikes
    # -------------------------------------------------

    def add_like(self, item):

        return self._add_unique_preference("likes", item)

    def add_dislike(self, item):

        return self._add_unique_preference("dislikes", item)

    def add_hobby(self, hobby):

        return self._add_unique_preference("hobbies", hobby)

    def _add_unique_preference(self, category, item):

        item = item.strip()

        if not item:
            return False

        items = self.profile["preferences"].setdefault(category, [])

        existing_items = [saved.lower() for saved in items]

        if item.lower() in existing_items:
            return False

        items.append(item)
        self.save_all()

        return True

    # -------------------------------------------------
    # Events, goals and projects
    # -------------------------------------------------

    def add_event(self, description, date_label=""):

        event = {
            "description": description.strip(),
            "date_label": date_label.strip(),
            "created_at": self.current_timestamp()
        }

        self.profile["events"].append(event)
        self.save_all()

        return event

    def add_goal(self, description):

        goal = {
            "description": description.strip(),
            "created_at": self.current_timestamp(),
            "completed": False
        }

        self.profile["goals"].append(goal)
        self.save_all()

        return goal

    def add_project(self, name):

        project = {
            "name": name.strip(),
            "created_at": self.current_timestamp(),
            "status": "active"
        }

        self.profile["projects"].append(project)
        self.save_all()

        return project

    # -------------------------------------------------
    # General facts
    # -------------------------------------------------

    def set_profile_fact(self, key, value):

        facts = self.profile.setdefault("facts", {})
        old_value = facts.get(key, "")

        facts[key] = value
        self.save_all()

        return old_value

    def set_knowledge(self, key, value):

        if value is True:
            statement = str(key)
        else:
            statement = f"{key} is {value}"

        item, updated = self.add_knowledge_item(
            statement=statement,
            subject=str(key),
            knowledge_type="fact",
            source="user",
            confidence="medium",
            verified=False,
            notes="Saved through the older set_knowledge method."
        )

        return item if updated else ""

    # -------------------------------------------------
    # Structured world knowledge
    # -------------------------------------------------

    def _next_knowledge_id(self):

        next_id = self.knowledge.get(
            "next_item_id",
            1
        )

        self.knowledge["next_item_id"] = (
            next_id + 1
        )

        return f"knowledge_{next_id}"

    def _next_curiosity_id(self):

        next_id = self.knowledge.get(
            "next_curiosity_id",
            1
        )

        self.knowledge["next_curiosity_id"] = (
            next_id + 1
        )

        return f"curiosity_{next_id}"

    def add_knowledge_item(
        self,
        statement,
        subject,
        knowledge_type,
        source,
        confidence,
        verified=False,
        notes=""
    ):

        statement = statement.strip()
        subject = subject.strip()
        knowledge_type = knowledge_type.strip().lower()

        normalised = self._normalise_text(
            statement
        )

        items = self.knowledge.setdefault(
            "items",
            []
        )

        for item in items:

            if (
                self._normalise_text(
                    item.get("statement", "")
                )
                == normalised
            ):

                item["subject"] = subject
                item["type"] = knowledge_type
                item["source"] = source
                item["confidence"] = confidence
                item["verified"] = bool(verified)
                item["notes"] = notes
                item["updated_at"] = (
                    self.current_timestamp()
                )

                self.save_all()
                return item, True

        item = {
            "id": self._next_knowledge_id(),
            "statement": statement,
            "subject": subject,
            "type": knowledge_type,
            "source": source,
            "confidence": confidence,
            "verified": bool(verified),
            "notes": notes,
            "created_at": self.current_timestamp(),
            "updated_at": self.current_timestamp(),
            "times_recalled": 0
        }

        items.append(item)
        self.save_all()

        return item, False

    def search_knowledge(
        self,
        query,
        knowledge_type=""
    ):

        query = self._normalise_text(query)
        knowledge_type = (
            knowledge_type.strip().lower()
        )

        results = []

        for item in self.knowledge.get(
            "items",
            []
        ):

            if (
                knowledge_type
                and item.get("type", "").lower()
                != knowledge_type
            ):
                continue

            searchable = " ".join([
                item.get("statement", ""),
                item.get("subject", ""),
                item.get("type", ""),
                item.get("notes", "")
            ])

            if query in self._normalise_text(
                searchable
            ):
                item["times_recalled"] = (
                    item.get("times_recalled", 0)
                    + 1
                )
                results.append(item)

        if results:
            self.save_all()

        return results

    def add_curiosity(
        self,
        question,
        topic,
        priority="low",
        status="open"
    ):

        question = question.strip()
        topic = topic.strip()

        curiosities = self.knowledge.setdefault(
            "curiosities",
            []
        )

        normalised_topic = self._normalise_text(
            topic
        )

        for curiosity in curiosities:

            if (
                self._normalise_text(
                    curiosity.get("topic", "")
                )
                == normalised_topic
                and curiosity.get("status")
                not in ["closed", "answered"]
            ):
                return curiosity

        curiosity = {
            "id": self._next_curiosity_id(),
            "question": question,
            "topic": topic,
            "priority": priority,
            "status": status,
            "created_at": self.current_timestamp(),
            "updated_at": self.current_timestamp()
        }

        curiosities.append(curiosity)
        self.save_all()

        return curiosity

    def get_open_curiosities(self):

        valid_statuses = [
            "open",
            "waiting"
        ]

        return [
            curiosity
            for curiosity in self.knowledge.get(
                "curiosities",
                []
            )
            if curiosity.get("status")
            in valid_statuses
        ]

    def update_curiosity_status(
        self,
        curiosity_id,
        status
    ):

        for curiosity in self.knowledge.get(
            "curiosities",
            []
        ):

            if curiosity.get("id") == curiosity_id:

                curiosity["status"] = status
                curiosity["updated_at"] = (
                    self.current_timestamp()
                )

                self.save_all()
                return True

        return False

    def _normalise_text(self, text):

        return " ".join(
            str(text).lower().strip().split()
        )

    # -------------------------------------------------
    # Forget memories
    # -------------------------------------------------

    def forget(self, category, key=""):

        category = category.strip().lower()
        key = key.strip().lower()

        if category == "name":

            if self.profile.get("name", ""):
                self.profile["name"] = ""
                self.save_all()
                return True

            return False

        if category in ["age", "birthday", "gender", "school"]:

            personal = self.profile["personal"]

            if personal.get(category, ""):
                personal[category] = ""
                self.save_all()
                return True

            return False

        if category == "favourite":

            favourites = self.profile["preferences"]["favourites"]

            for saved_key in list(favourites.keys()):

                if saved_key.lower() == key:
                    del favourites[saved_key]
                    self.save_all()
                    return True

            return False

        if category in ["like", "likes"]:

            return self._remove_from_list("likes", key)

        if category in ["dislike", "dislikes"]:

            return self._remove_from_list("dislikes", key)

        if category in ["hobby", "hobbies"]:

            return self._remove_from_list("hobbies", key)

        if category == "fact":

            facts = self.profile.get("facts", {})

            for saved_key in list(facts.keys()):

                if saved_key.lower() == key:
                    del facts[saved_key]
                    self.save_all()
                    return True

            return False

        return False

    def _remove_from_list(self, category, item):

        items = self.profile["preferences"].get(category, [])

        for saved_item in list(items):

            if saved_item.lower() == item.lower():
                items.remove(saved_item)
                self.save_all()
                return True

        return False

    # -------------------------------------------------
    # Search memories
    # -------------------------------------------------

    def search(self, query):

        query = query.lower().strip()
        results = []

        if not query:
            return results

        name = self.profile.get("name", "")

        if query in name.lower():
            results.append("Name: " + name)

        for key, value in self.profile.get("personal", {}).items():

            text = f"{key}: {value}"

            if value and query in text.lower():
                results.append(text)

        preferences = self.profile.get("preferences", {})

        for category in ["likes", "dislikes", "hobbies"]:

            for item in preferences.get(category, []):

                text = f"{category}: {item}"

                if query in text.lower():
                    results.append(text)

        for key, value in preferences.get("favourites", {}).items():

            text = f"favourite {key}: {value}"

            if query in text.lower():
                results.append(text)

        for key, value in self.profile.get("facts", {}).items():

            text = f"{key}: {value}"

            if query in text.lower():
                results.append(text)

        for event in self.profile.get("events", []):

            description = event.get("description", "")

            if query in description.lower():
                results.append("event: " + description)

        for goal in self.profile.get("goals", []):

            description = goal.get("description", "")

            if query in description.lower():
                results.append("goal: " + description)

        for project in self.profile.get("projects", []):

            name = project.get("name", "")

            if query in name.lower():
                results.append("project: " + name)

        return results