# Flask-PubSubDecorator

Decorates publisher functions and subscriber routes creating topics/subscriptions if necessary.

## Installation

Add this line to your application's requirements.txt

```python
Flask-PubSubDecorator
```

And then execute:

    $ pip install -r requirements.txt

Or install it yourself as:

    $ pip install Flask-PubSubDecorator

## Usage

Using PubSubDecorator is dead simple. First set your GOOGLE_APPLICATION_CREDENTIALS environment variable to point at a valid JSON creds file.

    $ export GOOGLE_APPLICATION_CREDENTIALS=/path/to/creds.json

The following snippet should get you coding
```python
from flask import Flask, request
from PubSubDecorator import PubSubDecorator
import base64
import json

app = Flask(__name__)
app.pubsub = PubSubDecorator(app)


# publisher decorator will inject publisher client and topic path
@app.pubsub.publisher(topic='user_confirmed')
def user_confirmed(publisher, topic, user):
    publisher.publish(topic, data=base64.b64encode(json.dumps({
        'user_id': user.id
    })))


@app.pubsub.subscriber(
    subscription='process_user_confirmation',
    topic='user_confirmed',
    route='/_ah/push-handlers/process_user_confirmation',
    methods=['POST']
)
def process_user_confirmation(*args, **kwargs):
    subscription = kwargs.get('__subscription__')
    try:
        envelope = json.loads(request.data.decode('utf-8'))
        data = json.loads(base64.b64decode(envelope['message']['data']).decode())
        _logger.info('User Confirmed: {0}'.format(envelope))
        try:
            user_id = data.get('user_id')
            # do some async work here!
        except Exception:
            _logger.exception(
                'An unexpected error occurred processing subscription "{0}": {1}'.format(
                    subscription, request.data
                )
            )
            # Unexpected failure, do not ack message
            return '', 422
    except ValueError:
        _logger.exception(
            'Failed to parse subscription "{0}" Envelope: {1}'.format(subscription, request.data)
        )

    return '', 200
```

# Testing

    $ pytest -s tests.py
