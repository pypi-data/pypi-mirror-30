from setuptools import setup, find_packages

__version__ = '0.0.8'

setup(
    name='Flask-PubSubDecorator',
    version=__version__,
    description='Decorates publisher functions and subscriber routes creating topics/subscriptions if necessary',
    url='https://github.com/MobiusWorksLLC/Flask-PubSubDecorator.git',
    author='Tyson Holub',
    author_email='tholub@mobiusworks.com',
    license='MIT',
    packages=find_packages(exclude=['tests', 'tests.*']),
    install_requires=[
        'clint',
        'requests',
        'google-cloud-pubsub',
        'Flask'
    ]
)
