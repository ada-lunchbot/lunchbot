from os import environ
from slackclient import SlackClient

sc = SlackClient(environ['SLACK_BOT_TOKEN'])
sc.rtm_connect()
sc.rtm_send_message('general', 'A new version of @meetbot has been deployed!')
