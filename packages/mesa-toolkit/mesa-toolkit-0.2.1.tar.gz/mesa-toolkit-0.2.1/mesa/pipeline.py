'''
Pipeline datastructures manage data through a workflow of casa objects.
'''
import abc
import multiprocessing as mp


class bootstrap(object):
    def __init__(self, data):
        self.data = data

    def __call__(self, async):
        async(self.data)


class Pipeline():

    def __init__(self, serial_pipes=None, async_msg_pipes=None, async_spawn_pipes=None):
        self.serial = serial_pipes
        self.async_msg = async_msg_pipes
        self.async_spawn = async_spawn_pipes
        self.pool = None
        if len(self.async_spawn):
            self.pool = mp.Pool(len(self.async_spawn))

    def execute(self, data):
        # serial data is fed back in as enriched/processed
        for pipe in self.serial:
            data = pipe(data)

        # no enrichment happening on the inline call - just communicating with a distributed service
        for pipe in self.async_msg:
            pipe(data)

        # return if any for async is offline so each pipe is detached from process
        bs = bootstrap(data)
        self.pool.map_async(bs , self.async_spawn )


class Pipe():

    @abc.abstractmethod
    def __call__(self, data):
        raise NotImplementedError('flow must be implemented by a subclass of type Pipe')


class AsyncPipe(Pipe):

    '''
    initiator should be an idempotent function

    e.g. a call to a REST endpoint, message queue or some other out of process communication mechanism.
    '''
    def __init__(self, initiator):
        # create the structures necessary for this to be async on instantiation else break
        self.initiator = initiator

    def __call__(self, data):
        self.initiator(data)
