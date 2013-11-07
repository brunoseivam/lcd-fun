#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from PyQt4 import QtGui, QtCore
import serial
import collections

pix = 10
margin = 10
pixSpace = 1
charSpace = 3
blackSS = "QWidget { background-color: Black; border-color: Black; border-style: solid; border-width: 1px; }"
graySS  = "QWidget { background-color: Gray;  border-color: Black; border-style: solid; border-width: 1px; }"
whiteSS = "QWidget { background-color: White; border-color: Black; border-style: solid; border-width: 1px; }"

Pos = collections.namedtuple('Pos', ['col', 'row'])
Char = collections.namedtuple('Char', ['pos', 'pixels'])
Pixel = collections.namedtuple('Pixel', ['pos','parent'])

ser = None;
class Canvas(QtGui.QWidget):

    def __init__(self):
        super(Canvas, self).__init__()
        self.pressed = False
        self.initUI()

    def initUI(self):
        self.setWindowTitle("LCD Draw!")
        self.chars = []

        for char_row in range(2):
            for char_col in range(16):
                char = Char(pos=Pos(row=char_row,col=char_col),pixels=[[0 for i in range(5)] for i in range(8)])
                self.chars.append(char)
                for pixel_row in range(8):
                    for pixel_col in range(5):
                        frame = QtGui.QFrame(self)
                        frame.setStyleSheet(whiteSS)
                        frame.setGeometry(pix,pix,pix,pix)
                        frame.setMouseTracking(True)

                        x = margin + (char_col)*charSpace + ((char_col*5)+pixel_col)*(pixSpace+pix)
                        y = margin + (char_row)*charSpace + ((char_row*8)+pixel_row)*(pixSpace+pix)

                        frame.move(x, y);

                        frame.info = Pixel(pos=Pos(row=pixel_row,col=pixel_col),parent=char)

        self.show()

    def mouseMoveEvent(self, event):
        if(self.pressed):
            target = QtGui.qApp.widgetAt(QtGui.QCursor().pos())
            if hasattr(target, "info"):
                pixel_row = target.info.pos.row
                pixel_col = target.info.pos.col

                paintColor = None
                paintSS = None
                if event.buttons() == QtCore.Qt.LeftButton:
                    paintColor = 1
                    paintSS = blackSS
                elif event.buttons() == QtCore.Qt.RightButton:
                    paintColor = 0
                    paintSS = whiteSS
                else:
                    return

                if target.info.parent.pixels[pixel_row][pixel_col] != paintColor:
                    target.info.parent.pixels[pixel_row][pixel_col] = paintColor
                    target.setStyleSheet(paintSS)
                    self.packetFromChar(target.info.parent)

    def mousePressEvent(self, event):
        self.pressed = True

    def mouseReleaseEvent(self, event):
        self.pressed = False

    def packetFromChar(self, char):
        print char

        rows = []
        for pix_row in range(8):
            row = 0
            for pix_col in range(5):
                row = (row << 1) | char.pixels[pix_row][pix_col]
            rows.append(row)

        packet = [0]*6

        packet[0] = ((char.pos.col << 4) | (char.pos.row << 3) | (rows[0] >> 2)) & 0xFF
        packet[1] = ((rows[0] << 6) | (rows[1] << 1) | (rows[2] >> 4)) & 0xFF
        packet[2] = ((rows[2] << 4) | (rows[3] >> 1)) & 0xFF
        packet[3] = ((rows[3] << 7) | (rows[4] << 2) | (rows[5] >> 3)) & 0xFF
        packet[4] = ((rows[5] << 5) | rows[6]) & 0xFF
        packet[5] = (rows[7] << 3) & 0xFF

        ser.write("".join(map(chr, packet)))

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "Usage: %s SERIAL_PORT" % sys.argv[0]
        sys.exit()
    ser = serial.Serial(sys.argv[1], 115200);
    app = QtGui.QApplication(sys.argv)
    ex = Canvas()
    sys.exit(app.exec_())
