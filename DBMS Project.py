import mysql.connector
import random
import cv2
import numpy as np
import face_recognition
import os
import csv
from datetime import datetime
from scipy.spatial import distance as dist
import time
from tkinter import Tk, Label, Frame, Toplevel, Scrollbar, Button, PhotoImage
from tkinter import ttk
from PIL import Image, ImageTk

# Database connection and setup
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="laboon123",
    database="management"
)
cursor = db.cursor()

# Create SQL tables if they do not exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Atnd (
        Name VARCHAR(255),
        Time DATETIME,
        RollNo INT,
        PRIMARY KEY (RollNo)
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS course (
        CourseID INT PRIMARY KEY,
        RollNo INT,
        Course_Name VARCHAR(255),
        FOREIGN KEY (RollNo) REFERENCES Atnd(RollNo)
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS enrollment (
        Enrollment_ID INT PRIMARY KEY,
        RollNo INT,
        CourseID INT,
        FOREIGN KEY (RollNo) REFERENCES Atnd(RollNo),
        FOREIGN KEY (CourseID) REFERENCES course(CourseID)
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS student_information (
        RollNo INT,
        Name VARCHAR(255),
        CourseID INT,
        EnrollmentID INT,
        Attendance INT,
        PRIMARY KEY (RollNo),
        FOREIGN KEY (CourseID) REFERENCES course(CourseID),
        FOREIGN KEY (EnrollmentID) REFERENCES enrollment(Enrollment_ID)
    )
''')

def show_popup(message):
    popup = Toplevel(root)
    popup.title("Notification")
    popup.geometry("300x150")
    popup.config(bg='#ffffff')

    message_label = Label(popup, text=message, font=('Arial', 12), bg='#ffffff', fg='#333333')
    message_label.pack(expand=True)

    root.after(1000, popup.destroy)

# Function to update table display with data from the 'Atnd' table
def update_table_display():
    for row in tree.get_children():
        tree.delete(row)

    cursor.execute("SELECT * FROM Atnd")
    rows = cursor.fetchall()

    for row in rows:
        tree.insert("", "end", values=row)

def save_to_csv(name):
    with open(r'C:\Users\avish\OneDrive\Desktop\DS Programs\fronte\attendance_log.csv', 'r+') as f:
        datlist = f.readlines()
        nlist = []
        for line in datlist:
            ent = line.split(',')
            nlist.append(ent[0])
        if name not in nlist:
            now = datetime.now()
            dtString = now.strftime('%Y-%m-%d %H:%M:%S')
            f.writelines(f'\n{name},{dtString}')

def close_db_connection():
    cursor.close()
    db.close()

# Facial recognition and attendance marking logic
path = r"C:\Users\avish\OneDrive\Documents\+=AAAAA\cmon\faces_known"
images = []
classNames = []
myList = os.listdir(path)

for person in myList:
    personFolder = os.path.join(path, person)
    if os.path.isdir(personFolder):
        for imgName in os.listdir(personFolder):
            imgPath = os.path.join(personFolder, imgName)
            curImg = cv2.imread(imgPath)
            if curImg is not None:
                images.append(curImg)
                classNames.append(person)

def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList

def eye_aspect_ratio(eye):
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    C = dist.euclidean(eye[0], eye[3])
    ear = (A + B) / (2.0 * C)
    return ear

def detect_blink(landmarks):
    leftEye = landmarks['left_eye']
    rightEye = landmarks['right_eye']
    leftEAR = eye_aspect_ratio(leftEye)
    rightEAR = eye_aspect_ratio(rightEye)
    ear = (leftEAR + rightEAR) / 2.0
    return ear

encodeListKnown = findEncodings(images)

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320) 
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

BLINK_THRESHOLD = 0.33
CONSEC_FRAMES = 3
BLINK_COOLDOWN = 3

blink_counter = 0
blinked = False
last_blink_time = time.time()
ear_history = []

save_folder = r"C:\Users\avish\OneDrive\Documents\+=AAAAA\cmon\captured_enc"

def show_frame():
    global blink_counter, blinked, last_blink_time, ear_history
    success, img = cap.read()
    if not success:
        root.after(10, show_frame)
        return

    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    facesCurFrame = face_recognition.face_locations(imgS)
    encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)
    faceLandmarksList = face_recognition.face_landmarks(imgS)

    for encodeFace, faceLoc, landmarks in zip(encodesCurFrame, facesCurFrame, faceLandmarksList):
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
        matchIndex = np.argmin(faceDis)
        cords = (0, 255, 0)

        if faceDis[matchIndex] < 0.50:
            name = classNames[matchIndex].upper()
            ear = detect_blink(landmarks)

            ear_history.append(ear)
            if len(ear_history) > CONSEC_FRAMES:
                ear_history.pop(0)
            
            avg_ear = sum(ear_history) / len(ear_history)

            if avg_ear < BLINK_THRESHOLD:
                blink_counter += 1
            else:
                if blink_counter >= CONSEC_FRAMES and (time.time() - last_blink_time) > BLINK_COOLDOWN:
                    blinked = True
                    last_blink_time = time.time()
                blink_counter = 0

            if blinked:
                markatnd(name)
                save_path = os.path.join(save_folder, f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.npy")
                np.save(save_path, encodeFace)
                blinked = False
        else:
            name = 'Unknown'
            cords = (0, 0, 255)

        y1, x2, y2, x1 = faceLoc
        y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
        cv2.rectangle(img, (x1, y1), (x2, y2), cords, 2)
        cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_pil = Image.fromarray(img)
    img_tk = ImageTk.PhotoImage(image=img_pil)
    label.imgtk = img_tk
    label.configure(image=img_tk)

    root.after(10, show_frame)

# Attendance registration function
def markatnd(name):
    cursor.execute("SELECT Name FROM Atnd WHERE Name = %s", (name,))
    result = cursor.fetchone()

    if result is None:
        rollno = random.randint(1000, 9999)  # Random roll number
        courseid = random.randint(100, 999)  # Random course ID
        enrollment_id = random.randint(1000, 9999)  # Random enrollment ID
        attendance = random.randint(1, 100)  # Random attendance value

        now = datetime.now()
        dtString = now.strftime('%Y-%m-%d %H:%M:%S')  # Date and time format

        cursor.execute("INSERT INTO Atnd (Name, Time, RollNo) VALUES (%s, %s, %s)", (name, dtString, rollno))
        cursor.execute("INSERT INTO course (CourseID, RollNo, Course_Name) VALUES (%s, %s, %s)", (courseid, rollno, 'Sample Course'))
        cursor.execute("INSERT INTO enrollment (Enrollment_ID, RollNo, CourseID) VALUES (%s, %s, %s)", (enrollment_id, rollno, courseid))
        cursor.execute("INSERT INTO student_information (RollNo, Name, CourseID, EnrollmentID, Attendance) VALUES (%s, %s, %s, %s, %s)", 
                       (rollno, name, courseid, enrollment_id, attendance))

        db.commit()
        update_table_display()
        save_to_csv(name)
        show_popup(f"Attendance marked for {name} at {dtString}")
    else:
        print(f"{name} is already marked for today.")

# Main attendance registration GUI
def run_attendance_gui():
    global root, label, tree

    # Close the first window (start_window)
    start_window.destroy()

    # Initialize main Tkinter window
    root = Tk()
    root.geometry("1300x800")

    label = Label(root)
    label.pack()

    frame_table = Frame(root)
    frame_table.pack()

    scrollbar_y = Scrollbar(frame_table, orient="vertical")
    scrollbar_y.pack(side="right", fill="y")

    tree = ttk.Treeview(frame_table, columns=("Name", "Time", "RollNo"), show="headings", yscrollcommand=scrollbar_y.set)
    tree.heading("Name", text="Name")
    tree.heading("Time", text="Time")
    tree.heading("RollNo", text="RollNo")
    tree.pack()

    scrollbar_y.config(command=tree.yview)

    # Display all previous records in the Atnd table when the program starts
    update_table_display()

    # Start the camera feed and update display
    root.after(10, show_frame)
    root.mainloop()

# Starting window with options for registering or modifying attendance
from tkinter import Tk, Label, Button, Entry
from PIL import Image, ImageTk

def modify_attendance_gui():
    # New window for modifying attendance
    modify_window = Toplevel(start_window)
    modify_window.title("Modify Attendance")
    modify_window.geometry("600x400")
    
    # Input fields for adding/updating records
    Label(modify_window, text="Name:").grid(row=0, column=0, padx=10, pady=10)
    name_entry = Entry(modify_window)
    name_entry.grid(row=0, column=1, padx=10, pady=10)

    Label(modify_window, text="Time:").grid(row=1, column=0, padx=10, pady=10)
    time_entry = Entry(modify_window)
    time_entry.grid(row=1, column=1, padx=10, pady=10)

    Label(modify_window, text="RollNo:").grid(row=2, column=0, padx=10, pady=10)
    rollno_entry = Entry(modify_window)
    rollno_entry.grid(row=2, column=1, padx=10, pady=10)

    def add_record():
        name = name_entry.get()
        time = time_entry.get()
        rollno = rollno_entry.get()

        if name and time and rollno:
            cursor.execute("INSERT INTO Atnd (Name, Time, RollNo) VALUES (%s, %s, %s)", (name, time, rollno))
            db.commit()
            update_table_display()
            show_popup(f"Record added for {name}")
        else:
            show_popup("Please fill in all fields.")

    def delete_record():
        rollno = rollno_entry.get()
        if rollno:
            cursor.execute("DELETE FROM Atnd WHERE RollNo = %s", (rollno,))
            db.commit()
            update_table_display()
            show_popup(f"Record with RollNo {rollno} deleted.")
        else:
            show_popup("Please enter a RollNo to delete.")

    def update_record():
        name = name_entry.get()
        time = time_entry.get()
        rollno = rollno_entry.get()

        if name and time and rollno:
            cursor.execute("UPDATE Atnd SET Name = %s, Time = %s WHERE RollNo = %s", (name, time, rollno))
            db.commit()
            update_table_display()
            show_popup(f"Record updated for RollNo {rollno}")
        else:
            show_popup("Please fill in all fields.")

    # Buttons for record operations
    Button(modify_window, text="Add Record", command=add_record).grid(row=3, column=0, padx=10, pady=20)
    Button(modify_window, text="Delete Record", command=delete_record).grid(row=3, column=1, padx=10, pady=20)
    Button(modify_window, text="Update Record", command=update_record).grid(row=3, column=2, padx=10, pady=20)

# Update the Modify Attendance button command to open modify_attendance_gui
def start_window_gui():
    global start_window
    start_window = Tk()
    start_window.title("Attendance System")
    start_window.geometry("1920x1080")

    bg_image = Image.open(r"C:\Users\avish\Downloads\Attendance-Management-System.jpg")
    bg_image = bg_image.resize((1920, 1080), Image.LANCZOS)
    bg_photo = ImageTk.PhotoImage(bg_image)

    bg_label = Label(start_window, image=bg_photo)
    bg_label.image = bg_photo
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    welcome_label = Label(start_window, text="Welcome, Admin", font=('Arial', 18, 'bold'), bg="white")
    welcome_label.place(x=20, y=20)

    register_btn = Button(start_window, text="Register Attendance", command=run_attendance_gui, width=40, height=4)
    register_btn.place(relx=0.5, rely=0.4, anchor="center")

    modify_btn = Button(start_window, text="Modify Attendance", command=modify_attendance_gui, width=40, height=4)
    modify_btn.place(relx=0.5, rely=0.5, anchor="center")

    start_window.mainloop()


# Start the program with the start window
start_window_gui()

