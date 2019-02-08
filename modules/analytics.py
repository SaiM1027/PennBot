#from .base import Module
import requests
import re
import sys
from pprint import pprint
import os

at = os.environ["GROUPME_ACCESS_TOKEN"]
GROUP_ID = 46649296

class Analytics:
    users = []
    def __init__(self):
        group = self.get_group(GROUP_ID)
        self.prepare_analysis_of_group(group)

        # Display info to user before the analysis begins
        message_count = group['messages']['count']
        print("Analyzing " + str(message_count) + " messages.")

        # Make dictionary of members
        self.populate_users(group['members'])

        # Perform analysis
        self.users = self.analyze_group(GROUP_ID, user_dictionary, message_count)

        #this line displays the data to the user
        self.display_data(self.users)

    def get_group_data(self, group_id):
        response = requests.get('https://api.groupme.com/v3/groups?token=' + at)
        data = response.json()
        return data['response']

    def new_user(self, name):
        return {"name": name, "messages": 0, "likes": 0, "likes_received": 0.0}

    def populate_users(self, members):
        for member in members:
            self.users[member['user_id']] = self.new_user(member['name'])

    def analyze_group(self, GROUP_ID, self.users, message_count):
        response = requests.get('https://api.groupme.com/v3/groups/' + GROUP_ID + '/messages?token=' + at)
        messages = response.json()['response']['messages']
        message_id = 0
        message_number = 0
        while message_number < message_count:
            for message in messages:  # API sends 20 messages at once
                message_number += 1
                name = message['name']
                message = message['text']

                sender_id = message['sender_id']
                likers = message['favorited_by']

                if sender_id not in self.users.keys():
                    self.users[sender_id] = self.new_user(name)

                # Fill the name in if user liked a message but hasn't yet been added to the dictionary
                if self.users[sender_id]['name'] == '':
                    self.users[sender_id]['name'] = name

                for liker_id in likers:
                    if liker_id not in self.users.keys():
                        # Leave name blank until user sends their first message
                        self.users[user_id] = self.new_user('')
                    self.users[liker_id]["likes"] += 1

                self.users[sender_id]["messages"] += 1  # add one to sent message count
                self.users[sender_id]["likes_received"] += len(likers)

            message_id = messages[-1]['id']  # Get last message's ID for next request
            remaining = 100 *  message_number / message_count
            print(str(remaining)+'% done')

            payload = {'before_id': message_id}
            response = requests.get('https://api.groupme.com/v3/groups/'+GROUP_ID+'/messages?token='+at, params=payload)
            data = response.json()

    def display_data(self):
        for key in self.users:
            print(self.users[key]['name'])
            print('Messages Sent: ' + str(self.users[key]["messages"]))
            print('Likes Given: ' + str(self.users[key]["likes"]))
            print('Likes Received: ' + str(self.users[key]["likes_received"]))

if __name__ == "__main__":
    print(Analytics().response(""))