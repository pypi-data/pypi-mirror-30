from __future__ import print_function, unicode_literals
import stomp
from proton.handlers import MessagingHandler
from proton import Message
from proton.reactor import Container


class MessageSubscriberListener(stomp.ConnectionListener):
    def __init__(self, connection, message_received_function, destinations=None):
        super(MessageSubscriberListener, self).__init__()
        self.message_received_function = message_received_function
        self.destinations = destinations
        self.connection = connection

    def on_error(self, headers, message):
        print(message)

    def on_message(self, headers, message):
        destination = headers.get('destination')
        kwargs = {'destination': destination, 'message': message}
        functions = {
            True: lambda: self.message_received_function(**kwargs),
            False: lambda: None
        }
        functions.get(self.message_received_function is not None)()

    def on_disconnected(self):
        pass


class MessageBrokerClient(object):
    def __init__(self):
        pass

    def send_message(self, destination, message, content_type=None, headers=None):
        raise NotImplementedError('This method is not implemented')

    def stop(self):
        raise NotImplementedError('This method is not implemented')

    def disconnect(self):
        raise NotImplementedError('This method is not implemented')

    def start(self):
        raise NotImplementedError('This method is not implemented')

    def subscribe_message(self, destination, subscription_id, headers=None):
        raise NotImplementedError('This method is not implemented')

    def add_message_listener(self, message_received_function, listener_name, destinations=None):
        raise NotImplementedError('This method is not implemented')


class MessageBrokerClientStomp(MessageBrokerClient):
    connection = None

    def __init__(self, host_and_ports=None, heartbeats=None, user=None, password=None):
        super(MessageBrokerClientStomp, self).__init__()
        self.host_and_ports = host_and_ports
        self.heartbeats = heartbeats
        self.user = user
        self.password = password
        self.reconnect()

    def reconnect(self):
        self.connection = stomp.Connection(
            host_and_ports=self.host_and_ports,
            heartbeats=self.heartbeats, keepalive=True)
        self.connection.start()
        self.connection.connect(
            self.user, self.password,
            wait=True)

    def send_message(self, destination, message, content_type=None, headers=None):
        content_type = {True: content_type, False: 'application/json'}.get(content_type is not None)
        headers = {True: {}, False: headers}.get(headers is None)
        return self.connection.send(destination=destination, body=message,
                                    content_type=content_type, headers=headers)

    def subscribe_message(self, destination, subscription_id, headers=None):
        return self.connection.subscribe(destination=destination, id=subscription_id, headers=headers)

    def add_message_listener(self, message_received_function, listener_name, destinations=None):
        listener = MessageSubscriberListener(
            self.connection, message_received_function, destinations)
        self.connection.set_listener(listener_name, listener)

    def stop(self):
        return self.connection.stop()

    def start(self):
        return self.connection.start()

    def disconnect(self):
        return self.connection.disconnect()

    def is_connected(self):
        return self.connection.is_connected()

    def connect(self, user=None, password=None):
        return self.connection.connect(user=user, password=password, wait=True)

    def is_running(self):
        return self.connection.running


class ProtonMessageReceiverHandler(MessagingHandler):
    def __init__(self, server, address, on_message_function):
        super(ProtonMessageReceiverHandler, self).__init__()
        self.server = server
        self.address = address
        self.on_message_function = on_message_function

    def on_start(self, event):
        connection = event.container.connect(self.server)
        event.container.create_receiver(connection, self.address)

    def on_message(self, event):
        self.on_message_function(event.message.body)


class MessageSenderHandler(MessagingHandler):
    def __init__(self, server, address, message):
        super(MessageSenderHandler, self).__init__()
        self.server = server
        self.address = address
        self.message = message

    def on_start(self, event):
        connection = event.container.connect(self.server)
        event.container.create_sender(connection, self.address)

    def on_sendable(self, event):
        event.sender.send(Message(body=self.message))
        event.sender.close()

    def on_accepted(self, event):
        event.connection.close()


class MessageSender(object):

    def __init__(self, server, address):
        self.server = server
        self.address = address

    def send_message(self, message):
        Container(MessageSenderHandler(self.server, self.address, message)).run()
