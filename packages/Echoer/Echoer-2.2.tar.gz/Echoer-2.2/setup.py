
#!/usr/bin/env python

from distutils.core import setup

setup(name='Echoer',
    version='2.2',
    description='Say things out loud',
    author='Mike Sandford',
    author_email='mike.sandford@arundo.com',
    url='https://github.com/MikeSandfordArundo/echoer.git',
    packages=['echoer'],
    install_requires=[
        'click',
        'pyttsx3==2.7',
      ],
    entry_points={
        'console_scripts': [
            'echoer=echoer.cli:say',
        ],
    },
    )
