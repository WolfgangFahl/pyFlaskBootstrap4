'''
Created on 2021-02-06

@author: wf
'''
from flask import Blueprint, Response, request, abort, stream_with_context
from queue import Queue
from pydispatch import dispatcher
import logging

class SSE_BluePrint(object):
    '''
    a blueprint for server side events 
    '''
    def __init__(self,app,name:str,template_folder:str=None,debug=False):
        '''
        Constructor
        '''
        self.name=name
        self.debug=debug
        if template_folder is not None:
            self.template_folder=template_folder
        else:
            self.template_folder='templates'    
        self.blueprint=Blueprint(name,__name__,template_folder=self.template_folder)
        self.app=app
        app.register_blueprint(self.blueprint)
        
        @self.app.route('/sse/<channel>')
        def subscribe(channel):
            def events():
                PubSub.subscribe(channel)
            self.stream(events)
                
    def stream(self,generator): 
        '''
        stream the given generator
        '''  
        if request.headers.get('accept') == 'text/event-stream':
            return Response(stream_with_context(generator), content_type='text/event-stream')
        else:
            abort(404)       
                
    def generate(self,func,limit=-1):
        '''
        create a generator from a given function
        Args:
            func: the function to convert to a generator
            limit (int): optional limit of how often the generator should be applied - 1 for endless
        Returns:
            a generator for the function
        '''   
        count=0
        while limit==-1 or count<limit:
            # wait for source data to be available, then push it
            count+=1
            result=func()
            yield 'data: {}\n\n'.format(result)
            
    def enableDebug(self,debug:bool):
        '''
        set my debugging
        
        Args:
            debug(bool): True if debugging should be switched on
        '''
        self.debug=debug
        if self.debug:
            logging.basicConfig(level=logging.DEBUG, format='%(asctime)s.%(msecs)03d %(levelname)s:\t%(message)s', datefmt='%Y-%m-%d %H:%M:%S')
            
    def publish(self, message:str, channel:str='sse', debug=False):
        """
        Publish data as a server-sent event.
        
        Args:
            message(str): the message to send
            channel(str): If you want to direct different events to different
                clients, you may specify a channel for this event to go to.
                Only clients listening to the same channel will receive this event.
                Defaults to "sse".
            debug(bool): if True  enable debugging
        """
        return PubSub.publish(channel=channel, message=message,debug=debug)

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
    
    def __init__(self,channel:str='sse',maxsize:int=15, debug=False,dispatch=False):
        '''
        Args:
            channel(string): the channel name
            maxsize(int): the maximum size of the queue
            debug(bool): whether debugging should be switched on
            dispatch(bool): if true use the pydispatch library - otherwise only a queue
        '''
        self.channel=channel
        self.queue=Queue(maxsize=maxsize)
        self.debug=debug
        self.receiveCount=0
        self.dispatch=False
        if dispatch:
            dispatcher.connect(self.receive,signal=channel,sender=dispatcher.Any)
        
    @staticmethod
    def reinit():
        '''
        reinitialize the pubSubByChannel dict
        '''
        PubSub.pubSubByChannel={}
        
    @staticmethod
    def forChannel(channel):    
        '''
        return a PubSub for the given channel
        
        Args:
            channel(str): the id of the channel
        Returns:
            PubSub: the PubSub for the given channel
        '''
        if channel in PubSub.pubSubByChannel:
            pubsub=PubSub.pubSubByChannel[channel]
        else:
            pubsub=PubSub(channel)
            PubSub.pubSubByChannel[channel]=pubsub
        return pubsub
    
    @staticmethod    
    def publish(channel:str,message:str,debug=False):
        '''
        publish a message via the given channel
        
        Args:
            channel(str): the id of the channel to use
            message(str): the message to publish/send
        Returns:
            PubSub: the pub sub for the channel
            
        '''
        pubsub=PubSub.forChannel(channel)
        pubsub.debug=debug
        pubsub.send(message)
        return pubsub
        
    @staticmethod    
    def subscribe(channel,limit=-1,debug=False): 
        '''
        subscribe to the given channel
        
        Args:
            channel(str): the id of the channel to use
            limit(int): limit the maximum amount of messages to be received        
            debug(bool): if True debugging info is printed
        '''  
        pubsub=PubSub.forChannel(channel)
        pubsub.debug=debug
        return pubsub.listen(limit)
    
    def send(self,message):
        '''
        send the given message
        '''
        sender=object();
        if self.dispatch:
            dispatcher.send(signal=self.channel,sender=sender,msg=message)
        else:
            self.receive(sender,message)
        
    def receive(self,sender,message):
        '''
        receive a message
        '''
        if sender is not None:
            self.receiveCount+=1;
            if self.debug:
                logging.debug("received %d:%s" % (self.receiveCount,message))
            self.queue.put(message)
        
    def listen(self,limit=-1):
        '''
        listen to my channel
        
        this is a generator for the queue content of received messages
        
        Args:
            limit(int): limit the maximum amount of messages to be received
        
        Return:
            generator: received messages to be yielded
        '''
        if limit>0 and self.receiveCount>limit:
            return
        yield self.queue.get()
    
    def unsubscribe(self):
        '''
        unsubscribe me
        '''
        if self.dispatch:
            dispatcher.disconnect(self.receive, signal=self.channel)
        pass
            
   
        