
ai_name = 'C.A.B.A'.lower()
EXIT_COMMANDS = ['bye bye']
rec_email, rec_phoneno = "", ""
WAEMEntry = None
avatarChoosen = 0
choosedAvtrImage = None
botChatTextBg = "#007cc7"
botChatText = "white"
userChatTextBg = "#4da8da"
ownerDesignation = "Sir"
chatBgColor = '#12232e'
background = '#203647'
textColor = 'white'
AITaskStatusLblBG = '#203647'
KCS_IMG = 1  # 0 for light, 1 for dark
voice_id = 0  # 0 for female, 1 for male
ass_volume = 1  # max volume
ass_voiceRate = 200  # normal voice rate

####################################### IMPORTING MODULES ###########################################
""" User Created Modules """

""" System Modules """
import speech_recognition as sr
import pyttsx3
from tkinter import *
from tkinter import ttk
from time import sleep
from threading import Thread
import requests
from tkinter import colorchooser
from tkscrolledframe import ScrolledFrame

def reponse(message):
    bot_message = ""
    while bot_message != 'Bye bye':
        r = requests.post('http://localhost:5002/webhooks/rest/webhook', json={"message": message})
        for i in r.json():
            bot_message += i['text'] + '\n'
        return bot_message

try:
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty("voice", voices[1].id)
    newVoiceRate = 150
    engine.setProperty('rate', newVoiceRate)
except Exception as e:
    print(e)

def main(text):
    bot_message = reponse(text)
    speak(bot_message,True,True)
    return bot_message

def voiceMedium():
    while True:
        query = record()
        if query == 'None': continue
        if isContain(query, EXIT_COMMANDS):
            break
        else:
            main(query)
    root.destroy()

def changeVolume(e):
    global ass_volume
    ass_volume = volumeBar.get() / 100
    engine.setProperty('volume', ass_volume)

def changeTheme():
    global background, textColor, AITaskStatusLblBG, KCS_IMG, botChatText, botChatTextBg, userChatTextBg, chatBgColor
    if themeValue.get()==1:
        background, textColor, AITaskStatusLblBG, KCS_IMG = "#203647", "white", "#203647",1
        cbl['image'] = cblDarkImg
        kbBtn['image'] = kbphDark
        settingBtn['image'] = sphDark
        AITaskStatusLbl['bg'] = AITaskStatusLblBG
        botChatText, botChatTextBg = "white", "#007cc7"
        chatBgColor = "#12232e"
        colorbar['bg'] = chatBgColor
    else:
        background, textColor, AITaskStatusLblBG, KCS_IMG = "#F6FAFB", "#303E54", "#14A769", 0
        cbl['image'] = cblLightImg
        kbBtn['image'] = kbphLight
        settingBtn['image'] = sphLight
        AITaskStatusLbl['bg'] = AITaskStatusLblBG
        botChatText, botChatTextBg,  = "#494949", "#EAEAEA"
        chatBgColor = "#F6FAFB"
        colorbar['bg'] = '#E8EBEF'

    root['bg'], root2['bg'] = background, background
    settingsFrame['bg'] = background
    settingsLbl['fg'], volumeLbl['fg'], themeLbl['fg'], chooseChatLbl['fg'] = textColor, textColor, textColor, textColor
    settingsLbl['bg'], volumeLbl['bg'], themeLbl['bg'], chooseChatLbl['bg'] = background, background, background, background
    s.configure('Wild.TRadiobutton', background=background, foreground=textColor)
    volumeBar['bg'], volumeBar['fg'], volumeBar['highlightbackground'] = background, textColor, background
    chat_frame['bg'], root1['bg'] = chatBgColor, chatBgColor

def getChatColor():
        global chatBgColor
        myColor = colorchooser.askcolor()
        if myColor[1] is None:
            return
        chatBgColor = myColor[1]
        colorbar['bg'] = chatBgColor
        chat_frame['bg'] = chatBgColor
        #second_frame['bg'] = chatBgColor
        root1['bg'] = chatBgColor

def speak(text, display=False, icon=False):
    AITaskStatusLbl['text'] = 'Speaking...'
    if icon: Label(chat_frame, image=botIcon, bg=chatBgColor).pack(anchor='w', pady=0)
    if display: attachTOframe(text, True)
    try:
        engine.say(text)
        engine.runAndWait()
    except:
        print("Try not to type more...")

####################################### SET UP SPEECH TO TEXT #######################################
def record(clearChat=True, iconDisplay=True):
    AITaskStatusLbl['text'] = 'Listening...'
    r = sr.Recognizer()
    r.dynamic_energy_threshold = False
    r.energy_threshold = 4000
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)
        audio = r.record(source, duration=5)
        try:
            AITaskStatusLbl['text'] = 'Processing...'
            said = r.recognize_google(audio, language='vi-VI')
            if clearChat:
                clearChatScreen()
            if iconDisplay: Label(chat_frame, image=userIcon,bg=chatBgColor).pack(anchor='e', pady=0)
            attachTOframe(said)
        except Exception as e:
            if "connection failed" in str(e):
                speak("Trợ lý ảo đang bận rồi.......", True, True)
            else:
                speak('Tôi không nghe rõ lắm, bạn có thể nói lại không',True,True)
            return 'None'
    return said



def keyboardInput(e):
    user_input = UserField.get()
    if user_input != "":
        clearChatScreen()
        if isContain(user_input, EXIT_COMMANDS):
            speak("Trợ lý Off đây, Tạm biệt bạn", True, True)
        else:
            Label(chat_frame, bg=chatBgColor,image=userIcon).pack(anchor='e', pady=0)
            attachTOframe(user_input.capitalize())
            Thread(target=main, args=(user_input,)).start()
        UserField.delete(0, END)


###################################### TASK/COMMAND HANDLER #########################################
def isContain(txt, lst):
    for word in lst:
        if word in txt:
            return True
    return False


############ ATTACHING BOT/USER CHAT ON CHAT SCREEN ###########
def attachTOframe(text, bot=False):
    if bot:
        botchat = Label(chat_frame, text=text, bg=botChatTextBg, fg=botChatText, justify=LEFT, wraplength=250,
                        font=('Montserrat', 12, 'bold'))
        botchat.pack(anchor='w', ipadx=5, ipady=5, pady=5)
    else:
        userchat = Label(chat_frame, text=text, bg=userChatTextBg, fg='white', justify=RIGHT, wraplength=250,
                         font=('Montserrat', 12, 'bold'))
        userchat.pack(anchor='e', ipadx=2, ipady=2, pady=5)


def clearChatScreen():
    for wid in chat_frame.winfo_children():
        wid.destroy()


### SWITCHING BETWEEN FRAMES ###
def raise_frame(frame):
    frame.tkraise()
    clearChatScreen()


chatMode = 0
def changeChatMode():
    global chatMode

    if chatMode == 0:
        TextModeFrame.pack_forget()
        VoiceModeFrame.pack(fill=BOTH)
        VoiceThread.start()
        root.focus()
        chatMode = 1
    else:
        #volumeControl('mute')
        VoiceModeFrame.pack_forget()
        TextModeFrame.pack(fill=BOTH)
        UserField.focus()
        chatMode = 0



def progressbar():
    s = ttk.Style()
    s.theme_use('clam')
    s.configure("white.Horizontal.TProgressbar", foreground='white', background='white')
    progress_bar = ttk.Progressbar(splash_root, style="white.Horizontal.TProgressbar", orient="horizontal",
                                   mode="determinate", length=303)
    progress_bar.place(x=130,y=200)
    splash_root.update()
    progress_bar['value'] = 0
    splash_root.update()

    while progress_bar['value'] < 100:
        progress_bar['value'] += 5
        # splash_percentage_label['text'] = str(progress_bar['value']) + ' %'
        splash_root.update()
        sleep(0.1)


def destroySplash():
    splash_root.destroy()


if __name__ == '__main__':
    splash_root = Tk()
    splash_root.configure(bg='#3895d3')
    splash_root.overrideredirect(True)
    splash_label1 = Label(splash_root, text=f"LUẬN VĂN TỐT NGHIỆP ", font=('montserrat', 20,'bold'), bg='#3895d3', fg='white')
    splash_label1.place(x=150,y=20)
    splash_label2 = Label(splash_root, text=f"Đề Tài: " +'\n'
                                            f"TRỢ LÝ ẢO GIÚP XÂY DỰNG LỊCH BIỂU",
                          font=('montserrat', 15), bg='#3895d3', fg='white')
    splash_label2.place(x=120,y=60)
    splash_label3 = Label(splash_root, text=f"Giáo viên hướng dẫn:                                            Sinh viên thực hiện:",
                          font=('montserrat', 12), bg='#3895d3', fg='white')
    splash_label3.place(x=50,y=130)
    splash_label4 = Label(splash_root, text=f"ThS. Trần Nguyễn Dương Chi                        Trương Hoàng Gia Bảo",
                          font=('montserrat', 12,'bold'), bg='#3895d3', fg='white')
    splash_label4.place(x=30, y=150)

    w_width, w_height = 600, 300
    s_width, s_height = splash_root.winfo_screenwidth(), splash_root.winfo_screenheight()
    x, y = (s_width / 2) - (w_width / 2), (s_height / 2) - (w_height / 2)
    splash_root.geometry('%dx%d+%d+%d' % (w_width, w_height, x, y - 30))

    progressbar()
    splash_root.after(10, destroySplash)
    splash_root.mainloop()

    root = Tk()
    root.title('Virtual Assistant')
    w_width, w_height = 400, 650
    s_width, s_height = root.winfo_screenwidth(), root.winfo_screenheight()
    x, y = (s_width / 2) - (w_width / 2), (s_height / 2) - (w_height / 2)
    root.geometry('%dx%d+%d+%d' % (w_width, w_height, x, y - 30))  # center location of the screen
    root.configure(bg=background)
    root.resizable(width=False, height=False)
    root.pack_propagate(0)

    root1 = Frame(root, bg=chatBgColor)
    root2 = Frame(root, bg=background)
    root3 = Frame(root, bg=background)

    for f in (root1, root2, root3):
        f.grid(row=0, column=0, sticky='news')

        ################################
    ########  CHAT SCREEN  #########
    ################################

    # Chat Frame
    chat_frame = Frame(root1, width=380, height=551, bg=chatBgColor)
    chat_frame.pack(padx=10)
    chat_frame.pack_propagate(0)





    bottomFrame1 = Frame(root1, bg='#dfdfdf', height=100)
    bottomFrame1.pack(fill=X, side=BOTTOM)
    VoiceModeFrame = Frame(bottomFrame1, bg='#dfdfdf')
    VoiceModeFrame.pack(fill=BOTH)
    TextModeFrame = Frame(bottomFrame1, bg='#dfdfdf')
    TextModeFrame.pack(fill=BOTH)

    VoiceModeFrame.pack_forget()
    #TextModeFrame.pack_forget()

    cblLightImg = PhotoImage(file='images/centralButton.png')
    cblDarkImg = PhotoImage(file='images/centralButton1.png')
    if KCS_IMG == 1:
        cblimage = cblDarkImg
    else:
        cblimage = cblLightImg
    cbl = Label(VoiceModeFrame, fg='white', image=cblimage, bg='#dfdfdf')
    cbl.pack(pady=17)
    AITaskStatusLbl = Label(VoiceModeFrame, text='    Offline', fg='white', bg=AITaskStatusLblBG,
                            font=('montserrat', 16))
    AITaskStatusLbl.place(x=140, y=32)

    # Settings Button
    sphLight = PhotoImage(file="images/setting.png")
    sphLight = sphLight.subsample(2, 2)
    sphDark = PhotoImage(file="images/setting1.png")
    sphDark = sphDark.subsample(2, 2)
    if KCS_IMG == 1:
        sphimage = sphDark
    else:
        sphimage = sphLight
    settingBtn = Button(TextModeFrame, image=sphimage, height=30, width=30, bg='#dfdfdf', borderwidth=0,
                        activebackground="#dfdfdf", command=lambda: raise_frame(root2))
    settingBtn.place(relx=1.0, y=35, x=-10, anchor="ne")

    # Keyboard Button
    kbphLight = PhotoImage(file="images/keyboard.png")
    kbphLight = kbphLight.subsample(2, 2)
    kbphDark = PhotoImage(file="images/keyboard1.png")
    kbphDark = kbphDark.subsample(2, 2)
    if KCS_IMG == 1:
        kbphimage = kbphDark
    else:
        kbphimage = kbphLight
    kbBtn = Button(VoiceModeFrame, image=kbphimage, height=30, width=30, bg='#dfdfdf', borderwidth=0,
                   activebackground="#dfdfdf", command=changeChatMode)
    kbBtn.place(x=25, y=30)

    # Mic
    micImg = PhotoImage(file="images/mic.png")
    micImg = micImg.subsample(2, 2)
    micBtn = Button(TextModeFrame, image=micImg, height=30, width=30, bg='#dfdfdf', borderwidth=0,
                    activebackground="#dfdfdf", command=changeChatMode)
    micBtn.place(relx=1.0, y=35, x=-365, anchor="ne")

    # Text Field
    TextFieldImg = PhotoImage(file='images/textField.png')
    UserFieldLBL = Label(TextModeFrame, fg='white', image=TextFieldImg, bg='#dfdfdf')
    UserFieldLBL.pack(pady=17, side=LEFT, padx=35)
    UserField = Entry(TextModeFrame, fg='white', bg='#203647', font=('Montserrat', 16), bd=6, width=20, relief=FLAT)
    UserField.place(x=40, y=30)
    UserField.bind('<Return>', keyboardInput)
    userIcon = PhotoImage(file="images/avatars/ChatIcons/a14.png")
    botIcon = PhotoImage(file="images/assistant2.png")
    botIcon = botIcon.subsample(2, 2)

    ###########################
    ########  SETTINGS  #######
    ###########################

    settingsLbl = Label(root2, text='Settings', font=('Arial Bold', 15), bg=background, fg=textColor)
    settingsLbl.pack(pady=10)
    separator = ttk.Separator(root2, orient='horizontal')
    separator.pack(fill=X)

    # Settings Frame
    settingsFrame = Frame(root2, width=300, height=300, bg=background)
    settingsFrame.pack(pady=20)


    volumeLbl = Label(settingsFrame, text='Volume', font=('Arial', 13), fg=textColor, bg=background)
    volumeLbl.place(x=0, y=105)
    volumeBar = Scale(settingsFrame, bg=background, fg=textColor, sliderlength=30, length=135, width=16,
                      highlightbackground=background, orient='horizontal', from_=0, to=100, command=changeVolume)
    volumeBar.set(int(ass_volume * 100))
    volumeBar.place(x=150, y=85)

    themeLbl = Label(settingsFrame, text='Theme', font=('Arial', 13), fg=textColor, bg=background)
    themeLbl.place(x=0, y=143)
    themeValue = IntVar()
    s = ttk.Style()
    s.configure('Wild.TRadiobutton', font=('Arial Bold', 10), background=background, foreground=textColor,
                focuscolor=s.configure(".")["background"])
    darkBtn = ttk.Radiobutton(settingsFrame, text='Dark', value=1, variable=themeValue, style='Wild.TRadiobutton',
                              command=changeTheme, takefocus=False)
    darkBtn.place(x=150, y=145)
    lightBtn = ttk.Radiobutton(settingsFrame, text='Light', value=2, variable=themeValue, style='Wild.TRadiobutton',
                               command=changeTheme, takefocus=False)
    lightBtn.place(x=230, y=145)
    themeValue.set(1)
    if KCS_IMG == 0: themeValue.set(2)

    chooseChatLbl = Label(settingsFrame, text='Chat Background', font=('Arial', 13), fg=textColor, bg=background)
    chooseChatLbl.place(x=0, y=180)
    cimg = PhotoImage(file="images/colorchooser.png")
    cimg = cimg.subsample(3, 3)
    colorbar = Label(settingsFrame, bd=3, width=18, height=1, bg=chatBgColor)
    colorbar.place(x=150, y=180)
    if KCS_IMG == 0: colorbar['bg'] = '#E8EBEF'
    Button(settingsFrame, image=cimg, relief=FLAT, command=getChatColor).place(x=261, y=180)

    backBtn = Button(settingsFrame, text='Back', bd=0, font=('Arial 12'), fg='white', bg='#14A769', relief=FLAT,
                     command=lambda: raise_frame(root1))
    backBtn.place(x=5, y=250)
    try:
        VoiceThread = Thread(target=voiceMedium)

    except:
        pass
    root.iconbitmap('images/assistant2.ico')
    raise_frame(root1)
    root.mainloop()


# rasa run -m models --endpoints endpoints.yml --port 5002 --credentials credentials.yml