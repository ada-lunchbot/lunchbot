from os import environ
from slackclient import SlackClient
import time

# CONSTANTS
AT_BOT = ''
CHANNELS = {}
USERS = {}
BOT_NAME = 'meetbot'
NEWLINE = '\n'

# COMMANDS
CREATE_COMMAND = 'create'
SEE_COMMAND = 'what\'s up'
JOIN_COMMAND = 'join'


# global variables
event_list = [
    {'name': 'drinks @ styx', 'attendees': []},
    {'name': 'refactoring some of our code', 'attendees': []},
    {'name': 'jam session @ Google', 'attendees': []}
    ]

slack_client = SlackClient(environ.get('SLACK_BOT_TOKEN'))

def get_id_and_name(entity):
    return entity['id'], entity['name']

def make_dict(entity_list):
    return dict(map(get_id_and_name, entity_list))

def fetch(client, path, key):
    response = client.api_call(path)
    if response.get('ok'):
        return make_dict(response.get(key))
    else:
        print('Error fetching from api')
        return {}

def fetch_bot_id(client):
    response = slack_client.api_call('users.list')
    if response.get('ok'):
        # retrieve all users so we can find our bot
        users = response.get('members')
        for user in users:
            if 'name' in user and user.get('name') == BOT_NAME:
                return '<@' + user.get('id') + '>'

def trim_response(response, delimiter):
    return response.split(delimiter)[1].strip()

def format_event((i, e)):
    return '  [' + str(i) + '] _' + e['name'] + '_'

def print_event_list(events):
    return NEWLINE.join(map(format_event, enumerate(events, start = 1)))

def handle_command(command, channel, user):
    response = "Not sure what you mean. Use the *" + CREATE_COMMAND + \
               "* command followed by a short description of the event."
    if command.startswith(CREATE_COMMAND):
        new_event = {'name': trim_response(command, CREATE_COMMAND), 'attendees': []}
        event_list.append(new_event)
        response = 'Event created: _' + new_event['name'] + '_'
    elif command.startswith(SEE_COMMAND):
        response = 'Sure, here\'s what\'s going on:\n' + print_event_list(event_list)
    elif command.startswith(JOIN_COMMAND):
        event = event_list[int(trim_response(command, JOIN_COMMAND)) - 1]
        event['attendees'].append(user)
        response = 'You\'ve joined the event: _' + event['name'] + '_'
    slack_client.api_call('chat.postMessage', channel='#' + channel,
                          text=response, as_user=True)

def parse_slack_output(slack_rtm_output):
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                return trim_response(output['text'], AT_BOT).lower(), output['channel'], output['user']
    return None, None, None

# Main
def main():
    if slack_client.rtm_connect():
        print('Meetbot connected and running!')
        global CHANNELS
        CHANNELS = fetch(slack_client, 'channels.list', 'channels')
        global AT_BOT
        AT_BOT = fetch_bot_id(slack_client)
        global USERS
        USERS = fetch(slack_client, 'users.list', 'members')

        while True:
            command, channel_id, user = parse_slack_output(slack_client.rtm_read())
            if command and channel_id and user:
                handle_command(command, CHANNELS[channel_id], user)
            time.sleep(0.5)
    else:
        print('Connection failed. Invalid Slack token or bot ID?')

main()
