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
cs = ContinuousClient("localhost", 50000)
cs.start()
while True:
    try:
        time.sleep(1)
    except KeyboardInterrupt:
        break


        

        

