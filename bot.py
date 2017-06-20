from os import environ
from slackclient import SlackClient
import time

# constants
AT_BOT = ''
CHANNELS = {}
EXAMPLE_COMMAND = 'do'
BOT_NAME = 'meetbot'

def make_channel_dict (channels_list):
    channel_tuples = map(lambda (channel): (channel['id'], channel['name']), channels_list)
    for channel_id, channel_name in channel_tuples:
        CHANNELS[channel_id] = channel_name


def handle_command(command, channel):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    response = "Not sure what you mean. Use the *" + EXAMPLE_COMMAND + \
               "* command with numbers, delimited by spaces."
    if command.startswith(EXAMPLE_COMMAND):
        response = "Sure...write some more code then I can do that!"
    print response
    slack_client.api_call('chat.postMessage', channel='#' + channel,
                          text=response, as_user=True)


def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                print output
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel']
    return None, None


slack_client = SlackClient(environ.get('SLACK_BOT_TOKEN'))
if slack_client.rtm_connect():
    print('Meetbot connected and running!')
    users_call = slack_client.api_call('users.list')
    if users_call.get('ok'):
        # retrieve all users so we can find our bot
        users = users_call.get('members')
        for user in users:
            if 'name' in user and user.get('name') == BOT_NAME:
                AT_BOT =  '<@' + user.get('id') + '>'
        if AT_BOT == '':
            raise Exception
    channel_call = slack_client.api_call('channels.list')
    if channel_call.get('ok'):
        channels = channel_call.get('channels')
        make_channel_dict(channels)

    while True:
        command, channel_id = parse_slack_output(slack_client.rtm_read())
        if command and channel_id:
            handle_command(command, CHANNELS[channel_id])
        time.sleep(0.5)
else:
    print('Connection failed. Invalid Slack token or bot ID?')
