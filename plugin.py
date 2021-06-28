###
# Copyright (c) 2021, Nicolas Coevoet
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
###

from supybot import ircutils, callbacks, ircdb, ircmsgs
from supybot.commands import *
try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('AutoRegister')
except ImportError:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    _ = lambda x: x


class AutoRegister(callbacks.Plugin):
    """Auto register or identify users"""
    threaded = True

    def __init__(self, irc):
        self.__parent = super(AutoRegister, self)
        self.__parent.__init__(irc)

    def hello(self, irc, msg, args):
        """takes no arguments

        auto identify you based on your services account"""
        account = None
        if 'account' not in msg.server_tags:
            irc.error(_('You are not logged in to services, '
                        'see /msg NickServ help identify or register'), Raise=True)
        account = msg.server_tags['account']
        user = None
        try:
            user = ircdb.users.getUser(msg.prefix)
        except:
            pass
        if user:
            irc.reply(_('You are already authenticated as %s.') % user.name)
            return
        user = ircdb.users.getUserFromNick(irc.network, account)
        if user:
            try:
                user.addAuth(msg.prefix)
            except ValueError:
                irc.error(_('Your secure flag is true and your hostmask '
                            'doesn\'t match any of your known hostmasks.'), Raise=True)
            ircdb.users.setUser(user, flush=False)
            irc.reply(_('You are now authenticated as %s.') % user.name)
            return
        try:
            ircdb.users.getUserId(account)
            irc.error(_('That name is already assigned to someone. '
                        'Please contact staff.'), Raise=True)
        except KeyError:
            pass

        user = ircdb.users.newUser()
        user.name = account
        user.addHostmask(msg.prefix)
        user.addNick(irc.network, account)
        ircdb.users.setUser(user)
        irc.reply(_('You are now authenticated as %s') % account)
        if self.registryValue('logChannel') in irc.state.channels:
            irc.queueMsg(ircmsgs.privmsg(self.registryValue('logChannel'),'[AR] %s created %s (hello)' % (account, msg.prefix)))
    hello = wrap(hello)

    def fregister(self, irc, msg, args, account, hostmask, channels=None):
        """<accountname> <hostmask> [<channel>,[<channel>]]

        create an <account> for <hostmask> and grant <channel>,op capability
        if not already exists, <account> must match services account"""
        user = ircdb.users.getUserFromNick(irc.network, account)
        if user:
            irc.error(_('That name is already assigned to someone. '
                        'Please contact staff.'), Raise=True)
        user = ircdb.users.newUser()
        user.name = account
        user.addHostmask(hostmask)
        user.addNick(irc.network, account)
        ircdb.users.setUser(user)
        if channels:
            for channel in channels:
                capability = '%s,op' % channel
                user.addCapability(capability)
                ircdb.users.setUser(user)
        irc.replySuccess()
        if self.registryValue('logChannel') in irc.state.channels:
            irc.queueMsg(ircmsgs.privmsg(self.registryValue('logChannel'),'[AR] %s created %s (by %s)' % (account,hostmask,msg.nick)))
    fregister = wrap(fregister, ['owner', 'nick', 'hostmask', optional('channels')])

    callBefore = ['ChanTracker']
    def doMode(self, irc, msg):
        if not ircutils.isUserHostmask(msg.prefix):
            return
        if 'account' not in msg.server_tags:
            return
        account = msg.server_tags['account']
        channel = msg.args[0]
        if not channel:
            return
        capability = '%s,op' % channel
        flag = ircdb.makeChannelCapability(channel, 'op')
        modes = ircutils.separateModes(msg.args[1:])
        for (mode, value) in modes:
            m = mode[1:]
            if m in 'bqrmz':
                user = None
                try:
                    user = ircdb.users.getUser(msg.prefix)
                except:
                    pass
                if user:
                    if not ircdb.checkCapability(msg.prefix, flag):
                        user.addCapability(capability)
                        ircdb.users.setUser(user)
                    return
                user = ircdb.users.getUserFromNick(irc.network, account)
                if user:
                    if not ircdb.checkCapability(msg.prefix, flag):
                        user.addCapability(capability)
                        ircdb.users.setUser(user)
                    return
                try:
                    user = ircdb.users.getUserId(account)
                    return
                except KeyError:
                    pass
                user = ircdb.users.newUser()
                user.name = account
                user.addHostmask(msg.prefix)
                user.addNick(irc.network, account)
                user.addCapability(capability)
                ircdb.users.setUser(user)
                if self.registryValue('logChannel') in irc.state.channels:
                    irc.queueMsg(ircmsgs.privmsg(self.registryValue('logChannel'),'[AR] %s created %s (%s)' % (account, msg.prefix, channel)))

    def _auth(self, irc, prefix, account):
        user = ircdb.users.getUserFromNick(irc.network, account)
        if not user:
            try:
                user = ircdb.users.getUser(prefix)
            except KeyError:
                pass
        if user:
            user.addAuth(prefix)
            ircdb.users.setUser(user, flush=False)

    def doAccount(self, irc, msg):
        account = msg.args[0]
        if account != '*':
            self._auth(irc, msg.prefix, account)

    def doJoin(self, irc, msg):
        if 'extended-join' not in irc.state.capabilities_ack:
            return
        account = msg.args[1]
        if account != '*':
            self._auth(irc, msg.prefix, account)

    def grant(self, irc, msg, args, user, channels):
        """<account> <channel>,[<channel>]

        grant <account> <channel>,op capability"""
        for channel in channels:
            capability = '%s,op' % channel
            user.addCapability(capability)
            ircdb.users.setUser(user)
        irc.reply('[%s]' % '; '.join(user.capabilities), private=True)
    grant = wrap(grant, ['owner', 'otherUser', 'channels'])

    def revoke(self, irc, msg, args, user, channels):
        """<account> <channel>,[<channel>]

        revoke <account> <channel>,op capability"""
        for channel in channels:
            try:
                capability = '%s,op' % channel
                user.removeCapability(capability)
                ircdb.users.setUser(user)
            except KeyError:
                pass
        irc.reply('[%s]' % '; '.join(user.capabilities), private=True)
    revoke = wrap(revoke, ['owner', 'otherUser', 'channels'])


Class = AutoRegister
