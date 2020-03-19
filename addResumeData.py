# Import packagess
import json
import sqlite3
import pdfplumber
import re
import string
from string import digits
import os
from docx import Document

# Connect to sqlite database
conn = sqlite3.connect('resumedb.sqlite')
cur = conn.cursor()

# If the table doesn't exist, create one
cur.execute('''CREATE TABLE IF NOT EXISTS Resume (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    filename TEXT NOT NULL,
    content TEXT NOT NULL,
    hired TEXT NOT NULL,
    UNIQUE(filename)
)''')

# Prompt for the folder of resumes to add
folder = input('Enter folder name: ')
# if len(folder) == 0:
#     folder = "Resumes"

# Define acceptance inputs for hired status and file type
hiredInputs = ['y','yes','Yes','Y','YES']
notHiredInputs = ['n','no','No','N','NO']

# Hold off on removing all dashes
string.punctuation = string.punctuation.replace('-','')

# Only accept a hired status input of yes or no
while True:
    hiredStatus = input('Were these applicants hired? ')
    if hiredStatus in hiredInputs:
        hiredVal = 'Y'
        break
    elif hiredStatus in notHiredInputs:
        hiredVal = 'N'
        break
    else:
        print("Please enter yes or no")
        continue

# Loop through the files in the given folder
for fname in os.listdir(folder):

# If the file is already in the database, skip
    cur.execute('SELECT filename FROM Resume')
    rows = cur.fetchall()
    if (fname,) in rows:
        continue
    text = str()
    if fname.endswith('.pdf'):
        print(fname)
        pdf = pdfplumber.open(folder+'/'+fname)
        for page in pdf.pages :
            text_new = page.extract_text()
            if text_new is None:
                continue
            text = text + text_new
# Cleanup the text
        text = text.replace('\n●'," ")
        text = text.replace('●',"")
        text = text.replace('•',"")
        text = text.replace('',"")
        text = [''.join(c for c in s if c not in string.punctuation) for s in text]
        text = ''.join([x for x in text if x in string.printable])
        text = re.sub("((?<=[\s\.])\-+)|(\-+(?=[\s\.]))",'', text)
        text = text.replace('\n'," ")
        text = text.replace('\xa0',"")
        text = re.sub('\s+',' ', text).strip()
        text = text.lower()
    elif fname.endswith('.txt'):
        print(fname)
        file = open(folder+'/'+fname)
        while True:
            line = file.readline()
            if not line:
                break
            line = line.rstrip()
            text = text + ' ' + line
            text = text.lower()
        file.close()
    elif fname.endswith('.docx'):
        print(fname)
        document = Document(folder+'/'+fname)
        for paragraph in document.paragraphs:
            text = text + ' ' + paragraph.text
        text = text.translate(str.maketrans('','',string.punctuation))
        text = text.replace('\n●',"")
        text = text.replace('●',"")
        text = text.replace('•',"")
        text = text.replace('',"")
        text = text.replace('–',"")
        text = text.replace('\n',"")
        text = text.replace('\xa0',"")
        text = re.sub('\s+',' ', text).strip()
        text = text.lower()
    else:
        print('Cannot process file :',fname)
        continue
    if len(text) < 200:
        print('Error processing :',fname)
        continue

# Add the data into the database for this resume
    cur.execute('''INSERT OR IGNORE INTO Resume (filename,content, hired)
        VALUES (?,?,?)''', (fname, text, hiredVal) )


conn.commit()
