from asyncore import dispatcher
from asynchat import async_chat
import socket
import asyncore

PORT = 5005
NAME = "TestChat"


class ChatSession(async_chat):
    """
    A class that takes care of a connection between the server and a single user.
    """

    def __init__(self, server, sock):
        super().__init__(sock)
        self.server = server
        self.set_terminator(b"\r\n")
        self.data = []
        self.push(f"Welcome to {self.server.name}\r\n".encode())

    def collect_incoming_data(self, data):
        self.data.append(data)

    def found_terminator(self):
        """
        If a terminator is found, that means that a full
        line has been read. Broadcast it to everyone.
        """
        line = "".join(self.data)
        self.data = []
        self.server.broadcast(line)

    def handle_close(self):
        super().handle_close()
        self.server.disconnect(self)


class ChatServer(dispatcher):
    """
    A class that receives connections and spawns individual
    sessions. It also handles broadcasts to these sessions.
    """

    def __init__(self, port, name):
        super().__init__()
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind(("", port))
        self.listen(5)
        self.name = name
        self.sessions = []

    def disconnect(self, session):
        self.sessions.remove(session)

    def broadcast(self, line):
        for session in self.sessions:
            session.push(f"{line}\r\n".encode())

    def handle_accept(self):
        conn, addr = self.accept()
        self.sessions.append(ChatSession(self, conn))


if __name__ == "__main__":
    s = ChatServer(PORT, NAME)
    try:
        asyncore.loop()
    except KeyboardInterrupt:
        print()
