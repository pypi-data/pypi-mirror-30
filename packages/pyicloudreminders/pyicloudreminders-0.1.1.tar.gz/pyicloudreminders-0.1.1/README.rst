.. image:: https://travis-ci.org/coumbole/pyicloudreminders.svg?branch=master
   :alt: Check out our test status at https://travis-ci.org/coumbole/pyicloudreminders
   :target: https://travis-ci.org/coumbole/pyicloudreminders

=========
Attention
=========

This is a fork of `PyiCloud <https://github.com/picklepete/pyicloud>`_, but stripped down to only provide the
Reminders webservice. However, the reminder support is more complete, offering access to more fields. The rest
of the README is from the original upstream repo and provides a usage guide.

This fork plans to stay up to date with the upstream repo when it comes to reminders or authentication related
things.


===============
Original README
===============

PyiCloudReminders is a module which allows pythonistas to interact with iCloud Reminders. It's powered by the fantastic `requests <https://github.com/kennethreitz/requests>`_ HTTP library.

At its core, PyiCloud connects to iCloud using your username and password, then performs calendar and iPhone queries against their API.

==============
Authentication
==============

Authentication without using a saved password is as simple as passing your username and password to the ``PyiCloudService`` class:

>>> from pyicloud import PyiCloudService
>>> api = PyiCloudService('jappleseed@apple.com', 'password')

In the event that the username/password combination is invalid, a ``PyiCloudFailedLoginException`` exception is thrown.

You can also store your password in the system keyring using the command-line tool:

>>> icloud --username=jappleseed@apple.com
ICloud Password for jappleseed@apple.com:
Save password in keyring? (y/N)

If you have stored a password in the keyring, you will not be required to provide a password when interacting with the command-line tool or instantiating the ``PyiCloudService`` class for the username you stored the password for.

>>> api = PyiCloudService('jappleseed@apple.com')

If you would like to delete a password stored in your system keyring, you can clear a stored password using the ``--delete-from-keyring`` command-line option:

>>> icloud --username=jappleseed@apple.com --delete-from-keyring

**Note**: Authentication will expire after an interval set by Apple, at which point you will have to re-authenticate. This interval is currently two months.

************************************************
Two-step and two-factor authentication (2SA/2FA)
************************************************

If you have enabled `two-step authentication (2SA) <https://support.apple.com/en-us/HT204152>`_ for the account you will have to do some extra work:

.. code-block:: python

    if api.requires_2sa:
        import click
        print "Two-step authentication required. Your trusted devices are:"

        devices = api.trusted_devices
        for i, device in enumerate(devices):
            print "  %s: %s" % (i, device.get('deviceName',
                "SMS to %s" % device.get('phoneNumber')))

        device = click.prompt('Which device would you like to use?', default=0)
        device = devices[device]
        if not api.send_verification_code(device):
            print "Failed to send verification code"
            sys.exit(1)

        code = click.prompt('Please enter validation code')
        if not api.validate_verification_code(device, code):
            print "Failed to verify verification code"
            sys.exit(1)

This approach also works if the account is set up for `two-factor authentication (2FA) <https://support.apple.com/en-us/HT204915>`_, but the authentication will time out after a few hours. Full support for two-factor authentication (2FA) is not implemented in PyiCloud yet. See issue `#102 <https://github.com/picklepete/pyicloud/issues/102>`_.
