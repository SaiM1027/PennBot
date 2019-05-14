from .base import Module
import requests
import re
import sys
from pprint import pprint
import os

GROUP_ID = 48071223


class Analytics(Module):
    DESCRIPTION = "View statistics on user activity in the chat"
    groups = {}

    def generate_data(self):
        self.groups[group_id] = {}
        group = self.get_group(GROUP_ID)

        # Display info to user before the analysis begins
        message_count = group["messages"]["count"]
        print("Analyzing " + str(message_count) + " messages.")

        # Make dictionary of members
        self.populate_users(group["members"])

        # Perform analysis
        self.analyze_group(GROUP_ID, message_count)
        return "%d messages processed." % message_count

    def get_group(self, group_id):
        return requests.get(f"https://api.groupme.com/v3/groups/{group_id}?token={self.ACCESS_TOKEN}").json()["response"]

    def new_user(self, name):
        return {"name": name, "messages": 0, "likes": 0, "likes_received": 0.0}

    def populate_users(self, members):
        for member in members:
            self.groups[group_id][member["user_id"]] = self.new_user(member["name"])

    def analyze_group(self, group_id, message_count):
        message_id = 0
        message_number = 0
        last_percentage = 0
        while message_number < message_count:
            params = {
                # Get maximum number of messages at a time
                "limit": 100,
            }
            if message_id:
                params["before_id"] = message_id
            response = requests.get(f"https://api.groupme.com/v3/groups/{group_id}/messages?token={self.ACCESS_TOKEN}", params=params)
            messages = response.json()["response"]["messages"]
            for message in messages:
                message_number += 1
                name = message["name"]

                sender_id = message["sender_id"]
                likers = message["favorited_by"]

                if sender_id not in self.groups[group_id].keys():
                    self.groups[group_id][sender_id] = self.new_user(name)

                # Fill the name in if user liked a message but hasn"t yet been added to the dictionary
                if not self.groups[group_id][sender_id].get("name"):
                    self.groups[group_id][sender_id]["name"] = name

                for liker_id in likers:
                    if liker_id not in self.groups[group_id].keys():
                        # Leave name blank until user sends their first message
                        self.groups[group_id][liker_id] = self.new_user("")
                    self.groups[group_id][liker_id]["likes"] += 1

                self.groups[group_id][sender_id]["messages"] += 1  # Increment sent message count
                self.groups[group_id][sender_id]["likes_received"] += len(likers)

            message_id = messages[-1]["id"]  # Get last message's ID for next request
            percentage = int(10 * message_number / message_count) * 10
            if percentage > last_percentage:
                last_percentage = percentage
                print("%d%% done" % remaining)

    def response(self, query, message):
        parameters = query.split(" ")
        command = parameters.pop(0)
        output = ""
        if command == "generate":
            return self.generate_data()
        if command == "profile":
            return "Profiling coming soon"
        elif command == "leaderboard":
            users = [self.groups[group_id][key] for key in self.groups[group_id]]
            users.sort(key=lambda user: user["messages"], reverse=True)
            try:
                length = int(parameters.pop(0))
            except Exception:
                length = 10
            leaders = users[:length]
            for place, user in enumerate(leaders):
                output += str(place + 1) + ". " + user["name"] + " / Messages Sent: %d" % user["messages"]
                output += " / Likes Given: %d" % user["likes"]
                output += " / Likes Received: %d" % user["likes_received"]
                output += "\n"
        else:
            return "No command specified!"
        return output
