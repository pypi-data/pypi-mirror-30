import collections

from flask import request


class SlackWebHook:
    """Build a slack-webhook for a flask application

    :param app An flask application
    :param endpoint Name for a endpoint
    """
    def __init__(self, app, endpoint='/slack-webhook'):
        app.add_url_rule(rule=endpoint, endpoint=endpoint,
                         view_func=self._receive_text, methods=['POST'])

        self._webhooks = collections.defaultdict(list)
        self._webhook_types = ['out-going-hook']

    def hook(self, hook_type='out-going-hook'):
        """Register an functions as hook

        :param hook_type A name of a hook
        """
        def wrapper(func):
            self._webhooks[hook_type].append(func)
            return func
        return wrapper

    def _receive_text(self):
        """Callback from a Flask application"""
        data = request.form.get('text', '')
        for type_ in self._webhook_types:
            if type_ in self._webhooks.keys():
                for hook in self._webhooks.get(type_):
                    return hook(data)
            else:
                raise ValueError('Hook type {} not allowed'.format(type_))
