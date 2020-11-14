#!/usr/bin/env python
from PyQt5.QtCore import QSize, QRect, Qt
from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QApplication, QDial, QDialog, QGridLayout,
                             QGroupBox, QHBoxLayout, QLabel, QPushButton,
                             QStyleFactory, QVBoxLayout, QListWidget, QComboBox
                             , QCheckBox)


import alsaaudio
from application.util.net_util import Network_util as network
import sys
import vlc
from vlc import VLCException


class WidgetGallery(QDialog):

    def __init__(self, parent=None):
        super(WidgetGallery, self).__init__(parent)

        self.init_mediaplayer()

        self.originalPalette = QApplication.palette()

        styleComboBox = QComboBox()
        styleComboBox.addItems(QStyleFactory.keys())

        styleLabel = QLabel("&Style:")
        styleLabel.setBuddy(styleComboBox)

        disableWidgetsCheckBox = QCheckBox("&Inactive Buttons")

        self.createTopLeftGroupBox()
        self.createTopRightGroupBox()

        styleComboBox.activated[str].connect(self.changeStyle)
        disableWidgetsCheckBox.toggled.connect(self.topLeftGroupBox.setDisabled)
        disableWidgetsCheckBox.toggled.connect(self.topRightGroupBox.setDisabled)

        topLayout = QHBoxLayout()
        topLayout.addWidget(styleLabel)
        topLayout.addWidget(styleComboBox)
        topLayout.addStretch(1)
        topLayout.addWidget(disableWidgetsCheckBox)

        mainLayout = QGridLayout()
        mainLayout.addLayout(topLayout, 0, 0, 1, 2)
        mainLayout.addWidget(self.topLeftGroupBox, 1, 0)
        mainLayout.addWidget(self.topRightGroupBox, 1, 1)
        mainLayout.setRowStretch(5, 5)
        mainLayout.setRowStretch(2, 1)
        mainLayout.setColumnStretch(0, 1)
        mainLayout.setColumnStretch(1, 1)
        self.setLayout(mainLayout)
        self.setWindowTitle("Radios Angola")
        self.changeStyle('windows')

    def init_mediaplayer(self):

        self.instance = vlc.Instance('--quiet --audio-visual visualizer --effect-list spectrum')
        self.media = None
        # Create an empty vlc media player
        self.mediaplayer = self.instance.media_player_new()
        self.mediaplayer.video_set_aspect_ratio("16:5")
        self.mediaplayer.video_set_scale(0.25)
        self.alsa = alsaaudio.Mixer(alsaaudio.mixers()[0])
        self.is_paused = False

    def getStatus(self):

        status = {
                  "stream length": self.mediaplayer.get_length(),
                  "current time": self.mediaplayer.get_time(),
                  "volume media player": self.mediaplayer.audio_get_volume(),
                  "volume ": self.alsa.getvolume()[0],
                  "state": self.mediaplayer.get_state()
                          }
        return status

    def changeStyle(self, styleName):
        QApplication.setStyle(QStyleFactory.create(styleName))

    def select_radio(self, qmodelindex):

        self.stop_stream()
        self.station_name = self.radio_stations_list.currentItem()

        if self.station_name is None:
            self.video_frame.setText("reloading ... ")
        else:
            self.radio_obj = network.get_station_obj(self.radio_json)
            self.selected = [radio for radio in self.radio_obj if
                             radio.r_name == self.station_name.text()]
            self.load_station(self.selected[0])

    def set_volume(self, volume):
        self.alsa.setvolume(volume)

    def refresh_stream(self):
        self.video_frame.setText("reloading ... ")
        self.stop_stream()
        self.play_pause()

    def previous_station(self, qmodelindex):
        self.stop_stream()
        try:
            curr_position = self.radio_stations_list.indexFromItem(self.station_name).row()
            previous_pos = curr_position - 1

            if previous_pos < 0:
                previous_station = self.radio_stations_list.item(len(self.radio_obj)-1)
                self.radio_stations_list.setCurrentItem(previous_station)
                self.select_radio(qmodelindex)
            else:
                previous_station = self.radio_stations_list.item(previous_pos)
                self.radio_stations_list.setCurrentItem(previous_station)
                self.select_radio(qmodelindex)
        except AttributeError:
            self.video_frame.setText("select a radio station")
            pass

    def next_station(self, qmodelindex):
        self.stop_stream()
        try:
            curr_position = self.radio_stations_list.indexFromItem(self.station_name).row()
            next_pos = curr_position + 1

            if (next_pos > len(self.radio_obj) - 1):
                next_station = self.radio_stations_list.item(0)
                self.radio_stations_list.setCurrentItem(next_station)
                self.select_radio(qmodelindex)

            else:
                next_station = self.radio_stations_list.item(next_pos)
                self.radio_stations_list.setCurrentItem(next_station)
                self.select_radio(qmodelindex)
        except AttributeError:
            self.video_frame.setText("select a radio station")
            pass

    def stop_stream(self):

        self.reset_video_frame()
        self.mediaplayer.stop()
        self.b_play.setIcon(QIcon('application/img/play.png'))
        self.is_paused = False

    def load_station(self, radio_station):
        self.video_frame.setText("loading ... ")
        try:
            self.media = self.instance.media_new(radio_station.stream_link)
            self.mediaplayer.set_media(self.media)
            self.media.parse()
            # for Linux using the X Server
            if sys.platform.startswith('linux'):
                self.mediaplayer.set_xwindow(self.video_frame.winId())

            # for Windows
            elif sys.platform == "win32":
                self.mediaplayer.set_hwnd(self.video_frame.winId())

            # for MacOS(
            elif sys.platform == "darwin":
                self.mediaplayer.set_nsobject(int(self.video_frame.winId()))

            self.play_pause()

        except VLCException as err:
            raise err

    def play_pause(self):

        if self.mediaplayer.is_playing():
            self.stop_stream()
            self.b_play.setIcon(QIcon('application/img/play.png'))
            self.is_paused = True
        else:
            if self.mediaplayer.play() == -1:
                self.video_frame.setText("select a radio station")
                self.video_frame.setAlignment(Qt.AlignCenter)
                return

            self.mediaplayer.play()
            self.b_play.setIcon(QIcon('application/img/pause.png'))
            self.is_paused = False
            self.video_frame.setText("")

    def createTopLeftGroupBox(self):

        self.topLeftGroupBox = QGroupBox("")

        self.video_frame = QLabel()
        self.reset_video_frame()

        self.b_refresh = QPushButton()
        self.b_refresh.setIcon(QIcon("application/img/refresh.png"))
        self.b_refresh.setIconSize(QSize(30, 30))
        self.b_refresh.setGeometry(QRect(30, 10, 10, 30))
        self.b_refresh.setToolTip("Refresh stream")
        self.b_refresh.clicked.connect(self.refresh_stream)

        self.b_previous = QPushButton()
        self.b_previous.setIcon(QIcon("application/img/back.png"))
        self.b_previous.setIconSize(QSize(30, 30))
        self.b_previous.setGeometry(QRect(30, 10, 10, 30))
        self.b_previous.setToolTip("Previous Radio Station")
        self.b_previous.clicked.connect(self.previous_station)

        self.b_play = QPushButton()
        self.b_play.setIcon(QIcon("application/img/play.png"))
        self.b_play.setIconSize(QSize(30, 30))
        self.b_play.setGeometry(QRect(30, 30, 30, 30))
        self.b_play.clicked.connect(self.play_pause)

        self.b_next = QPushButton()
        self.b_next.setIcon(QIcon("application/img/next.png"))
        self.b_next.setIconSize(QSize(30, 30))
        self.b_next.setGeometry(QRect(30, 30, 30, 30))
        self.b_next.setToolTip("Next Radio Station")
        self.b_next.clicked.connect(self.next_station)

        self.b_stop = QPushButton()
        self.b_stop.setIcon(QIcon("application/img/stop.png"))
        self.b_stop.setIconSize(QSize(30, 30))
        self.b_stop.setGeometry(QRect(30, 30, 30, 3))
        self.b_stop.setToolTip("Stop Streaming")
        self.b_stop.clicked.connect(self.stop_stream)

        layoutbuttons = QHBoxLayout()
        layoutbuttons.addWidget(self.b_refresh)
        layoutbuttons.addWidget(self.b_previous)
        layoutbuttons.addWidget(self.b_play)
        layoutbuttons.addWidget(self.b_next)
        layoutbuttons.addWidget(self.b_stop)

        self.dial_volume = QDial()
        #self.dial_volume.setMaximum(100)
        #self.dial_volume.setValue(self.mediaplayer.audio_get_volume())
        self.dial_volume.setValue(self.alsa.getvolume()[0])
        self.dial_volume.setNotchesVisible(True)
        self.dial_volume.setToolTip("Volume")
        self.dial_volume.valueChanged.connect(self.set_volume)

        layoutbuttons.addWidget(self.dial_volume)

        layout = QVBoxLayout()
        layout.addWidget(self.video_frame)
        layout.addLayout(layoutbuttons)
        self.topLeftGroupBox.setLayout(layout)

    def createTopRightGroupBox(self):

        self.topRightGroupBox = QGroupBox("radio stations")
        self.radio_json = network.get_stations_from_api()
        if self.radio_json is not None:
            self.station_names = network.get_station_names(self.radio_json)
            self.radio_stations_list = QListWidget()
            self.radio_stations_list.insertItems(0, self.station_names)
            self.radio_stations_list.clicked.connect(self.select_radio)
        else:
            self.radio_stations_list = QListWidget()
            self.radio_stations_list.insertItems(0, ["Server Down .... no radio stations"])

        layout = QVBoxLayout()
        layout.addWidget(self.radio_stations_list)

        self.topRightGroupBox.setLayout(layout)

    def reset_video_frame(self):
        self.video_frame.setStyleSheet("background-color: black")
        self.video_frame.setAutoFillBackground(True)


StyleSheet = '''
QDialog{
background:#333;
color:red;
}
QPushButton:hover{
background:#999
}
QDial:hover{
color:blue;
background:#999;
}
QListWidget:selected{
color:blue;
background:#999;
}
QGroupBox{
color:white;
}
QCheckBox{
color:white;
}
QLabel{
color:white;
}
QListWidget{
color:white;
background:gray;
}
QListView {
    show-decoration-selected: 1; /* make the selection span the entire width of the view */
}

QListView::item:alternate {
    background: #EEEEEE;
}

QListView::item:selected {
    border: 1px solid #6a6ea9;
}
QListView::item:selected:!active {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #ABAFE5, stop: 1 #8588B2);
}
QListView::item:selected:active {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #6a6ea9, stop: 1 #888dd9);
}
QListView::item:hover {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #FAFBFE, stop: 1 #DCDEF1);
}
'''
if __name__ == '__main__':
    #appctxt = ApplicationContext()
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(StyleSheet)

    gallery = WidgetGallery()
    gallery.setFixedHeight(300)
    gallery.setFixedWidth(800)

    gallery.show()
    sys.exit(app.exec_())
