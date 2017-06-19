from os import environ
from slackclient import SlackClient
import time

# starterbot's ID
BOT_ID = ''

# constants
AT_BOT = '<@' + BOT_ID + '>'
EXAMPLE_COMMAND = 'do'
BOT_NAME = 'meetbot'

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
    slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)


def parse_slack_output(slack_rtm_output):
    print slack_rtm_output
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'], output['channel']
    return None, None


slack_client = SlackClient(environ.get('SLACK_BOT_TOKEN'))
if slack_client.rtm_connect():
    print('Meetbot connected and running!')
    api_call = slack_client.api_call('users.list')
    if api_call.get('ok'):
        # retrieve all users so we can find our bot
        users = api_call.get('members')
        for user in users:
            if 'name' in user and user.get('name') == BOT_NAME:
                BOT_ID =  user.get('id')
    while True:
        command, channel = parse_slack_output(slack_client.rtm_read())
        if command and channel:
            print (command)
            print (channel)
            handle_command(command, channel)
        time.sleep(0.5)
else:
    print('Connection failed. Invalid Slack token or bot ID?')
