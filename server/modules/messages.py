from server.modules import (accounts, groups)
import pickle
import time


"""
Manages and stores messages between users and in groups.
"""
class MessageManager:
    def __init__(self):
        self.callbacks = {}
        try:
            with open('messages.pickle', 'rb') as f:
                self.messages = pickle.load(f)
        except FileNotFoundError:
            self.messages = []

    """
    Gets all messages between two users.
    """
    def get_all_with_users(self, username1, username2):
        messages = []
        for message in self.messages:
            if message["sender"] == username1 and message["receiver"]["type"] == "user" and message["receiver"]["username"] == username2:
                messages.append(message)
            elif message["sender"] == username2 and message["receiver"]["type"] == "user" and message["receiver"]["username"] == username1:
                messages.append(message)
        return messages

    """
    Gets all messages in a group.
    """
    def get_all_in_group(self, group):
        groups.manager.validate_group(group)

        messages = []
        for message in self.messages:
            if message["receiver"]["type"] == "group" and message["receiver"]["id"] == group:
                messages.append(message)
        return messages

    """
    Sends a message.
    """
    def send(self, sender, receiver_type, text, username=None, group=None):
        message = {
            "id": len(self.messages),
            "sender": sender,
            "receiver": {
                "type": receiver_type
            },
            "timestamp": time.time(),
            "text": text
        }

        if receiver_type == "user":
            accounts.manager.validate_user(username)
            message["receiver"]["username"] = username
        elif receiver_type == "group":
            groups.manager.validate_group(group)
            message["receiver"]["id"] = group
        else:
            raise Exception("Invalid recipient type")

        self.messages.append(message)

        # If a callback was set to send a message immediately, invoke it now.
        if receiver_type == "user":
            self.call_callback(sender, message)
            self.call_callback(username, message)
        elif receiver_type == "group":
            for user in groups.manager.get_group(group)["users"]:
                self.call_callback(user, message)

        self.save()

    """
    Sets a callback to be invoked when a given user gets a message.
    """
    def set_callback(self, username, callback):
        self.callbacks[username] = callback

    """
    Removes a callback.
    """
    def remove_callback(self, username):
        del self.callbacks[username]

    """
    Invokes a message callback.
    """
    def call_callback(self, username, message):
        try:
            if username in self.callbacks:
                return self.callbacks[username](message)
        except:
            pass

    """
    Saves the message database.
    """
    def save(self):
        with open('messages.pickle', 'wb') as f:
            pickle.dump(self.messages, f)


manager = MessageManager()
