import pickle

import requests

from . import __version__
from .base import CleverbotBase, ConversationBase
from .errors import APIError, DecodeError, Timeout


class SayMixin:

    def say(self, input=None, **kwargs):
        """Talk to Cleverbot.

        Arguments:
            input: The input argument is what you want to say to Cleverbot,
                such as "hello".
            **kwargs: Keyword arguments to update the request parameters with.

        Returns:
            Cleverbot's reply.

        Raises:
            APIError: A Cleverbot API error occurred.
            DecodeError: An error occurred while reading the reply.
            Timeout: The request timed out.
        """
        params = {
            'key': self.key,
            'input': input,
            'cs': self.data.get('cs'),
            'wrapper': 'cleverbot.py'
        }
        if kwargs:
            params.update(kwargs)

        headers = {
            'User-Agent': 'cleverbot.py/' + __version__ + ' '
            '(+https://github.com/orlnub123/cleverbot.py)'
        }
        try:
            reply = self.session.get(
                self.url, params=params, headers=headers, timeout=self.timeout)
        except requests.Timeout:
            raise Timeout(self.timeout)
        else:
            try:
                data = reply.json()
            except ValueError as error:
                raise DecodeError(error)
            else:
                if reply.status_code == 200:
                    self.data = data
                    return data.get('output')
                else:
                    raise APIError(data.get('error'), data.get('status'))


class Cleverbot(SayMixin, CleverbotBase):
    """A Cleverbot API wrapper."""

    def __init__(self, *args, **kwargs):
        """Initialize Cleverbot with the given arguments.

        Arguments:
            key: The key argument is always required. It is your API key.
            cs: The cs argument stands for "cleverbot state". It is the encoded
                state of the conversation so far and includes the whole
                conversation history up to that point.
            timeout: How many seconds to wait for the API to respond before
                giving up and raising an error.
        """
        super(Cleverbot, self).__init__(*args, **kwargs)
        self.session = requests.Session()

    def conversation(self, name=None, **kwargs):
        """Make a new conversation.

        Arguments:
            name: The key for the dictionary the conversation will be stored as
                in conversations. If None the conversation will be stored as a
                list instead. Mixing both types results in an error.
            **kwargs: Keyword arguments to pass into the new conversation.
                These accept the same arguments as Cleverbot.

        Returns:
            The new conversation.
        """
        convo = Conversation(self, **kwargs)
        super(Cleverbot, self).conversation(name, convo)
        return convo

    def close(self):
        """Close Cleverbot's connection to the API."""
        self.session.close()


class Conversation(SayMixin, ConversationBase):
    pass


def load(file):
    """Load and return the previously saved Cleverbot with its conversations.

    Arguments:
        file: The file object to load Cleverbot and its conversations from.

    Returns:
        A new Cleverbot instance.
    """
    cleverbot_kwargs, convos = pickle.load(file)
    cleverbot = Cleverbot(**cleverbot_kwargs)
    for convo_kwargs in convos:
        cleverbot.conversation(**convo_kwargs)
    return cleverbot
