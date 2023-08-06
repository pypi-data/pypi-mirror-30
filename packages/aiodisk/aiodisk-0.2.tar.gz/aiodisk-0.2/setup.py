import re
from setuptools import setup

version = re.search(
    '^__version__\s*=\s*"(.*)"',
    open('aiodisk/aiodisk.py').read(),
    re.M
    ).group(1)

setup(
    name='aiodisk',
    packages=['aiodisk'],  # this must be the same as the name above
    version=version,
    description='Access all cloud services in one script',
    author='Oguz BAKIR',
    author_email='worms298@gmail.com',
    url='https://github.com/oguzbakir/AioDisk',  # use the URL to the github repo
    download_url='https://github.com/oguzbakir/aiodisk/archive/0.1.tar.gz',
    keywords=['drive', 'mega', 'cloud', 'cloudaio'],  # arbitrary keywords
    classifiers=['Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3.6'],
    entry_points = {
        "console_scripts": ['aiodisk = aiodisk.aiodisk:main']
        },
    install_requires=[
        'google-api-python-client',
    ],
)
