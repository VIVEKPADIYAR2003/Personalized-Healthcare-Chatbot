import re
import pandas as pd
from sklearn import preprocessing
from sklearn.tree import DecisionTreeClassifier,_tree
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
from sklearn.svm import SVC
import csv
import tkinter as tk
from tkinter import ttk, scrolledtext
from tkinter import *
from PIL import Image, ImageTk
import time
import warnings
import speech_recognition as sr
import pyttsx3  # Added for text-to-speech
import datetime # Added for date/time
import os # Added for file operations

# Suppress warnings
warnings.filterwarnings('ignore')

training = pd.read_csv('Data/Training.csv')
testing= pd.read_csv('Data/Testing.csv')
cols= training.columns
cols= cols[:-1]
x = training[cols]
y = training['prognosis']
y1= y

reduced_data = training.groupby(training['prognosis']).max()

le = preprocessing.LabelEncoder()
le.fit(y)
y = le.transform(y)

x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.33, random_state=42)
testx    = testing[cols]
testy    = testing['prognosis']  
testy    = le.transform(testy)

clf1  = DecisionTreeClassifier()
clf = clf1.fit(x_train,y_train)
scores = cross_val_score(clf, x_test, y_test, cv=3)
print (scores.mean())

model=SVC()
model.fit(x_train,y_train)
print("for svm: ")
print(model.score(x_test,y_test))

importances = clf.feature_importances_
indices = np.argsort(importances)[::-1]
features = cols

severityDictionary=dict()
description_list = dict()
precautionDictionary=dict()
doctorDictionary=dict() 
hospitalDictionary=dict()
medicineDictionary=dict()
symptoms_dict = {}

for index, symptom in enumerate(x):
       symptoms_dict[symptom] = index

# Function to save user data to CSV
def save_user_data(name, disease, precautions, hospitals, medicines, doctors):
    # Get current date and time
    current_time = datetime.datetime.now()
    date = current_time.strftime("%Y-%m-%d")
    time = current_time.strftime("%H:%M:%S")
    
    # Prepare data for CSV
    data = {
        'Name': [name],
        'Disease': [disease],
        'Precautions': [', '.join(precautions) if precautions else 'None'],
        'Hospitals': [', '.join(hospitals) if hospitals else 'None'], 
        'Medicines': [', '.join(medicines) if medicines else 'None'],
        'Doctors': [', '.join(doctors) if doctors else 'None'],
        'Date': [date],
        'Time': [time]
    }
    
    df = pd.DataFrame(data)
    
    # Check if file exists
    file_exists = os.path.isfile('info.csv')
    
    # Write to CSV
    if file_exists:
        df.to_csv('info.csv', mode='a', header=False, index=False)
    else:
        df.to_csv('info.csv', mode='w', header=True, index=False)

# Chat UI Class
class HealthcareChatbot:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Healthcare Assistant")
        self.window.geometry("800x900")  # Made window bigger
        
        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        
        # Initialize text-to-speech engine
        self.tts_engine = pyttsx3.init()
        self.tts_enabled = True  # Text-to-speech enabled by default
        
        # Theme variables
        self.is_dark_mode = False
        self.themes = {
            'light': {
                'bg': '#128C7E',
                'chat_bg': '#ECE5DD',
                'message_bg': '#DCF8C6',
                'text': '#000000',
                'button_bg': '#25D366'
            },
            'dark': {
                'bg': '#1F2937',
                'chat_bg': '#374151',
                'message_bg': '#4B5563',
                'text': '#000000',
                'button_bg': '#3B82F6'
            }
        }
        
        self.window.configure(bg=self.themes['light']['bg'])
        
        # Set window icon
        try:
            icon = Image.open('images/icon.png')
            photo = ImageTk.PhotoImage(icon)
            self.window.iconphoto(False, photo)
        except:
            pass

        # Header frame
        self.header_frame = tk.Frame(self.window, bg=self.themes['light']['bg'], height=80)
        self.header_frame.pack(fill=X)
        
        # Theme toggle button
        self.theme_button = tk.Button(
            self.header_frame,
            text="🌙",
            font=('Segoe UI', 14),
            bg=self.themes['light']['button_bg'],
            fg='white',
            relief=FLAT,
            command=self.toggle_theme,
            width=3,
            cursor='hand2'
        )
        self.theme_button.pack(side=RIGHT, padx=10, pady=10)
        
        # Text-to-speech toggle button
        self.tts_button = tk.Button(
            self.header_frame,
            text="🔊",
            font=('Segoe UI', 14),
            bg=self.themes['light']['button_bg'],
            fg='white',
            relief=FLAT,
            command=self.toggle_tts,
            width=3,
            cursor='hand2'
        )
        self.tts_button.pack(side=RIGHT, padx=10, pady=10)
        
        # App title with larger font
        self.title_label = tk.Label(
            self.header_frame,
            text="Personalized Healthcare Chatbot",
            font=('Segoe UI', 24, 'bold'),
            bg=self.themes['light']['bg'],
            fg='white'
        )
        self.title_label.pack(pady=15)
            
        # Chat display area with Instagram-like styling
        self.chat_frame = tk.Frame(self.window, bg=self.themes['light']['message_bg'])
        self.chat_frame.pack(fill=BOTH, expand=True, padx=0, pady=0)
        
        # Custom style for the chat area with larger font
        self.chat_area = scrolledtext.ScrolledText(
            self.chat_frame, 
            wrap=WORD,
            font=('Segoe UI', 14),
            bg=self.themes['light']['chat_bg'],
            fg=self.themes['light']['text'],
            padx=15,
            pady=15,
            borderwidth=0,
            relief="flat"
        )
        self.chat_area.pack(fill=BOTH, expand=True, padx=2, pady=2)
        self.chat_area.config(state=DISABLED)
        
        # Message styling with larger fonts
        self.chat_area.tag_config(
            'bot', 
            background=self.themes['light']['message_bg'],
            lmargin1=50,
            lmargin2=50,
            rmargin=25,
            spacing1=12,
            spacing3=12,
            font=('Segoe UI', 14)
        )
        self.chat_area.tag_config(
            'user',
            background=self.themes['light']['message_bg'],
            justify='right',
            rmargin=50,
            lmargin1=25,
            lmargin2=25,
            spacing1=12,
            spacing3=12,
            font=('Segoe UI', 14)
        )
        
        # Add new tags for bold text
        self.chat_area.tag_config(
            'bold',
            background=self.themes['light']['message_bg'],
            font=('Segoe UI', 14, 'bold')
        )
        
        # Bottom input area with larger elements
        self.input_frame = tk.Frame(self.window, bg=self.themes['light']['bg'], height=100)
        self.input_frame.pack(fill=X, side=BOTTOM)
        
        # Message input field with larger font
        self.input_field = tk.Entry(
            self.input_frame,
            font=('Segoe UI', 16),
            bg='white',
            fg=self.themes['light']['text'],
            relief=FLAT,
            bd=12
        )
        self.input_field.pack(side=LEFT, fill=X, expand=True, padx=(15,8), pady=15)
        
        # Voice command button
        self.voice_button = tk.Button(
            self.input_frame,
            text="🎤",
            font=('Segoe UI', 14, 'bold'),
            bg=self.themes['light']['button_bg'],
            fg='white',
            relief=FLAT,
            command=self.take_voice_input,
            width=3,
            cursor='hand2'
        )
        self.voice_button.pack(side=RIGHT, padx=(0,8), pady=15)
        
        # Send button with larger font
        self.send_button = tk.Button(
            self.input_frame,
            text="Send",
            font=('Segoe UI', 14, 'bold'),
            bg=self.themes['light']['button_bg'],
            fg='white',
            relief=FLAT,
            command=self.send_message,
            width=10,
            cursor='hand2'
        )
        self.send_button.pack(side=RIGHT, padx=(8,15), pady=15)
        
        self.input_field.bind("<Return>", lambda e: self.send_message())
        
        # Symptom selection frame (initially hidden)
        self.symptom_frame = tk.Frame(self.window, bg=self.themes['light']['bg'])
        
        # Symptom selection listbox with scrollbar
        self.symptom_label = tk.Label(
            self.symptom_frame,
            text="Select your symptoms:",
            font=('Segoe UI', 16, 'bold'),
            bg=self.themes['light']['bg'],
            fg='white'
        )
        self.symptom_label.pack(pady=(10, 5))
        
        self.symptom_listbox_frame = tk.Frame(self.symptom_frame, bg=self.themes['light']['bg'])
        self.symptom_listbox_frame.pack(fill=BOTH, expand=True, padx=15, pady=5)
        
        self.symptom_scrollbar = tk.Scrollbar(self.symptom_listbox_frame)
        self.symptom_scrollbar.pack(side=RIGHT, fill=Y)
        
        self.symptom_listbox = tk.Listbox(
            self.symptom_listbox_frame,
            selectmode=MULTIPLE,
            font=('Segoe UI', 14),
            bg='white',
            fg=self.themes['light']['text'],
            height=10,
            yscrollcommand=self.symptom_scrollbar.set
        )
        self.symptom_listbox.pack(side=LEFT, fill=BOTH, expand=True)
        self.symptom_scrollbar.config(command=self.symptom_listbox.yview)
        
        # Search field for symptoms
        self.search_frame = tk.Frame(self.symptom_frame, bg=self.themes['light']['bg'])
        self.search_frame.pack(fill=X, padx=15, pady=5)
        
        self.search_label = tk.Label(
            self.search_frame,
            text="Search:",
            font=('Segoe UI', 14),
            bg=self.themes['light']['bg'],
            fg='white'
        )
        self.search_label.pack(side=LEFT, padx=(0, 5))
        
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.update_symptom_list)
        
        self.search_entry = tk.Entry(
            self.search_frame,
            textvariable=self.search_var,
            font=('Segoe UI', 14),
            bg='white',
            fg=self.themes['light']['text']
        )
        self.search_entry.pack(side=LEFT, fill=X, expand=True)
        
        # Buttons for symptom selection
        self.symptom_button_frame = tk.Frame(self.symptom_frame, bg=self.themes['light']['bg'])
        self.symptom_button_frame.pack(fill=X, padx=15, pady=10)
        
        self.confirm_symptoms_button = tk.Button(
            self.symptom_button_frame,
            text="Confirm Symptoms",
            font=('Segoe UI', 14, 'bold'),
            bg=self.themes['light']['button_bg'],
            fg='white',
            relief=FLAT,
            command=self.confirm_symptoms,
            cursor='hand2'
        )
        self.confirm_symptoms_button.pack(side=RIGHT, padx=5)
        
        self.cancel_symptoms_button = tk.Button(
            self.symptom_button_frame,
            text="Cancel",
            font=('Segoe UI', 14, 'bold'),
            bg='#E74C3C',
            fg='white',
            relief=FLAT,
            command=self.hide_symptom_selection,
            cursor='hand2'
        )
        self.cancel_symptoms_button.pack(side=RIGHT, padx=5)
        
        # Populate symptom listbox
        self.all_symptoms = list(cols)
        self.all_symptoms.sort()
        self.update_symptom_list()
        
        self.current_step = "name"
        self.user_name = ""
        self.symptoms_exp = []
        self.disease_input = ""
        self.num_days = 0
        
        # Start chat
        self.display_bot_message("Welcome to Personalized Healthcare Chatbot!")
        self.display_bot_message("Please enter your name:")

    def update_symptom_list(self, *args):
        search_term = self.search_var.get().lower()
        self.symptom_listbox.delete(0, END)
        
        for symptom in self.all_symptoms:
            if search_term == "" or search_term in symptom.lower():
                # Replace underscores with spaces for display
                display_symptom = symptom.replace('_', ' ')
                self.symptom_listbox.insert(END, display_symptom)
    
    def show_symptom_selection(self):
        # Hide chat frame and show symptom selection
        self.chat_frame.pack_forget()
        self.input_frame.pack_forget()
        self.symptom_frame.pack(fill=BOTH, expand=True, padx=0, pady=0)
        
    def hide_symptom_selection(self):
        # Hide symptom selection and show chat frame
        self.symptom_frame.pack_forget()
        self.chat_frame.pack(fill=BOTH, expand=True, padx=0, pady=0)
        self.input_frame.pack(fill=X, side=BOTTOM)
        
    def confirm_symptoms(self):
        selected_indices = self.symptom_listbox.curselection()
        if not selected_indices:
            # If no symptoms selected, show a message
            self.hide_symptom_selection()
            self.display_bot_message("No symptoms selected. Please enter a symptom or select from the list.")
            return
            
        # Get selected symptoms
        self.symptoms_exp = []
        for i in selected_indices:
            # Convert display format back to database format
            symptom_display = self.symptom_listbox.get(i)
            symptom_db = symptom_display.replace(' ', '_')
            self.symptoms_exp.append(symptom_db)
            
        # Display selected symptoms
        self.hide_symptom_selection()
        self.display_bot_message("You've selected the following symptoms:")
        for symptom in self.symptoms_exp:
            display_symptom = symptom.replace('_', ' ')
            self.display_bot_message(f"- {display_symptom}")
            
        self.display_bot_message("From how many days are you experiencing these symptoms?")
        self.current_step = "days"

    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        theme = self.themes['dark'] if self.is_dark_mode else self.themes['light']
        
        # Update theme button text
        self.theme_button.config(text=" ☀️" if self.is_dark_mode else " 🌙")
        
        # Update colors
        self.window.configure(bg=theme['bg'])
        self.header_frame.configure(bg=theme['bg'])
        self.title_label.configure(bg=theme['bg'])
        self.chat_frame.configure(bg=theme['message_bg'])
        self.chat_area.configure(bg=theme['chat_bg'], fg=theme['text'])
        self.input_frame.configure(bg=theme['bg'])
        self.input_field.configure(fg=theme['text'])
        
        # Update symptom frame colors
        self.symptom_frame.configure(bg=theme['bg'])
        self.symptom_label.configure(bg=theme['bg'])
        self.symptom_listbox_frame.configure(bg=theme['bg'])
        self.search_frame.configure(bg=theme['bg'])
        self.search_label.configure(bg=theme['bg'])
        self.symptom_button_frame.configure(bg=theme['bg'])
        
        # Update button colors
        self.theme_button.configure(bg=theme['button_bg'])
        self.tts_button.configure(bg=theme['button_bg'])
        self.voice_button.configure(bg=theme['button_bg'])
        self.send_button.configure(bg=theme['button_bg'])
        self.confirm_symptoms_button.configure(bg=theme['button_bg'])
        
        # Update message tags
        self.chat_area.tag_configure('bot', background=theme['message_bg'])
        self.chat_area.tag_configure('user', background=theme['message_bg'])
        self.chat_area.tag_configure('bold', background=theme['message_bg'])

    def toggle_tts(self):
        self.tts_enabled = not self.tts_enabled
        self.tts_button.config(text="🔊" if self.tts_enabled else "🔇")
        status = "enabled" if self.tts_enabled else "disabled"
        self.display_bot_message(f"Text-to-speech {status}")

    def speak_text(self, text):
        if self.tts_enabled:
            # Remove emojis and bot/you prefixes for cleaner speech
            clean_text = text
            if clean_text.startswith("🤖 Bot: "):
                clean_text = clean_text[7:]
            
            # Start TTS in a separate thread to avoid freezing the UI
            self.window.after(10, lambda: self._speak_in_background(clean_text))
    
    def _speak_in_background(self, text):
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            print(f"TTS Error: {str(e)}")

    def take_voice_input(self):
        try:
            with sr.Microphone() as source:
                self.display_bot_message("Listening...")
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                try:
                    # Increased timeout and added phrase_time_limit
                    audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=5)
                    self.display_bot_message("Processing speech...")
                    text = self.recognizer.recognize_google(audio)
                    self.input_field.delete(0, END)
                    self.input_field.insert(0, text)
                    self.send_message()
                except sr.UnknownValueError:
                    self.display_bot_message("Sorry, I couldn't understand that. Please try again.")
                except sr.RequestError as e:
                    self.display_bot_message(f"Could not request results; {e}")
                except sr.WaitTimeoutError:
                    self.display_bot_message("No speech detected. Please try again.")
        except Exception as e:
            self.display_bot_message("Error accessing microphone. Please check your microphone settings.")
            print(f"Microphone Error: {str(e)}")

    def display_bot_message(self, message, bold=False):
        self.chat_area.config(state=NORMAL)
        full_message = "🤖 Bot: " + message
        self.chat_area.insert(END, "🤖 Bot: ", 'bot')
        if bold:
            self.chat_area.insert(END, message + "\n\n", ('bot', 'bold'))
        else:
            self.chat_area.insert(END, message + "\n\n", 'bot')
        self.chat_area.config(state=DISABLED)
        self.chat_area.see(END)
        
        # Speak the message
        self.speak_text(message)

    def display_user_message(self, message):
        self.chat_area.config(state=NORMAL)
        self.chat_area.insert(END, "👤 You: " + message + "\n\n", 'user')
        self.chat_area.config(state=DISABLED)
        self.chat_area.see(END)

    def send_message(self):
        message = self.input_field.get()
        if message.strip() == "":
            return
            
        self.display_user_message(message)
        self.input_field.delete(0, END)
        
        if self.current_step == "name":
            self.user_name = message
            self.display_bot_message(f"Hello {self.user_name}!")
            self.display_bot_message("You can either type a symptom or select from our symptom list.")
            self.display_bot_message("Would you like to select symptoms from a list? (yes/no)")
            self.current_step = "symptom_selection_choice"
            
        elif self.current_step == "symptom_selection_choice":
            if message.lower() == "yes":
                self.show_symptom_selection()
            else:
                self.display_bot_message("Please enter the symptom you are experiencing:")
                self.current_step = "symptom"
            
        elif self.current_step == "symptom":
            self.disease_input = message
            chk_dis = list(cols)  # Convert columns to list
            conf, cnf_dis = check_pattern(chk_dis, self.disease_input)
            if conf == 1:
                if len(cnf_dis) > 1:
                    self.display_bot_message("Searches related to input:")
                    for i, dis in enumerate(cnf_dis):
                        display_symptom = dis.replace('_', ' ')
                        self.display_bot_message(f"{i}) {display_symptom}")
                    self.display_bot_message(f"Select the one you meant (0-{len(cnf_dis)-1}):")
                    self.current_step = "select_symptom"
                    self.cnf_dis = cnf_dis
                else:
                    self.disease_input = cnf_dis[0]
                    self.symptoms_exp.append(self.disease_input)
                    self.display_bot_message("From how many days are you experiencing this?")
                    self.current_step = "days"
            else:
                self.display_bot_message("Please enter a valid symptom or type 'list' to select from a list")
                if message.lower() == "list":
                    self.show_symptom_selection()
                
        elif self.current_step == "select_symptom":
            try:
                selection = int(message)
                if 0 <= selection < len(self.cnf_dis):
                    self.disease_input = self.cnf_dis[selection]
                    self.symptoms_exp.append(self.disease_input)
                    self.display_bot_message("From how many days are you experiencing this?")
                    self.current_step = "days"
                else:
                    self.display_bot_message("Please enter a valid number")
            except:
                if message.lower() == "list":
                    self.show_symptom_selection()
                else:
                    self.display_bot_message("Please enter a valid number or type 'list' to select from a list")
                
        elif self.current_step == "days":
            try:
                self.num_days = int(message)
                self.process_diagnosis()
            except:
                self.display_bot_message("Please enter a valid number of days")
        
        elif self.current_step == "confirm_symptoms":
            if message.lower() not in ['yes', 'no']:
                self.display_bot_message("Please enter a valid input (yes/no)")
                return
                
            if message.lower() == 'yes':
                self.symptoms_exp.append(self.symptoms_to_ask[self.current_symptom_index])
            self.current_symptom_index += 1
            self.ask_next_symptom()

    def process_diagnosis(self):
        if not self.symptoms_exp:
            self.display_bot_message("No symptoms provided. Please enter at least one symptom.")
            self.current_step = "symptom"
            return
            
        tree_ = clf.tree_
        feature_name = [
            cols[i] if i != _tree.TREE_UNDEFINED else "undefined!"
            for i in tree_.feature
        ]
        
        def recurse(node, depth):
            if tree_.feature[node] != _tree.TREE_UNDEFINED:
                name = feature_name[node]
                threshold = tree_.threshold[node]

                if name in self.symptoms_exp:
                    val = 1
                else:
                    val = 0
                if val <= threshold:
                    return recurse(tree_.children_left[node], depth + 1)
                else:
                    return recurse(tree_.children_right[node], depth + 1)
            else:
                present_disease = print_disease(tree_.value[node])
                red_cols = reduced_data.columns 
                symptoms_given = red_cols[reduced_data.loc[present_disease].values[0].nonzero()]
                
                self.display_bot_message("Are you experiencing any of these symptoms?")
                self.symptoms_to_ask = list(symptoms_given)
                self.current_symptom_index = 0
                self.current_step = "confirm_symptoms"
                self.ask_next_symptom()
                return present_disease[0]

        self.predicted_disease = recurse(0, 1)

    def ask_next_symptom(self):
        if self.current_symptom_index < len(self.symptoms_to_ask):
            symptom = self.symptoms_to_ask[self.current_symptom_index]
            display_symptom = symptom.replace('_', ' ')
            self.display_bot_message(f"Do you have {display_symptom}? (yes/no)")
        else:
            self.finish_diagnosis()

    def finish_diagnosis(self):
        second_prediction = sec_predict(self.symptoms_exp)
        condition_msg = calc_condition(self.symptoms_exp, self.num_days)
        self.display_bot_message(condition_msg, bold=True)
        
        precautions = []
        hospitals = []
        medicines = []
        doctors = []
        
        if self.predicted_disease == second_prediction[0]:
            self.display_bot_message(f"You may have {self.predicted_disease}", bold=True)
            self.display_bot_message(f"Description: {description_list[self.predicted_disease]}")
            disease = self.predicted_disease
        else:
            self.display_bot_message(f"You may have {self.predicted_disease} or {second_prediction[0]}", bold=True)
            self.display_bot_message(f"Description for {self.predicted_disease}: {description_list[self.predicted_disease]}")
            self.display_bot_message(f"Description for {second_prediction[0]}: {description_list[second_prediction[0]]}")
            disease = f"{self.predicted_disease} or {second_prediction[0]}"

        try:
            precautions = precautionDictionary[self.predicted_disease]
            self.display_bot_message("\nTake following measures:", bold=True)
            for i, precaution in enumerate(precautions):
                self.display_bot_message(f"{i+1}) {precaution}")
        except KeyError:
            self.display_bot_message("\nNo specific precautions found for this condition")
            
        try:    
            doctors = doctorDictionary[self.predicted_disease]
            self.display_bot_message("\nRecommended doctors:", bold=True)
            for i, doctor in enumerate(doctors):
                self.display_bot_message(f"{i+1}) {doctor}")
        except KeyError:
            self.display_bot_message("\nNo specific doctor recommendations found")

        try:
            hospitals = hospitalDictionary[self.predicted_disease]
            self.display_bot_message("\nRecommended hospitals:", bold=True)
            for i, hospital in enumerate(hospitals):
                self.display_bot_message(f"{i+1}) {hospital}")
        except KeyError:
            self.display_bot_message("\nNo specific hospital recommendations found")

        try:
            medicines = medicineDictionary[self.predicted_disease]
            self.display_bot_message("\nRecommended medicines:", bold=True)
            for i, medicine in enumerate(medicines):
                self.display_bot_message(f"{i+1}) {medicine}")
        except KeyError:
            self.display_bot_message("\nNo specific medicine recommendations found")

        # Save user data to CSV
        save_user_data(
            self.user_name,
            disease,
            precautions,
            hospitals,
            medicines,
            doctors
        )

        # Reset for new diagnosis
        self.display_bot_message("\nDo you have any other symptoms to check? Would you like to select from the symptom list? (yes/no)")
        self.current_step = "symptom_selection_choice"
        self.symptoms_exp = []
        self.disease_input = ""
        self.num_days = 0

    def run(self):
        self.window.mainloop()

def calc_condition(exp,days):
    sum=0
    for item in exp:
         sum=sum+severityDictionary[item]
    if((sum*days)/(len(exp)+1)>13):
        return "You should take the consultation from doctor."
    else:
        return "It might not be that bad but you should take precautions."

def getDescription():
    global description_list
    with open('MasterData/symptom_Description.csv', encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            _description={row[0]:row[1]}
            description_list.update(_description)

def getSeverityDict():
    global severityDictionary
    with open('MasterData/symptom_severity.csv', encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        try:
            for row in csv_reader:
                _diction={row[0]:int(row[1])}
                severityDictionary.update(_diction)
        except:
            pass

def getprecautionDict():
    global precautionDictionary
    with open('MasterData/symptom_precaution.csv', encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            _prec={row[0]:[row[1],row[2],row[3],row[4]]}
            precautionDictionary.update(_prec)

def getDoctorDict():
    global doctorDictionary
    with open('MasterData/symptom_doctors.csv', encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            _doc={row[0]:[row[1]]}
            doctorDictionary.update(_doc)

def getHospitalDict():
    global hospitalDictionary
    with open('MasterData/symptom_hospitals.csv', encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            _hosp={row[0]:[row[1]]}
            hospitalDictionary.update(_hosp)

def getMedicineDict():
    global medicineDictionary
    with open('MasterData/symptom_medicines.csv', encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            _med={row[0]:[row[1],row[2],row[3],row[4]]}
            medicineDictionary.update(_med)

def check_pattern(dis_list,inp):
    pred_list=[]
    inp=inp.replace(' ','_')
    patt = f"{inp}"
    regexp = re.compile(patt)
    pred_list=[item for item in dis_list if regexp.search(item)]
    if(len(pred_list)>0):
        return 1,pred_list
    else:
        return 0,[]

def sec_predict(symptoms_exp):
    df = pd.read_csv('Data/Training.csv')
    X = df.iloc[:, :-1]
    y = df['prognosis']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=20)
    rf_clf = DecisionTreeClassifier()
    rf_clf.fit(X_train, y_train)

    symptoms_dict = {symptom: index for index, symptom in enumerate(X)}
    input_vector = np.zeros(len(symptoms_dict))
    for item in symptoms_exp:
      input_vector[[symptoms_dict[item]]] = 1

    return rf_clf.predict([input_vector])

def print_disease(node):
    node = node[0]
    val  = node.nonzero() 
    disease = le.inverse_transform(val[0])
    return list(map(lambda x:x.strip(),list(disease)))

# Initialize and run chat interface
getSeverityDict()
getDescription()
getprecautionDict()
getDoctorDict()
getHospitalDict() 
getMedicineDict()
chatbot = HealthcareChatbot()
chatbot.run()
