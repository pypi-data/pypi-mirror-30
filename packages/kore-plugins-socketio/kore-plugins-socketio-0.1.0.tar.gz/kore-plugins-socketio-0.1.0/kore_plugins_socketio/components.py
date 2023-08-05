import logging

from socketio import AsyncServer

from kore.components.plugins.base import BasePluginComponent

log = logging.getLogger(__name__)


class SocketIOPluginComponent(BasePluginComponent):

    def get_services(self):
        return (
            ('config', self.config),
            ('async_server', self.async_server),
        )

    def config(self, container):
        config = container('config')

        return config.get_section('socketio')

    def async_server(self, container):
        engineio_options = container('config', namespace=self.namespace)

        return AsyncServer(**engineio_options)
