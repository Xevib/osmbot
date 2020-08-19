from setuptools import setup, find_packages

setup(
    name='osmbot',
    version='2.8.19',
    packages=find_packages(),
    url='http://git.gisce.net/gis/webgis',
    license='MIT',
    author='OSM català (Comunitat catalana de l\'OpenStreetMap)',
    author_email='xbarnada@gmail.com',
    description='OpenStreetMap Telegram bot',
    entry_points='''
        [console_scripts]
        osmbot=osmbot.cli:osmbotgroup
    ''',
    install_requires=[
        "pynominatim",
        "requests",
        "configobj",
        "raven",
        "flask",
        "psycopg2",
        "overpass",
        "lxml",
        "osmapi",
        "python-telegram-bot",
        "blinker",
        "click"
    ]
)
