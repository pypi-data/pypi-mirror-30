import sys, os
sys.path.insert(0, os.path.abspath('..'))
from multiprocessing.connection import Listener
from threading import Thread
import time
import threading
import random
import timeit
import MySQLdb
import timeit
import multiprocessing
from multiprocessing import Process, Value
import time
import os
import pymysql
import queue
from apscheduler.schedulers.background import BackgroundScheduler


#-----------------------------------------------------------------------------Database connection

def monitor():
    print(threading.current_thread().name)
    print("----------------------------")
    sched.print_jobs()



class dbc(object):
    def __init__(self,credentials,q,m,cv):
        self.actions={"r_update":self.update,
                        "r_get_pallets_for_barn_and_barn":self.get_all_pallets,
                        "r_get_pallets_history":self.get_pallets_history,
                        "r_get_pallet_edit":self.get_pallet_edit,
                        "r_send_pallet_edit":self.send_pallet_edit,
                        "r_send_sensor_data":self.send_sensor_data,
                        "r_load_sensor_data_fromfile":self.load_sensor_data_from_file,
                        "r_load_sensor_to_file":self.load_sensor_data_to_file,
                        "r_get_sensor_data_date_range":self.get_sensor_data_date_range
                    }
        self.conn=""
        self.q=q #commands in
        self.m=m #messages out
        self.cv=cv #messages out lock
        self.hostname=credentials['hostname']
        self.username=credentials['username']
        self.password=credentials['password']
        self.database=credentials['database']
        
    def run(self):
        threading.current_thread().setName("DB Connection "  +self.hostname);
        cv=self.cv
        q=self.q
        m=self.m
        hostname=self.hostname
        username=self.username
        password=self.password
        database=self.database
        
        dbconnected=False
        while True:
            
                time.sleep(.01)
                mymessagelist=[]
                while not q.empty():
                   
                    if not dbconnected:
                        try:
                            self.conn = pymysql.connect( host=hostname, user=username, passwd=password, db=database )            
                            dbconnected=True
                            #print("connected...")
                        except:
                            #print("Database not connected!")
                            dbconnected=False
                    else:                       
                        
                            mytask=q.get()
                            #print(mytask)
                            result=self.actions[mytask[1]](mytask)
                            self.msg=[mytask[0],result]
                            #print("DB Connection:   " + str(self.msg))
                            with cv:                                                
                                m.put(self.msg)
                                cv.notify(1)
                             
                if dbconnected:
                    self.conn.close()
                    dbconnected=False
                    #print("connection closed")
                
            

    def archiveticketin_db(self,table, myDict):
        cur = self.conn.cursor()
        print(myDict)
        print("Updated Record...")
        command='active=%s';
        condition='ticket_num=%s'
        values=['H',myDict['ticket_num']]
    
        sql = "UPDATE " + table + " SET " + command + " WHERE " +condition
        print(sql)
        cur.execute(sql,values)
        self.conn.commit()
    
    def add_items_to_db(self,table, myDict):
        print(myDict)
        cur = self.conn.cursor()
        #print("Added Record...")
        placeholders = ', '.join(['%s'] * len(myDict))
        columns = ', '.join(myDict.keys())
        sql = "INSERT INTO %s ( %s ) VALUES ( %s )" % (table, columns, placeholders)
        #print(sql)
        cur.execute(sql, myDict.values())
        self.conn.commit()
    def get_all_pallets(self,mytask):
        cur = self.conn.cursor()
        sql="""   SELECT mypallets.ticket_num,
                                           mypallets.date_of_action,
                                           mypallets.farm,
                                           mypallets.barn,
                                           mypallets.case_weight,
                                           mypallets.dozen,
                                           mypallets.date_collected,
                                           mypallets.pallet_state,
                                           mypallets.region,
                                           mypallets.active
                          FROM pallets mypallets
                          INNER JOIN
                                    (SELECT ticket_num, MAX(date_of_action) AS MaxDateTime
                                     FROM pallets
                                     GROUP BY ticket_num) groupedpallets 
                          ON mypallets.ticket_num = groupedpallets.ticket_num 
                          AND mypallets.date_of_action = groupedpallets.MaxDateTime
                          GROUP BY mypallets.ticket_num"""
        #sql = 'SELECT ticket_num, max(date_of_action) date_of_action, farm, barn, case_weight, dozen, date_collected, pallet_state, region, active FROM pallets GROUP By date_of_action'
        cur.execute(sql)
        msg=list(cur.fetchall())
        #print(msg)
        header=('Ticket Number', 'Last Updated', 'Farm', 'Barn', 'Case Weight', 'Dozen', 'Date Coll', 'Status', 'Region', 'Active')
        mymsg=msg.insert(0,header)
        #print(mymsg)
        return msg
    def get_pallets_history(self,mytask):
        cur = self.conn.cursor()
        sql = 'SELECT ticket_num, date_of_action, farm, barn, case_weight, dozen, date_collected, pallet_state, region, active FROM pallets WHERE %s ORDER BY date_of_action'
        condition='ticket_num="'+mytask[2] + '"'
        sql=sql % (condition)
        #print(sql)
        cur.execute(sql)
        msg=list(cur.fetchall())
        #print(msg)
        header=('Ticket Number', 'Last Updated', 'Farm', 'Barn', 'Case Weight', 'Dozen', 'Date Coll', 'Status', 'Region', 'Active')
        mymsg=msg.insert(0,header)
        print(mymsg)
        return msg
    def get_pallet_edit(self,mytask):
        cur = self.conn.cursor()
        sql = 'SELECT ticket_num, max(date_of_action) date_of_action, farm, barn, case_weight, dozen, date_collected, pallet_state, region, active FROM pallets WHERE %s '
        condition='ticket_num="'+mytask[2] + '"'
        sql=sql % (condition)
        #print(sql)
        cur.execute(sql)
        msg=list(cur.fetchall())
        #print(msg)
        header=('Ticket Number', 'Last Updated', 'Farm', 'Barn', 'Case Weight', 'Dozen', 'Date Coll', 'Status', 'Region', 'Active')
        fields=['ticket_num', 'date_of_action', 'farm', 'barn', 'case_weight', 'dozen', 'date_collected', 'pallet_state', 'region', 'active']
        mymsg=msg.insert(0,fields)
        mymsg=msg.insert(0,header)
        #print(mymsg)
        return msg

        return msg
    def send_pallet_edit(self,mytask):
        cur = self.conn.cursor()
        myDict=mytask[2]
        myDict['date_of_action']=time.strftime('%Y-%m-%d %H:%M:%S')
        myDict['active']='A'
        
        table='pallets'
         #------------------------------------------First, archive all previous instances---------------------------------------
        command='active=%s';
        condition='ticket_num=%s'
        values=['H',myDict['ticket_num']]
        
        sql = "UPDATE " + table + " SET " + command + " WHERE " +condition
        print(sql)
        cur.execute(sql,values)
        self.conn.commit()
        
        #------------------------------------------Insert new record into database---------------------------------------
        placeholders = ', '.join(['%s'] * len(myDict))
        columns = ', '.join(myDict.keys())
        sql = "INSERT INTO %s ( %s ) VALUES ( %s )" % (table, columns, placeholders)
        
        #print(sql)
        #print(myDict.values())
        cur.execute(sql, myDict.values())
        self.conn.commit()
        
        
        #------------------------------------------Now get the most recent entry of all the tickets---------------------------------------

        sql="""   SELECT mypallets.ticket_num,
                                           mypallets.date_of_action,
                                           mypallets.farm,
                                           mypallets.barn,
                                           mypallets.case_weight,
                                           mypallets.dozen,
                                           mypallets.date_collected,
                                           mypallets.pallet_state,
                                           mypallets.region,
                                           mypallets.active
                          FROM pallets mypallets
                          INNER JOIN
                                    (SELECT ticket_num, MAX(date_of_action) AS MaxDateTime
                                     FROM pallets
                                     GROUP BY ticket_num) groupedpallets 
                          ON mypallets.ticket_num = groupedpallets.ticket_num 
                          AND mypallets.date_of_action = groupedpallets.MaxDateTime
                          GROUP BY mypallets.ticket_num"""
        cur.execute(sql)
        msg=list(cur.fetchall())
        header=('Ticket Number', 'Last Updated', 'Farm', 'Barn', 'Case Weight', 'Dozen', 'Date Coll', 'Status', 'Region', 'Active')
        mymsg=msg.insert(0,header)

        return msg
    
    def dosql(self,command):
        self.actions[command[0]]()
    def update(self):
        print("hey")
    def requesttable(self):
        print("hey")
    def send_sensor_data(self,mytask):
        cur = self.conn.cursor()
        table='sensor_data'
        myDict={}
        myDict['sensor_id']=mytask[2]
        myDict['value']=mytask[3]
        myDict['timestamp']=mytask[4]
               
        placeholders = ', '.join(['%s'] * len(myDict))
        columns = ', '.join(myDict.keys())
        sql = "INSERT INTO %s ( %s ) VALUES ( %s )" % (table, columns, placeholders)
        
        #print(sql)
        #print(myDict.values())
        cur.execute(sql, myDict.values())
        self.conn.commit()
        msg=''
        return msg
    def get_sensor_data(self,mytask):
        cur = self.conn.cursor()
        table='sensor_data'
        myDict={}
        myDict['sensor_id']=mytask[2]
        myDict['value']=mytask[3]
        myDict['timestamp']=mytask[4]
        sql = 'SELECT ticket_num, max(date_of_action) date_of_action, farm, barn, case_weight, dozen, date_collected, pallet_state, region, active FROM pallets WHERE %s '
        condition='timestamp>=%s and sensor_id=%s'
        sql=sql % (condition)
        sql=sql % (myDict['timestamp'],myDict['sensor_id'])
        #print(sql)
        cur.execute(sql)
        msg=list(cur.fetchall())
    def load_sensor_data_from_file(self,mytask):
       cur = self.conn.cursor()
       table='sensor_data'
       sensorid=mytask[2]
       #print('/var/lib/mysql-files/'+sensorid+'r.txt')
       try:
           
            os.remove('/var/lib/mysql-files/'+sensorid+'r.txt')
            #print('removed file ' + '/var/lib/mysql-files/'+sensorid+'r.txt')
       except:
            print("file not found")
       sql="""SELECT * INTO OUTFILE '/var/lib/mysql-files/%sr.txt'
                                  FIELDS TERMINATED BY ','
                                  FROM %s
                                  WHERE sensor_id="%s" AND
  	            timestamp>subdate(NOW(), 7) 
  	            Order By timestamp;"""
       sql=sql % (sensorid, table,  sensorid)
       #print(sql)
       cur.execute(sql)
       self.conn.commit()
       msg='File Read from DB'
       #print(list(cur.fetchall()))
       return msg
    def load_sensor_data_to_file(self,mytask):
       cur = self.conn.cursor()
       table='sensor_data'
       sensorid=mytask[2]
       sql=""" LOAD DATA INFILE '/var/lib/mysql-files/%sw.txt'
                                        REPLACE
                                        INTO TABLE %s
                                        COLUMNS
                                            TERMINATED BY ','            
                                        LINES
                                            TERMINATED BY '\n';"""
       sql=sql % (sensorid, table)
       #print(sql)
       cur.execute(sql)
       self.conn.commit()
       msg='File Written to DB'
       
       #print(msg)
       #print(list(cur.fetchall()))
       return msg
    def get_sensor_data_date_range(self,mytask):
       cur = self.conn.cursor()
       table='sensor_data'
       sensorid=mytask[2][0]
       mindate=mytask[2][1]
       maxdate=mytask[2][2]
       scale=mytask[2][3]
       timezone='+06:00'
       sql="""                           
SELECT *, sum(value) mysum, min(value) mymin, max(value) mymax, avg(value) mymean, CONVERT_TZ(FROM_UNIXTIME(FLOOR(UNIX_TIMESTAMP(`timestamp`)/(%s*60))*%s*60),'+0:00', '%s') timeslot
FROM `sensor_data` 
WHERE sensor_id="%s" and 
timestamp>="%s" and timestamp<="%s" 
Group By floor(timestampdiff(minute,"1900-01-01",timestamp)/%s)*%s       
        """
       sql=sql % (scale,scale,timezone,sensorid, mindate,maxdate,scale,scale)
       #print(sql)
       cur.execute(sql)
       msg=list(cur.fetchall())
       #print(msg)
       return msg

    
"""
        SELECT * FROM `sensor_data` WHERE timestamp>subdate(NOW(), 7) and sensor_id='wm1'
        SELECT * INTO OUTFILE '/var/lib/mysql-files/data.txt' FIELDS TERMINATED BY ',' FROM sensor_data WHERE sensor_id='wm1' AND timestamp>='2018-02-19' Order By timestamp
       
"""

#-----------------------------------------------------------------------------------------------------------

class dbserver(object):
    def __init__(self,address, authkey,credentials):
        self.address=address
        self.authkey=authkey
        self.credentials=credentials
        self.server_c=""
        
    def run(self):
        q=queue.Queue() #commands going in
        m=queue.Queue() #messages coming back
        condition = threading.Condition()
        #Start the database connection thread
        mydbconnection=dbc(self.credentials,q,m,condition)
        print("start a dbconnection")
        s = Thread(target=mydbconnection.run)
        
        s.daemon = True
        s.start()
        
        #start threads to listen for commands to send to the database  
        self.server_c = Listener(self.address, authkey=self.authkey)
        
        while True:
            
            client_c = self.server_c.accept()
            client_c.send("connected")
            sensorid=client_c.recv()
            print(sensorid)
            t = Thread(target=self.handle_client, args=(client_c,sensorid,q,m,condition),name="Sensor " + str(sensorid))
            print(t.name)
            t.daemon = True
            t.start()
            
    def handle_client(self,c,sensorid,q,m,cv):
        #print("client connected on port " + str(self.address))

        mynum=random.randint(0,100000)
        rtnmsg=''
        timeout=0
        msg=[[]]
        mymsg=[[0],[0]]
        discardpile=[]
        #print("sending confirmation")
        
        
        threading.current_thread().setName("Sensor "  +str(sensorid)+ "  " + str(mynum));
        msg = c.recv()
        connected=True
        if connected:            
                q.put([mynum]+msg[1:])
               
                found=False
                while not found:
                    #print(str(mynum) + " Num in q is:" + str(m.qsize()))
                    time.sleep(.01)
                    with cv:                        
                        cv.wait()                        
                        #print(str(mynum) + " is trying!")                                             
                        for i, j in enumerate(list(m.queue)):
                            temp=m.get()
                            if j[0]==mynum:
                                    found=True
                                    #print(str(mynum)+ " Found!")
                                    mymsg=temp
                            else:
                                m.put(temp)                        
                        cv.notifyAll()
                        
                c.send(mymsg[1:])                        
                c.close()
                #print(mymsg)
                #print(sensorid + " closed " +str(mynum))
                connected=False
               # print("client disconnected")


if __name__ == '__main__':
    rdbq = multiprocessing.Queue()#commands in
    rdbm = multiprocessing.Queue()#messages back

    ldbq = multiprocessing.Queue()#commands in
    ldbm = multiprocessing.Queue()#messages back

    rdbcredentials={}
    rdbcredentials['hostname'] = 'datasirin.a2hosted.com'
    rdbcredentials['username'] = 'datasiri_clarkfa'
    rdbcredentials['password'] = 'Fflm7~d52^v)'
    rdbcredentials['database'] = 'datasiri_wp802'

    ldbcredentials={}
    ldbcredentials['hostname'] = 'localhost'
    ldbcredentials['username'] = 'localprogram'
    ldbcredentials['password'] = 'mypassword'
    ldbcredentials['database'] = 'hbf'

    
    ldbc=dbserver(("",16001), b"peekaboo",ldbcredentials)
    rdbc=dbserver(("",16002), b"peekaboo",rdbcredentials)
    print("ldb")
    l = Thread(target=ldbc.run,name="Local DB to sensor thread")
    print(l.name)
    l.daemon = True
    l.start()
    
    print("rdb")
    r = Thread(target=rdbc.run,name="Remote DB to sensor thread")
    print(r.name)
    r.daemon = True
    r.start()
    #sched=BackgroundScheduler()
    #sched.start()
    #sched.add_job(monitor,'interval',seconds=60,id='system monitor',name='system monitor')
    while True:
        time.sleep(60)
        print("----------------------------")
        for thread in threading.enumerate(): print(thread.name)        
