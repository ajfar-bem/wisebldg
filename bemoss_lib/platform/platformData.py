from multiprocessing import Queue
import zmq
import settings

AGENT_QUEUE_SIZE = 1000
MANAGER_QUEUE_SIZE = 1000
LOGGING_QUEUE_SIZE = 10000

address = settings.PLATFORM_SOCKET_ADDRESS
context = zmq.Context()
rep_socket = context.socket(zmq.REP)
rep_socket.bind(address)

inQueues_dict = dict() #map to store all in queueus of the agents
outQueue = Queue(MANAGER_QUEUE_SIZE) #all agents put their outgoing messages into this queue
processes_dict = dict() # dict to save all active agent process
archived_process_list = list() #save process that have been attempted to be stopped, as (date_of_archive,process) tuple
logQueue = Queue(LOGGING_QUEUE_SIZE)

