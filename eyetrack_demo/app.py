#!/usr/bin/env python
from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit, disconnect
import socket
import threading
import json
import csv
import models
import psycopg2


# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = None

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

def background_thread():
    """Send server generated events to clients in background thread, includes EyeTribe data getting."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP, TCP_PORT))
    s.send(MESSAGE)

    count = 0
    while True:
      try:
          lst = []
          data = s.recv(BUFFER_SIZE)
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
      save_session_to_csv(START_TIME, end_time, EYETRACK_SESSION_DATA, object_coordinates)
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

  while True: ## loop until thread is killed ?
    try:
        lst = []
        data = s.recv(BUFFER_SIZE)
        lst.append(data)
        data_json = json.loads(lst.pop())
        avg_eye_coord =  data_json['values']['frame']
    except socket.error as e:
        s.close()
        print("Error getting Eyetribe data:", e)
        raise e
    
    EYETRACK_SESSION_DATA.append(avg_eye_coord)
    if START_TRACKING_FLAG == False:
      return EYETRACK_SESSION_DATA
  #start saving that stream of coordinates
  return EYETRACK_SESSION_DATA

#-------------------------------- Save relevant data to csv file --------------------------------
def save_session_to_csv(start_time, end_time, eyetrack_session_data, object_coordinates):
  # with open('sessions.csv', 'a') as f:
  #   fieldnames = ['start_time', 'end_time', 'eyetrack_session_data', 'object_coordinates']
  #   writer = csv.DictWriter(f, fieldnames=fieldnames)
  #   writer.writerow({
  #     'start_time': start_time,
  #     'end_time': end_time,
  #     'eyetrack_session_data': eyetrack_session_data,
  #     'object_coordinates': object_coordinates})

  session_data = {'start_time': str(start_time), 'end_time': str(end_time)}
  models.insert_session_data(session_data, eyetrack_session_data, object_coordinates)

  # models.insert_tracking_data(session_id, eyetrack_session_data, object_coordinates)

  return



@app.route('/')
def index():
  return render_template('index.html', async_mode=socketio.async_mode)


@socketio.on('my_event', namespace='/test')
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

