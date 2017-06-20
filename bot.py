import tasks.post_deploy

from os import environ
from slackclient import SlackClient
import time

# constants
AT_BOT = ''
CHANNELS = {}
CREATE_COMMAND = 'create'
BOT_NAME = 'meetbot'

# global variables
events = []

def get_id_and_name(channel):
    return channel['id'], channel['name']

def make_channel_dict(channels_list):
    return dict(map(get_id_and_name, channels_list))

def fetch_channels(client):
    response = client.api_call('channels.list')
    if response.get('ok'):
        return make_channel_dict(response.get('channels'))
    else:
        print('Error: no channels found')
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

def handle_command(command, channel):
    response = "Not sure what you mean. Use the *" + CREATE_COMMAND + \
               "* command followed by a short description of the event."
    if command.startswith(CREATE_COMMAND):
        events.append(trim_response(command, CREATE_COMMAND))
        response = 'Event created: _' + events[-1] + '_'
    slack_client.api_call('chat.postMessage', channel='#' + channel,
                          text=response, as_user=True)

def parse_slack_output(slack_rtm_output):
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                return trim_response(output['text'], AT_BOT).lower(), output['channel']
    return None, None

slack_client = SlackClient(environ.get('SLACK_BOT_TOKEN'))
if slack_client.rtm_connect():
    print('Meetbot connected and running!')
    CHANNELS = fetch_channels(slack_client)
    AT_BOT = fetch_bot_id(slack_client)

    while True:
        command, channel_id = parse_slack_output(slack_client.rtm_read())
        if command and channel_id:
            handle_command(command, CHANNELS[channel_id])
        time.sleep(0.5)
else:
    print('Connection failed. Invalid Slack token or bot ID?')
