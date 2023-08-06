"""Subclass specific to Cisco ASA"""

import re

from ..ios_like import IOSLikeDevice
from ..logger import logger


class CiscoASA(IOSLikeDevice):
    """Class for working with Cisco ASA"""

    def __init__(self, host=u'', username=u'', password=u'', secret=u'', port=22, device_type=u'', known_hosts=None,
                 local_addr=None, client_keys=None, passphrase=None, loop=None):
        """
        Initialize class for asynchronous working with network devices

        :param str host: hostname or ip address for connection
        :param str username: username for logger to device
        :param str password: password for user for logger to device
        :param str secret: secret password for privilege mode
        :param int port: ssh port for connection. Default is 22
        :param str device_type: network device type
        :param str device_type: network device type. This is subclasses of this class
        :param known_hosts: file with known hosts. Default is None (no policy). with () it will use default file
        :param str local_addr: local address for binding source of tcp connection
        :param client_keys: path for client keys. With () it will use default file in OS.
        :param str passphrase: password for encrypted client keys
        :param loop: asyncio loop object
        """
        super().__init__(host=host, username=username, password=password, secret=secret, port=port,
                         device_type=device_type, known_hosts=known_hosts, local_addr=local_addr,
                         client_keys=client_keys, passphrase=passphrase, loop=loop)

        self._multiple_mode = False

    _disable_paging_command = 'terminal pager 0'

    @property
    def multiple_mode(self):
        """ Returning Bool True if ASA in multiple mode"""
        return self._multiple_mode

    async def connect(self):
        """
        Async Connection method

        Using 5 functions:

        * _establish_connection() for connecting to device
        * _set_base_prompt() for finding and setting device prompt
        * _enable() for getting privilege exec mode
        * _disable_paging() for non interact output in commands
        *  _check_multiple_mode() for checking multiple mode in ASA
        """
        logger.info("Host {}: trying to connect to the device".format(self._host))
        await self._establish_connection()
        await self._set_base_prompt()
        await self.enable_mode()
        await self._disable_paging()
        await self._check_multiple_mode()
        logger.info("Host {}: Has connected to the device".format(self._host))

    async def _set_base_prompt(self):
        """
        Setting two important vars for ASA
            base_prompt - textual prompt in CLI (usually hostname)
            base_pattern - regexp for finding the end of command. IT's platform specific parameter

        For ASA devices base_pattern is "prompt([\/\w]+)?(\(.*?\))?[#|>]
        """
        logger.info("Host {}: Setting base prompt".format(self._host))
        prompt = await self._find_prompt()
        # Cut off prompt from "prompt/context/other" if it exists
        # If not we get all prompt
        prompt = prompt[:-1].split('/')
        prompt = prompt[0]
        self._base_prompt = prompt
        delimiters = map(re.escape, type(self)._delimiter_list)
        delimiters = r"|".join(delimiters)
        base_prompt = re.escape(self._base_prompt[:12])
        pattern = type(self)._pattern
        self._base_pattern = pattern.format(base_prompt, delimiters)
        logger.debug("Host {}: Base Prompt: {}".format(self._host, self._base_prompt))
        logger.debug("Host {}: Base Pattern: {}".format(self._host, self._base_pattern))
        return self._base_prompt

    async def _check_multiple_mode(self):
        """Check mode multiple. If mode is multiple we adding info about contexts"""
        logger.info("Host {}:Checking multiple mode".format(self._host))
        out = await self.send_command('show mode')
        if 'multiple' in out:
            self._multiple_mode = True

        logger.debug("Host {}: Multiple mode: {}".format(self._host, self._multiple_mode))
