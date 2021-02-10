'''
Created on 2021-02-06

@author: wf
'''
from flask import Blueprint, Response
import json
import six
import queue
from collections import OrderedDict

class SSE_BluePrint(object):
    '''
    a blueprint for server side events 
    '''
    def __init__(self,app,name:str,template_folder:str=None):
        '''
        Constructor
        '''
        self.name=name
        if template_folder is not None:
            self.template_folder=template_folder
        else:
            self.template_folder='templates'    
        self.blueprint=Blueprint(name,__name__,template_folder=self.template_folder)
        self.app=app
        app.register_blueprint(self.blueprint)
        self.pubsub=PubSub()
        
        @self.app.route('/subscribe/<channel>')
        def subscribe(channel):
            return self.subscribe(channel)        
            
    def publish(self, data, type=None, id=None, retry=None, channel='sse'):
        """
        Publish data as a server-sent event.
        :param data: The event data. If it is not a string, it will be
            serialized to JSON using the Flask application's
            :class:`~flask.json.JSONEncoder`.
        :param type: An optional event type.
        :param id: An optional event ID.
        :param retry: An optional integer, to specify the reconnect time for
            disconnected clients of this stream.
        :param channel: If you want to direct different events to different
            clients, you may specify a channel for this event to go to.
            Only clients listening to the same channel will receive this event.
            Defaults to "sse".
        """
        message = Message(data, type=type, id=id, retry=retry)
        msg_json = json.dumps(message.to_dict())
        return self.pubsub.publish(channel=channel, message=msg_json)
    
    def messages(self, channel='sse'):
        """
        A generator of :class:`~flask_sse.Message` objects from the given channel.
        """
        pubsub = self.pubsub
        pubsub.subscribe(channel)
        try:
            for pubsub_message in pubsub.listen():
                if pubsub_message['type'] == 'message':
                    msg_dict = json.loads(pubsub_message['data'])
                    yield Message(**msg_dict)
        finally:
            try:
                pubsub.unsubscribe(channel)
            except ConnectionError:
                pass
            
    def subscribe(self,channel):
        def stream():
            for message in self.messages(channel=channel):
                yield str(message)
                
        return Response(stream(), mimetype='text/event-stream')
    
class PubSub:
    '''
    redis pubsub duck replacement
    '''
    def __init__(self):
        '''
        constructor
        '''
        self.publisherByChannel={}
        
    def publish(self,channel:str,message):
        '''
        publish the given message thru the given channel
        
        Args:
            channel(str): the id of the channel to be used
            message(Message): the message to publish
        ''' 
        if channel in self.publisherByChannel:
            publisher=self.publisherByChannel[channel]
        else:
            publisher=Publisher(channel)
            self.publisherByChannel[channel]=publisher
        publisher.publish(message)
        
    def subscribe(self,channel):
        '''
        subscribe to the given channel
        
        Args:
            channel(str): the id of the channel to be used
            
        '''
        if not channel in self.publisherByChannel:
            raise Exception("channel %s is not published" % channel)
        publisher=self.publisherByChannel[channel]
        return publisher.subscribe()
    
    def listen(self):
        pass
    
    def get_message(self):
        pass
        
    def unsubscribe(self,channel):
        pass
    
class Publisher:
    def __init__(self,channel='sse',queueSize=15,deleteIfFull=True):
        '''
        Args:
            channel(string): the channel name
            queueSize(int): the maximum number of message to be kept in a queue
            deleteIfFull(bool): if true a queue will be deleted if it is full 
        '''
        self.listeners = []
        self.channel=channel
        self.queueSize=queueSize
        self.deleteIfFull=deleteIfFull

    def subscribe(self):
        '''
        create another queue and return it
        
        Returns:
            Queue: a new queue
        '''
        self.listeners.append(queue.Queue(maxsize=self.queueSize))
        return self.listeners[-1]

    def publish(self, msg):
        '''
        publish the given message
        
        Args:
            msg: the message to publish
        
        '''
        # We go in reverse order because we might have to delete an element, which will shift the
        # indices backward
        for i in reversed(range(len(self.listeners))):
            try:
                self.listeners[i].put_nowait(msg)
            except queue.Full:
                del self.listeners[i]
            
            
class Message(object):
    """
    Data that is published as a server-sent event.
    """
    def __init__(self, data, type=None, id=None, retry=None):
        """
        Create a server-sent event.
        :param data: The event data. If it is not a string, it will be
            serialized to JSON using the Flask application's
            :class:`~flask.json.JSONEncoder`.
        :param type: An optional event type.
        :param id: An optional event ID.
        :param retry: An optional integer, to specify the reconnect time for
            disconnected clients of this stream.
        """
        self.data = data
        self.type = type
        self.id = id
        self.retry = retry

    def to_dict(self):
        """
        Serialize this object to a minimal dictionary, for storing in Redis.
        """
        # data is required, all others are optional
        d = {"data": self.data}
        if self.type:
            d["type"] = self.type
        if self.id:
            d["id"] = self.id
        if self.retry:
            d["retry"] = self.retry
        return d

    def __str__(self):
        """
        Serialize this object to a string, according to the `server-sent events
        specification <https://www.w3.org/TR/eventsource/>`_.
        """
        if isinstance(self.data, six.string_types):
            data = self.data
        else:
            data = json.dumps(self.data)
        lines = ["data:{value}".format(value=line) for line in data.splitlines()]
        if self.type:
            lines.insert(0, "event:{value}".format(value=self.type))
        if self.id:
            lines.append("id:{value}".format(value=self.id))
        if self.retry:
            lines.append("retry:{value}".format(value=self.retry))
        return "\n".join(lines) + "\n\n"

    def __repr__(self):
        kwargs = OrderedDict()
        if self.type:
            kwargs["type"] = self.type
        if self.id:
            kwargs["id"] = self.id
        if self.retry:
            kwargs["retry"] = self.retry
        kwargs_repr = "".join(
            ", {key}={value!r}".format(key=key, value=value)
            for key, value in kwargs.items()
        )
        return "{classname}({data!r}{kwargs})".format(
            classname=self.__class__.__name__,
            data=self.data,
            kwargs=kwargs_repr,
        )

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__) and
            self.data == other.data and
            self.type == other.type and
            self.id == other.id and
            self.retry == other.retry
        )

            
   
        