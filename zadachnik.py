import telebot
import json
from telebot import types

WEEK_BUTTONS = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
TIME_START = 7
TIME_END = 21
TASK_BUTTONS = ["✔","❌","🗓","🕘"]

bot=telebot.TeleBot("6005035120:AAFSz1F_mHqiVITJSVY-M-0jH7intiaRBr4")

def day_keyboard(id_task):
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    keyboard_buttons = []
    for day in WEEK_BUTTONS:
        data= {'id':id_task, 'action':'day'}
        data['day_index'] = WEEK_BUTTONS.index(day)
        json_string=json.dumps(data)
        day_btn=types.InlineKeyboardButton(day, callback_data=json_string)
        keyboard_buttons.append(day_btn)
    keyboard.add(*keyboard_buttons)
    return keyboard
def time_keyboard(id_task):
    keyboard = types.InlineKeyboardMarkup(row_width=5)
    keyboard_buttons_time = []
    for time in range(TIME_START, TIME_END + 1):
        data= {'id':id_task, 'action':'time'}
        time_str = f"{time}:00"
        data['time'] = time_str
        json_string=json.dumps(data)
        time_btn=types.InlineKeyboardButton(time_str, callback_data=json_string)
        keyboard_buttons_time.append(time_btn)
    keyboard.add(*keyboard_buttons_time)
    return keyboard
def task_keyboard(id_task):
    keyboard = types.InlineKeyboardMarkup(row_width=4)
    keyboard_buttons = []
    for button in TASK_BUTTONS:
        data = {'id':id_task, 'action':button}
        json_string = json.dumps(data)
        task_button=types.InlineKeyboardButton(button, callback_data=json_string)
        keyboard_buttons.append(task_button)
    keyboard.add(*keyboard_buttons)
    return keyboard


todo_list=[]
id_next_task = 0

class Task:
    def __init__(self,name,day="",time=0):
        global id_next_task
        self.id = id_next_task
        id_next_task +=1
        self.day=day
        self.name=name
        self.time=time

BUTTONS=["✏️Новая задача", "📝Список дел"]

#@bot.callback_query_handler(func=lambda call: call.data in WEEK_BUTTONS)
@bot.callback_query_handler(func=lambda call:True)
def day_week(call):
    if len(todo_list) > 0:
        todo_list[-1].day=call.data
    bot.edit_message_text(f"Запланирована на {call.data}", call.message.chat.id, call.message.message_id)

#@bot.callback_query_handler(func=lambda call: call.data[0:11:] == "time_select")
def time_select(call, id_task, time):
    for i, task in enumerate(todo_list):
        if task.id == id_task:
            task.time = time
            bot.edit_message_text(f"🔸 Задача № {i + 1}. {task.name}\n{task.day} {task.time}", call.message.chat.id, call.message.message_id, reply_markup=task_keyboard(task.id))
            bot.answer_callback_query(call.id)

def day_select(call, id_task, day_index):
    for i, task in enumerate(todo_list):
        if task.id == id_task:
            task.day = WEEK_BUTTONS[day_index]
            bot.edit_message_text(f"🔸 Задача № {i + 1}. {task.name}\n{task.day} {task.time}", call.message.chat.id, call.message.message_id, reply_markup=task_keyboard(task.id))
            bot.answer_callback_query(call.id)

def delete_task(call, id_task, new_text):
    for task in todo_list:
        if task.id == id_task:
            todo_list.remove(task)
            bot.edit_message_text(new_text, call.message.chat.id, call.message.message_id)
            bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call:True)
def handler(call):
    data = json.loads(call.data)
    id_task = data.get("id")
    action = data.get("action")
    if action == TASK_BUTTONS[0]:
       delete_task(call, id_task, "задача выполнена")
    elif action == TASK_BUTTONS[1]:
        delete_task(call, id_task,"Задача удалена ❌")
    elif action == TASK_BUTTONS[2]:
        bot.edit_message_text(call.message.text,call.message.chat.id,call.message.message_id,reply_markup=day_keyboard(id_task))
    elif action == "day":
       day_index = data.get("day_index")
       day_select(call, id_task, day_index)
    elif action == TASK_BUTTONS[3]:
        bot.edit_message_text(call.message.text,call.message.chat.id,call.message.message_id,reply_markup=time_keyboard(id_task))
    elif action == 'time':
        time = data.get("time")
        time_select(call, id_task, time)

#@bot.message_handler(commands=["new_task"])
def add_new_task(message):
    bot.send_message(message.chat.id, "✏️Введите название задачи:")

#@bot.message_handler(commands=["todo_list"])
def print_todo_list(message):
    bot.send_message(message.chat.id, "📝Здесь будет твой список дел")
    if len (todo_list)==0 :
        bot.send_message(message.chat.id, "Ваш список пуст!☕")
    else:
        for i, task in enumerate(todo_list):
            text = f"Задача №{i+1}: {task.name} {task.day} {task.time}\n"
            bot.send_message(message.chat.id, text, reply_markup=task_keyboard(task.id))

@bot.message_handler(commands=["start", "/start", "/hi", "hi", "/hello", "hello"])
def start(message):
    markup = types.ReplyKeyboardMarkup()
    new_task_btn = types.KeyboardButton(BUTTONS[0])
    todo_list_btn = types.KeyboardButton(BUTTONS[1])
    markup.row(new_task_btn, todo_list_btn)
    bot.send_message(message.chat.id, "Привет, напиши 'Новая задача' для добовления новой задачи или 'Список дел' для просмотра твоего списка", reply_markup=markup)

@bot.message_handler(content_types=['text'])
def answer(message):
    if message.text == BUTTONS[0]:
        add_new_task(message)
    elif message.text == BUTTONS[1]:
        print_todo_list(message)
    else:
        new_task = Task(message.text)
        todo_list.append(new_task)
        bot.send_message(message.chat.id, f"Добавлена новая задача!📝\n {new_task.name}\n",reply_markup=task_keyboard(new_task.id))
        #bot.send_message(message.chat.id, "Выберите день начала задачи🌍", reply_markup=day_keyboard(new_task.id))
        #bot.send_message(message.chat.id, "Выберите время начала задачи⌚", reply_markup=time_keyboard(new_task.id))

bot.polling(none_stop=True, interval=0)