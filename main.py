# import cv2
# import os
# import pickle
# import face_recognition
# import numpy as np
# import time
# import csv
# import cvzone
# from datetime import datetime
# import firebase_admin
# from firebase_admin import credentials, db, storage

# # Initialize Firebase
# cred = credentials.Certificate("./serviceAccountKey.json")
# firebase_admin.initialize_app(cred, {
#     'databaseURL': "https://faceattendancerealtime-7a66f-default-rtdb.firebaseio.com/",
#     'storageBucket': "faceattendancerealtime-7a66f.appspot.com"
# })

# # Load the welcome screen image
# welcome_screen = cv2.imread('Resources/welcome.png')

# # Capture video from webcam (index 0 or 1 for multiple cameras)
# cap = cv2.VideoCapture(0)

# # Check if webcam opened successfully
# if not cap.isOpened():
#     print("Error: Cannot open webcam. Please check if it's connected.")
#     exit()

# # Set frame width and height
# cam_width = 480
# cam_height = 640
# cap.set(3, cam_width)
# cap.set(4, cam_height)

# # Overlay the webcam
# imgBackground = cv2.imread('Resources/background.png')

# # Import mode images to a list
# folderModePath = 'Resources/modes'
# modePathList = os.listdir(folderModePath)
# imgModeList = []
# for path in modePathList:
#     imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))

# # Loading the encoding file
# print("Loading Encode File...")
# encodeFile = open("EncodeFile.p", 'rb')
# encodingListKnownWithIds = pickle.load(encodeFile)
# encodeFile.close()
# encodeListKnown, studentIds = encodingListKnownWithIds
# print(studentIds)
# print("Encode File Loaded")

# modeType = 0
# counter = 0
# id = -1
# imgStudent = []

# start_program = False

# def check_click(event, x, y, flags, param):
#     global start_program
#     if event == cv2.EVENT_LBUTTONDOWN:
#         # Check for Start button click
#         if not start_program and 600 <= x <= 750 and 350 <= y <= 400:
#             start_program = True
#         # Check for Export button click
#         if start_program and 1020 <= x <= 1200 and 650 <= y <= 700:
#             export_data()

# def export_data():
#     ref = db.reference('Students')
#     data = ref.get()

#     with open('students_data.csv', mode='w', newline='') as file:
#         writer = csv.writer(file)
#         writer.writerow(['ID', 'Name', 'Total Attendance', 'Last Attendance Time'])

#         for key, value in data.items():
#             writer.writerow([key, value['name'], value['total_attendance'], value['last_attendance_time']])

#     print("Data exported to students_data.csv")

# cv2.namedWindow("Face Attendance")
# cv2.setMouseCallback("Face Attendance", check_click)

# while True:
#     success, img = cap.read()

#     if not start_program:
#         # Display the welcome screen with the start button
#         cv2.imshow("Face Attendance", welcome_screen)
#     else:
#         # The main program logic
#         imgSized = cv2.resize(img, (0, 0), None, 0.25, 0.25)
#         imgSized = cv2.cvtColor(imgSized, cv2.COLOR_BGR2RGB)

#         faceCurFrame = face_recognition.face_locations(imgSized)
#         encodeCurFrame = face_recognition.face_encodings(imgSized, faceCurFrame)

#         imgBackground[180:180 + cam_width, 75:75 + cam_height] = img

#         x_offset = 814
#         y_offset = 0
#         imgBackground[y_offset:y_offset + imgModeList[modeType].shape[0],
#                       x_offset:x_offset + imgModeList[modeType].shape[1]] = imgModeList[modeType]

#         # Add export button to the main program
#         # cv2.rectangle(imgBackground, (1050, 10), (1150, 60), (0, 255, 0), cv2.FILLED)
#         # cv2.putText(imgBackground, "Export", (1050, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

#         if faceCurFrame:
#             for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
#                 matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
#                 faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
#                 matchIndex = np.argmin(faceDis)

#                 if matches[matchIndex]:
#                     y1, x2, y2, x1 = faceLoc
#                     y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
#                     bbox = 80 + x1, 20 + y2, x2 - x1, y2 - y1
#                     imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)

#                     id = studentIds[matchIndex]

#                     if counter == 0:
#                         cvzone.putTextRect(imgBackground, "Loading", (275, 480))
#                         cv2.imshow("Face Attendance", imgBackground)
#                         cv2.waitKey(1)

#                         counter = 1
#                         modeType = 1

#             if counter != 0:
#                 if counter == 1:
#                     studentInfo = db.reference(f'Students/{id}').get()
#                     print(studentInfo)

#                     bucket = storage.bucket()
#                     blob = bucket.get_blob(f'Images/{id}.jpg')
#                     array = np.frombuffer(blob.download_as_string(), np.uint8)
#                     imgStudent = cv2.imdecode(array, cv2.IMREAD_COLOR)

#                     dateTimeObject = datetime.strptime(studentInfo['last_attendance_time'], "%Y-%m-%d %H:%M:%S")
#                     secElapsed = (datetime.now() - dateTimeObject).total_seconds()
#                     print(secElapsed)

#                     if secElapsed > 30:
#                         ref = db.reference(f'Students/{id}')
#                         studentInfo['total_attendance'] += 1
#                         ref.child('total_attendance').set(studentInfo['total_attendance'])
#                         ref.child('last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
#                     else:
#                         modeType = 3
#                         counter = 0
#                         imgBackground[y_offset:y_offset + imgModeList[modeType].shape[0],
#                                       x_offset:x_offset + imgModeList[modeType].shape[1]] = imgModeList[modeType]

#                 if modeType != 3:
#                     if 10 < counter < 20:
#                         modeType = 2

#                     imgBackground[y_offset:y_offset + imgModeList[modeType].shape[0],
#                                   x_offset:x_offset + imgModeList[modeType].shape[1]] = imgModeList[modeType]

#                     if counter <= 10:
#                         cv2.putText(imgBackground, str(studentInfo['name']),
#                                     (1003, 555),  # location
#                                     cv2.FONT_HERSHEY_DUPLEX, 0.6,
#                                     (255, 255, 255), 1)
#                         cv2.putText(imgBackground, str(studentInfo['ID']),
#                                     (1003, 590),  # location
#                                     cv2.FONT_HERSHEY_DUPLEX, 0.6,
#                                     (255, 255, 255), 1)
#                         cv2.putText(imgBackground, str(studentInfo['total_attendance']),
#                                     (930, 180),  # location
#                                     cv2.FONT_HERSHEY_DUPLEX, 0.6,
#                                     (255, 255, 255), 1)

#                         imgBackground[266:266 + 216, 950:950 + 216] = imgStudent

#                 counter += 1

#                 if counter >= 20:
#                     counter = 0
#                     modeType = 0
#                     studentInfo = []
#                     imgStudent = []
#                     imgBackground[y_offset:y_offset + imgModeList[modeType].shape[0],
#                                   x_offset:x_offset + imgModeList[modeType].shape[1]] = imgModeList[modeType]
#         else:
#             modeType = 0
#             counter = 0

#         cv2.imshow("Face Attendance", imgBackground)

#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# cap.release()
# cv2.destroyAllWindows()


import cv2
import os
import pickle
import face_recognition
import numpy as np
import time
import csv
import cvzone
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, db, storage

# Initialize Firebase
cred = credentials.Certificate("./serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://faceattendancerealtime-7a66f-default-rtdb.firebaseio.com/",
    'storageBucket': "faceattendancerealtime-7a66f.appspot.com"
})

# Load the welcome screen image
welcome_screen = cv2.imread('Resources/welcome.png')

# Capture video from webcam (index 0 or 1 for multiple cameras)
cap = cv2.VideoCapture(0)

# Check if webcam opened successfully
if not cap.isOpened():
    print("Error: Cannot open webcam. Please check if it's connected.")
    exit()

# Set frame width and height
cam_width = 480
cam_height = 640
cap.set(3, cam_width)
cap.set(4, cam_height)

# Overlay the webcam
imgBackground = cv2.imread('Resources/background.png')

# Import mode images to a list
folderModePath = 'Resources/modes'
modePathList = os.listdir(folderModePath)
imgModeList = [cv2.imread(os.path.join(folderModePath, path)) for path in modePathList]

# Loading the encoding file
print("Loading Encode File...")
with open("EncodeFile.p", 'rb') as encodeFile:
    encodingListKnownWithIds = pickle.load(encodeFile)
encodeListKnown, studentIds = encodingListKnownWithIds
print(studentIds)
print("Encode File Loaded")

modeType = 0
counter = 0
imgStudent = []

start_program = False

def check_click(event, x, y, flags, param):
    global start_program
    if event == cv2.EVENT_LBUTTONDOWN:
        # Check for Start button click
        if not start_program and 600 <= x <= 750 and 350 <= y <= 400:
            start_program = True
        # Check for Export button click
        if start_program and 1020 <= x <= 1200 and 650 <= y <= 700:
            export_data()

def export_data():
    ref = db.reference('Students')
    data = ref.get()

    with open('students_data.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['ID', 'Name', 'Total Attendance', 'Last Attendance Time'])

        for key, value in data.items():
            writer.writerow([key, value['name'], value['total_attendance'], value['last_attendance_time']])

    print("Data exported to students_data.csv")

cv2.namedWindow("Face Attendance")
cv2.setMouseCallback("Face Attendance", check_click)

while True:
    success, img = cap.read()

    if not start_program:
        # Display the welcome screen with the start button
        cv2.imshow("Face Attendance", welcome_screen)
    else:
        # The main program logic
        imgSized = cv2.resize(img, (0, 0), None, 0.25, 0.25)
        imgSized = cv2.cvtColor(imgSized, cv2.COLOR_BGR2RGB)

        faceCurFrame = face_recognition.face_locations(imgSized)
        encodeCurFrame = face_recognition.face_encodings(imgSized, faceCurFrame)

        imgBackground[180:180 + cam_width, 75:75 + cam_height] = img

        x_offset = 814
        y_offset = 0
        imgBackground[y_offset:y_offset + imgModeList[modeType].shape[0],
                      x_offset:x_offset + imgModeList[modeType].shape[1]] = imgModeList[modeType]

        detected_faces = []

        if faceCurFrame:
            for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
                matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
                faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
                matchIndex = np.argmin(faceDis)

                if matches[matchIndex]:
                    y1, x2, y2, x1 = faceLoc
                    y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                    bbox = 80 + x1, 20 + y2, x2 - x1, y2 - y1
                    imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)

                    id = studentIds[matchIndex]
                    detected_faces.append((id, faceLoc))

            for id, faceLoc in detected_faces:
                if counter == 0:
                    cvzone.putTextRect(imgBackground, "Loading", (275, 480))
                    cv2.imshow("Face Attendance", imgBackground)
                    cv2.waitKey(1)

                    counter = 1
                    modeType = 1

            if counter != 0:
                if counter == 1:
                    for id, faceLoc in detected_faces:
                        studentInfo = db.reference(f'Students/{id}').get()
                        print(studentInfo)

                        bucket = storage.bucket()
                        blob = bucket.get_blob(f'Images/{id}.jpg')
                        array = np.frombuffer(blob.download_as_string(), np.uint8)
                        imgStudent = cv2.imdecode(array, cv2.IMREAD_COLOR)

                        dateTimeObject = datetime.strptime(studentInfo['last_attendance_time'], "%Y-%m-%d %H:%M:%S")
                        secElapsed = (datetime.now() - dateTimeObject).total_seconds()
                        print(secElapsed)

                        if secElapsed > 30:
                            ref = db.reference(f'Students/{id}')
                            studentInfo['total_attendance'] += 1
                            ref.child('total_attendance').set(studentInfo['total_attendance'])
                            ref.child('last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                        else:
                            modeType = 3
                            counter = 0
                            imgBackground[y_offset:y_offset + imgModeList[modeType].shape[0],
                                          x_offset:x_offset + imgModeList[modeType].shape[1]] = imgModeList[modeType]

                if modeType != 3:
                    if 10 < counter < 20:
                        modeType = 2

                    imgBackground[y_offset:y_offset + imgModeList[modeType].shape[0],
                                  x_offset:x_offset + imgModeList[modeType].shape[1]] = imgModeList[modeType]

                    if counter <= 10:
                        for id, faceLoc in detected_faces:
                            studentInfo = db.reference(f'Students/{id}').get()

                            cv2.putText(imgBackground, str(studentInfo['name']),
                                        (1003, 555),  # location
                                        cv2.FONT_HERSHEY_DUPLEX, 0.6,
                                        (255, 255, 255), 1)
                            cv2.putText(imgBackground, str(studentInfo['ID']),
                                        (1003, 590),  # location
                                        cv2.FONT_HERSHEY_DUPLEX, 0.6,
                                        (255, 255, 255), 1)
                            cv2.putText(imgBackground, str(studentInfo['total_attendance']),
                                        (930, 180),  # location
                                        cv2.FONT_HERSHEY_DUPLEX, 0.6,
                                        (255, 255, 255), 1)

                            imgBackground[266:266 + 216, 950:950 + 216] = imgStudent

                counter += 1

                if counter >= 20:
                    counter = 0
                    modeType = 0
                    studentInfo = []
                    imgStudent = []
                    imgBackground[y_offset:y_offset + imgModeList[modeType].shape[0],
                                  x_offset:x_offset + imgModeList[modeType].shape[1]] = imgModeList[modeType]
        else:
            modeType = 0
            counter = 0

        cv2.imshow("Face Attendance", imgBackground)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
