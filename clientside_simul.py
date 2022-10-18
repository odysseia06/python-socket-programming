from client import * 
'''
Server offline:
    Client -> trying to connect server constantly.
Server online:
    Client -> connects to server.
    try to see qr.
    if see qr, sends the qr info.
    When server says start, starts the robot. 
    When see redline, says saw the red line.
    move two seconds and stop, waits to photo to finish sending.
    When see qr again, stops.
'''
IDLE = 10
READY = 11
START = 12
RED_SEEN = 13
PHOTO_TAKING = 14
STOP = 15
event = None
event_simul_counter = 0
def qr_seen_event():
    global event, event_simul_counter
    event_simul_counter += 1
    if event_simul_counter > 1000:
        event = START
        event_simul_counter = 0


def red_seen_event():
    global event, event_simul_counter
    event_simul_counter += 1
    if event_simul_counter > 10000:
        event = RED_SEEN
        event_simul_counter = 0


def photo_take_event():
    global event, event_simul_counter
    event_simul_counter += 1
    if event_simul_counter > 10000:
        event = PHOTO_TAKING
        event_simul_counter = 0


def stop_event():
    global event, event_simul_counter
    event_simul_counter += 1
    if event_simul_counter > 10000:
        event = STOP
        event_simul_counter = 0

count = 0
while True:
    while not IS_CONNECTED.is_set():
        print("Not Connected.")
        cs = ContinuousClient("localhost", 50000)
        cs.connect()
        if cs.connected.is_set():
            print("Connected.")
            event = IDLE
            IS_CONNECTED.set()
            
    while IS_CONNECTED.is_set():
        
        if not cs.connected.is_set():
            IS_CONNECTED.clear()
            break
        cs.send(str(count))
        print(cs.reply_queue.get())
        count += 1


        

        

