from pexpect import pxssh


class Node:
    default_user = "root"
    default_password = 'xxx'
    default_address = "localhost"
    default_rpc_port = 9334
    default_ws_port = 19334

    def __init__(self, address=default_address, username=default_user, password=default_password,
                 rpc_port=default_rpc_port, ws_port=default_ws_port, sshkey=None, node_name=None):
        self.address = address
        self.username = username
        self.password = password
        self.sshkey = sshkey
        self.rpc_port = rpc_port
        self.ws_port = ws_port
        self.node_name = node_name

        self.spawn = pxssh.pxssh()
        # initial ssh-login session:

    def ssh_connect(self):
        if self.password is not None:
            print(f' !!! Logging in with password. User: {self.username}')
            self.spawn.login(self.address, self.username, password=self.password)
            return self
        if self.ssh_key is not None:
            print(f' !!! Logging in with ssh key. User: {self.username}')
            self.spawn.login(self.username, ssh_key=self.ssh_key)
            return self

    def logout(self):
        self.spawn.logout()
        print(f' !!! Logout of: {self.address}')

    def send_cmd(self, command, expected=None):
        if not self.spawn.isalive():
            self.ssh_connect()

        self.spawn.sendline(command)
        self.spawn.prompt()

    def get_rpc_url(self):
        return f'http://{self.address}:{self.rpc_port}'

    def get_ws_url(self):
        return f'ws://{self.address}:{self.ws_port}'


def load_node(node) -> Node:
    return node
