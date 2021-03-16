from asyncore import dispatcher
from asynchat import async_chat
from typing import List, Optional
import socket
import asyncore

PORT = 5005
NAME = "TestChat"


class EndSession(Exception):
    pass


class CommandHandler:
    """
    Simple command handler similar to cmd.Cmd from the standard library.
    """

    def unknown(self, session, cmd):
        session.push(f"Unknown command: {cmd}s\r\n".encode())

    def handle(self, session, line):
        if not line.strip():
            return

        parts = line.split(" ", 1)
        cmd = parts[0]
        try:
            line = parts[1].strip()
        except IndexError:
            line = ""

        meth = getattr(self, f"do_{cmd}", None)
        try:
            meth(session, line)
        except TypeError:
            self.unknown(session, cmd)


class Room(CommandHandler):
    """
    A generic environment that may contain one or more users (sessions).
    It takes care of basic command handling and broadcasting.
    """

    def __init__(self, server):
        self.server = server
        self.sessions = []

    def add(self, session):
        self.sessions.append(session)

    def remove(self, session):
        self.sessions.remove(session)

    def broadcast(self, line):
        for session in self.sessions:
            session.push(line.encode())

    def do_logout(self, session, line):
        raise EndSession


class LoginRoom(Room):
    """
    A room meant for a single person who has just connected.
    """

    def add(self, session):
        super().add(session)
        self.broadcast(f"Welcome to {self.server.name}\r\n")

    def unknown(self, session, cmd):
        session.push('Please log in\nUse "login <nick>"\r\n'.encode())

    def do_login(self, session, line):
        name = line.strip()
        if not name:
            session.push("Please enter a name\r\n".encode())
        elif name in self.server.users:
            session.push(f'The name "{name}" is taken.\r\n'.encode())
            session.push("Please try again.\r\n".encode())
        else:
            session.name = name
            session.enter(self.server.main_room)


class ChatRoom(Room):
    """
    A room meant for multiple users who can chat with the others in the room.
    """

    def add(self, session):
        self.broadcast(session.name + " has entered the room.\r\n")
        self.server.users[session.name] = session
        super().add(session)

    def remove(self, session):
        super().remove(session)
        self.broadcast(session.name + " has left the room.\r\n")

    def do_say(self, session, line):
        self.broadcast(session.name + ": " + line + "\r\n")

    def do_look(self, session, line):
        session.push("The following are in this room:\r\n".encode())
        for other in self.sessions:
            session.push(f"{other.name}\r\n".encode())

    def do_who(self, session, line):
        session.push("The following are logged in:\r\n".encode())
        for name in self.server.users:
            session.push(f"{name}\r\n".encode())


class LogoutRoom(Room):
    """
    A simple room for a single user. Its sole purpose is to remove the
    user's name from the server.
    """

    def add(self, session):
        try:
            del self.server.users[session.name]
        except KeyError:
            pass


class ChatSession(async_chat):
    """
    A single session, which takes care of the communication with a single user.
    """

    data: List[bytes]
    name: Optional[str]

    def __init__(self, server, sock):
        super().__init__(sock)
        self.server = server
        self.set_terminator(b"\r\n")
        self.data = []
        self.name = None

        self.enter(LoginRoom(server))

    def enter(self, room):
        try:
            cur = self.room
        except AttributeError:
            pass
        else:
            cur.remove(self)
        self.room = room
        room.add(self)

    def collect_incoming_data(self, data: bytes) -> None:
        self.data.append(data)

    def found_terminator(self):
        line = b"".join(self.data)
        line = line.decode()
        self.data = []
        try:
            self.room.handle(self, line)
        except EndSession:
            self.handle_close()

    def handle_close(self):
        super().handle_close()
        self.enter(LogoutRoom(self.server))


class ChatServer(dispatcher):
    """
    A chat server with a single room.
    """

    def __init__(self, port, name):
        super().__init__()
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind(("", port))
        self.listen(5)
        self.name = name
        self.users = {}
        self.main_room = ChatRoom(self)

    def handle_accept(self):
        conn, addr = self.accept()
        ChatSession(self, conn)


if __name__ == "__main__":
    s = ChatServer(PORT, NAME)
    try:
        asyncore.loop()
    except KeyboardInterrupt:
        print()
