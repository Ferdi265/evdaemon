from socket import socket, AF_UNIX
from subprocess import Popen, PIPE, DEVNULL
import struct
import json

from evdaemon import Module

MAGIC = b"i3-ipc"
IS_EVENT = 1 << 31

MSG = {
    "command": 0,
    "workspaces": 1,
    "subscribe": 2,
    "outputs": 3,
    "tree": 4,
    "marks": 5,
    "bar_config": 6,
    "version": 7,
    "binding_modes": 8,
    "config": 9
}

REPLY = {
    "command": 0,
    "workspaces": 1,
    "subscribe": 2,
    "outputs": 3,
    "tree": 4,
    "marks": 5,
    "bar_config": 6,
    "version": 7,
    "binding_modes": 8,
    "config": 9
}

EVENT = {
    "workspace": IS_EVENT | 0,
    "output": IS_EVENT | 1,
    "mode": IS_EVENT | 2,
    "window": IS_EVENT | 3,
    "bar_config_update": IS_EVENT | 4,
    "binding": IS_EVENT | 5,
    "shutdown": IS_EVENT | 6
}

class i3ipcModule(Module):
    name = "i3ipc"
    def __init__(self):
        super().__init__()
        self._connect()

    def _get_socketpath(self):
        i3 = Popen(["i3", "--get-socketpath"], stdout = PIPE, stderr = DEVNULL)
        i3.wait()
        raw = i3.stdout.read()
        decoded = raw[:-1].decode()
        return decoded

    def _connect(self):
        sock = socket(AF_UNIX)
        sockpath = self._get_socketpath()
        sock.connect(sockpath)
        self.register_file(sock, "socket_ready")
        self.listen_private("socket_ready", self._ready)
        self._socket = sock

    def _ready(self):
        magic = self._socket.recv(len(MAGIC))
        if magic == b"":
            self._socket.close()
            self.unregister_file(self._socket)
        elif magic != MAGIC:
            raise ValueError("remote i3 does not follow the protocol!")
        else:
            payload_len = struct.unpack("I", self._socket.recv(4))[0]
            msg_type = struct.unpack("I", self._socket.recv(4))[0]
            payload = self._socket.recv(payload_len).decode()
            self._decode_message(msg_type, payload)

    def _decode_message(self, msg_type, payload):
        payload = json.loads(payload)
        path = [self.name]
        if msg_type & IS_EVENT == 0:
            path.append("reply")
            for name, value in REPLY.items():
                if msg_type == value:
                    path.append(name)
                    break
            if len(path) < 3:
                path.append("unknown")
        else:
            path.append("event")
            for name, value in EVENT.items():
                if msg_type == value:
                    path.append(name)
                    break
            if len(path) < 3:
                path.append("unknown")
        self.emit(*path, payload)

    def send_cmd(self, cmd, payload = ""):
        self._socket.send(
            MAGIC +
            struct.pack("I", len(payload)) +
            struct.pack("I", MSG[cmd]) +
            payload.encode()
        )
