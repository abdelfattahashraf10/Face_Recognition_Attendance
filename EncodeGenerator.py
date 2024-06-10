# import cv2
# import face_recognition
# import pickle
# import os
# # firebase imports
# import firebase_admin
# from firebase_admin import credentials
# from firebase_admin import db
# from firebase_admin import storage

# cred = credentials.Certificate("./serviceAccountKey.json")
# firebase_admin.initialize_app(cred, {
#     'databaseURL': "https://faceattendancerealtime-7a66f-default-rtdb.firebaseio.com/",
#     'storageBucket': "faceattendancerealtime-7a66f.appspot.com"
# })



# # import the student images
# folderPath = 'Images'
# imgPathList = os.listdir(folderPath)
# print(imgPathList)
# imgList = []
# studentIds = []
# # importing the modes images into a list
# for path in imgPathList:  # Iterate over the list of paths
#     imgList.append(cv2.imread(os.path.join(folderPath, path)))
#     # for splitting the extension 
#     studentIds.append(os.path.splitext(path)[0])
    
#     # uploading images to database 
#     fileName = f'{folderPath}/{path}'
#     bucket = storage.bucket()
#     blob = bucket.blob(fileName)
#     blob.upload_from_filename(fileName)
    
    
# print(studentIds)

# def findEncodings(imagesList):
#     encodeList = []
#     for img in imagesList:
#         # from BGR to RGB           open-cv(BGR)     face_recognition(RBB)
#         img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
#         encode = face_recognition.face_encodings(img)[0]
#         encodeList.append(encode)
    
#     return encodeList

# print("Encoding Started....")
# encodeListKnown = findEncodings(imgList)
# # print(encodeListKnown)
# # we need to save the names(IDs) with the encoding
# encodingListKnownWithIds = [encodeListKnown, studentIds]
# print("Encoding Complete")


# # Generate the pickle file
# encodeFile = open("EncodeFile.p", 'wb')
# pickle.dump(encodingListKnownWithIds, encodeFile)
# encodeFile.close()
# print("Encoding File Saved")


import cv2
import face_recognition
import pickle
import os
import firebase_admin
from firebase_admin import credentials, db, storage

# Initialize Firebase
cred = credentials.Certificate("./serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://faceattendancerealtime-7a66f-default-rtdb.firebaseio.com/",
    'storageBucket': "faceattendancerealtime-7a66f.appspot.com"
})

# Function to load and encode images
def load_and_encode_images(folder_path):
    img_paths = os.listdir(folder_path)
    img_list = []
    student_ids = []
    
    for path in img_paths:
        # Load image
        img = cv2.imread(os.path.join(folder_path, path))
        if img is None:
            print(f"Error loading image: {path}")
            continue
        
        img_list.append(img)
        student_ids.append(os.path.splitext(path)[0])
        
        # Upload image to Firebase storage
        try:
            file_name = f'{folder_path}/{path}'
            bucket = storage.bucket()
            blob = bucket.blob(file_name)
            blob.upload_from_filename(file_name)
        except Exception as e:
            print(f"Error uploading image {path} to Firebase: {e}")

    return img_list, student_ids

# Function to find encodings of images
def find_encodings(images_list):
    encode_list = []
    for img in images_list:
        try:
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            encodes = face_recognition.face_encodings(img_rgb)
            if encodes:
                encode_list.append(encodes[0])
            else:
                print("No face found in the image.")
        except Exception as e:
            print(f"Error encoding image: {e}")
    
    return encode_list

# Main process
if __name__ == "__main__":
    folder_path = 'Images'
    img_list, student_ids = load_and_encode_images(folder_path)
    
    if img_list:
        print(f"Loaded images: {len(img_list)}")
        print("Encoding Started....")
        encode_list_known = find_encodings(img_list)
        
        if encode_list_known:
            print("Encoding Complete")
            # Save the encodings and IDs
            encoding_list_known_with_ids = [encode_list_known, student_ids]
            
            with open("EncodeFile.p", 'wb') as encode_file:
                pickle.dump(encoding_list_known_with_ids, encode_file)
            print("Encoding File Saved")
        else:
            print("No encodings were found.")
    else:
        print("No images to process.")
