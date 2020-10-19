from bemoss_lib.databases.cassandraAPI import cassandraDB
from datetime import datetime
import uuid
nickname = "Agent3"
from bemoss_lib.utils.offline_table_init import *

agent_id = "agent34"
offline_variables = dict()
offline_variables['date_id'] = str(datetime.now().date())
offline_variables['time'] = datetime.utcnow()
offline_variables['event_id'] = uuid.uuid4()
offline_variables['agent_id'] = nickname + ' (' + agent_id + ')'
offline_variables['event'] = 'device-tampering'
offline_variables['reason'] = 'tamperer'
offline_variables['related_to'] = None
offline_id = None
offline_variables['logged_time'] = datetime.utcnow()
cassandraDB.customInsert(all_vars=offline_variables, log_vars=EVENTS_TABLE_VARS,
                         tablename=EVENTS_TABLE_NAME)