'''
Created on 2021-02-06

@author: wf
'''
from flask import Blueprint, Response, request, abort
from queue import Queue
from pydispatch import dispatcher

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
        
        @self.app.route('/subscribe/<channel>')
        def subscribe(channel):
            if request.headers.get('accept') == 'text/event-stream':
                def events():
                    PubSub.subscribe(channel)
                return Response(events(), content_type='text/event-stream')
            else:
                abort(404)   
            
    def publish(self, message, channel='sse'):
        """
        Publish data as a server-sent event.
        :param message: the message to send
        :param channel: If you want to direct different events to different
            clients, you may specify a channel for this event to go to.
            Only clients listening to the same channel will receive this event.
            Defaults to "sse".
        """
        return PubSub.publish(channel=channel, message=message)

    def subscribe(self,channel,limit=-1,debug=False):
        def stream():
            for message in PubSub.subscribe(channel,limit,debug=debug):
                yield str(message)
                
        return Response(stream(), mimetype='text/event-stream')
    
class PubSub:
    '''
    redis pubsub duck replacement
    '''
    pubSubByChannel={}
    
    def __init__(self,channel:str='sse',maxsize:int=15, debug=False):
        '''
        Args:
            channel(string): the channel name
            maxsize(int): the maximum size of the queue
            debug(bool): whether debugging should be switched on
        '''
        self.channel=channel
        self.queue=Queue(maxsize=maxsize)
        self.debug=debug
        self.receiveCount=0
        dispatcher.connect(self.receive,signal=channel,sender=dispatcher.Any)
        
    @staticmethod
    def reinit():
        PubSub.pubSubByChannel={}
        
    @staticmethod
    def forChannel(channel):    
        if channel in PubSub.pubSubByChannel:
            pubsub=PubSub.pubSubByChannel[channel]
        else:
            pubsub=PubSub(channel)
            PubSub.pubSubByChannel[channel]=pubsub
        return pubsub
    
    @staticmethod    
    def publish(channel,message):
        '''
        publish a message via the given channel
        '''
        pubsub=PubSub.forChannel(channel)
        pubsub.send(message)
        return pubsub
        
    @staticmethod    
    def subscribe(channel,limit=-1,debug=False):   
        pubsub=PubSub.forChannel(channel)
        pubsub.debug=debug
        return pubsub.listen(limit)
    
    def send(self,msg):
        '''
        send the given message
        '''
        sender=object();
        dispatcher.send(signal=self.channel,sender=sender,msg=msg)
        
    def receive(self,sender,msg):
        '''
        receive a message
        '''
        if sender is not None:
            self.receiveCount+=1;
            if self.debug:
                print("received %d:%s" % (self.receiveCount,msg))
            self.queue.put(msg)
        
    def listen(self,limit=-1):
        if limit>0 and self.receiveCount>limit:
            return
        yield self.queue.get()
    
    def unsubscribe(self):
        dispatcher.disconnect(self.receive, signal=self.channel)
        pass
            
   
        