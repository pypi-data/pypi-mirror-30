import pygame as pg
import serial
ser = serial.Serial('/dev/tty.usbmodem1411', 9600, timeout = 0)
serial_buffer = ''

# custom event type is an int based on USEREVENT.
GIGGLE = pg.USEREVENT + 1
SERIAL = pg.USEREVENT + 2
def send_giggle():
    e = pg.event.Event(GIGGLE, something='lalala', giggle=True)
    pg.event.post(e)


_, going = pg.init(), pg.display.set_mode((320,200))
pg.display.set_caption('g key to giggle')
while going:
    serial_data = ser.read()
    while serial_data:
        serial_buffer += serial_data
        if '\r\n' in serial_buffer:
            evt = pg.event.Event(SERIAL, line=serial_buffer)
            pg.event.post(evt)
            serial_buffer = ''
        serial_data = ser.read()

    for e in [pg.event.wait()] + pg.event.get():
        if e.type == pg.QUIT: going = False
        elif e.type == pg.KEYDOWN and e.key == pg.K_g: send_giggle()
        elif e.type == GIGGLE: print('Got a giggle! %s' % e)
        elif e.type == SERIAL: print('Line from serial: %s' % e)
