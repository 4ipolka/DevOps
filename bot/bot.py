import logging
import os
import re
import paramiko
import psycopg2
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from dotenv import load_dotenv

load_dotenv()


TOKEN = os.getenv('TOKEN')
host = os.getenv('RM_HOST')
port = os.getenv('RM_PORT')
username = os.getenv('RM_USER')
password = os.getenv('RM_PASSWORD')
db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')
db_username = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_name = os.getenv('DB_DATABASE')
found_email = ""
found_phone_number = ""
# Подключаем логирование
logging.basicConfig(
    filename='logfile.txt', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


def start(update: Update, context):
    user = update.effective_user
    update.message.reply_text(f'Привет {user.full_name}. Посмотреть доступные команды - /commands')

def commands(update: Update, context):
    update.message.reply_text("""
/find_email - поиск email-адреса в тексте
/find_phone_number - поиск номера телефона в тексте
/get_emails - получить записанные email-адреса
/get_phone_numbers - получить записанные номера телефонов
/verify_password - проверить надёжность пароля
/get_release - информация о релизе
/get_uname - информация об архитектуре процессора, имени хоста системы и версии ядра
/get_df - информация о состоянии файловой системы 
/get_free - информация о состоянии оперативной памяти
/get_mpstat - информация о производительности системы
/get_w - информация о работающих в данной системе пользователях.
/get_auths - последние 10 входов в систему
/get_critical - последние 5 критических событий
/get_ps - информация о запущенных процессах
/get_ss - информация об используемых портах
/get_apt_list - информация об установленных пакетах
/get_services - информация о запущенных сервисах
/get_repl_logs - логи репликаций
/help - HELP!
""")

def helpCommand(update: Update, context):
    update.message.reply_text('Help!')

def find_phone_numberCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска телефонных номеров: ')
    return 'find_phone_number'

def find_emailCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска email-адресов: ')
    return 'find_email'

def verify_passwordCommand(update: Update, context):
    update.message.reply_text('Введите пароль для проверки: ')
    return 'verify_password'

GET_APT_LIST, SEARCH_PACKAGE = range(2)

def get_apt_list_command(update: Update, context):
    update.message.reply_text('Выберите действие:\n1. Показать список установленных пакетов\n2. Поиск пакета')
    return GET_APT_LIST

def find_email(update: Update, context):
    global found_email
    user_input = update.message.text
    emailRegex = re.compile(r'\b[a-zA-Z0-9.!#$%&\'*+/=?^_{|}~-]+(?:\.[a-zA-Z0-9.!#$%&\'*+/=?^_{|}~-]+)*' \
                r'@(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}\b')
    emailList = emailRegex.findall(user_input)
    if not emailList:
        update.message.reply_text('Email-адреса не найдены')
        return ConversationHandler.END
    found_email = '\n'.join(emailList)
    update.message.reply_text('Найденные email-адреса:\n' + found_email + '\nХотите ли вы записать их в базу данных? (да/нет)')
    return 'ask_to_save_email'

def ask_to_save_email(update: Update, context):
    user_input = update.message.text
    if user_input.lower() == 'да':
        save_email(update, context)
    else:
        update.message.reply_text('Операция отменена.')
    return ConversationHandler.END

def save_email(update: Update, context):
    global found_email
    if update.message.text.lower() == 'да':
        try:
            conn = psycopg2.connect(host=db_host, port=db_port, user=db_username, password=db_password, dbname=db_name)
            cur = conn.cursor()
            for email in found_email.split('\n'):
                if email.strip():  # Проверяем, что строка не пустая
                    cur.execute("INSERT INTO emails (email) VALUES (%s)", (email.strip(),))
            conn.commit()
            conn.close()
            update.message.reply_text("Email-адреса успешно записаны в базу данных.")
        except Exception as e:
            update.message.reply_text(f"Ошибка при записи email-адресов: {e}")
    else:
        update.message.reply_text("Операция отменена.")

def find_phone_number(update: Update, context):
    global found_phone_number
    user_input = update.message.text
    phoneNumberRegex = re.compile(r"\+?7[ -]?\(?\d{3}\)?[ -]?\d{3}[ -]?\d{2}[ -]?\d{2}|\+?7[ -]?\d{10}|\+?7[ -]?\d{3}[ -]?\d{3}[ -]?\d{4}|8[ -]?\(?\d{3}\)?[ -]?\d{3}[ -]?\d{2}[ -]?\d{2}|8[ -]?\d{10}|8[ -]?\d{3}[ -]?\d{3}[ -]?\d{4}")
    phoneNumberList = phoneNumberRegex.findall(user_input)
    if not phoneNumberList:
        update.message.reply_text('Номера телефона не найдены')
        return ConversationHandler.END
    found_phone_number = '\n'.join(phoneNumberList)
    update.message.reply_text('Найденные номера телефона:\n' + found_phone_number + '\nХотите ли вы записать их в базу данных? (да/нет)')
    return 'ask_to_save_phone_number'

def ask_to_save_phone_number(update: Update, context):
    user_input = update.message.text
    if user_input.lower() == 'да':
        save_phone_number(update, context)
    else:
        update.message.reply_text('Операция отменена.')
    return ConversationHandler.END

def save_phone_number(update: Update, context):
    global found_phone_number
    if update.message.text.lower() == 'да':
        try:
            conn = psycopg2.connect(host=db_host, port=db_port, user=db_username, password=db_password, dbname=db_name)
            cur = conn.cursor()
            for number in found_phone_number.split('\n'):
                if number.strip():  # Проверяем, что строка не пустая
                    cur.execute("INSERT INTO numbers (number) VALUES (%s)", (number.strip(),))
            conn.commit()
            conn.close()
            update.message.reply_text("Номера телефонов успешно записаны в базу данных.")
        except Exception as e:
            update.message.reply_text(f"Ошибка при записи номеров телефонов: {e}")
    else:
        update.message.reply_text("Операция отменена.")

def verify_password(update: Update, context):
    user_input = update.message.text
    passwordRegex = re.compile(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*()_\-])[A-Za-z\d!@#$%^&*()_\-]{8,}$')
    if passwordRegex.match(user_input):
        update.message.reply_text('Пароль сложный')
    else:
        update.message.reply_text('Пароль простой')
    return ConversationHandler.END

def get_release_command(update: Update, context):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = ssh.exec_command('cat /etc/os-release')
    result = stdout.read().decode()
    ssh.close()
    update.message.reply_text(result)

def get_uname_command(update: Update, context):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = ssh.exec_command('uname -a')
    result = stdout.read().decode()
    ssh.close()
    update.message.reply_text(result)

def get_uptime_command(update: Update, context):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = ssh.exec_command('uptime')
    result = stdout.read().decode()
    ssh.close()
    update.message.reply_text(result)

def get_df_command(update: Update, context):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = ssh.exec_command('df -h')
    result = stdout.read().decode()
    ssh.close()
    update.message.reply_text(result)

def get_free_command(update: Update, context):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = ssh.exec_command('free -h')
    result = stdout.read().decode()
    ssh.close()
    update.message.reply_text(result)

def get_mpstat_command(update: Update, context):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = ssh.exec_command('mpstat')
    result = stdout.read().decode()
    ssh.close()
    update.message.reply_text(result)

def get_w_command(update: Update, context):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = ssh.exec_command('w')
    result = stdout.read().decode()
    ssh.close()
    update.message.reply_text(result)

def get_auths_command(update: Update, context):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = ssh.exec_command('last -n 10')
    result = stdout.read().decode()
    ssh.close()
    update.message.reply_text(result)

def get_critical_command(update: Update, context):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = ssh.exec_command('journalctl -p err -n 5')
    result = stdout.read().decode()
    ssh.close()
    update.message.reply_text(result)

def get_ps_command(update: Update, context):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = ssh.exec_command('ps aux | head -n 10')
    result = stdout.read().decode()
    ssh.close()
    update.message.reply_text(result)

def get_ss_command(update: Update, context):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = ssh.exec_command('ss -tuln')
    result = stdout.read().decode()
    ssh.close()
    update.message.reply_text(result)

def get_apt_list(update: Update, context):
    user_input = update.message.text
    if user_input == '1':
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=host, username=username, password=password, port=port)
        stdin, stdout, stderr = ssh.exec_command('apt list --installed | head -n 10')
        result = stdout.read().decode()
        ssh.close()
        update.message.reply_text(result)
    elif user_input == '2':
        update.message.reply_text('Введите название пакета для поиска:')
        return SEARCH_PACKAGE
    else:
        update.message.reply_text('Неверный ввод. Попробуйте снова.')
        return GET_APT_LIST

def search_package(update: Update, context):
    package_name = update.message.text
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = ssh.exec_command(f'apt list --installed | grep {package_name}')
    result = stdout.read().decode()
    ssh.close()
    if result:
        update.message.reply_text(result)
    else:
        update.message.reply_text('Пакет не найден.')
    return ConversationHandler.END

def get_services_command(update: Update, context):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = ssh.exec_command('systemctl list-units --type=service | head -n 10')
    result = stdout.read().decode()
    ssh.close()
    update.message.reply_text(result)

def get_repl_logs_command(update, context):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = ssh.exec_command("docker logs -n 40 db_image")
    result = stdout.read() + stderr.read()
    ssh.close()
    result = str(result).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    data = ''
    for line in result.split('\n'):
        if 'replic' in line:
            data += line + '\n'
    if len(data)==0:
        update.message.reply_text('Логи репликации не найдены')
    if len(data)>0:
        update.message.reply_text(data)

def get_emails_command(update: Update, context):
    try:
        conn = psycopg2.connect(host=db_host, port=db_port, user=db_username, password=db_password, dbname=db_name)
        cur = conn.cursor()
        cur.execute("SELECT email FROM emails")
        emails = cur.fetchall()
        conn.close()
        emails_list = '\n'.join([f"{email[0]}" for email in emails])
        update.message.reply_text(emails_list)
    except Exception as e:
        update.message.reply_text(f"Ошибка при получении email-адресов: {e}")

def get_phone_numbers_command(update: Update, context):
    try:
        conn = psycopg2.connect(host=db_host, port=db_port, user=db_username, password=db_password, dbname=db_name)
        cur = conn.cursor()
        cur.execute("SELECT number FROM numbers")
        phone_number = cur.fetchall()
        conn.close()
        phone_number_list = '\n'.join([f"{number[0]}" for number in phone_number])
        update.message.reply_text(phone_number_list)
    except Exception as e:
        update.message.reply_text(f"Ошибка при получении номеров телефонов: {e}")

def echo(update: Update, context):
    update.message.reply_text(update.message.text)

def main():
    updater = Updater(TOKEN, use_context=True)

    # Получаем диспетчер для регистрации обработчиков
    dp = updater.dispatcher

    # Обработчик диалога
    convHandlerfind_phone_number = ConversationHandler(
        entry_points=[CommandHandler('find_phone_number', find_phone_numberCommand)],
        states={
            'find_phone_number': [MessageHandler(Filters.text & ~Filters.command, find_phone_number)],
        },
        fallbacks=[]
    )
    convHandlerfind_email = ConversationHandler(
        entry_points=[CommandHandler('find_email', find_emailCommand)],
        states={
            'find_email': [MessageHandler(Filters.text & ~Filters.command, find_email)],
        },
        fallbacks=[]
    )

    convHandlerverify_password = ConversationHandler(
        entry_points=[CommandHandler('verify_password', verify_passwordCommand)],
        states={
            'verify_password': [MessageHandler(Filters.text & ~Filters.command, verify_password)],
        },
        fallbacks=[]
    )

    convHandlerget_release = ConversationHandler(
        entry_points=[CommandHandler('get_release', get_release_command)],
        states={
            'get_release': [MessageHandler(Filters.text & ~Filters.command, get_release_command)],
        },
        fallbacks=[]
    )

    convHandlerget_uname = ConversationHandler(
        entry_points=[CommandHandler('get_uname', get_uname_command)],
        states={
            'get_uname': [MessageHandler(Filters.text & ~Filters.command, get_uname_command)],
        },
    fallbacks=[]
    )

    convHandlerget_uptime = ConversationHandler(
        entry_points=[CommandHandler('get_uptime', get_uptime_command)],
        states={
            'get_uptime': [MessageHandler(Filters.text & ~Filters.command, get_uptime_command)],
        },
        fallbacks=[]
    )

    convHandlerget_df = ConversationHandler(
        entry_points=[CommandHandler('get_df', get_df_command)],
        states={
            'get_df': [MessageHandler(Filters.text & ~Filters.command, get_df_command)],
        },
        fallbacks=[]
    )

    convHandlerget_free = ConversationHandler(
        entry_points=[CommandHandler('get_free', get_free_command)],
        states={
            'get_free': [MessageHandler(Filters.text & ~Filters.command, get_free_command)],
        },
        fallbacks=[]
    )

    convHandlerget_mpstat = ConversationHandler(
        entry_points=[CommandHandler('get_mpstat', get_mpstat_command)],
        states={
            'get_mpstat': [MessageHandler(Filters.text & ~Filters.command, get_mpstat_command)],
        },
        fallbacks=[]
    )

    convHandlerget_w = ConversationHandler(
        entry_points=[CommandHandler('get_w', get_w_command)],
        states={
            'get_w': [MessageHandler(Filters.text & ~Filters.command, get_w_command)],
        },
        fallbacks=[]
    )

    convHandlerget_auths = ConversationHandler(
        entry_points=[CommandHandler('get_auths', get_auths_command)],
        states={
            'get_auths': [MessageHandler(Filters.text & ~Filters.command, get_auths_command)],
        },
        fallbacks=[]
    )

    convHandlerget_critical = ConversationHandler(
        entry_points=[CommandHandler('get_critical', get_critical_command)],
        states={
            'get_critical': [MessageHandler(Filters.text & ~Filters.command, get_critical_command)],
        },
        fallbacks=[]
    )

    convHandlerget_ps = ConversationHandler(
        entry_points=[CommandHandler('get_ps', get_ps_command)],
        states={
            'get_ps': [MessageHandler(Filters.text & ~Filters.command, get_ps_command)],
        },
        fallbacks=[]
    )

    convHandlerget_ss = ConversationHandler(
        entry_points=[CommandHandler('get_ss', get_ss_command)],
        states={
            'get_ss': [MessageHandler(Filters.text & ~Filters.command, get_ss_command)],
        },
        fallbacks=[]
    )

    convHandlerget_apt_list = ConversationHandler(
        entry_points=[CommandHandler('get_apt_list', get_apt_list_command)],
        states={
            GET_APT_LIST: [MessageHandler(Filters.text & ~Filters.command, get_apt_list)],
            SEARCH_PACKAGE: [MessageHandler(Filters.text & ~Filters.command, search_package)],
        },
        fallbacks=[]
    )

    convHandlerget_services = ConversationHandler(
        entry_points=[CommandHandler('get_services', get_services_command)],
        states={
            'get_services': [MessageHandler(Filters.text & ~Filters.command, get_services_command)],
        },
        fallbacks=[]
    )

    convHandlerget_repl_logs = ConversationHandler(
    entry_points=[CommandHandler('get_repl_logs', get_repl_logs_command)],
    states={
        'get_repl_logs': [MessageHandler(Filters.text & ~Filters.command, get_repl_logs_command)],
        },
        fallbacks=[]
    )

    convHandlerget_emails = ConversationHandler(
    entry_points=[CommandHandler('get_emails', get_emails_command)],
    states={
        'get_emails': [MessageHandler(Filters.text & ~Filters.command, get_emails_command)],
        },
        fallbacks=[]
    )
    
    convHandlerget_phone_numbers = ConversationHandler(
    entry_points=[CommandHandler('get_phone_numbers', get_phone_numbers_command)],
    states={
        'get_phone_numbers': [MessageHandler(Filters.text & ~Filters.command, get_phone_numbers_command)],
        },
        fallbacks=[]
    )

    convHandlerfind_phone_number = ConversationHandler(
    entry_points=[CommandHandler('find_phone_number', find_phone_numberCommand)],
    states={
        'find_phone_number': [MessageHandler(Filters.text & ~Filters.command, find_phone_number)],
        'ask_to_save_phone_number': [MessageHandler(Filters.text & ~Filters.command, ask_to_save_phone_number)],
        },
        fallbacks=[]
    )

    convHandlerfind_email = ConversationHandler(
    entry_points=[CommandHandler('find_email', find_emailCommand)],
    states={
        'find_email': [MessageHandler(Filters.text & ~Filters.command, find_email)],
        'ask_to_save_email': [MessageHandler(Filters.text & ~Filters.command, ask_to_save_email)],
        },
        fallbacks=[]
    )

	# Регистрируем обработчики команд
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", helpCommand))
    dp.add_handler(CommandHandler("commands", commands))
    dp.add_handler(convHandlerfind_phone_number)
    dp.add_handler(convHandlerfind_email)
    dp.add_handler(convHandlerverify_password)
    dp.add_handler(convHandlerget_release)
    dp.add_handler(convHandlerget_uname)
    dp.add_handler(convHandlerget_uptime)
    dp.add_handler(convHandlerget_df)
    dp.add_handler(convHandlerget_free)
    dp.add_handler(convHandlerget_mpstat)
    dp.add_handler(convHandlerget_w)
    dp.add_handler(convHandlerget_auths)
    dp.add_handler(convHandlerget_critical)
    dp.add_handler(convHandlerget_ps)
    dp.add_handler(convHandlerget_ss)
    dp.add_handler(convHandlerget_apt_list)
    dp.add_handler(convHandlerget_services)
    dp.add_handler(convHandlerget_repl_logs)
    dp.add_handler(convHandlerget_phone_numbers)
    dp.add_handler(convHandlerget_emails)

	# Регистрируем обработчик текстовых сообщений
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))
		
	# Запускаем бота
    updater.start_polling()

	# Останавливаем бота при нажатии Ctrl+C
    updater.idle()


if __name__ == '__main__':
    main()
# Алексеенко М.С.
