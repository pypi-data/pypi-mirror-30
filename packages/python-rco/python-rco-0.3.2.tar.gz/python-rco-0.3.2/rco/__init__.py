# -*- coding: utf-8 -*-

__version__ = '0.3.2'

from sys import version_info as _vi
py3 = _vi[0] > 2


from . import base, client, tickets, security, tools, naming, plugins, async
from .base import Service
from .interfaces import CryptoInterface, MetaInterface, Namespace


import cherrypy
toolbox = cherrypy.tools
toolbox.encrypted_xmlrpc = tools.EncryptedXmlrpcTool()


cherrypy.config.update({
    'engine.starter_stopper.on': True,
    'engine.task_manager.on': True
})
