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
			""" INSERT INTO session (start_time, end_time) VALUES (%(start_time)s, %(end_time)s);
					SELECT currval('session_id_seq');""",
					session_data)

		# get last session id
		rows = curr.fetchall()
		session_id = int(rows[0][0])
		
		print 'here1'

		# insert eyetrack data into eyetrack table
		for eye_coord in eyetrack_data:
			eye_data = {'session_id': session_id, 'x': eye_coord['avg']['x'], 'y': eye_coord['avg']['y']} #implement
			curr.execute(
				""" INSERT INTO eyetrack (session_id, x, y) VALUES (%(session_id)s, %(x)s, %(y)s);""",
						eye_data)

		print 'here2'

		# insert object data into moving_object table 
		for obj_coord in object_data:
 			eye_data = {'session_id': session_id, 'x': object_data['left'], 'y': eye_coord['top']} # implement
			curr.execute(
				""" INSERT INTO moving_object (session_id, x, y) VALUES (%(session_id)s, %(x)s, %(y)s);""",
						obj_data)


		# commit transaction
		conn.commit()

	except:
		print 'something went wrong...'
	
	return


#------------------------------Inserts the eyetracking and moving object data--------------------------------
# def insert_tracking_data(session_id, eyetrack_data, object_data):
# 	try:
# 	  conn = psycopg2.connect("dbname='eyetrack_session' user='olivergoodman' host='localhost' password='dbpass'")
# 	  print "Connected to db"
# 	  curr = conn.cursor()
# 	except:
# 	  print "I am unable to connect to the database"
# 	  return
# 	# need separate functions for eye data and object data, executemany for each object in eyedata/objectdata
# 	try:
# 		eyetrack = {'session_id': session_id, 'x': eyetrack_data[0]['avg']['x'], 'y': eyetrack_data[0]['avg']['y']}
# 		obj_data = {'session_id': session_id, 'x': object_data[0]['left'], 'y': object_data[0]['top']}

# 		for row in eyetrack_data:
# 			curr.execute(
# 				""" INSERT INTO eyetrack (session_id, x, y) 
# 						VALUES (%(session_id)s, %(x)s, %(y)s);""",
# 						{'session_id': session_id, 'x': row['avg']['x'], 'y': row['avg']['y']})

# 		for row in object_data:
# 			curr.execute(
# 				""" INSERT INTO moving_object (x, y) 
# 						VALUES (%(session_id)s, %(x)s, %(y)s);""",
# 						{'session_id': session_id, 'x': row['left'], 'y': row['top']})

# 		print 'succesful insert! wow!'
# 	except:
# 		print 'something went wrong...'
# 	return



# # def insert_object_data(session_id, object_data):
# # 	try:
# # 	  conn = psycopg2.connect("dbname='eyetrack_session' user='olivergoodman' host='localhost' password='dbpass'")
# # 	  print "Connected to db"
# # 	  curr = conn.cursor()
# # 	except:
# # 	  print "I am unable to connect to the database"
# # 	  return

# # 	try:
# # 		object_data = {'session_id': session_id, 'x': object_coordinates[0]['left'], 'y': object_coordinates[0]['top']}
# # 		curr.execute(
# # 			""" INSERT INTO moving_object (start_time, end_time) 
# # 					VALUES (%(session_id)s, %(start_time)s, %(end_time)s);""",
# # 					object_data)
# # 		conn.commit()
# # 		print 'successful insert'
# # 	except:
# # 		print 'something went wrong..'
# # 	return
