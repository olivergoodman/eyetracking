import psycopg2

#------------------------------Inserts the session data--------------------------------
def insert_session_data(session_data, eyetrack_data, object_data):
	try:
	  conn = psycopg2.connect("dbname='eyetrack_session' user='olivergoodman' host='localhost' password='dbpass'")
	  print "Connected to db"
	  curr = conn.cursor()
	except:
	  print "I am unable to connect to the database"
	  return

	try:
		# insert last session into session table
		curr.execute(
			""" INSERT INTO session (start_time, end_time) 
			VALUES (%(start_time)s, %(end_time)s);
			SELECT currval('session_id_seq');""",
					session_data)
		# get last session id
		session_id = int(curr.fetchone()[0])

		# insert eyetrack data into eyetrack table
		for eye_coord in eyetrack_data:
			eye_data = {
						'session_id': session_id, 
						'x': int(eye_coord['avg']['x']), 
						'y': int(eye_coord['avg']['y']),
						'timestamp': eye_coord['timestamp'],
						'time': eye_coord['time']}
			curr.execute(
				""" INSERT INTO eyetrack (session_id, x, y, timestamp, time) 
				VALUES (%(session_id)s, %(x)s, %(y)s, %(timestamp)s, %(time)s);""",
						eye_data)

		# insert object data into moving_object table 
		for obj_coord in object_data:
 			obj_data = {
 						'session_id': session_id,
 						'x': obj_coord['coordinates']['left'], 
 						'y': obj_coord['coordinates']['top'],
 						'timestamp': obj_coord['timestamp']}
			curr.execute(
				""" INSERT INTO moving_object (session_id, x, y, timestamp) 
				VALUES (%(session_id)s, %(x)s, %(y)s, %(timestamp)s);""",
						obj_data)

		# commit + close transaction
		conn.commit()
		conn.close()

	except psycopg2.DatabaseError as error:
		conn.rollback()
		print error

	finally:
		if conn is not None:
			conn.close()
	return

#------------------------------Fetches most recent session data--------------------------------
def get_last_session():
	eyetribe_data = []
	moving_object_data = []
	try:
	  conn = psycopg2.connect("dbname='eyetrack_session' user='olivergoodman' host='localhost' password='dbpass'")
	  print "Connected to db"
	  curr = conn.cursor()
	except:
	  print "I am unable to connect to the database"
	  return

	try:	
		# get eyetribe data from last session
		curr.execute(""" SELECT * FROM eyetrack WHERE session_id = (SELECT MAX(session_id) FROM eyetrack) """)
		eyetribe_data = curr.fetchall()

		# get object data from last session
		curr.execute(""" SELECT * FROM moving_object WHERE session_id = (SELECT MAX(session_id) FROM moving_object) """)
		moving_object_data = curr.fetchall()

	except psycopg2.DatabaseError as error:
	 	conn.rollback()
	 	print error	 	

	finally:
		if conn is not None:
			conn.close()
	
	return {'eyetribe_data' : eyetribe_data, 'moving_object_data': moving_object_data}