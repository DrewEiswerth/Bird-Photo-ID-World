import tensorflow as tf
import csv
import sys
import mysql.connector

from tensorflow import keras
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QFont, QPixmap, QColor
from PyQt5.QtWidgets import QFileDialog, QApplication, QMainWindow, QFrame, QLabel, QPushButton, QWidget
from PyQt5.QtChart import QChart, QChartView, QPieSeries, QPieSlice
from mysql.connector import pooling


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.current_index = -1           # will hold database index of the current identification
        # self.datasource = datasource
        self.current_file_path = ""       # will save path to selected image on user's machine, needed for CNN analysis
        self.bird_id_model = keras.models.load_model("bird_id_cnn")
        self.bird_dict = {}

        with open("bird_data/bird_dict.csv") as species_table:
            species_data = csv.reader(species_table)

            # assigns CNN model's training index for each category to it's corresponding species String in bird_dict
            for species in species_data:
                self.bird_dict[int(species[0])] = species[1]

        frame_rect = QRect(0, 0, 1011, 1032)                                     # makes a rectangle the same size as MainWindow
        screen_center = QtWidgets.QDesktopWidget().availableGeometry().center()  # finds center point of active screen
        frame_rect.moveCenter(screen_center)                                     # centers that rectangle on screen
        centered_rect = frame_rect

        if centered_rect.y() < 40:                                               # ensures rectangle is low enough on screen
            centered_rect.setY(40)

        self.setGeometry(centered_rect.x(), centered_rect.y(), 1011, 1032)       # places MainWindow in approx. center of screen

        self.setWindowTitle("Bird Photo ID: World")
        self.setMinimumSize(QtCore.QSize(1011, 1032))
        self.setMaximumSize(QtCore.QSize(1011, 1032))
        self.setObjectName("MainWindow")

        self.central_widget = QWidget(self)
        self.central_widget.setAutoFillBackground(False)
        self.central_widget.setStyleSheet("background-color: rgb(247, 247, 239);")

        self.setCentralWidget(self.central_widget)

        self.logo_label_1 = QLabel(self.central_widget)
        self.logo_label_1.setGeometry(QRect(890, -2, 101, 51))
        self.logo_label_1.setFont(QFont("Calibri", weight=75, pointSize=11))
        self.logo_label_1.setText("Bird Photo ID")
        self.logo_label_1.setStyleSheet("background-color: transparent;\n"
                                        "color: rgb(95, 95, 94);")
        self.logo_label_1.setAlignment(Qt.AlignCenter)

        self.logo_label_2 = QLabel(self.central_widget)
        self.logo_label_2.setGeometry(QRect(880, -2, 121, 101))
        self.logo_label_2.setFont(QFont("Brush Script MT", italic=True, pointSize=23))
        self.logo_label_2.setText("World")
        self.logo_label_2.setStyleSheet("background-color: transparent;\n"
                                        "color: qlineargradient(spread:pad, x1:0.09, y1:1, x2:0.803378, y2:0.273, \n" +
                                        "stop:0 rgba(50, 186, 19, 255), stop:1 rgba(36, 160, 217, 255));")
        self.logo_label_2.setAlignment(Qt.AlignCenter)

        self.top_bird_label = QLabel(self.central_widget)
        self.top_bird_label.setGeometry(QRect(1, 8, 91, 61))
        self.top_bird_label.setStyleSheet("background-color: transparent;")
        self.top_bird_label.setPixmap(QPixmap("gui_graphics/bird_outline.png"))

        self.b_left_bird_label = QLabel(self.central_widget)
        self.b_left_bird_label.setGeometry(QRect(-5, 962, 91, 61))
        self.b_left_bird_label.setStyleSheet("background-color: transparent;")
        self.b_left_bird_label.setPixmap(QPixmap("gui_graphics/rev_bird_outline.png"))

        self.b_right_bird_label = QLabel(self.central_widget)
        self.b_right_bird_label.setGeometry(QRect(937, 967, 91, 61))
        self.b_right_bird_label.setStyleSheet("background-color: transparent;")
        self.b_right_bird_label.setPixmap(QPixmap("gui_graphics/bird_outline.png"))

        self.start_label = QLabel(self.central_widget)
        self.start_label.setGeometry(QRect(50, 30, 271, 51))
        self.start_label.setFont(QFont("Calibri", weight=75, pointSize=25))
        self.start_label.setText("Start")
        self.start_label.setStyleSheet("background-color: transparent;\n"
                                       "color: rgb(29, 179, 122);")
        self.start_label.setAlignment(Qt.AlignLeading | Qt.AlignLeft | Qt.AlignVCenter)

        self.start_frame = QFrame(self.central_widget)
        self.start_frame.setGeometry(QRect(50, 80, 431, 411))
        self.start_frame.setStyleSheet(".QFrame {\n"
                                       "    background-color:rgb(222, 239, 235);\n"
                                       "    border-style: solid;\n"
                                       "    border-width: 5px;\n"
                                       "    border-color: rgb(200, 235, 227);\n"
                                       "}")
        self.start_frame.setFrameShape(QFrame.StyledPanel)
        self.start_frame.setFrameShadow(QFrame.Raised)

        self.start_top_line = QFrame(self.central_widget)
        self.start_top_line.setGeometry(QRect(50, 70, 431, 20))
        self.start_top_line.setStyleSheet("color: rgb(29, 179, 122);\n"
                                          "background-color: transparent;")
        self.start_top_line.setFrameShadow(QFrame.Plain)
        self.start_top_line.setLineWidth(5)
        self.start_top_line.setFrameShape(QFrame.HLine)

        self.start_bottom_line = QFrame(self.central_widget)
        self.start_bottom_line.setGeometry(QRect(50, 480, 431, 20))
        self.start_bottom_line.setStyleSheet("color: rgb(29, 179, 122);\n"
                                             "background-color: transparent;")
        self.start_bottom_line.setFrameShadow(QFrame.Plain)
        self.start_bottom_line.setLineWidth(5)
        self.start_bottom_line.setFrameShape(QFrame.HLine)

        self.user_photo_label = QLabel(self.start_frame)
        self.user_photo_label.setGeometry(QRect(100, 30, 231, 231))
        self.user_photo_label.setFont(QFont("Calibri", weight=50, pointSize=11))
        self.user_photo_label.setAcceptDrops(True)
        self.user_photo_label.setStyleSheet("border: 5px;\n"
                                            "border-color: rgb(29, 179, 122);\n"
                                            "border-style: dashed;\n"
                                            "background-color: rgb(244, 244, 244);")
        self.user_photo_label.setText(QtCore.QCoreApplication.translate("MainWindow",
                                                                        "<html>"
                                                                        " <head/>"
                                                                        " <body>"
                                                                        "  <p align=\"center\">"
                                                                        "   <span style=\"font-size:14pt; color:#b9b9b9;\">"
                                                                        "    drag and drop<br/>photo here"
                                                                        "   </span>"
                                                                        "  </p>"
                                                                        " </body>"
                                                                        "</html>"))
        self.user_photo_label.setScaledContents(True)
        self.user_photo_label.setAlignment(Qt.AlignLeading | Qt.AlignLeft | Qt.AlignVCenter)
        self.user_photo_label.dragEnterEvent = self.drag_enter_event
        self.user_photo_label.dragMoveEvent = self.drag_move_event
        self.user_photo_label.dropEvent = self.drop_event

        self.select_button = QPushButton(self.start_frame)
        self.select_button.setGeometry(QRect(100, 280, 231, 41))
        self.select_button.setFont(QFont("Calibri", weight=75, pointSize=15))
        self.select_button.setText("Select Photo")
        self.select_button.setStyleSheet("QPushButton {\n"
                                         "    background-color: transparent;\n"
                                         "    border: 4px;\n"
                                         "    border-color: rgb(29, 179, 122);\n"
                                         "    border-style: solid;\n"
                                         "    border-radius: 7px;\n"
                                         "    color: rgb(29, 179, 122);\n"
                                         "}\n"
                                         "\n"
                                         "QPushButton:hover {\n"
                                         "    background-color: rgb(29, 179, 122);\n"
                                         "    border: 4px;\n"
                                         "    border-color: rgb(29, 179, 122);\n"
                                         "    border-style: solid;\n"
                                         "    border-radius: 7px;\n"
                                         "    color: rgb(255, 255, 255);\n"
                                         "}")
        self.select_button.clicked.connect(self.browse_files)

        self.identify_button = QPushButton(self.start_frame)
        self.identify_button.setGeometry(QRect(100, 340, 231, 41))
        self.identify_button.setFont(QFont("Calibri", weight=75, pointSize=15))
        self.identify_button.setText("Identify!")
        self.identify_button.setStyleSheet("QPushButton {\n"
                                           "    background-color: transparent;\n"
                                           "    border: 4px;\n"
                                           "    border-color: rgb(166, 208, 199);\n"
                                           "    border-style: solid;\n"
                                           "    border-radius: 7px;\n"
                                           "    color: rgb(166, 208, 199);\n"
                                           "}")
        self.identify_button.setDisabled(True)
        self.identify_button.clicked.connect(self.perform_identify)

        self.best_match_label = QLabel(self.central_widget)
        self.best_match_label.setGeometry(QRect(530, 30, 391, 51))
        self.best_match_label.setFont(QFont("Calibri", weight=75, pointSize=25))
        self.best_match_label.setText("Best Match")
        self.best_match_label.setStyleSheet("background-color: transparent;\n"
                                            "color: rgb(49, 173, 192);")
        self.best_match_label.setAlignment(Qt.AlignLeading | Qt.AlignLeft | Qt.AlignVCenter)

        self.best_match_frame = QFrame(self.central_widget)
        self.best_match_frame.setGeometry(QRect(530, 80, 431, 411))
        self.best_match_frame.setStyleSheet(".QFrame {\n"
                                            "    background-color: rgb(222, 235, 239);\n"
                                            "    border-style: solid;\n"
                                            "    border-color: rgb(203, 226, 236);\n"
                                            "    border-width: 5px;\n"
                                            "}")
        self.best_match_frame.setFrameShape(QFrame.StyledPanel)
        self.best_match_frame.setFrameShadow(QFrame.Raised)

        self.best_match_top_line = QFrame(self.central_widget)
        self.best_match_top_line.setGeometry(QRect(530, 70, 431, 20))
        self.best_match_top_line.setStyleSheet("color: rgb(49, 173, 192);\n"
                                               "background-color: transparent;")
        self.best_match_top_line.setFrameShadow(QFrame.Plain)
        self.best_match_top_line.setLineWidth(5)
        self.best_match_top_line.setFrameShape(QFrame.HLine)

        self.best_match_bottom_line = QFrame(self.central_widget)
        self.best_match_bottom_line.setGeometry(QRect(530, 480, 431, 20))
        self.best_match_bottom_line.setStyleSheet("color: rgb(49, 173, 192);\n"
                                                  "background-color: transparent;")
        self.best_match_bottom_line.setFrameShadow(QFrame.Plain)
        self.best_match_bottom_line.setLineWidth(5)
        self.best_match_bottom_line.setFrameShape(QFrame.HLine)

        self.best_match_photo_label = QLabel(self.best_match_frame)
        self.best_match_photo_label.setGeometry(QRect(100, 30, 231, 231))
        self.best_match_photo_label.setFont(QFont("MS Shell Dlg 2", weight=75, pointSize=22))
        self.best_match_photo_label.setAcceptDrops(True)
        self.best_match_photo_label.setStyleSheet("border: 6px;\n"
                                                  "border-color: rgb(49, 173, 192);\n"
                                                  "border-style: solid;")
        self.best_match_photo_label.setScaledContents(True)
        self.best_match_photo_label.setPixmap(QPixmap("gui_graphics/question_mark.png"))

        self.best_match_name_label = QLabel(self.best_match_frame)
        self.best_match_name_label.setGeometry(QRect(20, 280, 391, 41))
        self.best_match_name_label.setFont(QFont("Calibri", weight=75, pointSize=22))
        self.best_match_name_label.setText("BIRD NAME HERE")
        self.best_match_name_label.setStyleSheet("background-color: transparent;\n"
                                                 "color: rgb(49, 173, 192);")
        self.best_match_name_label.setAlignment(Qt.AlignCenter)

        self.question_label = QLabel(self.best_match_frame)
        self.question_label.setGeometry(QRect(40, 340, 181, 41))
        self.question_label.setFont(QFont("Calibri", weight=75, pointSize=15))
        self.question_label.setText("Is this your bird?")
        self.question_label.setStyleSheet("background-color: transparent;\n"
                                          "color: rgb(95, 95, 94);")
        self.question_label.setAlignment(Qt.AlignLeading | Qt.AlignLeft | Qt.AlignVCenter)

        self.yes_button = QPushButton(self.best_match_frame)
        self.yes_button.setGeometry(QRect(230, 340, 81, 41))
        self.yes_button.setFont(QFont("Calibri", weight=75, pointSize=14))
        self.yes_button.setText("Yes")
        self.yes_button.setStyleSheet("QPushButton {\n"
                                      "background-color: transparent;\n"
                                      "    border: 4px;\n"
                                      "    border-color: rgb(95, 95, 94);\n"
                                      "    border-style: solid;\n"
                                      "    border-radius: 7px;\n"
                                      "    color: rgb(95, 95, 94);\n"
                                      "}\n"
                                      "\n"
                                      "QPushButton:hover {\n"
                                      "    background-color: rgb(29, 179, 122);\n"
                                      "    border: 4px;\n"
                                      "    border-color: rgb(29, 179, 122);\n"
                                      "    border-style: solid;\n"
                                      "    border-radius: 7px;\n"
                                      "    color: rgb(255, 255, 255);\n"
                                      "}")
        self.yes_button.clicked.connect(self.yes_clicked)

        self.no_button = QPushButton(self.best_match_frame)
        self.no_button.setGeometry(QRect(320, 340, 81, 41))
        self.no_button.setFont(QFont("Calibri", weight=75, pointSize=14))
        self.no_button.setText("No")
        self.no_button.setStyleSheet("QPushButton {\n"
                                     "    background-color: transparent;\n"
                                     "    border: 4px;\n"
                                     "    border-color: rgb(95, 95, 94);\n"
                                     "    border-style: solid;\n"
                                     "    border-radius: 7px;\n"
                                     "    color: rgb(95, 95, 94);\n"
                                     "}\n"
                                     "\n"
                                     "QPushButton:hover {\n"
                                     "    background-color: rgb(231, 75, 74);\n"
                                     "    border: 4px;\n"
                                     "    border-color: rgb(231, 75, 74);\n"
                                     "    border-style: solid;\n"
                                     "    border-radius: 7px;\n"
                                     "    color: rgb(255, 255, 255);\n"
                                     "}")
        self.no_button.clicked.connect(self.no_clicked)

        self.appearing_label = QLabel(self.best_match_frame)
        self.appearing_label.setGeometry(QRect(5, 340, 421, 41))
        self.appearing_label.setFont(QFont("Calibri", weight=75, pointSize=15))
        self.appearing_label.setStyleSheet("background-color: rgb(222, 235, 239);\n"
                                           "color: rgb(95, 95, 94);")
        self.appearing_label.setText("")
        self.appearing_label.setAlignment(Qt.AlignCenter)

        self.probability_label = QLabel(self.central_widget)
        self.probability_label.setGeometry(QRect(50, 520, 431, 51))
        self.probability_label.setFont(QFont("Calibri", weight=75, pointSize=25))
        self.probability_label.setText("Probability")
        self.probability_label.setStyleSheet("background-color: transparent;\n"
                                             "color: rgb(251, 207, 0);")
        self.probability_label.setAlignment(Qt.AlignLeading | Qt.AlignLeft | Qt.AlignVCenter)

        self.probability_frame = QFrame(self.central_widget)
        self.probability_frame.setGeometry(QRect(50, 570, 431, 411))
        self.probability_frame.setStyleSheet(".QFrame {\n"
                                             "    background-color: rgb(245, 243, 222);\n"
                                             "    border-color: rgb(243, 239, 190);\n"
                                             "    border-style: solid;\n"
                                             "    border-width: 5px;\n"
                                             "}")
        self.probability_frame.setFrameShape(QFrame.StyledPanel)
        self.probability_frame.setFrameShadow(QFrame.Raised)

        self.probability_top_line = QFrame(self.central_widget)
        self.probability_top_line.setGeometry(QRect(50, 560, 431, 20))
        self.probability_top_line.setStyleSheet("color: rgb(251, 207, 0);\n"
                                                "background-color: transparent;")
        self.probability_top_line.setFrameShadow(QFrame.Plain)
        self.probability_top_line.setLineWidth(5)
        self.probability_top_line.setFrameShape(QFrame.HLine)

        self.probability_bottom_line = QFrame(self.central_widget)
        self.probability_bottom_line.setGeometry(QRect(50, 970, 431, 20))
        self.probability_bottom_line.setStyleSheet("color: rgb(251, 207, 0);\n"
                                                   "background-color: transparent;")
        self.probability_bottom_line.setFrameShadow(QFrame.Plain)
        self.probability_bottom_line.setLineWidth(5)
        self.probability_bottom_line.setFrameShape(QFrame.HLine)

        self.probability_left_line = QFrame(self.central_widget)
        self.probability_left_line.setGeometry(QRect(42, 573, 20, 405))
        self.probability_left_line.setStyleSheet("background-color: transparent;\n"
                                                 "color: rgb(243, 239, 190);")
        self.probability_left_line.setFrameShadow(QFrame.Plain)
        self.probability_left_line.setLineWidth(5)
        self.probability_left_line.setFrameShape(QFrame.VLine)

        self.probability_right_line = QFrame(self.central_widget)
        self.probability_right_line.setGeometry(QRect(468, 573, 20, 405))
        self.probability_right_line.setStyleSheet("background-color: transparent;\n"
                                                  "color: rgb(243, 239, 190);")
        self.probability_right_line.setFrameShadow(QFrame.Plain)
        self.probability_right_line.setLineWidth(5)
        self.probability_right_line.setFrameShape(QFrame.VLine)

        self.initial_layout = QWidget(self.probability_frame)
        self.initial_layout.setGeometry(QRect(-21, -21, 471, 451))

        self.probability_fill_frame = QFrame(self.initial_layout)
        self.probability_fill_frame.setStyleSheet(".QFrame {\n"
                                                  "    background-color: rgb(245, 243, 222);\n"
                                                  "}")
        self.probability_fill_frame.setFrameShape(QFrame.StyledPanel)
        self.probability_fill_frame.setFrameShadow(QFrame.Raised)

        self.chart_layout = QtWidgets.QHBoxLayout(self.initial_layout)
        self.chart_layout.setContentsMargins(0, 0, 0, 0)
        self.chart_layout.addWidget(self.probability_fill_frame)

        self.possible_matches_label = QLabel(self.central_widget)
        self.possible_matches_label.setGeometry(QRect(530, 520, 431, 51))
        self.possible_matches_label.setFont(QFont("Calibri", weight=75, pointSize=25))
        self.possible_matches_label.setText("Possible Matches")
        self.possible_matches_label.setStyleSheet("background-color: transparent;\n"
                                                  "color: rgb(255, 162, 2);")
        self.possible_matches_label.setAlignment(Qt.AlignLeading | Qt.AlignLeft | Qt.AlignVCenter)

        self.possible_matches_frame = QFrame(self.central_widget)
        self.possible_matches_frame.setGeometry(QRect(530, 570, 431, 411))
        self.possible_matches_frame.setStyleSheet(".QFrame {\n"
                                                  "    background-color: rgb(249, 241, 221);\n"
                                                  "    border-color: rgb(247, 233, 184);\n"
                                                  "    border-style: solid;\n"
                                                  "    border-width: 5px;\n"
                                                  "}")
        self.possible_matches_frame.setFrameShape(QFrame.StyledPanel)
        self.possible_matches_frame.setFrameShadow(QFrame.Raised)

        self.p_match_top_line = QFrame(self.central_widget)
        self.p_match_top_line.setGeometry(QRect(530, 560, 431, 20))
        self.p_match_top_line.setStyleSheet("color: rgb(255, 162, 2);\n"
                                            "background-color: transparent;")
        self.p_match_top_line.setFrameShadow(QFrame.Plain)
        self.p_match_top_line.setLineWidth(5)
        self.p_match_top_line.setFrameShape(QFrame.HLine)

        self.p_match_bottom_line = QFrame(self.central_widget)
        self.p_match_bottom_line.setGeometry(QRect(530, 970, 431, 20))
        self.p_match_bottom_line.setStyleSheet("color: rgb(255, 162, 2);\n"
                                               "background-color: transparent;")
        self.p_match_bottom_line.setFrameShadow(QFrame.Plain)
        self.p_match_bottom_line.setLineWidth(5)
        self.p_match_bottom_line.setFrameShape(QFrame.HLine)

        self.p_match_photo_label_1 = QLabel(self.possible_matches_frame)
        self.p_match_photo_label_1.setGeometry(QRect(30, 30, 116, 116))
        self.p_match_photo_label_1.setStyleSheet("border: 6px;\n"
                                                 "border-color: rgb(255, 162, 2);\n"
                                                 "border-style: solid;")
        self.p_match_photo_label_1.setScaledContents(True)
        self.p_match_photo_label_1.setPixmap(QPixmap("gui_graphics/question_mark.png"))

        self.p_match_name_label_1 = QLabel(self.possible_matches_frame)
        self.p_match_name_label_1.setGeometry(QRect(160, 70, 261, 31))
        self.p_match_name_label_1.setFont(QFont("Calibri", weight=75, pointSize=16))
        self.p_match_name_label_1.setText("BIRD NAME HERE")
        self.p_match_name_label_1.setStyleSheet("background-color: transparent;\n"
                                                "color: rgb(255, 162, 2);")

        self.p_match_photo_label_2 = QLabel(self.possible_matches_frame)
        self.p_match_photo_label_2.setGeometry(QRect(30, 150, 116, 116))
        self.p_match_photo_label_2.setStyleSheet("border: 6px;\n"
                                                 "border-color: rgb(231, 75, 74);\n"
                                                 "border-style: solid;")
        self.p_match_photo_label_2.setScaledContents(True)
        self.p_match_photo_label_2.setPixmap(QPixmap("gui_graphics/question_mark.png"))

        self.p_match_name_label_2 = QLabel(self.possible_matches_frame)
        self.p_match_name_label_2.setGeometry(QRect(160, 190, 261, 31))
        self.p_match_name_label_2.setFont(QFont("Calibri", weight=75, pointSize=16))
        self.p_match_name_label_2.setText("BIRD NAME HERE")
        self.p_match_name_label_2.setStyleSheet("background-color: transparent;\n"
                                                "color: rgb(231, 75, 74);")

        self.p_match_photo_label_3 = QLabel(self.possible_matches_frame)
        self.p_match_photo_label_3.setGeometry(QRect(30, 270, 116, 116))
        self.p_match_photo_label_3.setStyleSheet("border: 6px;\n"
                                                 "border-color: rgb(156, 137, 252);\n"
                                                 "border-style: solid;")
        self.p_match_photo_label_3.setScaledContents(True)
        self.p_match_photo_label_3.setPixmap(QPixmap("gui_graphics/question_mark.png"))

        self.p_match_name_label_3 = QLabel(self.possible_matches_frame)
        self.p_match_name_label_3.setGeometry(QRect(160, 310, 261, 31))
        self.p_match_name_label_3.setFont(QFont("Calibri", weight=75, pointSize=16))
        self.p_match_name_label_3.setText("BIRD NAME HERE")
        self.p_match_name_label_3.setStyleSheet("background-color: transparent;\n"
                                                "color: rgb(156, 137, 252);")

    def drag_enter_event(self, event):

        file_path = event.mimeData().urls()[0].toLocalFile()

        if (file_path[-3:] == "jpg") or (file_path[-3:] == "png") or (file_path[-3:] == "JPG") or (file_path[-3:] == "PNG"):

            event.accept()
        else:
            event.ignore()

    def drag_move_event(self, event):

        file_path = event.mimeData().urls()[0].toLocalFile()

        if (file_path[-3:] == "jpg") or (file_path[-3:] == "png") or (file_path[-3:] == "JPG") or (file_path[-3:] == "PNG"):

            event.accept()
        else:
            event.ignore()

    def drop_event(self, event):

        file_path = event.mimeData().urls()[0].toLocalFile()

        if (file_path[-3:] == "jpg") or (file_path[-3:] == "png") or (file_path[-3:] == "JPG") or (file_path[-3:] == "PNG"):

            event.accept()

            self.current_file_path = file_path   # saves image path for future CNN analysis
            self.user_photo_label.setPixmap(QPixmap(file_path))
            self.user_photo_label.setStyleSheet("border: 5px;\n"
                                                "border-color: rgb(29, 179, 122);\n"
                                                "border-style: solid;")

            # resets all match images if user selects new image to analyze
            self.best_match_photo_label.setPixmap(QPixmap("gui_graphics/question_mark.png"))
            self.p_match_photo_label_1.setPixmap(QPixmap("gui_graphics/question_mark.png"))
            self.p_match_photo_label_2.setPixmap(QPixmap("gui_graphics/question_mark.png"))
            self.p_match_photo_label_3.setPixmap(QPixmap("gui_graphics/question_mark.png"))

            # resets all match text
            self.best_match_name_label.setFont(QFont("Calibri", weight=75, pointSize=22))
            self.p_match_name_label_1.setFont(QFont("Calibri", weight=75, pointSize=16))
            self.p_match_name_label_2.setFont(QFont("Calibri", weight=75, pointSize=16))
            self.p_match_name_label_3.setFont(QFont("Calibri", weight=75, pointSize=16))

            self.best_match_name_label.setText("BIRD NAME HERE")
            self.p_match_name_label_1.setText("BIRD NAME HERE")
            self.p_match_name_label_2.setText("BIRD NAME HERE")
            self.p_match_name_label_3.setText("BIRD NAME HERE")

            # moves label to cover feedback question and buttons, and ensures label text is blank and background solid
            self.appearing_label.setText("")
            self.appearing_label.setStyleSheet("background-color: rgb(222, 235, 239);\n"
                                               "color: rgb(95, 95, 94);")
            self.appearing_label.setGeometry(QRect(5, 340, 421, 41))

            # enables identify button
            self.identify_button.setStyleSheet("QPushButton {\n"
                                               "    background-color: transparent;\n"
                                               "    border: 4px;\n"
                                               "    border-color: rgb(29, 179, 122);\n"
                                               "    border-style: solid;\n"
                                               "    border-radius: 7px;\n"
                                               "    color: rgb(29, 179, 122);\n"
                                               "}\n"
                                               "\n"
                                               "QPushButton:hover {\n"
                                               "    background-color: rgb(29, 179, 122);\n"
                                               "    border: 4px;\n"
                                               "    border-color: rgb(29, 179, 122);\n"
                                               "    border-style: solid;\n"
                                               "    border-radius: 7px;\n"
                                               "    color: rgb(255, 255, 255);\n"
                                               "}")
            self.identify_button.setDisabled(False)

            # if an identify was previously performed, this removes previous probability pie chart
            if self.chart_layout.count() == 1:
                self.chart_layout.removeWidget(self.chart_layout.itemAt(0).widget())

        else:
            event.ignore()

    def browse_files(self):
        file_path = (QFileDialog.getOpenFileName(caption="File Browser", directory="C:/", filter="*.png *.jpg"))[0]

        if (file_path != "") and (
                (file_path[-3:] == "jpg") or (file_path[-3:] == "png") or (file_path[-3:] == "JPG") or (file_path[-3:] == "PNG")):

            self.current_file_path = file_path  # saves image path for future CNN analysis

            self.user_photo_label.setPixmap(QPixmap(file_path))
            self.user_photo_label.setStyleSheet("border: 5px;\n"
                                                "border-color: rgb(29, 179, 122);\n"
                                                "border-style: solid;")

            # resets all match images if user selects new image to analyze
            self.best_match_photo_label.setPixmap(QPixmap("gui_graphics/question_mark.png"))
            self.p_match_photo_label_1.setPixmap(QPixmap("gui_graphics/question_mark.png"))
            self.p_match_photo_label_2.setPixmap(QPixmap("gui_graphics/question_mark.png"))
            self.p_match_photo_label_3.setPixmap(QPixmap("gui_graphics/question_mark.png"))

            # resets all match text
            self.best_match_name_label.setFont(QFont("Calibri", weight=75, pointSize=22))
            self.p_match_name_label_1.setFont(QFont("Calibri", weight=75, pointSize=16))
            self.p_match_name_label_2.setFont(QFont("Calibri", weight=75, pointSize=16))
            self.p_match_name_label_3.setFont(QFont("Calibri", weight=75, pointSize=16))

            self.best_match_name_label.setText("BIRD NAME HERE")
            self.p_match_name_label_1.setText("BIRD NAME HERE")
            self.p_match_name_label_2.setText("BIRD NAME HERE")
            self.p_match_name_label_3.setText("BIRD NAME HERE")

            # moves label to cover feedback question and buttons, and ensures label text is blank and background solid
            self.appearing_label.setText("")
            self.appearing_label.setStyleSheet("background-color: rgb(222, 235, 239);\n"
                                               "color: rgb(95, 95, 94);")
            self.appearing_label.setGeometry(QRect(5, 340, 421, 41))

            # enables identify button
            self.identify_button.setStyleSheet("QPushButton {\n"
                                               "    background-color: transparent;\n"
                                               "    border: 4px;\n"
                                               "    border-color: rgb(29, 179, 122);\n"
                                               "    border-style: solid;\n"
                                               "    border-radius: 7px;\n"
                                               "    color: rgb(29, 179, 122);\n"
                                               "}\n"
                                               "\n"
                                               "QPushButton:hover {\n"
                                               "    background-color: rgb(29, 179, 122);\n"
                                               "    border: 4px;\n"
                                               "    border-color: rgb(29, 179, 122);\n"
                                               "    border-style: solid;\n"
                                               "    border-radius: 7px;\n"
                                               "    color: rgb(255, 255, 255);\n"
                                               "}")
            self.identify_button.setDisabled(False)

            # if an identify was previously performed, this removes previous probability pie chart
            if self.chart_layout.count() == 1:
                self.chart_layout.removeWidget(self.chart_layout.itemAt(0).widget())

    def perform_identify(self):

        user_photo = keras.preprocessing.image.load_img(self.current_file_path)

        # image must be same size as images used during training, smart resize does not distort image proportions
        user_photo = keras.preprocessing.image.smart_resize(user_photo, (224, 224))

        # converts image to an array of RGB pixel values
        photo_array = keras.preprocessing.image.img_to_array(user_photo)

        # scales RGB pixel values to be 0 - 1, rather than 0 - 255
        photo_array = photo_array / 255.0

        # adds a single dimension to all array values, required shape for predict() to work
        photo_array = tf.expand_dims(photo_array, 0)

        # results in an ndarray data type, with prediction probabilities for each trained category at index 0
        predictions = self.bird_id_model.predict(photo_array)

        # convert ndarray's category probability predictions into an array
        predictions_list = predictions[0].ravel().tolist()

        first_prediction_value = max(predictions_list)
        first_prediction_index = predictions_list.index(first_prediction_value)
        first_prediction_name = self.bird_dict[first_prediction_index]

        # used so previous maximum values can be excluded from future max() operations on predictions_list
        index_exclusion_list = [first_prediction_index]

        second_prediction_value = max([val for index, val in enumerate(predictions_list) if index not in index_exclusion_list])
        second_prediction_index = predictions_list.index(second_prediction_value)
        second_prediction_name = self.bird_dict[second_prediction_index]

        index_exclusion_list.append(second_prediction_index)

        third_prediction_value = max([val for index, val in enumerate(predictions_list) if index not in index_exclusion_list])
        third_prediction_index = predictions_list.index(third_prediction_value)
        third_prediction_name = self.bird_dict[third_prediction_index]

        index_exclusion_list.append(third_prediction_index)

        fourth_prediction_value = max([val for index, val in enumerate(predictions_list) if index not in index_exclusion_list])
        fourth_prediction_index = predictions_list.index(fourth_prediction_value)
        fourth_prediction_name = self.bird_dict[fourth_prediction_index]

        # sets matching bird image and name, images from directory labeled with indices corresponding to CNN's trained indices
        self.best_match_photo_label.setPixmap(QPixmap("bird_data/bird_images/" + str(first_prediction_index) + ".jpg"))
        self.set_sized_text(self.best_match_name_label, first_prediction_name, 391, 22)

        self.p_match_photo_label_1.setPixmap(QPixmap("bird_data/bird_images/" + str(second_prediction_index) + ".jpg"))
        self.set_sized_text(self.p_match_name_label_1, second_prediction_name, 261, 16)

        self.p_match_photo_label_2.setPixmap(QPixmap("bird_data/bird_images/" + str(third_prediction_index) + ".jpg"))
        self.set_sized_text(self.p_match_name_label_2, third_prediction_name, 261, 16)

        self.p_match_photo_label_3.setPixmap(QPixmap("bird_data/bird_images/" + str(fourth_prediction_index) + ".jpg"))
        self.set_sized_text(self.p_match_name_label_3, fourth_prediction_name, 261, 16)

        first_prediction_percentage = float("{:.1f}".format(100 * first_prediction_value))
        second_prediction_percentage = float("{:.1f}".format(100 * second_prediction_value))
        third_prediction_percentage = float("{:.1f}".format(100 * third_prediction_value))
        fourth_prediction_percentage = float("{:.1f}".format(100 * fourth_prediction_value))
        remainder_percentage = 0.0

        total = first_prediction_percentage + second_prediction_percentage + third_prediction_percentage + fourth_prediction_percentage

        if total < 100:
            remainder_percentage = float("{:.1f}".format(100.0 - total))

        series = QPieSeries()
        series.append(str(first_prediction_percentage) + "%", first_prediction_percentage)
        series.append(str(second_prediction_percentage) + "%", second_prediction_percentage)
        series.append(str(third_prediction_percentage) + "%", third_prediction_percentage)
        series.append(str(fourth_prediction_percentage) + "%", fourth_prediction_percentage)
        series.append(str(remainder_percentage) + "%", remainder_percentage)

        series.setPieSize(.95)
        series.setLabelsVisible(True)
        series.setLabelsPosition(QPieSlice.LabelInsideHorizontal)

        pie_font = QFont("Calibri", weight=75, pointSize=20)

        for piece in series.slices():                           # if there will be outside labels
            if .05 <= piece.percentage() < .1:                  # reduce pie size and font
                series.setPieSize(.7)
                pie_font.setPointSize(13)
                break

        for piece in series.slices():

            piece.setLabelFont(pie_font)

            if piece.percentage() < .05:                        # if piece < 5%, don't show any label
                piece.setLabelVisible(False)
            elif piece.percentage() < .1:                       # if 5% <= piece < 10%, place label outside slice
                piece.setLabelPosition(QPieSlice.LabelOutside)
                piece.setLabelArmLengthFactor(.10)

        chart = QChart()
        chart.addSeries(series)
        chart.legend().hide()
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.setBackgroundBrush(QColor(245, 243, 222))

        slice0 = series.slices()[0]
        slice0.setBrush(QColor(49, 173, 192))

        slice1 = series.slices()[1]
        slice1.setBrush(QColor(255, 162, 2))

        slice2 = series.slices()[2]
        slice2.setBrush(QColor(231, 75, 74))

        slice3 = series.slices()[3]
        slice3.setBrush(QColor(156, 137, 252))

        slice4 = series.slices()[4]
        slice4.setBrush(QColor(214, 214, 214))

        chart_view = QChartView(chart)
        chart_view.setRenderHint(QtGui.QPainter.Antialiasing)

        self.chart_layout.addWidget(chart_view)

        # disables the identify button, which remains that way until user selects a new image to analyze
        self.identify_button.setStyleSheet("QPushButton {\n"
                                           "    background-color: transparent;\n"
                                           "    border: 4px;\n"
                                           "    border-color: rgb(166, 208, 199);\n"
                                           "    border-style: solid;\n"
                                           "    border-radius: 7px;\n"
                                           "    color: rgb(166, 208, 199);\n"
                                           "}")
        self.identify_button.setDisabled(True)

        with connection_pool.get_connection() as connection, connection.cursor() as cursor:

            try:
                # lock to ensure that when row is added, that same row's id is retrieved
                cursor.execute("LOCK TABLES identification_log WRITE;")

                sql = "INSERT INTO identification_log " \
                      "VALUES(default, \"" + first_prediction_name + "\", " + str(first_prediction_percentage) + ", NOW(), \"NONE\");"

                cursor.execute(sql)

                cursor.execute("SELECT MAX(id) "
                               "FROM identification_log;")

                max_results = cursor.fetchall()

                # retrieve the row's id and save in case user feedback is given
                for row in max_results:
                    self.current_index = row[0]

            except mysql.connector.Error as sql_error1:
                self.db_connection.rollback()
                print("ERROR: {}".format(sql_error1))

            finally:
                try:
                    cursor.execute("UNLOCK TABLES;")
                except mysql.connector.Error as sql_error2:
                    self.db_connection.rollback()
                    print("ERROR: {}".format(sql_error2))

        # try:
        #     cursor = self.db_connection.cursor()
        #
        #     # lock to ensure that when row is added, that same row's id is retrieved
        #     cursor.execute("LOCK TABLES identification_log WRITE;")
        #
        #     sql = "INSERT INTO identification_log " \
        #           "VALUES(default, \"" + first_prediction_name + "\", " + str(first_prediction_percentage) + ", NOW(), \"NONE\");"
        #
        #     cursor.execute(sql)
        #
        #     cursor.execute("SELECT MAX(id) "
        #                    "FROM identification_log;")
        #
        #     max_results = cursor.fetchall()
        #
        #     # retrieve the row's id and save in case user feedback is given
        #     for row in max_results:
        #         self.current_index = row[0]
        #
        #     cursor.execute("UNLOCK TABLES;")
        #
        #     self.db_connection.commit()
        #     cursor.close()
        #
        # except mysql.connector.Error as sql_error:
        #     self.db_connection.rollback()
        #     print("ERROR: {}".format(sql_error))

        # moves label to reveal feedback question and buttons, and ensures label text is blank and background transparent
        self.appearing_label.setText("")
        self.appearing_label.setStyleSheet("background-color: transparent;\n"
                                           "color: rgb(95, 95, 94);")
        self.appearing_label.setGeometry(QRect(5, 410, 421, 41))

    def set_sized_text(self, label, name, bounding_width, point_size):

        label.setText(name)

        text_width = label.fontMetrics().boundingRect(label.text()).width()

        reduction_size = 1

        while text_width > bounding_width:
            label.setFont(QFont("Calibri", weight=75, pointSize=(point_size - reduction_size)))

            reduction_size += 1

            text_width = label.fontMetrics().boundingRect(label.text()).width()

    def yes_clicked(self):

        # label is moved to cover feedback question and buttons
        self.appearing_label.setText("Thanks for the feedback!")
        self.appearing_label.setStyleSheet("background-color: rgb(222, 235, 239);\n"
                                           "color: rgb(95, 95, 94);")
        self.appearing_label.setGeometry(QRect(5, 340, 421, 41))

        with connection_pool.get_connection() as connection, connection.cursor() as cursor:

            sql = "UPDATE identification_log " \
                  "SET user_feedback = \"CORRECT\" " \
                  "WHERE id = " + str(self.current_index) + ";"
            try:
                cursor.execute(sql)
                connection.commit()

            except mysql.connector.Error as yes_error:
                print("ERROR: {}".format(yes_error))

    def no_clicked(self):

        # label is moved to cover feedback question and buttons
        self.appearing_label.setText("Thanks for the feedback!")
        self.appearing_label.setStyleSheet("background-color: rgb(222, 235, 239);\n"
                                           "color: rgb(95, 95, 94);")
        self.appearing_label.setGeometry(QRect(5, 340, 421, 41))

        with connection_pool.get_connection() as connection, connection.cursor() as cursor:

            sql = "UPDATE identification_log " \
                  "SET user_feedback = \"INCORRECT\" " \
                  "WHERE id = " + str(self.current_index) + ";"
            try:
                cursor.execute(sql)
                connection.commit()

            except mysql.connector.Error as no_error:
                print("ERROR: {}".format(no_error))

    # def closeEvent(self, event):
    #
    #     self.db_connection.close()
    #
    #     if self.db_connection.is_closed():
    #         print("Database connection closed.")
    #
    #     event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    splash = QtWidgets.QSplashScreen(QPixmap("gui_graphics/splash_screen.png"))
    splash.setWindowFlag(Qt.WindowStaysOnTopHint)
    splash.show()

    connection_pool = None

    try:
        connection_pool = pooling.MySQLConnectionPool(host="127.0.0.1",
                                                      database="bird_photo_id_database",
                                                      user="root",
                                                      password="NewPassword1!")

        if connection_pool is not None:
            print("Database connection successfully established.")

    except mysql.connector.Error as connect_error:
        print("Database connection failure: {}".format(connect_error))

    MainWindow = MainWindow()
    MainWindow.show()
    splash.finish(MainWindow)

    sys.exit(app.exec_())
