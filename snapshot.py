import streamlit as st
import pandas as pd
import datetime as dt
import numpy as np
import calStart 
from streamlit_gsheets import GSheetsConnection
import gspread
import random
import insert_event


### SETTING UP PAGE CONFIGURATION ###
st.set_page_config(
    page_title = "Snapshot",
    page_icon = " : )",
    layout = "wide",
    initial_sidebar_state="expanded",
)

st.image('snapshot_logo_2.png', width = 500)
st.markdown('##### Welcome to your personal journal! See your calendar events to reflect on your day. Upload your entries every day to maintain your routine, receive feedback, and schedule your next journaling session. Reflect on your past entries through the journal vault. Happy journaling!😊')
st.divider()

### DISPLAY THE GOAL ###
col1, col2, col3 = st.columns([1,1,1])

col1.markdown('## Enter your Metrics')
col1.markdown('**If you have not entered a goal this month, or you would like to update your goal, update below!**')
update_goal = col1.text_input('input a number between 1 and 30:', key = 'session_goal')
col1.markdown('**If you track your hours of sleep, enter it below!**')
hrs_sleep = col1.text_input('Enter a number rounded to the nearest half-hour:', key = 'sleep')

col2.markdown('## Goal Progress and Hours of Sleep')
col2.metric('Last night you got', value = f'{st.session_state.sleep} hours of sleep')

col3.markdown('## Daily Sleep')


### ESTABLISH CONNECTION TO SQL DB, FETCH DATA AND DISPLAY ###
conn = st.connection("gsheets", type = GSheetsConnection)

#LOAD IN JOURNAL VAULT
try:
    journal_vault = conn.read(worksheet = 'journal-vault')
except gspread.exceptions.WorksheetNotFound as e:
    print('journal vault not found')
    cols_create = pd.DataFrame({'Date':[], 'Events': [], 'Topic': [], 'Feedback': []})
    conn.create(worksheet = 'journal-vault', data = cols_create)
journal_vault = conn.read(worksheet = 'journal-vault')

#LOAD IN GOALS
try:
    goals_sheet = conn.read(worksheet = 'journal-goals')
except gspread.exceptions.WorksheetNotFound as e:
    print('not found')
    cols_create = pd.DataFrame({'Month': [],'Goal':[]})
    conn.create(worksheet = 'journal-goals', data = cols_create)
goals_sheet = conn.read(worksheet = 'journal-goals')

#LOAD IN SLEEP TRACKER
try:
    sleep_tracking = conn.read(worksheet = 'sleep-tracker')
except gspread.exceptions.WorksheetNotFound as e:
    print('not found')
    cols_create = pd.DataFrame({'Date': [],'Hours_sleep':[]})
    conn.create(worksheet = 'sleep-tracker', data = cols_create)
sleep_tracking = conn.read(worksheet = 'sleep-tracker')


if hrs_sleep:
    row_for_sleep = {'Date' : [str(dt.date.today())], 
             'Hours_sleep' : [int(st.session_state.sleep)]}
    as_df = pd.DataFrame(row_for_sleep, index = [0])
    sleep_tracker_updated = pd.concat([sleep_tracking, as_df], ignore_index = True).reset_index(drop = True)
    sleep_tracking = conn.update(worksheet = 'sleep-tracker', data = sleep_tracker_updated)


#sleep_tracking.Hours_sleep = sleep_tracking['Hours_sleep'].astype(int)
col3.line_chart(data = sleep_tracking, x = 'Date', y = 'Hours_sleep')



#get entries this month
month = int(dt.datetime.today().month)
entry_months = journal_vault['Date'].apply(lambda x: int(x[5:7]))
num_entries = sum(np.array(entry_months) == month)


### GET EVENTS FOR THE DAY ###
events_for_day, prompt, n_events = calStart.main()

#prompts from reddit https://www.reddit.com/r/Journaling/comments/r7bsmz/long_list_of_journal_prompts/
all_prompts = ['Are you taking enough risks in your life?', 
             'At what point in your life have you had the highest self-esteem?', 
             'Consider and reflect on what might be your “favorite failure".', 
             'How can you reframe one of your biggest regrets in life?', 
             'How did you bond with one of the best friends you have ever had?', 
             'How did your parents or caregivers try to influence or control your behavior when you were growing up?',
             'How do the opinions of others affect you?', 'How do you feel about asking for help?', 
             'How much do your current goals reflect your desires?', 
             'In what ways are you currently self-sabotaging or holding yourself back?', 
             'What are some small things that other people have done that really make your day?', 
             'What are some things that frustrate you?', 'What biases do you need to work on?', 
             'What could you do to make your life more meaningful?', 'What happens when you are angry?', 
             'What do you need to give yourself more credit for?', 
             'What is a boundary that you need to draw in your life?', 
             'What is a positive habit that you would really like to cultivate?',
             'What is a reminder that you would like to tell yourself next time you are in a downward spiral?',
             'What is holding you back from being more productive at the moment?']
dayPrompt = random.choice(all_prompts)
if 'dayPrompt' not in st.session_state:
    st.session_state.dayPrompt = dayPrompt

sleep_metric = f'You got {st.session_state.sleep} hours of sleep last night.'

if n_events == 0:
    string_opener = 'You had no events today! '
    string_ending = f'Hopefully you had some time to relax. Here is something to consider when you journal today: {st.session_state.dayPrompt}'

elif n_events<=3:
    string_opener = 'Today you went to '
    string_ending = f'. How did you feel about it? What was your favourite part? Here is something to consider when you journal today: {st.session_state.dayPrompt}'

elif 3<n_events<=5:
    string_opener = 'Woah you had a pretty busy today. You did '
    string_ending = f'. How are you feeling? Do you feel stressed at all? Here is something to consider when you journal today: {st.session_state.dayPrompt}'

else:
    string_opener = 'You had a super busy day! This is what you did today: '
    string_ending = f'. You should feel proud of yourself, you were super productive! Here is something to consider when you journal today: {st.session_state.dayPrompt}'

todays_full_prompt = string_opener + prompt + sleep_metric + string_ending

### IDENTIFY GOAL ###
#goals_sheet = conn.read(worksheet = 'journal-goals')
goals_sheet = goals_sheet.astype(int)

goal_month_df = goals_sheet.loc[goals_sheet['Month'] == month, 'Goal']
if goal_month_df.empty:
    goal = 'not set'
else:
    goal = goal_month_df.values[0]



if update_goal:
    new_goal_entry = {'Month': [month],
        'Goal': [st.session_state.session_goal]}
    if goals_sheet.loc[goals_sheet['Month'] == month, 'Goal'].empty:
        new_goal_df = pd.DataFrame(new_goal_entry, index = [0])
        goals_sheet = pd.concat([goals_sheet, new_goal_df], ignore_index = True)
    else: 
        goals_sheet.loc[goals_sheet['Month'] == month, 'Goal'] = int(update_goal)
        #print(goals_sheet)
    goals_sheet = conn.update(worksheet = 'journal-goals', data = goals_sheet)
    goal = st.session_state.session_goal




### DISPLAY THE JOURNAL ENTRY GOAL ###
#col2.markdown('## Goal Progress')
col2.metric('This month you have', value = f'{num_entries} entries')
col2.metric('Out of your goal of', value = f'{goal} entries')

if num_entries == goal: 
    col2.write('Congratulations! You have met your goal. Keep up the good work!')


### PROMPT GENERATION ###
st.markdown('### Prompt for the day')

##used chatgpt to get nice html textbox
st.markdown(
    f"""
    <div style="
        background-color: #ca9ce1;
        padding: 10px 20px;
        border-radius: 10px;
        color: #333333;
        font-size: 20px;
        border: 1px solid #A9A9A9;">
        {todays_full_prompt}
    
    """,
    unsafe_allow_html=True
)
### UPLOAD CAPABILITIES ###
journal_image = st.file_uploader("#### *Upload your reflection here:*", type= ['png', 'jpg', 'pdf'])

#generated using chat gpt
feedback_options = [
"You're doing great by taking time to reflect on your thoughts!",
"Journaling is an amazing habit—keep it up!",
"Your consistency in journaling shows incredible dedication!",
"Each entry is a step towards better self-awareness—well done!",
"You're building a meaningful record of your journey—great job!",
"It's inspiring to see you prioritize your mental well-being through journaling!",
"Writing your thoughts down is a powerful way to organize your mind—excellent work!",
"Your commitment to journaling will lead to deeper self-discovery!",
"You're creating a safe space for your thoughts and feelings—keep going!",
"Each journal entry is an investment in your personal growth—amazing work!",
"Reflecting on your day is a fantastic way to learn and grow—well done!",
"Your journal is a testament to your resilience and growth—great job!",
"You're turning introspection into a superpower—keep it up!",
"Journaling is a gift you give to yourself—fantastic effort!",
"Your habit of journaling will have a lasting positive impact—keep writing!"
]

if journal_image:
    feedback_to_add = random.choice(feedback_options)
    row_for_vault = {'Date' : [str(dt.date.today())], 
                 'Events' : [prompt],
                 'Topic': [st.session_state.dayPrompt],
                 'Feedback': [feedback_to_add]}
    as_df = pd.DataFrame(row_for_vault, index = [0])
    journal_vault_updated = pd.concat([journal_vault, as_df], ignore_index = True).reset_index(drop = True)
    journal_vault = conn.update(worksheet = 'journal-vault', data = journal_vault_updated)
    description_tomorrow = f'Your topic for yesterday was: {st.session_state.dayPrompt}, open up snapshot for your topic today!'
    insert_event.main(description = description_tomorrow)


st.divider()



st.markdown("### Your Journal Vault")
journal_vault = journal_vault.sort_values('Date', ascending = False)
st.dataframe(journal_vault, hide_index = True, width = 12000)

