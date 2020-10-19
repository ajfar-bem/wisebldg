# -*- coding: utf-8 -*-
'''
Copyright (c) 2017, Virginia Tech
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
 following conditions are met:
1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following
disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following
disclaimer in the documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

The views and conclusions contained in the software and documentation are those of the authors and should not be
interpreted as representing official policies, either expressed or implied, of the FreeBSD Project.

This material was prepared as an account of work sponsored by an agency of the United States Government. Neither the
United States Government nor the United States Department of Energy, nor Virginia Tech, nor any of their employees,
nor any jurisdiction or organization that has cooperated in the development of these materials, makes any warranty,
express or implied, or assumes any legal liability or responsibility for the accuracy, completeness, or usefulness or
any information, apparatus, product, software, or process disclosed, or represents that its use would not infringe
privately owned rights.

Reference herein to any specific commercial product, process, or service by trade name, trademark, manufacturer, or
otherwise does not necessarily constitute or imply its endorsement, recommendation, favoring by the United States
Government or any agency thereof, or Virginia Tech - Advanced Research Institute. The views and opinions of authors
expressed herein do not necessarily state or reflect those of the United States Government or any agency thereof.

VIRGINIA TECH – ADVANCED RESEARCH INSTITUTE
under Contract DE-EE0006352

#__author__ = "BEMOSS Team"
#__credits__ = "Rajarshi Roy"
#__version__ = "3.5"
#__maintainer__ = "BEMOSS Team"
#__email__ = "aribemoss@gmail.com"
#__website__ = "www.bemoss.org"
#__created__ = "2017-07-19 17:09:20"

'''

# settings file for BEMOSS project.

import psycopg2
import settings
import os

db_database = settings.DATABASES['default']['NAME']
db_host = settings.DATABASES['default']['HOST']
db_port = settings.DATABASES['default']['PORT']
db_user = settings.DATABASES['default']['USER']
db_password = settings.DATABASES['default']['PASSWORD']


#connecting to Pgadmin
conn = psycopg2.connect(host=db_host, port=db_port, database=db_database,
                            user=db_user, password=db_password)
print('You need to run the code and press enter once and then get the username and encrypted password when you run and store the username and password in Bemoss.'+'\n''If you press Enter when starting Bemoss and delete the'+
      'database, then press press any button at first and press enter in the second part to put the saved username and passwords into the database.')
cur = conn.cursor()
print('Connected to database...')
print('Connected...')
mydata = raw_input('Click Enter to save username and password of devices or any other key to abort process...')

if mydata=="":
    try:
        newpath = r'username_and_password_details'
        if not os.path.exists(newpath):
            os.makedirs(newpath)

        cur.execute("SELECT * FROM Passwords_manager")
        rows = cur.fetchall()
        ids1=open('username_and_password_details/id.txt','w')
        username1 = open('username_and_password_details/username.txt', 'w')
        password1 = open('username_and_password_details/password_encrypted.txt', 'w')
        time = open('username_and_password_details/time_of_last_change.txt', 'w')
        device = open('username_and_password_details/device_model.txt', 'w')
        building_id=open('username_and_password_details/building_id.txt', 'w')

        for row in rows:
            ids=str(row[0])
            username2=str(row[1])
            password2=str(row[2])
            time1=str(row[3])
            building=str(row[4])
            device1=str(row[5])


            ids1.write(ids+'\n')
            username1.write(username2+'\n')
            password1.write(password2+'\n')
            time.write(time1+'\n')
            device.write(device1+'\n')
            building_id.write(building+'\n')

        conn.close()
        ids1.close()
        username1.close()
        password1.close()
        time.close()
        device.close()
        building_id.close()
    except:
        print('Failed to get database...')
else:
     print('No action has been done!')
print('Done...')
