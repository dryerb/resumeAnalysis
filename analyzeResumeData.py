# Import packagess
import sqlite3
import nltk
import pandas as pd
import numpy as np
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string
from collections import defaultdict
from collections import Counter
import matplotlib
import matplotlib.pyplot as plt

print('Working on it...')

# Connect to sqlite database
conn = sqlite3.connect('resumedb.sqlite')
cur = conn.cursor()

# Initialize dictionaries
hiredContent = dict()
notHiredContent = dict()

cur.execute('SELECT * FROM Resume')

wordList = []
tokensFiltered = []
freqDict = dict()

# For every row of data, tokenize the text, remove stop words,
# only add each word once
stopWords = set(stopwords.words('english'))
pluralWords = ['schools','students','teachers','designed']
removeWords = stopWords.union(pluralWords)

resumeNumber = 0


for row in cur:
    resumeNumber = resumeNumber + 1
    if (resumeNumber % 10 == 0):
        print('Analyzed ', resumeNumber,' resumes')
    text = row[2]
    tokens = word_tokenize(text)
    for w in tokens:
        if w not in removeWords:
            tokensFiltered.append(w)
    for word in tokensFiltered:
        if word not in wordList:
            wordList.append(word)
wordList = [s for s in wordList if s]


# Sort the list of words
wordList.sort


# Set the default values in the dictionary as lists, initialize variables
freqDistHired = defaultdict(list)
countNumHired = defaultdict(list)
freqDistNotHired = defaultdict(list)
countNumNotHired = defaultdict(list)
hiredResumes = 0
notHiredResumes = 0


# For each row, find the frequency of each word in the word list in the text,
# split by hired and non-hired
cur.execute('SELECT * FROM Resume')
for row in cur:
    totalWords = len(row[2])
    text = row[2]
    text_list = text.split()
    text_list = ['school' if x == 'schools' else x for x in text_list]
    text_list = ['teacher' if x == 'teachers' else x for x in text_list]
    text_list = ['student' if x == 'students' else x for x in text_list]
    text_list = ['design' if x == 'designed' else x for x in text_list]
    hired = row[3]
    if hired == 'Y':
        hiredResumes = hiredResumes + 1
        for word in wordList:
            freqDistHired[word].append((text_list.count(word)/totalWords)*1000)
            if text_list.count(word) > 0:
                countNumHired[word].append(1)
            else:
                countNumHired[word].append(0)
    elif hired == 'N':
        notHiredResumes = notHiredResumes + 1
        for word in wordList:
            freqDistNotHired[word].append((text_list.count(word)/totalWords)*1000)
            if text_list.count(word) > 0:
                countNumNotHired[word].append(1)
            else:
                countNumNotHired[word].append(0)
    else:
        continue


# Create a dictionary for average word count for hired and non-hired,
# use the keys from the frequency dictionary, and set the values
# as the average count across the list (represting each resume)
hiredAverage = dict.fromkeys(freqDistHired.keys(),[])
for key in freqDistHired:
    hiredAverage[key] = sum(freqDistHired[key])/len(freqDistHired[key])

notHiredAverage = dict.fromkeys(freqDistNotHired.keys(),[])
for key in freqDistNotHired:
    notHiredAverage[key] = sum(freqDistNotHired[key])/len(freqDistNotHired[key])

# What percentages of resumes had this word
hiredInstances = dict.fromkeys(countNumHired.keys(),[])
for key in countNumHired:
    hiredInstances[key] = sum(countNumHired[key])/hiredResumes

notHiredInstances = dict.fromkeys(countNumNotHired.keys(),[])
for key in countNumNotHired:
    notHiredInstances[key] = sum(countNumNotHired[key])/notHiredResumes

# Look for the biggest diffs (hired minus not)
hiredMinusNotDiff = dict.fromkeys(hiredInstances.keys(),[])
for key in hiredInstances:
    if key in notHiredInstances:
        hiredMinusNotDiff[key] = hiredInstances[key]-notHiredInstances[key]
    else:
        hiredMinusNotDiff[key] = hiredInstances[key]

# Look for the biggest diffs (not minus hired)
notMinusHiredDiff = dict.fromkeys(notHiredInstances.keys(),[])
for key in notHiredInstances:
    if key in hiredInstances:
        notMinusHiredDiff[key] = notHiredInstances[key]-hiredInstances[key]
    else:
        notMinusHiredDiff[key] = notHiredInstances[key]

# Find the 20 highest values in the dictionary of hired/non-hired averages
counterHired = Counter(hiredAverage)
highest20Hired = counterHired.most_common(20)

counterNotHired = Counter(notHiredAverage)
highest20NotHired = counterNotHired.most_common(20)

# Find the 20 highest differences (hired - not)
counterHiredNotDiffs = Counter(hiredMinusNotDiff)
highest20CountHiredDiffs = counterHiredNotDiffs.most_common(20)

# Find the 20 highest differences (not - minus)
counterNotHiredDiffs = Counter(notMinusHiredDiff)
highest20CountNotHiredDiffs = counterNotHiredDiffs.most_common(20)

# Key words identified for analysis
keyWords = (['mission','coach','collaborate','synthesis','facilitate',
            'design','consult','communicate'])

hiredKeyWords = []
notHiredKeyWords = []

for word in keyWords:
    if word in hiredInstances:
        hiredKeyWords.append(hiredInstances[word])
    else:
        hiredKeyWords.append(0)
    if word in notHiredInstances:
        notHiredKeyWords.append(notHiredInstances[word])
    else:
        notHiredKeyWords.append(0)



# Initialize lists for graphics
xlabelsHired = []
yvalsHired = []
xlabelsNotHired = []
yvalsNotHired = []
xlabelsHiredDiffs = []
yvalsHiredDiffs = []
xlabelsNotDiffs = []
yvalsNotDiffs = []

# Print the top 20 words for hired and non-hired resumes
print('Top 20 words for hired resumes:')
for i in highest20Hired:
    print(i[0]," :",i[1]," ")
    xlabelsHired.append(i[0])
    yvalsHired.append(i[1])

print('Top 20 words for not hired resumes:')
for i in highest20NotHired:
    print(i[0]," :",i[1]," ")
    xlabelsNotHired.append(i[0])
    yvalsNotHired.append(i[1])

# Print the top 20 hired minus not differences
print('Top 20 words found in more hired resumes: ')
for i in highest20CountHiredDiffs:
    word = i[0]
    print(i[0]," :",hiredInstances[word]," ",notHiredInstances[word]," ",i[1]," ")
    xlabelsHiredDiffs.append(i[0])
    yvalsHiredDiffs.append(i[1])

# Print the top 20 not minus hired differences
print('Top 20 words found in more hired resumes: ')
for i in highest20CountNotHiredDiffs:
    word = i[0]
    print(i[0]," :",hiredInstances[word]," ",notHiredInstances[word]," ",i[1]," ")
    xlabelsNotDiffs.append(i[0])
    yvalsNotDiffs.append(i[1])

# Plot the top 20 words for hired and non-hired resumes
hiredPlot = plt.figure(0)
plt.bar(xlabelsHired,height=yvalsHired,tick_label=xlabelsHired)
plt.xticks(rotation=90)
plt.title('Hired resume analysis')
plt.tight_layout()
hiredPlot.savefig('Hired Resumes')

notHiredPlot = plt.figure(1)
plt.bar(xlabelsNotHired,height=yvalsNotHired,tick_label=xlabelsNotHired)
plt.xticks(rotation=90)
plt.title('Not hired resume analysis')
plt.tight_layout()
notHiredPlot.savefig('Not Hired Resumes')

hiredDiffsPlot = plt.figure(2)
plt.bar(xlabelsHiredDiffs,height=yvalsHiredDiffs,tick_label=xlabelsHiredDiffs)
plt.xticks(rotation=90)
plt.title('Percentage of hired resumes with a word minus not-hired percentage')
plt.tight_layout()
hiredDiffsPlot.savefig('Difference plot (hired minus not)')

notHiredDiffsPlot = plt.figure(3)
plt.bar(xlabelsNotDiffs,height=yvalsNotDiffs,tick_label=xlabelsNotDiffs)
plt.xticks(rotation=90)
plt.title('Percentage of not-hired resumes with a word minus hired percentage')
plt.tight_layout()
notHiredDiffsPlot.savefig('Difference plot (not minus hired)')

keyWordPlot = plt.figure(4)
barWidthKeyWords = 0.35
indexKeyWordsHired = np.arange(len(keyWords))
indexKeyWordsNotHired = [x+barWidthKeyWords for x in indexKeyWordsHired]

plt.bar(indexKeyWordsHired,hiredKeyWords,width=barWidthKeyWords,label='Hired')
plt.bar(indexKeyWordsNotHired,notHiredKeyWords,width=barWidthKeyWords,label='Not Hired')

plt.xlabel('Key word')
plt.ylabel('Percentage of resumes with key word')
plt.xticks((indexKeyWordsHired+barWidthKeyWords),keyWords,rotation=90)
plt.legend()
plt.tight_layout()

keyWordPlot.savefig('Key Word Plot')


# State how many resumes were evaluated
print('Evaluated: ', hiredResumes,' hired resumes')
print('Evaluated: ', notHiredResumes,' not hired resumes')


conn.commit()
