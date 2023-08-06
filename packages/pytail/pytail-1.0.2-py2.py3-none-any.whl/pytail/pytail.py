"""TCP component of pyTail"""
import threading
import logging
import os
import time
import socket
import string

from . import config

LOGGER = logging.getLogger(__name__)


class Server(object):
    """Server"""

    def __init__(self):
        cfg = config.Config()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((cfg.get('tcp_host'), cfg.get('tcp_port')))

    def listen(self):
        """Starts TCP"""
        self.sock.listen(5)
        while True:
            client, address = self.sock.accept()
            client.settimeout(config.Config().get('tcp_timeout'))
            threading.Thread(target=self.listen_client,
                             args=(client, address[0])).start()

    @staticmethod
    def get_file(tcpclient):
        """Get file to tail"""
        cfg = config.Config()
        if isinstance(cfg.get('file'), str):
            return cfg.get('file'), cfg.get('file')
        data = tcpclient.recv(1024)
        if data:
            tailed = data.decode().replace('\n', '').replace('\r', '')
            for possible_path in cfg.get('paths'):
                ppath = string.Template(possible_path)
                path = ppath.safe_substitute(file=tailed)
                if os.path.exists(path) and os.path.isfile(path):
                    return path, tailed
        return (False, tailed if tailed else False)

    @staticmethod
    def listen_client(client, address):
        """Listens to client request"""
        LOGGER.info('%s: Connection', address)
        listen = True
        while listen:
            try:
                path, tailed = Server.get_file(client)
                if not path:
                    raise Exception('Unable to find logfile %s' % tailed)
                LOGGER.info('%s: Using log %s', address, path)
                with open(path, 'r') as logfile:
                    st_results = os.stat(path)
                    st_size = st_results[6]
                    logfile.seek(st_size)
                    while True:
                        where = logfile.tell()
                        line = logfile.readline()
                        if not line:
                            time.sleep(0.5)
                            logfile.seek(where)
                        else:
                            client.send(line.encode())
            except Exception as errn:  # pylint: disable=broad-except
                client.send('Error: {0}'.format(errn).encode())
                LOGGER.error('%s: %s', address, str(errn))
            finally:
                client.close()
                LOGGER.info('%s: Connection closed', address)
                listen = False
