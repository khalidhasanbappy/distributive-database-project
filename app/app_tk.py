import os
import vlc
import shutil
import tkinter as tk
from PIL import Image, ImageTk
from mongodb.query_manager import *
from mongodb.collection import *
from hadoop.hadoop_manager import HadoopManager

hdfs = HadoopManager()
TMP_FILE_DIR = './tmp/'
HUGE_FONT = ("Verdana", 100)
LARGE_FONT = ("Verdana", 26)
MEDIUM_FONT = ("Verdana", 18)

class ArticleApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.geometry("800x500")
        self.title('Article App')

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        self.pages = (
            StartPage,
            UserPage,
            CreateUserPage,
            EditUserPage,
            DeleteUserPage,
            ArticlePage,
            ReadPage,
            BeReadPage,
            PopularRankPage,
            DailyRankPage,
            WeeklyRankPage,
            MonthlyRankPage
        )

        for F in self.pages:
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

    def fetch_user(self, uid, tklist, found_label):
        tklist.delete(0, tk.END)
        if uid == '':
            query_id = {}
        else:
            uids = uid.split(',')
            query_id = {'uid': {'$in': uids}}
        res = QueryManager.query_user(query_id)

        if len(res) == 1:
            found_label['text'] = f'Found 1 result.'
        else:
            found_label['text'] = f'Found {len(res)} results.'

        for i in sorted(res, key=lambda x: int(x['uid'])):
            tklist.insert(tk.END, f'User ID: {i["uid"]}, Name: {i["name"]}, Region: {i["region"]}, Gender: {i["gender"]}')

    def create_user(self, tkVars):
        QueryManager.insert_user({
            'id': f'u{tkVars[0]}',
            'timestamp': Collection.get_current_timestamp(),
            'uid': tkVars[0],
            'name': tkVars[1],
            'gender': tkVars[2],
            'email': tkVars[3],
            'phone': tkVars[4],
            'dept': tkVars[5],
            'grade': tkVars[6],
            'language': tkVars[7],
            'region': tkVars[8],
            'role': tkVars[9],
            'preferTags': tkVars[10],
            'obtainedCredits': tkVars[11]
        })

    def edit_user(self, edit_vars):
        edit_vars = {k: v for k, v in edit_vars.items() if v}
        if not 'uid' in edit_vars:
            return
        QueryManager.update_user(edit_vars)

    def delete_user(self, uid):
        QueryManager.delete_user({'uid': uid.get()})

    def fetch_article(self, aid, tklist, found_label, sort=True):
        tklist.delete(0, tk.END)
        if aid == '':
            query_id = {}
        else:
            aids = aid.split(',')
            query_id = {'aid': {'$in': aids}}
        res = QueryManager.query_article(query_id)

        if len(res) == 1:
            found_label['text'] = f'Found 1 result.'
        else:
            found_label['text'] = f'Found {len(res)} results.'
        if sort:
            for i in sorted(res, key=lambda x: int(x['aid'])):
                tklist.insert(tk.END, f'Article ID: {i["aid"]}, Title: {i["title"]}, Category: {i["category"]}, Authors: {i["authors"]}')
        else:
            for i in res:
                tklist.insert(tk.END, f'Article ID: {i["aid"]}, Title: {i["title"]}, Category: {i["category"]}, Authors: {i["authors"]}')

    def fetch_be_read(self, aid, tklist, found_label):
        tklist.delete(0, tk.END)
        if aid.get() == '':
            query_id = {}
        else:
            aids = aid.get().split(',')
            query_id = {'aid': {'$in': aids}}
        res = QueryManager.query_be_read(query_id)

        if len(res) == 1:
            found_label['text'] = f'Found 1 result.'
        else:
            found_label['text'] = f'Found {len(res)} results.'

        for i in sorted(res, key=lambda x: int(x['aid'])):
            tklist.insert(tk.END, f'Article ID: {i["aid"]}, '
                                  f'Read count: {i["readNum"]}, '
                                  f'Comment count: {i["commentNum"]}, '
                                  f'Agree count: {i["agreeNum"]}, '
                                  f'Share count: {i["shareNum"]}')

    def fetch_daily_rank(self, day_text, top_text, tklist, found_label):
        tklist.delete(0, tk.END)
        day = DateToTimestamp.day_tmp(day_text.get())
        res = QueryManager.query_popular_rank({'timestamp': day, 'temporalGranularity': 'daily'})
        if res:
            aids = res[0]['articleAidList']
            self.fetch_article(','.join(aids[:int(top_text.get())]), tklist, found_label, sort=False)

    def fetch_weekly_rank(self, week_text, top_text, tklist, found_label):
        tklist.delete(0, tk.END)
        week = DateToTimestamp.week_tmp(week_text.get())
        res = QueryManager.query_popular_rank({'timestamp': week, 'temporalGranularity': 'weekly'})
        if res:
            aids = res[0]['articleAidList']
            self.fetch_article(','.join(aids[:int(top_text.get())]), tklist, found_label, sort=False)

    def fetch_monthly_rank(self, monthly_text, top_text, tklist, found_label):
        tklist.delete(0, tk.END)
        month = DateToTimestamp.month_tmp(monthly_text.get())
        res = QueryManager.query_popular_rank({'timestamp': month, 'temporalGranularity': 'monthly'})
        if res:
            aids = res[0]['articleAidList']
            self.fetch_article(','.join(aids[:int(top_text.get())]), tklist, found_label, sort=False)

    def fetch_article_user(self, uid, tklist, found_label):
        tklist.delete(0, tk.END)
        res = QueryManager.query_read({'uid': uid})
        aids = set(map(lambda x: x['aid'], res))
        self.fetch_article(','.join(aids), tklist, found_label)

    def fetch_user_article(self, aid, tklist, found_label):
        tklist.delete(0, tk.END)
        res = QueryManager.query_read({'aid': aid})
        uids = set(map(lambda x: x['uid'], res))
        self.fetch_user(','.join(uids), tklist, found_label)


    def open_article(self, list):
        selection = list.curselection()
        if selection:
            i = 5
            article = 'article' + list.get(selection[0]).split()[2][:-1]
            newWindow = tk.Toplevel()
            newWindow.title(article)
            newWindow.geometry("953x600")
            frame = tk.Frame(newWindow)
            frame.pack()
            article_files = hdfs.list_article(article)
            for file in article_files:
                ext = file.split('.')[-1]
                if ext == 'txt':
                    height = 22
                    width = 70
                    text = hdfs.read_file(article, file).decode('utf-8')
                    text_box = tk.Text(frame, height=height, width=width)
                    text_box.insert('end', text)
                    text_box.config(state='disabled')
                    text_box.grid(row=0, column=1)
                elif ext == 'jpg':
                    hdfs.download_file(article, file, TMP_FILE_DIR + file)
                    image = Image.open(TMP_FILE_DIR + file)
                    image = image.resize((150, 250))
                    img = ImageTk.PhotoImage(image)
                    panel = tk.Label(frame, image=img)
                    panel.image = img
                    panel.grid(row=0, column=i)
                    i += 1
                elif ext == 'flv':
                    hdfs.download_file(article, file, TMP_FILE_DIR + file)
                    video = vlc.MediaPlayer(TMP_FILE_DIR + file)
                    video.audio_set_volume(0)
                    video.play()


class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Article App", font=HUGE_FONT, fg='blue')
        label.pack(pady=10, padx=10)

        buttons = tk.Frame(self)
        buttons.pack()

        user_button = tk.Button(buttons, text="Users",
                           command=lambda: controller.show_frame(UserPage), font=LARGE_FONT)
        user_button.pack(side=tk.LEFT)

        articles_button = tk.Button(buttons, text="Articles",
                            command=lambda: controller.show_frame(ArticlePage), font=LARGE_FONT)
        articles_button.pack(side=tk.LEFT)

        read_button = tk.Button(buttons, text="Reads",
                                command=lambda: controller.show_frame(ReadPage), font=LARGE_FONT)
        read_button.pack(side=tk.LEFT)


        buttons = tk.Frame(self)
        buttons.pack(pady=10)

        articles_button = tk.Button(buttons, text="Article Stats",
                            command=lambda: controller.show_frame(BeReadPage), font=LARGE_FONT)
        articles_button.pack(side=tk.LEFT)

        read_button = tk.Button(buttons, text="Popular Rank",
                                command=lambda: controller.show_frame(PopularRankPage), font=LARGE_FONT)
        read_button.pack(side=tk.LEFT)


class UserPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Users", font=LARGE_FONT, fg='blue')
        label.pack(pady=10, padx=10)

        top_frame = tk.Frame(self)
        top_frame.pack()

        user_label = tk.Label(top_frame, text='User ID', font=('bold', 14), pady=20, padx=20)
        user_label.pack(side=tk.LEFT)

        user_text = tk.StringVar()
        user_entry = tk.Entry(top_frame, textvariable=user_text)
        user_entry.pack(side=tk.LEFT)

        user_submit = tk.Button(top_frame, text='Submit',
                                command=lambda: controller.fetch_user(user_text.get(), result_list, found_label),
                                pady=5, padx=20)
        user_submit.pack(side=tk.LEFT)

        found_label = tk.Label(self, text='', font=('bold', 14), padx=20)
        found_label.pack()

        result_list = tk.Listbox(self, height=20, width=80)
        result_list.pack()

        buttons = tk.Frame(self)
        buttons.pack(pady=5)

        create_user_button = tk.Button(buttons, text="Create User",
                           command=lambda: controller.show_frame(CreateUserPage))
        create_user_button.pack(side=tk.LEFT)

        edit_user_button = tk.Button(buttons, text="Edit User",
                            command=lambda: controller.show_frame(EditUserPage))
        edit_user_button.pack(side=tk.LEFT)

        delete_user_button = tk.Button(buttons, text="Delete User",
                            command=lambda: controller.show_frame(DeleteUserPage))
        delete_user_button.pack(side=tk.LEFT)

        back_button = tk.Button(self, text="Back to Home",
                            command=lambda: controller.show_frame(StartPage))
        back_button.pack(pady=5)


class CreateUserPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Create User", font=LARGE_FONT, fg='blue')
        label.pack(pady=10, padx=10)

        tkVars = []

        frame = tk.Frame(self)
        frame.pack()
        user_label = tk.Label(frame, text='User ID', font=('bold', 14), pady=20, padx=20)
        user_label.pack(side=tk.LEFT)
        uid = tk.StringVar()
        tkVars += [uid]
        user_entry = tk.Entry(frame, textvariable=uid)
        user_entry.pack(side=tk.LEFT)

        user_label = tk.Label(frame, text='Name', font=('bold', 14), pady=20, padx=20)
        user_label.pack(side=tk.LEFT)
        name = tk.StringVar()
        tkVars += [name]
        user_entry = tk.Entry(frame, textvariable=name)
        user_entry.pack(side=tk.RIGHT)

        frame = tk.Frame(self)
        frame.pack()
        user_label = tk.Label(frame, text='Gender', font=('bold', 14), pady=20, padx=20)
        user_label.pack(side=tk.LEFT)
        gender = tk.StringVar()
        tkVars += [gender]
        user_entry = tk.Entry(frame, textvariable=gender)
        user_entry.pack(side=tk.LEFT)

        user_label = tk.Label(frame, text='Email', font=('bold', 14), pady=20, padx=20)
        user_label.pack(side=tk.LEFT)
        email = tk.StringVar()
        tkVars += [email]
        user_entry = tk.Entry(frame, textvariable=email)
        user_entry.pack(side=tk.RIGHT)

        frame = tk.Frame(self)
        frame.pack()
        user_label = tk.Label(frame, text='Phone', font=('bold', 14), pady=20, padx=20)
        user_label.pack(side=tk.LEFT)
        phone = tk.StringVar()
        tkVars += [phone]
        user_entry = tk.Entry(frame, textvariable=phone)
        user_entry.pack(side=tk.LEFT)

        user_label = tk.Label(frame, text='Department', font=('bold', 14), pady=20, padx=20)
        user_label.pack(side=tk.LEFT)
        dept = tk.StringVar()
        tkVars += [dept]
        user_entry = tk.Entry(frame, textvariable=dept)
        user_entry.pack(side=tk.RIGHT)

        frame = tk.Frame(self)
        frame.pack()
        user_label = tk.Label(frame, text='Grade', font=('bold', 14), pady=20, padx=20)
        user_label.pack(side=tk.LEFT)
        grade = tk.StringVar()
        tkVars += [grade]
        user_entry = tk.Entry(frame, textvariable=grade)
        user_entry.pack(side=tk.LEFT)

        user_label = tk.Label(frame, text='Language', font=('bold', 14), pady=20, padx=20)
        user_label.pack(side=tk.LEFT)
        language = tk.StringVar()
        tkVars += [language]
        user_entry = tk.Entry(frame, textvariable=language)
        user_entry.pack(side=tk.RIGHT)

        frame = tk.Frame(self)
        frame.pack()
        user_label = tk.Label(frame, text='Region', font=('bold', 14), pady=20, padx=20)
        user_label.pack(side=tk.LEFT)
        region = tk.StringVar()
        tkVars += [region]
        user_entry = tk.Entry(frame, textvariable=region)
        user_entry.pack(side=tk.LEFT)

        user_label = tk.Label(frame, text='Role', font=('bold', 14), pady=20, padx=20)
        user_label.pack(side=tk.LEFT)
        role = tk.StringVar()
        tkVars += [role]
        user_entry = tk.Entry(frame, textvariable=role)
        user_entry.pack(side=tk.RIGHT)

        frame = tk.Frame(self)
        frame.pack()
        user_label = tk.Label(frame, text='Tags', font=('bold', 14), pady=20, padx=20)
        user_label.pack(side=tk.LEFT)
        tags = tk.StringVar()
        tkVars += [tags]
        user_entry = tk.Entry(frame, textvariable=tags)
        user_entry.pack(side=tk.LEFT)

        user_label = tk.Label(frame, text='Credits', font=('bold', 14), pady=20, padx=20)
        user_label.pack(side=tk.LEFT)
        credits = tk.StringVar()
        tkVars += [credits]
        user_entry = tk.Entry(frame, textvariable=credits)
        user_entry.pack(side=tk.RIGHT)

        user_submit = tk.Button(self, text='Create User',
                                command=lambda: controller.create_user(list(map(lambda x: x.get(), tkVars))),
                                pady=5, padx=20)
        user_submit.pack()

        back_buttons = tk.Frame(self)
        back_buttons.pack(pady=10)

        back = tk.Button(back_buttons, text="Back",
                            command=lambda: controller.show_frame(UserPage))
        back.pack(side=tk.LEFT)

        button1 = tk.Button(back_buttons, text="Back to Home",
                            command=lambda: controller.show_frame(StartPage))
        button1.pack(side=tk.LEFT)


class EditUserPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Edit User", font=LARGE_FONT, fg='blue')
        label.pack(pady=10, padx=10)

        tkVars = {}

        frame = tk.Frame(self)
        frame.pack()
        user_label = tk.Label(frame, text='User ID', font=('bold', 14), pady=20, padx=20)
        user_label.pack(side=tk.LEFT)
        uid = tk.StringVar()
        tkVars['uid'] = uid
        user_entry = tk.Entry(frame, textvariable=uid)
        user_entry.pack(side=tk.LEFT)

        user_label = tk.Label(frame, text='Name', font=('bold', 14), pady=20, padx=20)
        user_label.pack(side=tk.LEFT)
        name = tk.StringVar()
        tkVars['name'] = name
        user_entry = tk.Entry(frame, textvariable=name)
        user_entry.pack(side=tk.RIGHT)

        frame = tk.Frame(self)
        frame.pack()
        user_label = tk.Label(frame, text='Gender', font=('bold', 14), pady=20, padx=20)
        user_label.pack(side=tk.LEFT)
        gender = tk.StringVar()
        tkVars['gender'] = gender
        user_entry = tk.Entry(frame, textvariable=gender)
        user_entry.pack(side=tk.LEFT)

        user_label = tk.Label(frame, text='Email', font=('bold', 14), pady=20, padx=20)
        user_label.pack(side=tk.LEFT)
        email = tk.StringVar()
        tkVars['email'] = email
        user_entry = tk.Entry(frame, textvariable=email)
        user_entry.pack(side=tk.RIGHT)

        frame = tk.Frame(self)
        frame.pack()
        user_label = tk.Label(frame, text='Phone', font=('bold', 14), pady=20, padx=20)
        user_label.pack(side=tk.LEFT)
        phone = tk.StringVar()
        tkVars['phone'] = phone
        user_entry = tk.Entry(frame, textvariable=phone)
        user_entry.pack(side=tk.LEFT)

        user_label = tk.Label(frame, text='Department', font=('bold', 14), pady=20, padx=20)
        user_label.pack(side=tk.LEFT)
        dept = tk.StringVar()
        tkVars['dept'] = dept
        user_entry = tk.Entry(frame, textvariable=dept)
        user_entry.pack(side=tk.RIGHT)

        frame = tk.Frame(self)
        frame.pack()
        user_label = tk.Label(frame, text='Grade', font=('bold', 14), pady=20, padx=20)
        user_label.pack(side=tk.LEFT)
        grade = tk.StringVar()
        tkVars['grade'] = grade
        user_entry = tk.Entry(frame, textvariable=grade)
        user_entry.pack(side=tk.LEFT)

        user_label = tk.Label(frame, text='Language', font=('bold', 14), pady=20, padx=20)
        user_label.pack(side=tk.LEFT)
        language = tk.StringVar()
        tkVars['language'] = language
        user_entry = tk.Entry(frame, textvariable=language)
        user_entry.pack(side=tk.RIGHT)

        frame = tk.Frame(self)
        frame.pack()
        user_label = tk.Label(frame, text='Region', font=('bold', 14), pady=20, padx=20)
        user_label.pack(side=tk.LEFT)
        region = tk.StringVar()
        tkVars['region'] = region
        user_entry = tk.Entry(frame, textvariable=region)
        user_entry.pack(side=tk.LEFT)

        user_label = tk.Label(frame, text='Role', font=('bold', 14), pady=20, padx=20)
        user_label.pack(side=tk.LEFT)
        role = tk.StringVar()
        tkVars['role'] = role
        user_entry = tk.Entry(frame, textvariable=role)
        user_entry.pack(side=tk.RIGHT)

        frame = tk.Frame(self)
        frame.pack()
        user_label = tk.Label(frame, text='Tags', font=('bold', 14), pady=20, padx=20)
        user_label.pack(side=tk.LEFT)
        tags = tk.StringVar()
        tkVars['preferTags'] = tags
        user_entry = tk.Entry(frame, textvariable=tags)
        user_entry.pack(side=tk.LEFT)

        user_label = tk.Label(frame, text='Credits', font=('bold', 14), pady=20, padx=20)
        user_label.pack(side=tk.LEFT)
        obtainedCredits = tk.StringVar()
        tkVars['obtainedCredits'] = obtainedCredits
        user_entry = tk.Entry(frame, textvariable=obtainedCredits)
        user_entry.pack(side=tk.RIGHT)

        user_submit = tk.Button(self, text='Edit User',
                                command=lambda: controller.edit_user(dict(map(lambda x: (x[0], x[1].get()), tkVars.items()))),
                                pady=5, padx=20)
        user_submit.pack()

        back_buttons = tk.Frame(self)
        back_buttons.pack(pady=10)

        back = tk.Button(back_buttons, text="Back",
                            command=lambda: controller.show_frame(UserPage))
        back.pack(side=tk.LEFT)

        button1 = tk.Button(back_buttons, text="Back to Home",
                            command=lambda: controller.show_frame(StartPage))
        button1.pack(side=tk.LEFT)


class DeleteUserPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Delete User", font=LARGE_FONT, fg='blue')
        label.pack(pady=10, padx=10)

        top_frame = tk.Frame(self)
        top_frame.pack()

        user_label = tk.Label(top_frame, text='User ID', font=('bold', 14), pady=20, padx=20)
        user_label.pack(side=tk.LEFT)

        user_text = tk.StringVar()
        user_entry = tk.Entry(top_frame, textvariable=user_text)
        user_entry.pack(side=tk.LEFT)

        user_submit = tk.Button(top_frame, text='Delete',
                                command=lambda: controller.delete_user(user_text),
                                pady=5, padx=20)
        user_submit.pack(side=tk.LEFT)

        back_buttons = tk.Frame(self)
        back_buttons.pack(pady=10)

        back = tk.Button(back_buttons, text="Back",
                            command=lambda: controller.show_frame(UserPage))
        back.pack(side=tk.LEFT)

        button1 = tk.Button(back_buttons, text="Back to Home",
                            command=lambda: controller.show_frame(StartPage))
        button1.pack(side=tk.LEFT)


class ArticlePage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Articles", font=LARGE_FONT, fg='blue')
        label.pack(pady=10, padx=10)

        top_frame = tk.Frame(self)
        top_frame.pack()

        article_label = tk.Label(top_frame, text='Article ID', font=('bold', 14), pady=20, padx=20)
        article_label.pack(side=tk.LEFT)

        article_text = tk.StringVar()
        article_entry = tk.Entry(top_frame, textvariable=article_text)
        article_entry.pack(side=tk.LEFT)

        article_submit = tk.Button(top_frame, text='Submit',
                                command=lambda: controller.fetch_article(article_text.get(), result_list, found_label),
                                pady=5, padx=20)
        article_submit.pack(side=tk.LEFT)

        found_label = tk.Label(self, text='', font=('bold', 14), padx=20)
        found_label.pack()

        result_list = tk.Listbox(self, height=20, width=80)
        result_list.pack()

        buttons = tk.Frame(self)
        buttons.pack(pady=10)

        edit_user_button = tk.Button(buttons, text="Read article",
                                     command=lambda: controller.open_article(result_list))
        edit_user_button.pack()

        back_button = tk.Button(self, text="Back to Home",
                            command=lambda: controller.show_frame(StartPage))
        back_button.pack(pady=5)


class ReadPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Reads", font=LARGE_FONT, fg='blue')
        label.pack(pady=10, padx=10)

        top_frame = tk.Frame(self)
        top_frame.pack()

        user_label = tk.Label(top_frame, text='User ID', font=('bold', 14), pady=20, padx=20)
        user_label.pack(side=tk.LEFT)

        user_text = tk.StringVar()
        user_entry = tk.Entry(top_frame, textvariable=user_text)
        user_entry.pack(side=tk.LEFT)

        user_submit = tk.Button(top_frame, text='Submit User ID',
                                command=lambda: controller.fetch_article_user(user_text.get(), result_list, found_label),
                                pady=5, padx=20)
        user_submit.pack(side=tk.LEFT)

        top_frame = tk.Frame(self)
        top_frame.pack()

        article_label = tk.Label(top_frame, text='Article ID', font=('bold', 14), pady=20, padx=20)
        article_label.pack(side=tk.LEFT)

        article_text = tk.StringVar()
        article_entry = tk.Entry(top_frame, textvariable=article_text)
        article_entry.pack(side=tk.LEFT)

        article_submit = tk.Button(top_frame, text='Submit Article ID',
                                command=lambda: controller.fetch_user_article(article_text.get(), result_list, found_label),
                                pady=5, padx=20)
        article_submit.pack(side=tk.LEFT)

        found_label = tk.Label(self, text='', font=('bold', 14), padx=20)
        found_label.pack()

        result_list = tk.Listbox(self, height=15, width=80)
        result_list.pack()

        button1 = tk.Button(self, text="Back to Home",
                            command=lambda: controller.show_frame(StartPage))
        button1.pack(pady=30)


class BeReadPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Article Stats", font=LARGE_FONT, fg='blue')
        label.pack(pady=10, padx=10)

        top_frame = tk.Frame(self)
        top_frame.pack()

        article_label = tk.Label(top_frame, text='Article ID', font=('bold', 14), pady=20, padx=20)
        article_label.pack(side=tk.LEFT)

        article_text = tk.StringVar()
        article_entry = tk.Entry(top_frame, textvariable=article_text)
        article_entry.pack(side=tk.LEFT)

        user_submit = tk.Button(top_frame, text='Submit',
                                command=lambda: controller.fetch_be_read(article_text, result_list, found_label),
                                pady=5, padx=20)
        user_submit.pack(side=tk.LEFT)

        found_label = tk.Label(self, text='', font=('bold', 14), padx=20)
        found_label.pack()

        result_list = tk.Listbox(self, height=20, width=80)
        result_list.pack()

        back_button = tk.Button(self, text="Back to Home",
                            command=lambda: controller.show_frame(StartPage))
        back_button.pack(side=tk.BOTTOM, pady=30)


class PopularRankPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Popular Rank", font=LARGE_FONT, fg='blue')
        label.pack(pady=10, padx=10)

        buttons = tk.Frame(self)
        buttons.pack()

        user_button = tk.Button(buttons, text="Daily",
                           command=lambda: controller.show_frame(DailyRankPage), font=MEDIUM_FONT)
        user_button.pack(side=tk.LEFT)

        articles_button = tk.Button(buttons, text="Weekly",
                            command=lambda: controller.show_frame(WeeklyRankPage), font=MEDIUM_FONT)
        articles_button.pack(side=tk.LEFT)

        read_button = tk.Button(buttons, text="Monthly",
                                command=lambda: controller.show_frame(MonthlyRankPage), font=MEDIUM_FONT)
        read_button.pack(side=tk.LEFT)

        button1 = tk.Button(self, text="Back to Home",
                            command=lambda: controller.show_frame(StartPage))
        button1.pack(pady=30)

class DailyRankPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Daily Rank", font=LARGE_FONT, fg='blue')
        label.pack(pady=10, padx=10)

        top_frame = tk.Frame(self)
        top_frame.pack()

        day_label = tk.Label(top_frame, text='Day', font=('bold', 14), pady=20, padx=20)
        day_label.pack(side=tk.LEFT)

        day_text = tk.StringVar()
        day_entry = tk.Entry(top_frame, textvariable=day_text)
        day_entry.pack(side=tk.LEFT)

        top_label = tk.Label(top_frame, text='Top', font=('bold', 14), pady=20, padx=20)
        top_label.pack(side=tk.LEFT)

        top_text = tk.StringVar()
        top_entry = tk.Entry(top_frame, textvariable=top_text)
        top_entry.pack(side=tk.LEFT)

        user_submit = tk.Button(top_frame, text='Submit',
                                command=lambda: controller.fetch_daily_rank(day_text, top_text, result_list, found_label),
                                pady=5, padx=20)
        user_submit.pack(side=tk.LEFT)

        found_label = tk.Label(self, text='', font=('bold', 14), padx=20)
        found_label.pack()

        result_list = tk.Listbox(self, height=20, width=80)
        result_list.pack()

        edit_user_button = tk.Button(self, text="Read article",
                                     command=lambda: controller.open_article(result_list))
        edit_user_button.pack(pady=10)

        back_buttons = tk.Frame(self)
        back_buttons.pack(pady=10)

        back = tk.Button(back_buttons, text="Back",
                         command=lambda: controller.show_frame(PopularRankPage))
        back.pack(side=tk.LEFT)

        button1 = tk.Button(back_buttons, text="Back to Home",
                            command=lambda: controller.show_frame(StartPage))
        button1.pack(side=tk.LEFT)


class WeeklyRankPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Weekly Rank", font=LARGE_FONT, fg='blue')
        label.pack(pady=10, padx=10)

        top_frame = tk.Frame(self)
        top_frame.pack()

        week_label = tk.Label(top_frame, text='Week', font=('bold', 14), pady=20, padx=20)
        week_label.pack(side=tk.LEFT)

        week_text = tk.StringVar()
        week_entry = tk.Entry(top_frame, textvariable=week_text)
        week_entry.pack(side=tk.LEFT)

        top_label = tk.Label(top_frame, text='Top', font=('bold', 14), pady=20, padx=20)
        top_label.pack(side=tk.LEFT)

        top_text = tk.StringVar()
        top_entry = tk.Entry(top_frame, textvariable=top_text)
        top_entry.pack(side=tk.LEFT)

        user_submit = tk.Button(top_frame, text='Submit',
                                command=lambda: controller.fetch_weekly_rank(week_text, top_text, result_list, found_label),
                                pady=5, padx=20)
        user_submit.pack(side=tk.LEFT)

        found_label = tk.Label(self, text='', font=('bold', 14), padx=20)
        found_label.pack()

        result_list = tk.Listbox(self, height=20, width=80)
        result_list.pack()

        edit_user_button = tk.Button(self, text="Read article",
                                     command=lambda: controller.open_article(result_list))
        edit_user_button.pack(pady=10)

        back_buttons = tk.Frame(self)
        back_buttons.pack(pady=10)

        back = tk.Button(back_buttons, text="Back",
                         command=lambda: controller.show_frame(PopularRankPage))
        back.pack(side=tk.LEFT)

        button1 = tk.Button(back_buttons, text="Back to Home",
                            command=lambda: controller.show_frame(StartPage))
        button1.pack(side=tk.LEFT)


class MonthlyRankPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Monthly Rank", font=LARGE_FONT, fg='blue')
        label.pack(pady=10, padx=10)

        top_frame = tk.Frame(self)
        top_frame.pack()

        month_label = tk.Label(top_frame, text='Month', font=('bold', 14), pady=20, padx=20)
        month_label.pack(side=tk.LEFT)

        month_text = tk.StringVar()
        month_entry = tk.Entry(top_frame, textvariable=month_text)
        month_entry.pack(side=tk.LEFT)

        top_label = tk.Label(top_frame, text='Top', font=('bold', 14), pady=20, padx=20)
        top_label.pack(side=tk.LEFT)

        top_text = tk.StringVar()
        top_entry = tk.Entry(top_frame, textvariable=top_text)
        top_entry.pack(side=tk.LEFT)

        user_submit = tk.Button(top_frame, text='Submit',
                                command=lambda: controller.fetch_monthly_rank(month_text, top_text, result_list, found_label),
                                pady=5, padx=20)
        user_submit.pack(side=tk.LEFT)

        found_label = tk.Label(self, text='', font=('bold', 14), padx=20)
        found_label.pack()

        result_list = tk.Listbox(self, height=20, width=80)
        result_list.pack()

        edit_user_button = tk.Button(self, text="Read article",
                                     command=lambda: controller.open_article(result_list))
        edit_user_button.pack(pady=10)

        back_buttons = tk.Frame(self)
        back_buttons.pack(pady=10)

        back = tk.Button(back_buttons, text="Back",
                         command=lambda: controller.show_frame(PopularRankPage))
        back.pack(side=tk.LEFT)

        button1 = tk.Button(back_buttons, text="Back to Home",
                            command=lambda: controller.show_frame(StartPage))
        button1.pack(side=tk.LEFT)


if __name__ == '__main__':
    if not os.path.isdir(TMP_FILE_DIR):
        os.mkdir(TMP_FILE_DIR)
    app = ArticleApp()
    app.mainloop()
    if os.path.isdir(TMP_FILE_DIR):
        shutil.rmtree(TMP_FILE_DIR, ignore_errors=True)
