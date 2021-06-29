.. _plugin-AutoRegister:

Documentation for the AutoRegister plugin for Supybot
=====================================================

Purpose
-------
The main purpose of this plugin is to automatically create accounts on the bot based on network services accounts.
Grants them #channel,op capability when they are doing some operator actions before ChanTracker is called.
Also provides a few utilities to register accounts and manage op capabilities.

Usage
-----
Auto register or identify users

.. _commands-AutoRegister:

Commands
--------
.. _command-autoregister-fregister:

fregister <accountname> <hostmask> [<channel>,[<channel>]]
  create an <account> for <hostmask> and grant <channel>,op capability if not already exists, <account> must match services account

.. _command-autoregister-grant:

grant <account> <channel>,[<channel>]
  grant <account> <channel>,op capability

.. _command-autoregister-hello:

hello takes no arguments
  auto identify you based on your services account

.. _command-autoregister-revoke:

revoke <account> <channel>,[<channel>]
  revoke <account> <channel>,op capability

.. _conf-AutoRegister:

Configuration
-------------

.. _conf-supybot.plugins.AutoRegister.logChannel:


supybot.plugins.AutoRegister.logChannel
  This config variable defaults to "", is not network-specific, and is not channel-specific.

  log account creations

.. _conf-supybot.plugins.AutoRegister.public:


supybot.plugins.AutoRegister.public
  This config variable defaults to "True", is not network-specific, and is not channel-specific.

  Determines whether this plugin is publicly visible.

