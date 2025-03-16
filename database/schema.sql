CREATE TABLE Users (
    UserID CHAR(10) PRIMARY KEY,
    UserName VARCHAR(45) NOT NULL,
    UserRole VARCHAR(7) NOT NULL,
    UserPass VARCHAR(12) NOT NULL
);

CREATE TABLE Students (
    UserID CHAR(10) REFERENCES Users(UserID),
    StudentClass VARCHAR(10) NOT NULL
);

CREATE TABLE Teachers (
    UserID CHAR(10) REFERENCES Users(UserID),
    TeacherFName VARCHAR(45) NOT NULL,
    TeacherLName VARCHAR(45) NOT NULL
);             
 
CREATE TABLE Events (
    EventID VARCHAR(10) PRIMARY KEY,
    EventName VARCHAR(45) NOT NULL,
    EventDate DATE NOT NULL,
    EventStartTime TIME NOT NULL,
    EventEndTime TIME NOT NULL,
    EventVenue VARCHAR(30) NOT NULL,
    UserID CHAR(10) REFERENCES Users(UserID)
);

CREATE TABLE Event_Participation (
    EventID VARCHAR(10) REFERENCES Events(EventID),
    UserID VARCHAR(10) REFERENCES Users(UserID),
    Responsibility VARCHAR(30) NOT NULL
);

CREATE TABLE Event_Files (
    FileID CHAR(10) PRIMARY KEY,
    EventID VARCHAR(10) REFERENCES Events(EventID),
    UserID CHAR(10) REFERENCES Users(UserID),
    FileName VARCHAR(45) NOT NULL,
    FileContent BYTEA,
    UploadDate DATE DEFAULT CURRENT_DATE
    FileApprovalStatus VARCHAR(10) DEFAULT 'Pending'
);

CREATE TABLE Feedback (
    FeedbackID CHAR(10) PRIMARY KEY,
    FileID CHAR(10) REFERENCES Event_Files(FileID),
    UserID CHAR(10) REFERENCES Users(UserID),
    Feedback VARCHAR(200),
    FeedbackDate DATE DEFAULT CURRENT_DATE
);