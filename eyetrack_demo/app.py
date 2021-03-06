#!/usr/bin/env python
from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit, disconnect
import socket
import threading
import json
import models
import time
import pickle


# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = "gevent"

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None

TCP_IP = '127.0.0.1'
TCP_PORT = 6555 #EyeTribe port
BUFFER_SIZE = 1024
MESSAGE = "Hello, World!"

START_TRACKING_FLAG = False
EYETRACK_SESSION_DATA = []
START_TIME = 0
RUN_PLAYBACK_FLAG = False


#-------------------------------- Get FrontEnd info -------------------------------
@app.route('/_get_eyetrack_data', methods = ['GET', 'POST'])
def _get_eyetrack_data():
  global START_TRACKING_FLAG
  global EYETRACK_SESSION_DATA
  global START_TIME

  if request.method == 'POST':
    start_tracking_flag = request.json['record_eye_data']
    time = request.json['time']

    if start_tracking_flag == True: #and key doesn't contain object_coordinates
      START_TRACKING_FLAG = True
      START_TIME = time
      EYETRACK_SESSION_DATA = get_eyetrack_session_data()

    else: # and if key contains 'object_coordinates'
      START_TRACKING_FLAG = False
      object_coordinates = request.json['object_coordinates']
      end_time = time
      save_session(START_TIME, end_time, EYETRACK_SESSION_DATA, object_coordinates)
      EYETRACK_SESSION_DATA = [] # reset session data
      START_TIME = 0 # reset start time

  return str(request.form)

#-------------------------------- Get the eyetrack data from one session --------------------------------
def get_eyetrack_session_data():
  global START_TRACKING_FLAG
  global EYETRACK_SESSION_DATA

  #if existing thread exists, kill it
  # make eyetribe connection
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.connect((TCP_IP, TCP_PORT))
  s.send(MESSAGE)

  while True: ## loop until thread is killed
    try:
      decoder = json.JSONDecoder()
      data = s.recv(BUFFER_SIZE)
      obj, idx = decoder.raw_decode(data)
    except socket.error as e:
      s.close()
      print("Error getting Eyetribe data:", e)
      raise e
    
    EYETRACK_SESSION_DATA.append(obj)
    if START_TRACKING_FLAG == False:
      s.close()
      return EYETRACK_SESSION_DATA

  #start saving that stream of coordinates
  return EYETRACK_SESSION_DATA

#-------------------------------- Save relevant data to db --------------------------------
def save_session(start_time, end_time, eyetrack_session_data, object_coordinates):
  json_eye_data_list = []
  try:
    for eye_data in eyetrack_session_data:
      avg_eye_coord = eye_data['values']['frame']
      json_eye_data_list.append(avg_eye_coord)

    session_data = {'start_time': str(start_time), 'end_time': str(end_time)}
    models.insert_session_data(session_data, json_eye_data_list, object_coordinates)

  except ValueError as e:
    print "\t ***** ERROR: *****\n", e.message
  
  return

#-------------------------------- Basic background thread to display live eyetribe coordinates -------------------------------
def background_thread():
  """Send server generated events to clients in background thread, includes EyeTribe data getting."""
  global RUN_PLAYBACK_FLAG

  if RUN_PLAYBACK_FLAG == True:
    f = open('output.txt', 'w')
    f.write('\n thread start time:' + str(int(round(time.time() * 1000))))

    print 'inside playback thread'
    data = models.get_last_session()
    eyetribe_data = data['eyetribe_data']
    eyetribe_data = eyetribe_data[1:] # trim first gaze coordinate, it's always way earlier than rest
    moving_object_data = data['moving_object_data']

    # dicts in memory to map timestamps to coordinates
    gaze_coords = {}
    moving_object_coords = {}

    # initial and final timestamps for both gaze and object
    gaze_time_0 = eyetribe_data[0][5]
    obj_time_0 = moving_object_data[0][4]
    initial_time = min(gaze_time_0, obj_time_0)
    gaze_time_f = eyetribe_data[-1][5]
    obj_time_f = moving_object_data[-1][4]
    end_time = max(gaze_time_f, obj_time_f) # want our lists to have length equal to longest session
    total_time = end_time - initial_time

    ## ~~~~ DICTIONARY IN MEMORY ~~~~ #
    # # fill up coordinate dictionaries
    # for e in eyetribe_data:
    #   x = e[2] #x val for single eye coord
    #   y = e[3] #y val for single eye coord
    #   t = int(e[5] - gaze_time_0) #the timestamp for a single coordinate
    #   gaze_coords[t] = (x, y)
    # for m in moving_object_data:
    #   x = m[2] #x val for single eye coord
    #   y = m[3] #y val for single eye coord
    #   t = int(m[4] - obj_time_0) #the timestamp for a single coordinate
    #   moving_object_coords[t] = (x, y)

    ## ~~~~ LISTS IN MEMORY ~~~~ #
    # lists in memory to match coords with playback time
    gaze_list = [None]*int(total_time)
    moving_object_list = [None]*int(total_time)

    # fill up coordinate lists
    for e in eyetribe_data:
      x = e[2] #x val for single eye coord
      y = e[3] #y val for single eye coord
      t = int(e[5] - initial_time) #the normalized timestamp for a single coordinate
      if (t != len(gaze_list)):
        gaze_list[t] = (x, y)
    for m in moving_object_data:
      x = m[2] #x val for single eye coord
      y = m[3] #y val for single eye coord
      t = int(m[4] - initial_time) #the normalized timestamp for a single coordinate
      if (t != len(moving_object_list)):
        moving_object_list[t] = (x, y)

    start_time = int(round(time.time() * 1000))
    count = 0
    # playback_times = []
    while True:
      system_time_now = int(round(time.time() * 1000))
      playback_now = system_time_now - start_time 
      # playback_times.append(playback_now)

      if playback_now >= total_time:
        break
      eyetribe_coord = gaze_list[playback_now]
      object_coord = moving_object_list[playback_now]
      # print eyetribe_coord
      # print object_coord

      if eyetribe_coord is None or object_coord is None:
        if eyetribe_coord is not None:
          socketio.emit('my_response',
                        {'data': {'eyetribe_coord': eyetribe_coord, 'object_coord': None}, 'count': count},
                        namespace='/test')
        elif object_coord is not None:
          socketio.emit('my_response',
                       {'data': {'eyetribe_coord': None, 'object_coord': object_coord}, 'count': count},
                       namespace='/test')
      else:
        socketio.emit('my_response',
                     {'data': {'eyetribe_coord': eyetribe_coord, 'object_coord': object_coord}, 'count': count},
                     namespace='/test')       
      count += 1

      # f.write('\n' + str(count) + 'time in loop:' + str(int(round(time.time() * 1000)) -  playback_now))

    # data = {'playback_times': playback_times, 'eyetrack_data': eyetribe_data, 'moving_object_data': moving_object_data, 'gaze_list': gaze_list, 'moving_object_list': moving_object_list}
    # pickle.dump(data, open('playback', 'w'))
    # print "final count", count
    f.write('\n thread end time:' + str(int(round(time.time() * 1000))))
    f.close()
    

  else:
    print 'shouldnt be in here'
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP, TCP_PORT))
    s.send(MESSAGE)

    count = 0
    while True:
      try:
          lst = []
          data = s.recv(BUFFER_SIZE)
          data.replace('\n', '')
          lst.append(data)
          data_json = json.loads(lst.pop())
          eye_coord =  data_json['values']['frame']
      except socket.error as e:
          s.close()
          print("Error getting Eyetribe data:", e)
          raise e
      count += 1
      socketio.emit('my_response',
                    {'data': eye_coord, 'count': count},
                    namespace='/test')


#-------------------------------- Get playback flag to determine which background thread to use -------------------------------
@app.route('/_get_playback_flag', methods = ['GET', 'POST'])
def _get_playback_flag():
  global RUN_PLAYBACK_FLAG
  if request.method == 'POST':
    RUN_PLAYBACK_FLAG = request.json['run_playback']
  return str(request.form)

@app.route('/')
def index():
  return render_template('index.html', async_mode=socketio.async_mode)


@socketio.on('connect_playback', namespace='/test')
def test_message(message):
  session['receive_count'] = session.get('receive_count', 0) + 1
  emit('my_response',
       {'data': message['data'], 'count': session['receive_count']})


@socketio.on('my_broadcast_event', namespace='/test')
def test_broadcast_message(message):
  session['receive_count'] = session.get('receive_count', 0) + 1
  emit('my_response',
       {'data': message['data'], 'count': session['receive_count']},
       broadcast=True)


@socketio.on('disconnect_request', namespace='/test')
def disconnect_request():
  session['receive_count'] = session.get('receive_count', 0) + 1
  emit('my_response',
       {'data': 'Disconnected!', 'count': session['receive_count']})
  disconnect()


@socketio.on('my_ping', namespace='/test')
def ping_pong():
  emit('my_pong')


@socketio.on('connect', namespace='/test')
def test_connect():
  global thread
  if thread is None:
      thread = socketio.start_background_task(target=background_thread)
  emit('my_response', {'data': 'Connected', 'count': 0})


@socketio.on('disconnect', namespace='/test')
def test_disconnect():
  print('Client disconnected', request.sid)


if __name__ == '__main__':
  socketio.run(app, debug=True)
