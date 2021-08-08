from ui import Ui_MainWindow
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
import sys, os, cv2, sqlite3, pickle, dlib, shutil
import face_recognition as face
import numpy as np

global cap
cap = cv2.VideoCapture(0,cv2.CAP_DSHOW)

#!ห้ามลบ ส่วนสำคัญ
class Project(QtWidgets.QMainWindow, Ui_MainWindow, QThread):
    def __init__(self):
        super(Project, self).__init__()

        #ซ่อน title bar อันเดิม
        self.setWindowFlag(Qt.FramelessWindowHint)

        self.uif = Ui_MainWindow()
        self.uif.setupUi(self)
        #!--------------

        #แสดงผลภาพ
        self.Worker1 = Worker1()
        self.Worker1.start()
        self.Worker1.ImageUpdate.connect(self.ImageUpdateSlot)

        #เลื่อนหน้าต่าง
        def moveWindow(event):
            if event.buttons() == Qt.LeftButton:
                self.move(self.pos() + event.globalPos() - self.dragPos)
                self.dragPos = event.globalPos()
                event.accept()

        self.uif.frame_4.mouseMoveEvent = moveWindow

        #ปุ่มย่อและปุ่มปิด
        self.uif.minimize.pressed.connect(self.btn_minimize)
        self.uif.close.pressed.connect(self.btn_close)
        #ปุ่มเปลี่ยนหน้า
        self.uif.btn_page_1.pressed.connect(self.btn_to_page_1)
        self.uif.btn_page_2.pressed.connect(self.btn_to_page_2)
        self.uif.btn_page_3.pressed.connect(self.btn_to_page_3)
        #ปุ่มสั่งเทรน
        self.uif.minimize_4.pressed.connect(self.btn_train)
        #ปุ่มแสดงผล
        self.uif.minimize_5.pressed.connect(self.btn_show)
        #ปุ่มเคลียร์ data
        self.uif.cleardataall.pressed.connect(self.btn_deletedata)

        if cap.isOpened():
            self.uif.textBrowser_2.setText("camera on")
        else:
            self.uif.textBrowser_2.setText("camera off")

        #ตาราง database
        #self.uif.tableWidget.setRowCount(50)
        self.uif.connectdatabase.pressed.connect(self.connect_to_database)

    #ฟังก์ชั่นย่อและปิด
    def btn_minimize(self):
        self.showNormal()
        self.showMinimized()

    def btn_close(self):
        quit()
    
    #ฟังก์ชั่นเปลี่ยหน้า
    def btn_to_page_1(self):
        self.uif.stackedWidget.setCurrentWidget(self.uif.Detect)
    def btn_to_page_2(self):
        self.uif.stackedWidget.setCurrentWidget(self.uif.Datatable)
    def btn_to_page_3(self):
        self.uif.stackedWidget.setCurrentWidget(self.uif.Info)
    
    #ฟังก์ชั่นอัพเดทภาพทุกเฟรม
    def ImageUpdateSlot(self, Image):
        try:
            self.uif.Screen.setPixmap(QPixmap.fromImage(Image))
        except Exception as e:
            self.uif.textBrowser_2.setText("Update Error {}".format(e))

    #ฟังก์ชั่นสั่งเทรน
    def btn_train(self):
        try:
            os.mkdir('database')
            os.mkdir('image')
        except:
            pass

        try:
            ID = self.uif.lineEdit.text()
            NAME = self.uif.lineEdit_2.text()
            TIER = self.uif.comboBox.currentText()
            Running = True
            while(Running):
                ret, imageframe = cap.read()
                path = os.getcwd() + '\\image\\'
                cv2.imwrite('{}{}-{}-{}.jpg'.format(path, TIER, ID, NAME),imageframe)
                Running = False

            try:
                self.create_database()
                self.add_to_database()
                
            except Exception as e:
                self.uif.textBrowser.setText("{} : error here".format(e))

            self.uif.textBrowser_3.setText(" ")

        except Exception as e:
            self.uif.textBrowser.setText("Error : {}".format(e))
    
    #สร้างฐานข้อมูล
    def create_database(self):
        database_path = os.getcwd() + '\\database\\db.sqlite'
        try:
            with sqlite3.connect(database_path) as con:
                sql_cmd = """
                CREATE TABLE People (
                id   STRING NOT NULL,
                Name STRING NOT NULL,
                TIER STRING
                );
                """
                con.execute(sql_cmd)
            self.uif.textBrowser.setText(" ")
        except Exception as e:
            self.uif.textBrowser.setText("Update database complete")

    def add_to_database(self):
        database_path = os.getcwd() + '\\database\\db.sqlite'
        path = os.getcwd() + '\\image\\'
        FACE_ENCODINGS = {}
        #DATASET
        try:
            ID = self.uif.lineEdit.text()
            NAME = self.uif.lineEdit_2.text()
            TIER = self.uif.comboBox.currentText()
            outim = ('{}{}-{}-{}.jpg'.format(path, TIER, ID, NAME))
            NAME_image = face.load_image_file(outim)
            FACE_ENCODINGS['{} - {}'.format(TIER, NAME)] = face.face_encodings(NAME_image)[0]
            try:
                with open(os.getcwd() + '\\database\\dataset_faces.dat', 'rb') as fb1:
                    FBR1 = pickle.load(fb1)
                    try:
                        FBR1 = FBR1 | FACE_ENCODINGS
                        with open(os.getcwd() + '\\database\\dataset_faces.dat', 'wb') as ff:
                            pickle.dump(FBR1, ff)
                        #print(FBR1) แสดงอัพเดทล่าสุด
                    except Exception as e:
                        print('Cant dump maybe cuz u dumb')

            except:
                with open(os.getcwd() + '\\database\\dataset_faces.dat', 'wb') as f:
                    pickle.dump(FACE_ENCODINGS, f)
                    FACE_ENCODINGS['{} - {}'.format(TIER, NAME)] = face.face_encodings(NAME_image)[0]

            #! การเชื่อมต่อกับ database มีปัญหาตรง UNIQUE KEY ไม่สามารถแก้ไขได้
            with sqlite3.connect('{}'.format(database_path)) as con:
                sql_cmd = """
                insert into People values('{}','{}','{}')
                """.format(ID, NAME, TIER)
                con.execute(sql_cmd)
            self.uif.textBrowser.setText(" ")

        except:
            self.uif.textBrowser.setText("No face detect.")

    def connect_to_database(self):
        self.uif.tableWidget.setRowCount(0)
        try:
            connect = sqlite3.connect(os.getcwd() + '\\database\\db.sqlite')
            cur = connect.cursor()
            sql_cmd2 = "SELECT * FROM People"

            counter = 0
            for row in cur.execute(sql_cmd2):
                self.uif.tableWidget.setRowCount(counter + 1)
                self.uif.tableWidget.setItem(counter, 0, QtWidgets.QTableWidgetItem(str(row[0])))
                self.uif.tableWidget.setItem(counter, 1, QtWidgets.QTableWidgetItem(str(row[1])))
                self.uif.tableWidget.setItem(counter, 2, QtWidgets.QTableWidgetItem(str(row[2])))
                counter += 1
            self.uif.databrow.setText(' ')

        except:
            self.uif.databrow.setText('No database found!')

    def btn_show(self):
        try:
            self.Worker1.pause()
        except:
            pass

        self.Worker2 = Worker2()
        self.Worker2.start()
        self.Worker2.ImageUpdate.connect(self.ImageUpdateSlot)
        
    def btn_deletedata(self):
        try:
            shutil.rmtree('database')
            shutil.rmtree('image')
            self.uif.textBrowser_3.setText("Clear data complete")
        except Exception as e:
            self.uif.textBrowser_3.setText("ERROR : cant clear data folder")

    #เลื่อนหน้าต่าง    
    def mousePressEvent(self, event):
        self.dragPos = event.globalPos()

class Worker1(QThread,QtWidgets.QMainWindow, Ui_MainWindow):
    ImageUpdate = pyqtSignal(QImage)
    def run(self):
        self.ThreadActive = True
        Capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        while self.ThreadActive:
            ret, Frame = Capture.read()
            if ret:
                Image = cv2.cvtColor(Frame, cv2.COLOR_BGR2RGB)
                ConvertToQtFormat = QImage(Image.data, Image.shape[1], Image.shape[0], QImage.Format_RGB888)
                Pic = ConvertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
                self.ImageUpdate.emit(Pic)
    def pause(self):
        self.ThreadActive = False

class Worker2(QThread,QtWidgets.QMainWindow, Ui_MainWindow):
    ImageUpdate = pyqtSignal(QImage)
    def run(self):
        with open(os.getcwd() + '\\database\\dataset_faces.dat', 'rb') as f:
            all_face_encodings = pickle.load(f)

        face_names = list(all_face_encodings.keys())
        face_encodings = np.array(list(all_face_encodings.values()))

        face_locations = []
        known_face_encodings = face_encodings
        known_face_names = face_names
        face_percent = []

        self.ThreadActive = True
        Capture = cv2.VideoCapture(0)
        while self.ThreadActive:
            ret, frame = Capture.read()
            if ret:
                small_frame = cv2.resize(frame, (0,0), fx=0.5,fy=0.5)
                rgb_small_frame = small_frame[:,:,::-1]

                face_names = []
                face_percent = []

                #ส่วนของโมเดล hog = ใช้ cpu cnn = ใช้ GPU/Cuda แต่ไม่รู้ทำไม cnn ถึงกระตุกมาก
                face_locations = face.face_locations(rgb_small_frame, model="hog")

                face_encodings = face.face_encodings(rgb_small_frame, face_locations)
                
                try:
                    for face_encoding in face_encodings:
                        face_distances = face.face_distance(known_face_encodings, face_encoding)
                        best = np.argmin(face_distances)
                        face_percent_value = 1-face_distances[best]

                        if face_percent_value >= 0.5:
                            name = known_face_names[best]
                            percent = round(face_percent_value*100,2)
                            face_percent.append(percent)
                        else:
                            name = "UNKNOWN"
                            face_percent.append(0)
                        face_names.append(name)
                except Exception as e:
                    print(e)

                for (top,right,bottom, left), name, percent in zip(face_locations, face_names, face_percent):
                    top*= 2
                    right*= 2
                    bottom*= 2
                    left*= 2

                    if name == "UNKNOWN":
                        color = [46,2,209]
                    else:
                        color = [255,102,51]

                    cv2.rectangle(frame, (left,top), (right,bottom), color, 2)
                    cv2.rectangle(frame, (left-1, top -30), (right+1,top), color, cv2.FILLED)
                    cv2.rectangle(frame, (left-1, bottom), (right+1,bottom+30), color, cv2.FILLED)
                    font = cv2.FONT_HERSHEY_DUPLEX
                    cv2.putText(frame, name, (left+6, top-6), font, 0.6, (255,255,255), 1)
                    cv2.putText(frame, "MATCH: "+str(percent)+"%", (left+6, bottom+23), font, 0.6, (255,255,255), 1)

                Image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                ConvertToQtFormat = QImage(Image.data, Image.shape[1], Image.shape[0], QImage.Format_RGB888)
                Pic = ConvertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
                self.ImageUpdate.emit(Pic)
            else:
                break
    def pause(self):
        self.ThreadActive = False

#!ห้ามลบ ส่วนสำคัญ
app = QtWidgets.QApplication(sys.argv)
NCode = Project()
NCode.show()
app.exec_()
#!--------------