from distutils.core import setup

setup(
    name="metro_distribution_engine",
    version="0.1.9",
    url="https://metro.exchange",
    description="The distribution engine for moving metrics around the Metro network",
    author="Metro",
    author_email="admin@metro.exchange",
    packages=['metro_distribution_engine', 'metro_distribution_engine/sqs_engine']
)
