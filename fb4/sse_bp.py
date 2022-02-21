'''
Created on 2021-02-06

@author: wf
'''
import io
import json
import uuid
import time
import mimetypes
from datetime import datetime, timedelta
from functools import partial
from flask import Blueprint, Response, request, abort, stream_with_context, send_file
from queue import Queue, Empty
from pydispatch import dispatcher
from apscheduler.schedulers.background import BackgroundScheduler
import logging

class SSE_BluePrint(object):
    '''
    a blueprint for server side events 
    '''

    def __init__(self,app,name:str,template_folder:str=None,debug=False,withContext=False,withScheduler=True, appWrap=None):
        '''
        Constructor
        Args:
            app(FlaskApp): Flask server app
            name(str): name of the SSE api
            template_folder(str): template folder
            debug(bool): If true debug messages are printed
            withContext(bool): Send responses with request context
            withScheduler(bool):
            appWrap: appWrap with additional context for the app
        '''
        self.name=name
        self.debug=debug
        self.withContext=withContext
        if template_folder is not None:
            self.template_folder=template_folder
        else:
            self.template_folder='templates'    
        self.blueprint=Blueprint(name,__name__,template_folder=self.template_folder)
        self.app=app
        self.appWrap=appWrap
        if withScheduler:
            self.scheduler=BackgroundScheduler()
            self.scheduler.start()
        else:
            self.scheduler=None
        app.register_blueprint(self.blueprint)

        @self.app.route('/sse/file/<id>')
        def retrieveFile(id):
            fileGen=PubSub.subscribe(id,1)
            file=next(fileGen)
            PubSub.close(id)
            if isinstance(file, io.BytesIO):
                mimeType= mimetypes.guess_type(file.name)
                return send_file(file, as_attachment=True, attachment_filename=file.name, mimetype=mimeType[0])
        
        @self.app.route('/sse/<channel>')
        def subscribe(channel):
            def events():
                return PubSub.subscribe(channel)
            return self.streamGen(events())

    @property
    def baseUrl(self):
        if self.appWrap is not None:
            return getattr(self.appWrap, "baseUrl", None)
        return None
                
    def streamSSE(self,ssegenerator): 
        '''
        stream the Server Sent Events for the given SSE generator
        '''  
        response=None
        if self.withContext:
            if request.headers.get('accept') == 'text/event-stream':
                response=Response(stream_with_context(ssegenerator), content_type='text/event-stream')
            else:
                response=abort(404)    
        else:
            response= Response(ssegenerator, content_type='text/event-stream')
        return response
        
    def streamGen(self,gen):
        '''
        stream the results of the given generator
        '''
        ssegen=self.generateSSE(gen)
        return self.streamSSE(ssegen)   
            
    def streamFunc(self,func,limit=-1):
        '''
        stream a generator based on the given function
        Args:
            func: the function to convert to a generator
            limit (int): optional limit of how often the generator should be applied - 1 for endless
        Returns:
            an SSE Response stream
        '''
        gen=self.generate(func,limit)
        return self.streamGen(gen)
                
    def generate(self,func,limit=-1):
        '''
        create a SSE generator from a given function
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
            yield result
        
    def generateSSE(self,gen):
        '''
        generate Server Sent events from the given generator
        '''
        for result in gen:
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
            
    def publish(self, message, channel:str='sse', debug=False):
        """
        Publish data as a server-sent event.
        
        Args:
            message: the message to send
            channel(str): If you want to direct different events to different
                clients, you may specify a channel for this event to go to.
                Only clients listening to the same channel will receive this event.
                Defaults to "sse".
            debug(bool): if True  enable debugging
        """
        return PubSub.publish(channel=channel, message=message,debug=debug)

    def subscribe(self,channel,limit=-1,debug=False):
        '''
        subscribe to the given channel
        
        Args:
            channel(str): the id of the channel
            limit(int): a potential limit to the number of messages returned
            debug(bool): True if debugging should be switched on
        '''
        def stream():
            for message in PubSub.subscribe(channel,limit,debug=debug):
                yield str(message)
                
        return self.streamGen(stream)

    def streamDictGenerator(self, generator, slowdown: float = 0.0, startDirectly:bool=True):
        '''
        Stream the results of the given generator.
        Format: results are streamed in the following format and multiple dicts might be bundled into a list
            { "data": [...] }

        Args:
            generator(Generator): generator that yields dicts
            slowdown(float): minimum time between yielded results in seconds
            startDirectly(bool): Start the stream immediately otherwise the stream has to be started by calling startSseChannel()
        '''
        dictStream=DictStream(generator, slowdown, self)
        if startDirectly:
            dictStream.startSseChannel()
        return dictStream
    
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
    def publish(channel:str,message,debug=False):
        '''
        publish a message via the given channel
        
        Args:
            channel(str): the id of the channel to use
            message: the message to publish/send
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

        try:
            for item in iter(partial(self.queue.get, timeout=60), Empty):
                if item is None:
                    self.unsubscribe()
                    self.queue.task_done()
                yield item
        except Empty as e:
            # queue timeout close stream and let the client try later
            return
    def unsubscribe(self):
        '''
        unsubscribe me
        '''
        if self.dispatch:
            dispatcher.disconnect(self.receive, signal=self.channel)
        pass

    @classmethod
    def close(cls, channel):
        """
        Close the channel for given id

        Args:
            channel(str): id of the channel to close
        """
        pubsub=PubSub.forChannel(channel)
        pubsub.unsubscribe()
        pubsub.queue.task_done()


class DictStream:
    '''
    Gets a generator which yields dicts and publishes he dicts at an SSE Channel.
    Also provides functions to set the client side javascript code to subscribe to those results
    '''

    def __init__(self, generator, slowdown: float = 0.0, sseBlueprint: SSE_BluePrint = None):
        self.sseBl = sseBlueprint
        if slowdown > 0:
            def slowdown():
                for record in generator:
                    time.sleep(0.1)
                    yield json.dumps(record)
            self.generator = slowdown()
        else:
            self.generator = generator
        self.sseChannel = str(uuid.uuid1())

    def stream(self):
        '''
        Directly stream the generator as response. No subscription of the user to sse channel required but generator is
        dependent on the stream connection.

        Returns:
            Response
        '''
        return Response(self.generator, content_type="application/stream+json")

    def startSseChannel(self):
        """
        Start the generator and publish the results to the sse channel
        Returns:

        """
        run_date = datetime.now() + timedelta(seconds=0.5)
        self.sseBl.scheduler.add_job(self._publishCallback, 'date', run_date=run_date)

    def _publishCallback(self, bundleTime: float = 0.05):
        """
        publish all results of the generator to the sse channel.
        The results are bundled based on the required time to retrieve them. E.g. all results that are retrieved in a
        time interval of 0.05s are bundled into one publish message.
        If the end of the generator is reached None is yielded

        Args:
            bundleTime: Time in seconds in which all retrieved results are published as one data package

        Returns:

        """

        def time_passed(oldepoch, time: timedelta):
            return (datetime.now() - oldepoch) >= time

        buffer = []
        oldepoch = datetime.now()
        result=None
        for resPart in self.generator:
            if isinstance(resPart, DictStreamResult):
                result=resPart
                break
            buffer.append(resPart)
            if time_passed(oldepoch, timedelta(seconds=bundleTime)):
                self.sseBl.publish(json.dumps({'data': buffer}), self.sseChannel)
                buffer = []
                oldepoch = datetime.now()
        if buffer:
            self.sseBl.publish(json.dumps({'data': buffer}), self.sseChannel)
        if result:
            self.sseBl.publish(json.dumps(result.getResponse(self)), self.sseChannel)
        else:
            self.sseBl.publish(None, self.sseChannel)

    def progressMessages(self, show: int = -1, completdeMsg: str = None):
        """
        Show the progress of the stream by prining out the dicts.
        Usage:
            In the template the script can be called as follows (prgoress is in this case the forwarded object of DictStream)
            {{ progress.progressMessages()|safe }}

        Args:
            show(int): Number of messages that are displayed to the user. FIFO principle for message display. If -1 all incoming messages are shown
            completeMsg(str): Message to display once the stream is finished. If None the debug output will remain
        """
        showCompletedMessage = ""
        if completdeMsg:
            showCompletedMessage = f'targetContainer.innerHTML = "{completdeMsg}"'

        script = f"""
        <script>
            function showProgressMessages(id,url) {{
                var targetContainer = document.getElementById(id);
                var eventSource = new EventSource(url);
                    eventSource.onmessage = function(e) {{
                    if (e.data == 'None'){{
                        eventSource.close();
                        {showCompletedMessage}
                    }}else{{
                        if (targetContainer.innerHTML.split('<br>').length < {show} || {"true" if bool(show == -1) else "false"}){{
                            targetContainer.innerHTML += e.data +"<br>" ;
                        }}else{{
                            var prev_msg = targetContainer.innerHTML.split('<br>');
                            prev_msg.shift();
                            targetContainer.innerHTML = prev_msg.join('<br>') + e.data +"<br>" ;
                        }}

                    }}
                }};
            }};
        </script>"""
        progressMessages = f"""<pre id="{self.sseChannel}"></pre>"""
        if self.sseBl.baseUrl:
            sseChannel = f"{self.sseBl.baseUrl}/sse/{self.sseChannel}"
        else:
            sseChannel = f"/sse/{self.sseChannel}"
        fillProgressBar = f'<script>showProgressMessages("{self.sseChannel}","{sseChannel}");</script>'
        return script + progressMessages + fillProgressBar

    def progressWithDisplayOfResult(self):
        """
        Assumption: Gets progress messages in form of strings and a final result. The progress messages are displayed to
        as simple progress messages and the final result can be either a raw html element that is than embedded into the
        page or a file which is than forwarded to the user
        """
        script = f"""
                <script>
                    function showProgressMessages(id,url) {{
                        var targetContainer = document.getElementById(id);
                        var eventSource = new EventSource(url);
                            eventSource.onmessage = function(msg) {{
                            console.log(msg.data);
                            var e = JSON.parse(msg.data);
                            if (e.data == null){{
                                eventSource.close();
                                if (e.result != null){{
                                    var parser = new DOMParser();
                                    var htmlDoc = parser.parseFromString(e.result, 'text/html');
                                    console.log('Adding received result to target div');
                                    targetContainer.append(...htmlDoc.body.childNodes);
                                    console.log('Running received script tags');
                                    for (const element of $('#'+id).find('script')){{
                                        console.log(element.text);
                                        eval(element.text);
                                    }}
                                }}
                                if (e.file != null){{
                                    console.log('Get file form:', window.location.origin + e.file);
                                    window.location.href = window.location.origin + e.file;
                                }}
                            }}else{{
                                if (Array.isArray(e.data)){{
                                    targetContainer.innerHTML +=e.data.join("");
                                }}else{{
                                    targetContainer.innerHTML += e.data;
                                }}
                            }}
                        }};
                    }};
                </script>"""
        progressMessages = f"""<pre id="{self.sseChannel}"></pre>"""
        if self.sseBl.baseUrl:
            sseChannel = f"{self.sseBl.baseUrl}/sse/{self.sseChannel}"
        else:
            sseChannel = f"/sse/{self.sseChannel}"
        fillProgressBar = f'<script>showProgressMessages("{self.sseChannel}","{sseChannel}");</script>'
        return script + progressMessages + fillProgressBar


class DictStreamResult:
    """
    Indicates the end of a DictStream and can contain a final result
    """
    __slots__ = ["result"]

    def __init__(self, result):
        self.result=result

    def getResponse(self, dictStream:DictStream)->dict:
        """
        Returns the final stream result
        """
        return {'data': None, 'result': self.result}


class DictStreamFileResult(DictStreamResult):
    """
    Indicates the end of a DictStream and can contain final result in form of a file that is than offered for download
    """
    __slots__ = ["result", "file"]

    def __init__(self, result, file:io.BytesIO):
        super().__init__(result=result)
        self.file=file

    def getResponse(self, dictStream:DictStream)->dict:
        """
        Returns the final stream result and registers the file for download
        """
        channel=str(uuid.uuid1())
        fileChannel=f"sse/file/{channel}"
        if dictStream.sseBl.baseUrl:
            fileChannel=f"{dictStream.sseBl.baseUrl}/{fileChannel}"
        fileChannel=f"/{fileChannel}"
        dictStream.sseBl.publish(self.file, channel=channel)
        return {'data': None, 'result': self.result, 'file':fileChannel}