#!/usr/bin/env python
# coding: utf-8

# In[1]:


from copy import deepcopy
from functools import total_ordering
import pandas as pd
import random
import pygsheets
import datetime
import time


# In[3]:


gc = pygsheets.authorize(service_account_file='trial-353909-d66e1013be7e.json')
# opening spread sheet
sheet = gc.open('GRE Vocab')
# get the first worksheet
wk_inp = input("Which worksheet to use? [1/2/3]:  ")
while (wk_inp not in ["1","2","3"]):
    wk_inp = input("Enter again: Which worksheet to use? [1/2/3]:  ")

wksheet = sheet[int(wk_inp)-1]


# In[6]:


df_vocab = wksheet.get_as_df()
df_vocab = df_vocab[df_vocab['Word'].notna()]
df_vocab = df_vocab[df_vocab['Word']!=""]

time_taken_for_answering = 0
max_input_time = 30

total_quiz_time = 0

# In[11]:


def getQuestion(df, mode):
    
    df = df.loc[df['Done']==False]
    if len(df)<=0:
        return 0,0,0,0,0
    ind = random.choice(df.index)

    df.loc[ind, 'Done'] = True
    options = ["{NO OPTION}","{NO OPTION}","{NO OPTION}","{NO OPTION}"]
    if mode == "1":
        ques = df.loc[ind, 'Word']
    else:
        ques = str(df.loc[ind, 'Meaning']).split('{')[0]

    indexes = [0,1,2,3]
    random.shuffle(indexes)

    if int(mode) == 1:
        options[indexes[0]] = str(df.loc[ind, 'Meaning']).split('{')[0]
    else:
        options[indexes[0]] = str(df.loc[ind, 'Word'])

    # removing the correct row
    df = df.loc[df['Done']==False]

    opt_df = df.sample(min(3,len(df)))
    i=1
    for idx in opt_df.index:
        if mode == "1":
            options[indexes[i]] = str(df.loc[idx, 'Meaning']).split('{')[0]
        else:
            options[indexes[i]] = str(df.loc[idx, 'Word'])
        i += 1
    try:
        ques==0
    except:
        print(ques)
    return ques, options, indexes[0], df, ind


# In[ ]:


def start_revision(rev_list, df):
    
    if wk_inp != "3":
        rev_sheet = sheet[2].get_as_df()
        for ind in rev_list:
            # Inserting in new sheet
            if df.loc[ind,"Word"] not in rev_sheet["Word"].unique():
                rev_sheet = pd.concat([rev_sheet, df.loc[[ind]]])
            # rev_sheet = rev_sheet.append(df.loc[[ind]])
        sheet[2].set_dataframe(rev_sheet, 'A2', copy_head = False)

    for ind in rev_list:
        print(' - '*5)
        print("Word:\t\t", df.loc[ind, 'Word'])
        print("Meaning:\t", df.loc[ind, 'Meaning'])
        print("Synonyms:\t", df.loc[ind, 'Synonyms'])
        inp = input("Next? [y/n]: ")
        while inp not in ["y","n"]:
            inp = input("Enter again : Next? [y/n]: ")
        if inp == "n":
            break

    return


# In[12]:


def end_game(score, high, revision_list, df):
    print("Total Time To Complete The Quiz (in minutes): ", total_quiz_time/60)
    print()
    print("*"*15)
    print("Completed!")
    print("Your performance: ",str(score) + "/" + str(high))
    print("*"*15)
    if not revision_list:
        return
    else:
        inp = input("Would you like to start revision? [y/n]:  ")
        while inp not in ["y","n"]:
            inp = input("Enter again : Start revision? [y/n]:  ")
        if (inp == "y"):
            start_revision(revision_list, df)
    return


# In[13]:


def display_ques(question, opts, turn):
    print('-'*10)
    print("Q"+str(turn)+":\t", end="")
    print(question)
    i=1
    for opt in opts:
        print("\t",end = "")
        print(str(i)+"."+"\t", end = "")
        print(opt)
        i+=1


# In[14]:


def check_answer(correct_opt, score, high, rev_list, df):
    st_time = time.time()
    response = input("Correct Option [1/2/3/4]:  ")
    end_time = time.time()
    global time_taken_for_answering
    time_taken_for_answering = end_time-st_time
    while response not in ["1","2","3","4","5"]:
        st_time = time.time()
        response = input("Enter again: Correct Option [1/2/3/4]:\t")
        end_time = time.time()
        time_taken_for_answering = end_time-st_time
    if int(response)-1 == correct_opt:
        return True
    if int(response) == 5:
        end_game(score, high-1, rev_list, df)
        return -1
        
    return False


# In[15]:


def ReviseDate(df, date, level, mode):
    score = 0
    rev_lst = []

    df_temp = pd.DataFrame(list(df.columns))

    date_list = df["Date"].unique()
    first = True

    if not (date == "all" or date == "" or date == "anki" or date == "manhattan"):
        dates = date.split(", ")
        for date_ in dates:
            if date_ not in date_list:
                print("NOT A VALID DATE : ", date_)
                print("starting again ...")
                return startRevise(df, wk_inp)
            else:
                if first==True:
                    first=False
                    df_temp = df.loc[df['Date'] == date_]
                else:
                    df_temp = pd.concat([df_temp, df.loc[df['Date'] == date_]])
    elif date == "anki":
        date_anki_list = date_list[:26]
        for date_ in date_anki_list:
            if first==True:
                first=False
                df_temp = df.loc[df['Date'] == date_]
            else:
                df_temp = pd.concat([df_temp, df.loc[df['Date'] == date_]])
    elif date == "manhattan":
        date_anki_list = date_list[26:]
        for date_ in date_anki_list:
            if first==True:
                first=False
                df_temp = df.loc[df['Date'] == date_]
            else:
                df_temp = pd.concat([df_temp, df.loc[df['Date'] == date_]])
    else:
        df_temp = df.copy(deep=True)
    
    if level=="Hard":
        df_temp = df_temp.loc[df_temp['Level'] == "Hard"]
        print("Sampling from hard questions ...")
    else:
        print("Sampling from all questions ... ")

    num = input("How many questions? [Enter \'\' for all]:  ")

    if num != '':
        df_temp = df_temp.sample(min(int(num), len(df_temp)))

    if len(df_temp)<=0:
        print("NOT A VALID DATE")
        return 0
    else:
        print("Number of questions: ",len(df_temp))

    df_temp['Done'] = False
    ques, options, ans = '','',''

    turn = 1

    global total_quiz_time
    total_quiz_time = time.time()

    while(ques!=0):
        ques, options, ans, df_temp, idx = getQuestion(df_temp, mode)

        if ques == 0:
            total_quiz_time = time.time() - total_quiz_time
            end_game(score, turn-1, rev_lst,df)
            return 1
        
        display_ques(ques, options, turn)

        out = check_answer(ans, score, turn, rev_lst, df)
        print("Time Taken: ",time_taken_for_answering)
        if out == True:
            score+=1
            print("Correct Answer, hooray!")
            if len(df.loc[idx, 'Synonyms'])>0 :
                print("Synonyms: ", df.loc[idx, 'Synonyms'])
            if time_taken_for_answering >= max_input_time:
                rev_lst.append(idx)
            # print(time_taken_for_answering)
        elif out == False:
            print("Wrong answer, no worries, do better next time :)")
            print("Correct Answer was option: ", ans+1)
            # enter in the revision list
            rev_lst.append(idx)
        

        else:
            return -1
        turn +=1
        
    return 1


# In[ ]:


def choose_mode():
    mode = input("Mode [1/2]:  ")
    while mode not in ["1","2"]:
        mode = input("Enter again : Mode [1/2]:  ")
    return mode


# In[ ]:


def startRevise(df, wk):
    print("STARTING")
    print("-"*20)
    if wk=="1" or wk == "3":
        if wk == "1":
            date_list = df["Date"].unique()
            print("You can choose from these dates: ", date_list)
            date = input("Enter date of Revision in %Yyyy %dd Format: (like \"June 15\"):  ")
        
        print("There are 2 modes of revision: 1. Words as prompts, 2. Meanings as prompts")
        mode = choose_mode()
        level = input("Enter the level of questions to revise [Hard/'']:  ")
        if wk == "1":
            ReviseDate(df, date, level, mode)
        else:
            ReviseDate(df, "all",level, mode)
    if wk== "2":
        date = "X"
        print("There are 2 modes of revision: 1. Words as prompts, 2. Meanings as prompts")
        mode = choose_mode()
        ReviseDate(df, date, "", mode)


# In[ ]:


startRevise(df_vocab, wk_inp)

