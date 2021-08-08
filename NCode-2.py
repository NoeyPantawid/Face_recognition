import face_recognition as face 
import numpy as np 
import sys, cv2, os, sqlite3, pickle
from subprocess import call

video_capture = cv2.VideoCapture(0) 

global known_face_encodings, known_face_names

with open(os.getcwd() + '\\database\\dataset_faces.dat', 'rb') as f:
	all_face_encodings = pickle.load(f)

face_names = list(all_face_encodings.keys())
face_encodings = np.array(list(all_face_encodings.values()))

face_locations = []
known_face_encodings = face_encodings
known_face_names = face_names
face_percent = []

while True:
    ret, frame = video_capture.read()
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

        cv2.imshow("Output", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        break

video_capture.release()
cv2.destroyAllWindows()