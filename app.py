import os
from random import shuffle

from flask import Flask, render_template, request, url_for
from twilio.rest import Client


# Setup Twilio credentials and REST API client
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Setup Flask app
DEBUG = False
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_assignments', methods=['POST'])
def create_assignments():

    form_data = request.form.to_dict()
    names = []
    phone_numbers = []

    # Separate the name info from the phone number info in the response
    for key, value in form_data.items():
        if 'name' in key:
            names.append((key, value))
        if 'phone' in key:
            phone_numbers.append((key, value))

    # Sort each list so each index in each list represents the same participant
    names.sort()
    phone_numbers.sort()

    # Use a global variable so it's available to helper functions
    global mapped_user_info
    mapped_user_info = {}

    # Map each name to a phone number
    for i in range(len(phone_numbers)):
        phone_number = phone_numbers[i][1]
        name = names[i][1]
        mapped_user_info[phone_number] = name

    # This is the matching logic. Shuffle the order of the phone numbers.
    # The person in the 0th index gets a gift for the person in the 1st index and so on.
    # The person in the -1st index gets a gift for the person in the 0th index.
    shuffle(phone_numbers)
    assignments = {}
    for i in range(len(phone_numbers)):
        if i == len(phone_numbers) - 1:
            assignments[phone_numbers[i][1]] = phone_numbers[0][1]
        else:
            assignments[phone_numbers[i][1]] = phone_numbers[i+1][1]

    send_assignments(assignments)
    return "Matching complete. Check your CLI for details."


def send_assignments(assignments):

    successful_notification_counter = 0
    for gift_sender, gift_recipient in assignments.items():
        body = "{}, you are {}'s Secret Santa this year. Remember to get them a gift!".format(
            mapped_user_info[gift_sender],
            mapped_user_info[gift_recipient]
        )

        try:
            message = client.messages.create(
                 body=body,
                 from_=+12345678901,  # CHANGE THIS to your own Twilio number
                 to=gift_sender
             )
            print("Secret Santa assignment sent to {} via SMS".format(mapped_user_info[gift_sender]))
            successful_notification_counter += 1

        except Exception as e:
            print(e)
            print("There may have been a problem sending the notification to {}".format(mapped_user_info[gift_sender]))
            continue

    print("Notifications sent to {} people".format(successful_notification_counter))
    return
