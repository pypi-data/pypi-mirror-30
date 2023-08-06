"""
Lighweight Python interface for Varnish Manager

Tested against
    Varnish v4.x.x

Supports the following commands

help [command]
ping [timestamp]
auth response
quit
status
start
stop
vcl.load <configname> <filename>
vcl.inline <configname> <quoted_VCLstring>
vcl.use <configname>
vcl.discard <configname>
vcl.list
vcl.show <configname>
param.show [-l] [<param>]
param.set <param> <value>
ban.url <regexp>
ban <field> <operator> <arg> [&& <field> <oper> <arg>]...
ban.list

"""

from telnetlib import Telnet
from hashlib import sha256
import logging


class VarnishManager(Telnet):
    def __init__(self, host, port=6082, secret=None, **kwargs):
        Telnet.__init__(self, host=host, port=port)
        (status, length), content = self._read()

        if status == 107 and secret is not None:
            self.auth(secret, content)

        elif status != 200:
            logging.error('Connecting failed with status: %i' % status)

    def _read(self):
        (status, length), content = map(int, self.read_until('\n').split()), ''
        while len(content) < length:
            content += self.read_some()

        return (status, length), content[:-1]

    def command(self, cmd):
        """
        Run a command on the Varnish backend and return the result
        return value is a tuple of ((status, length), content)
        """
        logging.debug('SENT: {}: {}'.format(self.host, cmd))

        self.write('{}\n'.format(cmd))

        while 1:
            buffer = self.read_until('\n').strip()
            if len(buffer):
                break
        status, length = map(int, buffer.split())
        content = ''

        assert status == 200, 'Bad response code: {status} {text} ({command})'.format(
            status=status, text=self.read_until('\n').strip(), command=cmd)

        while len(content) < length:
            content += self.read_until('\n')

        logging.debug('RECV: {}: {}B {}'.format(status, length, content[:30]))

        self.read_eager()

        return (status, length), content

    # Service control methods
    def start(self):
        """start  Start the Varnish cache process if it is not already running."""
        return self.command('start')

    def stop(self):
        """stop   Stop the Varnish cache process."""
        return self.command('stop')

    def quit(self):
        """quit   Close the connection to the varnish admin port."""
        return self.close()

    def auth(self, secret, content):
        challenge = content[:32]
        response = sha256('{}\n{}\n{}\n'.format(challenge, secret, challenge))
        response_str = 'auth %s' % response.hexdigest()

        self.command(response_str)

    # Information methods
    def ping(self, timestamp=None):
        """
        ping [timestamp]
            Ping the Varnish cache process, keeping the connection alive.
        """
        cmd = 'ping {}'.format(timestamp) if timestamp else 'ping'

        return tuple(map(float, self.command(cmd)[1].split()[1:]))

    def status(self):
        """status Check the status of the Varnish cache process."""
        return self.command('status')[1]

    def help(self, command=None):
        """
        help [command]
            Display a list of available commands.
            If the command is specified, display help for this command.
        """

        cmd = 'help {}'.format(command) if command else 'help'

        return self.command(cmd)[1]

    # VCL methods
    def vcl_load(self, configname, filename):
        """
        vcl.load configname filename
            Create a new configuration named configname with the contents of the specified file.
        """
        return self.command('vcl.load {} {}'.format(configname, filename))

    def vcl_inline(self, configname, vclcontent):
        """
        vcl.inline configname vcl
            Create a new configuration named configname with the VCL code specified by vcl,
            which must be a quoted string.
        """
        return self.command('vcl.inline {} {}'.format(configname, vclcontent))

    def vcl_show(self, configname):
        """
        vcl.show configname
            Display the source code for the specified configuration.
        """
        return self.command('vcl.show {}'.format(configname))

    def vcl_use(self, configname):
        """
        vcl.use configname
            Start using the configuration specified by configname for all new requests.
            Existing requests will coninue using whichever configuration
            was in use when they arrived.
        """
        return self.command('vcl.use {}'.format(configname))

    def vcl_discard(self, configname):
        """
        vcl.discard configname
            Discard the configuration specified by configname.
            This will have no effect if the specified configuration has a non-zero reference count.
        """
        return self.command('vcl.discard {}'.format(configname))

    def vcl_list(self):
        """
        vcl.list
            List  available configurations and their respective reference counts.
            The active configuration is indicated with an asterisk ("*").
        """
        vcls = {}
        for line in self.command('vcl.list')[1].splitlines():
            a = line.split()
            vcls[a[2]] = tuple(a[:-1])
        return vcls

    # Param methods
    def param_show(self, param, flag=False):
        """
        param.show [-l] [param]
              Display a list if run-time parameters and their values.
              If the -l option is specified, the list includes a brief explanation of
              each parameter.
              If a param is specified, display only the value and explanation for this parameter.
        """

        cmd = 'param.show -l ' if flag else 'param.show '

        return self.command(cmd + param)

    def param_set(self, param, value):
        """
        param.set param value
              Set the parameter specified by param to the specified value.
              See Run-Time Parameters for a list of paramea ters.
        """
        self.command('param.set {} {}'.format(param, value))

    # Ban methods
    def ban(self, expression):
        """
        ban field operator argument [&& field operator argument [...]]
            Immediately invalidate all documents matching the ban expression.
            See Ban Expressions for more documentation and examples.
        """
        return self.command('ban {}'.format(expression))[1]

    def ban_url(self, regex):
        """
        ban.url regexp
            Immediately invalidate all documents whose URL matches the specified
            regular expression.  Please note  that the Host part of the URL is ignored,
            so if you have several virtual hosts all of them will be banned. Use ban to
            specify a complete ban if you need to narrow it down.
        """
        return self.command('ban.url {}'.format(regex))[1]

    def ban_list(self):
        """
        ban.list
            All requests for objects from the cache are matched against items on the ban list.
            If an object in the cache is older than a matching ban list item, it is  considered
            "banned",  and  will  be commanded from the backend instead.

            When a ban expression is older than all the objects in the cache, it
            is removed from the list.

            ban.list displays the ban list. The output looks something like this
            (broken into two lines):

            0x7fea4fcb0580 1303835108.618863 131G req.http.host ~ www.myhost.com && req.url ~ /some/url

            The first field is the address of the ban.

            The second is the time of entry into the list, given as a high precision timestamp.

            The  third  field  describes many objects point to this ban. When an object is
            compared to a ban the object is marked with a reference to the newest ban it was
            tested against. This isn't really useful unless you're debugging.

            A "G" marks that the ban is "Gone". Meaning it has been marked as a duplicate or
            it is no longer valid. It stays in the list for effiency reasons.

            Then follows the actual ban it self.
        """
        return self.command('ban.list')[1]
