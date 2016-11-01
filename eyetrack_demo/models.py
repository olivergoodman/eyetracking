import psycopg2

#------------------------------Inserts the session data--------------------------------
def insert_session_data(session_data):
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
					VALUES (%(start_time)s, %(end_time)s);""",
					session_data)
		
		# get session_id from session, to be referenced in eyetrack/moving_object tables -- need to get actual max, not last one
		curr.execute(""" SELECT MAX(id) FROM session """)
		rows = curr.fetchall()
		session_id = int(rows[0][0])
		

		# insert eyetrack data
		

		# insert 



		# commit transaction
		conn.commit()
		return session_id

	except:
		print 'something went wrong...'
	
	return


#------------------------------Inserts the eyetracking and moving object data--------------------------------
def insert_tracking_data(session_id, eyetrack_data, object_data):
	try:
	  conn = psycopg2.connect("dbname='eyetrack_session' user='olivergoodman' host='localhost' password='dbpass'")
	  print "Connected to db"
	  curr = conn.cursor()
	except:
	  print "I am unable to connect to the database"
	  return
	# need separate functions for eye data and object data, executemany for each object in eyedata/objectdata
	try:
		eyetrack = {'session_id': session_id, 'x': eyetrack_data[0]['avg']['x'], 'y': eyetrack_data[0]['avg']['y']}
		obj_data = {'session_id': session_id, 'x': object_data[0]['left'], 'y': object_data[0]['top']}

		for row in eyetrack_data:
			curr.execute(
				""" INSERT INTO eyetrack (session_id, x, y) 
						VALUES (%(session_id)s, %(x)s, %(y)s);""",
						{'session_id': session_id, 'x': row['avg']['x'], 'y': row['avg']['y']})

		for row in object_data:
			curr.execute(
				""" INSERT INTO moving_object (x, y) 
						VALUES (%(session_id)s, %(x)s, %(y)s);""",
						{'session_id': session_id, 'x': row['left'], 'y': row['top']})

		print 'succesful insert! wow!'
	except:
		print 'something went wrong...'
	return



# def insert_object_data(session_id, object_data):
# 	try:
# 	  conn = psycopg2.connect("dbname='eyetrack_session' user='olivergoodman' host='localhost' password='dbpass'")
# 	  print "Connected to db"
# 	  curr = conn.cursor()
# 	except:
# 	  print "I am unable to connect to the database"
# 	  return

# 	try:
# 		object_data = {'session_id': session_id, 'x': object_coordinates[0]['left'], 'y': object_coordinates[0]['top']}
# 		curr.execute(
# 			""" INSERT INTO moving_object (start_time, end_time) 
# 					VALUES (%(session_id)s, %(start_time)s, %(end_time)s);""",
# 					object_data)
# 		conn.commit()
# 		print 'successful insert'
# 	except:
# 		print 'something went wrong..'
# 	return
