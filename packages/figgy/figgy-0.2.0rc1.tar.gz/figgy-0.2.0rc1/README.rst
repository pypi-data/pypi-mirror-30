figgy
=====

Creates and populates configs for an app at first-time setup.

Are you sick and tired of writing packages or apps that are super great
but don’t work unless your end-user scours your README for instructions
on how to structure config files and how and where to instantiate them?

figgy allows you to ship code and have the end-user developer install
and configure it just by running your app or package. You can call it
from setup.py or bind it to whatever you like in your code so the
results of the new configuration are made immediately available to
whatever context the app or package will be used in.

--------------

Warning
-------

This software is in alpha development. That said, this package should
work. Please report bugs.

Key caveats: 
- Outputs your configuration data to the screen in some
cases.
- Only supports json.
- Only available for python 3. 
- You want this module to prompt from TTY. 
- You’re on a ’NIX system.

These are intended to guide feature development for future versions, but
in this state it should be useful nonetheless.

Installation
------------

::

    pip install figgy

Usage
-----

First import figgy

::

    import figgy

Then define your config template

::

    template = {
        'username': 'default',
        'password': 'anotherdefault'
    }

All you need to do is call ``make()``.

::

    figgy.make(template)

and the end user will be prompted with:

::

    Enter value for "username"
    (return for default "default")': ▋userinput
    Enter value for "username"
    (return for default "default")': 
    Set "username" to "userinput" in ./config.json
    Enter value for "password"
    (return for default "anotherdefault")': ▋anotheruserinput
    Enter value for "password"
    (return for default "anotherdefault")': 
    Set "password" to "anotheruserinput" in ./config.json

and generate a ``config.json`` file:

::

    {"username": "userinput", "password": "anotheruserinput"}

If you want the data to be used in the application after it’s created
use

::

    config = figgy.make(template)

so that you can access the data like so

::

    username = config['username']
    password = config['password']

By default figgy assumes a few things:

-  You want the file to be named ``config.json``
-  You want the file generated at the path the python code that executes
   it runs from
-  You want the function to return the configuration data
-  The user interface is TTY

But you can change most of that:

source code:

::

    template = {
        'PORT': '3000',
        'DEBUG': 'True'
    }
    figgy.make(data=template, filename='appconfig')

prompts:

::

    Enter value for "PORT"
    (return for default "3000")': ▋8080
    Set "PORT" to "8080" in ./appconfig.json
    Enter value for "DEBUG"
    (return for default "True")': ▋False

and returns:

::

    Set "DEBUG" to "False" in ./appconfig.json
    {'./appconfig.json': {'PORT': '3000', 'DEBUG': 'True'}}

source code:

::

    figgy.make(data=template, get=False)

generates the prompts:

::

    Enter value for "username"
    (return for default "default")': ▋userinput
    Set "username" to "userinput" in ./config.json
    Enter value for "password"
    (return for default "anotherdefault")': ▋anotheruserinput
    Set "password" to "anotheruserinput" in ./config.json

and returns:

::

    None

Contributing
------------

1. Fork the source repository https://github.com/dyspop/figgy
2. Make a new branch
3. Write the feature code
4. Make sure you add some tests
5. Submit a pull request with helpful notes about your feature and test
