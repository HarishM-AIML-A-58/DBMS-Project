
# Attendance Management System 📚💻

## Overview 🌟
This system leverages facial recognition to mark student attendance. It integrates with a MySQL database to store attendance data, course information, and student details. The system allows for both automatic and manual attendance marking, with an easy-to-use GUI for admin interaction.

### Key Features:
- Facial recognition for attendance marking using OpenCV and face_recognition.
- Student information and attendance stored in a MySQL database.
- Real-time attendance tracking via camera feed.
- Admin interface for managing student attendance data.
- CSV logging for attendance history.

## Technologies Used 🛠️
- Python 3.x
- OpenCV for facial recognition
- face_recognition library
- MySQL for database management
- Tkinter for the GUI
- PIL for image handling

## Database Structure 🗃️
### 1. `Atnd` Table:
- **Name**: Student Name
- **Time**: Date and time of attendance
- **RollNo**: Unique identifier for the student

### 2. `Course` Table:
- **CourseID**: Course Identifier
- **RollNo**: Reference to the student
- **Course_Name**: Name of the course

### 3. `Enrollment` Table:
- **Enrollment_ID**: Unique enrollment ID
- **RollNo**: Reference to the student
- **CourseID**: Reference to the course

### 4. `Student_information` Table:
- **RollNo**: Reference to the student
- **Name**: Student Name
- **CourseID**: Reference to the course
- **EnrollmentID**: Reference to the enrollment ID
- **Attendance**: Attendance percentage

## How It Works 🔍
1. The system captures images from a webcam.
2. It detects faces in the video feed and compares them to stored images in a pre-configured directory.
3. If a match is found, the student's attendance is recorded in the database.
4. The system also checks for blinking to ensure that the student is present and alert.
5. Admins can view and modify attendance records through a GUI interface.

## Requirements 📦
- Python 3.x
- OpenCV: `pip install opencv-python`
- face_recognition: `pip install face_recognition`
- MySQL Connector: `pip install mysql-connector-python`
- Tkinter (Usually pre-installed with Python)
- Pillow (for image handling): `pip install pillow`

## Getting Started 🚀
1. Install the required libraries using the commands above.
2. Set up a MySQL database and create the necessary tables (SQL code provided in the script).
3. Place known faces in the `faces_known` directory.
4. Run the script to start the attendance system.

## Future Improvements 🚧
- Implement real-time notifications for students whose attendance is marked.
- Enhance the facial recognition model to handle different lighting conditions.
- Integrate the system with an online student portal.

## Author 👨‍💻
Harish M.
