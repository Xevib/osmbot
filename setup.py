from setuptools import setup, find_packages

setup(
    name='osmbot',
    version='2.0.0',
    packages=find_packages(),
    url='https://github.com/Xevib/osmbot',
    license='MIT',
    author='OSM català (Comunitat catalana de l\'OpenStreetMap)',
    author_email='xbarnada@gmail.com',
    description='OpenStreetMap Telegram bot',
    python_requires='>=3.10',
    entry_points='''
        [console_scripts]
        osmbot=osmbot.cli:osmbotgroup
    ''',
    install_requires=[
        "pynominatim",
        "requests",
        "configobj",
        "sentry-sdk[flask]",
        "flask",
        "psycopg2-binary",
        "overpass",
        "lxml",
        "osmapi",
        "python-telegram-bot>=13.0,<14.0",
        "blinker",
        "click",
        "pony",
        "jinja2"
    ]
)
