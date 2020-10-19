import json
import logging
import sys

import psycopg2

from bemoss_lib.utils import db_helper

_log = logging.getLogger(__name__)
from bemoss_lib.platform.BEMOSSAgent import BEMOSSAgent
from bemoss_lib.utils.BEMOSS_ONTOLOGY import BEMOSS_ONTOLOGY

TEMP = BEMOSS_ONTOLOGY.TEMPERATURE.NAME

class ThermostatControlAgent(BEMOSSAgent):

    #1. agent initialization
    def __init__(self, *args, **kwargs):
        super(ThermostatControlAgent, self).__init__(*args,**kwargs)
        #1. initialize all agent variables
        self.agent_id = kwargs['name']
        self.data = {'thermostat': 'RTH8_1169269', 'sensor': '', 'sensor_weight':0.5,
                     'cool_setpoint':70,'heat_setpoint':80,'mode':'AUTO','deadband':0.5}

        dbcon = db_helper.db_connection()
        self.runPeriodically(self.periodicProcess,60)
        self.subscribe(topic='update',callback=self.appUpdate)
        self.updateAppData(self.dbcon)
        self.get_nicknames(self.dbcon)
        self.run()

    def appUpdate(self, dbcon, sender, topic, message):
        self.updateAppData(dbcon)

    def updateAppData(self,dbcon):
        dbcon.execute("select app_data from application_running where app_agent_id=%s", (self.agent_id,))
        if dbcon.rowcount:
            data = dbcon.fetchone()[0]
            for key, value in data.items():
                self.data[key] = value

    def get_nicknames(self,dbcon):
        try:
            dbcon.execute("select nickname from device_info where agent_id=%s",(self.data['thermostat'],))
            if dbcon.rowcount:
                self.thermostat_nickname = dbcon.fetchone()[0]

            dbcon.execute("select nickname from device_info where agent_id=%s", (self.data['sensor'],))
            if dbcon.rowcount:
                self.sensor_nickname = dbcon.fetchone()[0]
            else:
                self.sensor_nickname = "Sensor not selected"
        except psycopg2.IntegrityError as er: #Database trouble
            #reconnect first
            dbcon.database_connect()

    def make_thermostat(self,dbcon, thermo_data,action):
        control_message = dict()
        control_message['user'] = 'thermostat_control_app'
        control_message['hold'] = BEMOSS_ONTOLOGY.HOLD.POSSIBLE_VALUES.PERMANENT

        if action == 'COOL':
            if thermo_data['thermostat_mode'] != 'COOL' or thermo_data[TEMP] < thermo_data['cool_setpoint'] + 2:
                control_message['thermostat_mode'] = 'COOL'
                control_message['cool_setpoint'] = thermo_data[TEMP] - 5
                self.bemoss_publish(topic='update',target=self.data['thermostat'],message=control_message)
                print "Thermostat cooled to: " + str(control_message)

        if action == 'NOCOOL':
            if thermo_data['thermostat_mode'] != 'COOL' or thermo_data[TEMP] > thermo_data['cool_setpoint'] - 2:
                control_message['thermostat_mode'] = 'COOL'
                control_message['cool_setpoint'] = thermo_data[TEMP] + 5
                self.bemoss_publish(topic='update',target=self.data['thermostat'],message=control_message)
                print "Thermostat nocooled to: " + str(control_message)

        if action == 'HEAT':
            if thermo_data['thermostat_mode'] != 'HEAT' or thermo_data[TEMP] > thermo_data['heat_setpoint'] - 2:
                control_message['thermostat_mode'] = 'HEAT'
                control_message['heat_setpoint'] = thermo_data[TEMP] + 5
                self.bemoss_publish(topic='update',target=self.data['thermostat'],message=control_message)
                print "Thermostat heated to: " + str(control_message)

        if action == 'NOHEAT':
            if thermo_data['thermostat_mode'] != 'HEAT' or thermo_data[TEMP] < thermo_data['heat_setpoint'] + 2:
                control_message['thermostat_mode'] = 'HEAT'
                control_message['heat_setpoint'] = thermo_data[TEMP] - 5
                self.bemoss_publish(topic='update',target=self.data['thermostat'],message=control_message)
                print "Thermostat noheated to: " + str(control_message)


    def periodicProcess(self,dbcon):

        self.updateAppData(dbcon)
        dbcon.execute("select data from devicedata where agent_id=%s",(self.data['thermostat'],))
        if dbcon.rowcount:
            thermo_data = dbcon.fetchone()[0]
        else:
            return
        dbcon.execute("select data from devicedata where agent_id=%s", (self.data['sensor'],))
        if dbcon.rowcount:
            sensor_data = dbcon.fetchone()[0]
        else:
            return

        s_weight = self.data['sensor_weight']
        avg_temperature = thermo_data[TEMP] * (1 - s_weight) + sensor_data[TEMP] * s_weight
        if self.data['mode'] in ['COOL','AUTO']:
            if avg_temperature > self.data['cool_setpoint'] + self.data['deadband']:
                self.make_thermostat(dbcon, thermo_data,'COOL')
            elif avg_temperature < self.data['cool_setpoint'] - self.data['deadband']:
                self.make_thermostat(dbcon, thermo_data,'NOCOOL')

        if self.data['mode'] in ['HEAT','AUTO']:
            if avg_temperature < self.data['heat_setpoint'] - self.data['deadband']:
                self.make_thermostat(dbcon, thermo_data,'HEAT')
            elif avg_temperature > self.data['cool_setpoint'] + self.data['deadband']:
                self.make_thermostat(dbcon, thermo_data,'NOHEAT')

        self.data['avg_temperature'] = avg_temperature
        dbcon.execute("UPDATE application_running SET app_data=%s, status=%s WHERE app_agent_id=%s",
                            (json.dumps(self.data), "running", self.agent_id))
        dbcon.commit()
        print avg_temperature


def main(argv=sys.argv):
    '''Main method called by the eggsecutable.'''
    print "Cannot run as script"

if __name__ == '__main__':
    # Entry point for script
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass