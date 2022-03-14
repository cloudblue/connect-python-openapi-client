from locust import events

from connect.client.contrib.locust.user import ConnectHttpUser  # noqa


@events.init_command_line_parser.add_listener
def _(parser):
    parser.add_argument('--connect-api-key', default='', help='Connect Api Key')
