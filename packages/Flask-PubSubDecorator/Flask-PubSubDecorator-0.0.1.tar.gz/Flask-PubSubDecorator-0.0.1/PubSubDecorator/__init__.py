import os
from clint.textui import colored
from flask import Flask, Blueprint
from google.cloud import pubsub_v1
from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession
from requests.exceptions import HTTPError

_publisher = pubsub_v1.PublisherClient()
_subscriber = pubsub_v1.SubscriberClient()


class PubSubDecorator(object):

    def __init__(self, app, blueprint=None):
        if not isinstance(app, Flask):
            raise ValueError('PubSubDecorator must be initialized with a Flask app')
        if blueprint and not isinstance(blueprint, Blueprint):
            raise ValueError('PubSubDecorator blueprint param must be Flask Blueprint')

        scopes = [
            'https://www.googleapis.com/auth/pubsub'
        ]

        self.app = app
        self.blueprint = blueprint
        self.pub_client = _publisher
        self.sub_client = _subscriber
        self.creds = service_account.Credentials.from_service_account_file(
            os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'), scopes=scopes
        )

    def _get_authed_session(self):
        return AuthorizedSession(self.creds)

    def publisher(self, topic):
        if not topic:
            raise ValueError('You must specify a topic when using publisher decorator')

        topic = self.pub_client.topic_path(self.creds.project_id, topic)
        authed_session = self._get_authed_session()

        try:
            r = authed_session.get('https://pubsub.googleapis.com/v1/' + topic)
            r.raise_for_status()
        except HTTPError:
            print colored.yellow('Decorating Topic: {0}'.format(topic))
            r = authed_session.put('https://pubsub.googleapis.com/v1/' + topic)
            r.raise_for_status()

        def decorator(f):
            def wrap_f(*args, **kwargs):
                return f(self.pub_client, topic, *args, **kwargs)
            return wrap_f
        return decorator

    def subscriber(self, subscription, topic, route, methods):
        if not subscription:
            raise ValueError('You must specify a subscription when using subscriber decorator')
        if not topic:
            raise ValueError('You must specify a topic when using subscriber decorator')
        if not route:
            raise ValueError('You must specify a route when using subscriber decorator')
        if not methods:
            methods = ['POST']

        # stupid python https://www.python.org/dev/peps/pep-3104/
        decorator_args = (subscription, topic, route, methods)

        def decorator(f):
            subscription, topic, route, methods = decorator_args
            self.publisher(topic)
            subscription = self.sub_client.subscription_path(self.creds.project_id, subscription)
            topic = self.sub_client.topic_path(self.creds.project_id, topic)
            authed_session = self._get_authed_session()

            if self.blueprint:
                route = self.blueprint.url_prefix + route

            try:
                r = authed_session.get('https://pubsub.googleapis.com/v1/' + subscription)
                r.raise_for_status()
            except HTTPError:
                print colored.yellow('Decorating Subscription: {0}'.format(subscription))
                r = authed_session.put('https://pubsub.googleapis.com/v1/' + subscription, json={
                    'ackDeadlineSeconds': 600,
                    'pushConfig': {
                        'pushEndpoint': 'https://{0}.appspot.com{1}'.format(self.creds.project_id, route)
                    },
                    'topic': topic
                })
                r.raise_for_status()

            push_endpoint = r.json().get('pushConfig', {}).get('pushEndpoint')

            if self.blueprint:
                endpoint = '{0}.{1}'.format(self.blueprint.name, f.func_name)
            else:
                endpoint = f.func_name

            def wrap_f(*args, **kwargs):
                kwargs.update({
                    '__publisher__': self.pub_client,
                    '__topic__': topic,
                    '__subscriber__': self.sub_client,
                    '__subscription__': subscription,
                    '__push_endpoint__': push_endpoint
                })
                return f(*args, **kwargs)
            self.app.route(route, endpoint=endpoint, methods=methods)(wrap_f)
            return wrap_f
        return decorator
