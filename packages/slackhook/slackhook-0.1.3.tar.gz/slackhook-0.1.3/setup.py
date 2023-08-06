from setuptools import setup

import slackhook

author = slackhook.__author__
version = slackhook.__version__
email = slackhook.__email__

setup_information = {
    'name': 'slackhook',
    'author': author,
    'version': version,
    'url': 'https://github.com/MichaelYusko/slackhook',
    'author_email': email,
    'install_requires': ['flask==0.12.2'],
    'description': 'Simple, Slack webhook integration for Flask application ',
    'packages': ['slackhook'],
    'classifiers': [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: MIT License'
    ]
}

setup(**setup_information)

print(u"\n\n\t\t    "
      "Slackhook version {} installation succeeded.\n".format(version))
