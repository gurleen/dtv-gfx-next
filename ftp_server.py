import asyncio
import concurrent.futures

from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
from pyftpdlib.authorizers import DummyAuthorizer

from janus import Queue


class MyHandler(FTPHandler):

    def on_connect(self):
        print("%s:%s connected" % (self.remote_ip, self.remote_port))

    def on_disconnect(self):
        # do something when client disconnects
        pass

    def on_login(self, username):
        # do something when user login
        pass
    

    def on_logout(self, username):
        # do something when user logs out
        pass

    def on_file_sent(self, file):
        # do something when a file has been sent
        print(file)
        pass

    def on_file_received(self, file):
        # do something when a file has been received
        print("File recieved")
        print(file)
        pass

    def on_incomplete_file_sent(self, file):
        # do something when a file is partially sent
        pass

    def on_incomplete_file_received(self, file):
        # remove partially uploaded files
        import os
        os.remove(file)


def _run_ftp_server_sync(queue):
    authorizer = DummyAuthorizer()
    authorizer.add_user('drexel', 'dragons', homedir='.', perm='elradfmwMT')
    authorizer.add_anonymous(homedir='.')

    handler = MyHandler
    handler.queue = queue
    handler.authorizer = authorizer
    server = FTPServer(('', 21), handler)
    server.serve_forever()


async def run_ftp_server(queue):
    loop = asyncio.get_running_loop()

    with concurrent.futures.ThreadPoolExecutor() as pool:
        result = await loop.run_in_executor(
            pool, _run_ftp_server_sync, queue)