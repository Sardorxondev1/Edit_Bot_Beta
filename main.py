from threading import Thread
from random import randint
import traceback
import datetime
import telebot
import metod
import time


# 5052917948:AAFPg3FIPWllF8Kz0X5Bl5XRzRFOP6WUQmM Test
# 5205648942:AAHYxUFII69pZMZ78sU4EBX7uwTVj5_HfMg Main
bot = telebot.TeleBot('5168841978:AAGPbns3NLLb1Staj2C9FiM_N8QaNx826Q4')
channels = []
try:
    users, edits, mails, sinonims = metod.load_all(bot)
except Exception as e:
    bot.send_message(-1001694445646, 'Ошибка считывания базы!!!\n' + str(e))
    users, edits, mails, sinonims = metod.load_all(bot, load_base=False)

type_edits = ['Аниме', 'Фильм', 'Сериал', 'Игра', 'Всё']
all_save = False

all_names, edit_names = [], [[], [], [], [], ['']]
for e in edits:
    if e.video is not None and e.name is not None and e.type != 4:
        edit_names[e.type].append(e.name)
        all_names.append(e.name)
for i in range(len(edit_names)):
    edit_names[i] = list(set(edit_names[i]))
all_names = list(set(all_names))

num_req_hour = req_hour = num_act_users = req_all = 0
act_users_hour, first_hour = set(), True


def Timer():
    global act_users_hour, req_hour, num_act_users, num_req_hour, all_save, first_hour
    truetime = (datetime.datetime.now() + datetime.timedelta(hours=3)).strftime("%d %B %Y %H:%M:%S")
    bot.send_message(-1001698445646, 'Start ' + truetime)
    while True:
        for i in range(360):
            for m in mails:
                delta = datetime.datetime.strptime(m['date'], '%Y-%m-%d %H:%M:%S') - datetime.datetime.now()
                if delta.seconds < 10:
                    if m['button'] is not None:
                        keyboard = telebot.types.InlineKeyboardMarkup()
                        keyboard.row(telebot.types.InlineKeyboardButton(m['button'], url=m['link']))
                        for u in users:
                            time.sleep(0.05)
                            if u.user_id == 1532205759:
                                bot.send_photo(u.user_id, photo=m['photo'], caption=m['text'], reply_markup=keyboard)
                    else:
                        for u in users:
                            time.sleep(0.05)
                            if u.user_id == 1532205759:
                                bot.send_photo(u.user_id, photo=m['photo'], caption=m['text'])
                    all_save = True
                    mails.pop(mails.index(m))

            if all_save:
                t = time.time()
                try:
                    metod.save_all(bot, users, edits, mails, sinonims)
                except Exception as e:
                    bot.send_message(-1001644445646, 'Ошибка сохранения!!!\n' + str(e))
                all_save = False
                time.sleep(max(0.001, 10 - (time.time() - t)))
            else:
                time.sleep(10)

        all_save = True
        num_act_users = len(act_users_hour)
        act_users_hour = set()
        num_req_hour = req_hour
        first_hour = False
        req_hour = 0


def get_user(user_id):
    for i in range(len(users)):
        if users[i].user_id == user_id:
            return users[i]

    u = metod.User(user_id)
    users.append(u)
    return u


@bot.message_handler(commands=["start"])
def start(message):
    user = get_user(message.chat.id)
    metod.menu(bot, message.chat.id, user, edit=False)


@bot.message_handler(commands=["_creator"])
def start(message):
    bot.send_message(message.chat.id,
                     'Эдит бот разработал Косач Иван, студент 1 курса факультета КФУ ИТИС, в феврале 2022 года')


@bot.message_handler(commands=["save"])
def save(message):
    global all_save
    if message.chat.id == -1001444545646:
        all_save = True
        bot.send_message(message.chat.id, 'Сохраняю...')


@bot.message_handler(commands=["e3i90it"])
def admin(message):
    user = get_user(message.chat.id)

    if user.admin:
        user.message_del.append(bot.send_message(message.chat.id, 'Вы уже администратор').message_id)
        return 0
    user.admin = True

    user.message_del.append(bot.send_message(message.chat.id, 'Поздравляю! Теперь Вы администратор!').message_id)


@bot.callback_query_handler(func=lambda call: True)
def handle(call):
    global req_hour, req_all, all_save

    chat_id = call.message.chat.id
    user = get_user(chat_id)
    req_hour += 1
    req_all += 1

    if user.user_id not in act_users_hour:
        if not user.check_subscriber(bot, channels):
            user.subscribed = False
        act_users_hour.add(user.user_id)

    first_click = call.data == 'Del_folder' and user.vars.get('click') is None
    if call.data[:3] not in ['mor', 'add', 'del', 'Fol'] and not first_click:
        try:
            for id in user.message_del:
                bot.delete_message(chat_id, id)
        except Exception:
            pass
        user.message_del = []

    if not user.subscribed and not user.admin:
        if call.data != 'ready':
            call.data = ''
            keyboard = telebot.types.InlineKeyboardMarkup()
            keyboard.row(telebot.types.InlineKeyboardButton("Канал Subarashi_edits",
                                                            url='https://t.me/Subarashi_edits'))
            keyboard.row(telebot.types.InlineKeyboardButton("Канал AnimeEdit", url='https://t.me/editshub'))
            keyboard.row(telebot.types.InlineKeyboardButton("Готово", callback_data="ready"))
            text = '🌸 Подпишись на наши каналы, что бы пользоваться ботом:'
            bot.edit_message_text(text, chat_id=chat_id, message_id=call.message.message_id)
            bot.edit_message_reply_markup(chat_id=chat_id, message_id=call.message.message_id, reply_markup=keyboard)
        else:
            if not user.check_subscriber(bot, channels):
                bot.answer_callback_query(callback_query_id=call.id, text='🥺 Увы, но ты ещё не подписался')
            else:
                user.subscribed = True
                call.data = 'menu'

    elif call.data == 'menu0':
        text = 'Выбери категорию эдитов'
        user.vars = {}
        type_edits_smiles = ['🔮 Аниме', '🎬 Фильмы', '🎞 Сериалы', '🎮 Игры', '🌐 Всё']
        metod.message(bot, call, text, type_edits_smiles, 'inmenu0')

    elif call.data[:7] == 'inmenu0' or call.data[:6] == 'n_list':
        if user.vars.get('type') is None and call.data[:7] == 'inmenu0':
            user.vars['type'] = int(call.data[7:]) if call.data[7:] != '' else 0
            if user.vars.get('type') == 4:
                call.data = 'names0'
        if user.vars.get('type') is None:
            user.vars['type'] = 0

        if user.vars.get('type') != 4:

            text = 'Выбери название из списка, по которому хочешь увидеть ' \
                   'эдиты или напиши и отправь название, для быстрого поиска ' \
                   '(если не находит на русском, попробуй вводить на английском)'

            metod.show_list_names(bot, call, edit_names[user.vars['type']], text, 'names', 'menu0', user)

    elif call.data == 'menu1':
        text = 'Выбери настроение:'
        but = ['🤡 Радость', '🥳 Веселье', '😎 Спокойствие', '☹️ Грусть ',
               '🤬 Гнев', '😮‍💨 Тревожность', '🪓 Тильт', '⚰ 1000-7']
        metod.message(bot, call, text, but, 'mood', row1=False)

    elif call.data == 'menu2':
        text = 'Выбери знак зодиака:'
        but = ['🐏Овен', '🐂Телец', '👥Близнецы', '🦞Рак', '🦁Лев', '👱‍♀️Дева',
               '⚖Весы', '🦂Скорпион', '🏹Стрелец', '🐐Козерог', '🌊Водолей', '🐟Рыбы']
        metod.message(bot, call, text, but, 'zodiac', row1=False)

    elif call.data == 'menu3' or call.data[:6] == 'r_next':
        text = 'Выбери действие:'
        if call.data == 'menu3':
            metod.message(bot, call, 'нажми 🎲 что бы посмотреть случайные Эдиты', ['🎲'], 'r_next')
            return 0
        metod.random_edit(bot, call, user, text, edits)

    elif call.data == 'Add_folder':
        if len(user.folders) > 5:
            bot.answer_callback_query(callback_query_id=call.id, text='Превышено максимальное количество папок')
        elif user.vars.get('text') is None:
            bot.answer_callback_query(callback_query_id=call.id, text='Введите название папки')
        elif len(str(user.vars['text'])) > 15:
            bot.answer_callback_query(callback_query_id=call.id, text='Название слишком длинное')
        elif user.vars['text'] in [g[0] for g in user.folders]:
            bot.answer_callback_query(callback_query_id=call.id, text='Эта папка уже существует')
        else:
            for char in str(user.vars['text']):
                c = char.lower()
                if not ('a' <= c <= 'z' or 'а' <= c <= 'я' or '0' <= c <= '9'
                        or c in [' ', '_', '!', '?', ',', '.', '-', '/', '(', ')']):
                    text = 'В названии имеется неразрешённый символ "' + c + '"'
                    bot.answer_callback_query(callback_query_id=call.id, text=text)
                    return 0
            user.folders.append([user.vars['text']])
            bot.answer_callback_query(callback_query_id=call.id, text='Папка создана')
            call.data = 'menu4'

    elif call.data == 'Del_folder':
        if len(user.folders) == 1:
            bot.answer_callback_query(callback_query_id=call.id, text='Должна быть хотя бы одна папка')
        elif user.vars.get('click') is None:
            user.vars['click'] = True
            bot.answer_callback_query(callback_query_id=call.id, text='Нажми ещё раз, чтобы удалить')
        else:
            user.folders.pop(user.vars['ind_fold'])
            bot.answer_callback_query(callback_query_id=call.id, text='Папка удалена')
            call.data = 'menu4'

    if call.data == 'menu4':
        user.vars['click'] = None
        but = [f[0] for f in user.folders]
        spec = [[('📒 Создать папку', 'Add_folder'), ('🔙 Вернуться', 'menu')]]
        metod.message(bot, call, 'Мой эдитлист', but, 'fold', row1=False, spec_bat=spec)

    elif call.data[:4] == 'fold' or call.data[:6] == 'f_list':
        if call.data[:4] == 'fold':
            fold = user.folders[int(call.data[4:])]
            user.vars['ind_fold'] = int(call.data[4:])
        else:
            fold = user.folders[user.vars['ind_fold']]
        user.message_del.append(bot.send_message(chat_id, fold[0]).message_id)
        list_ind_edits = [i for i in fold[1:] if edits[i].video is not None]
        spec = [[('❌ Удалить папку', 'Del_folder'), ('🔙 Вернуться', 'menu4')]]
        metod.show_list_edits(bot, user, call, list_ind_edits, edits, 'f', spec_bat=spec)

    elif call.data == 'menu5':
        user.vars = {}
        but = ['📕 База эдитов', '📈 Статистика', '⏰ Рассылки', '📖 Синонимы']
        metod.message(bot, call, 'Меню администратора', but, 'admin')

    elif call.data == 'admin0' or call.data[:6] == 'b_list':
        user.vars['admin_del'] = True
        user.message_del.append(bot.send_message(chat_id, 'База всех эдитов').message_id)
        list_ind_edits = [i for i in range(len(edits)) if edits[i].video is not None]
        metod.show_list_edits(bot, user, call, list_ind_edits, edits, 'b')

    elif call.data[:6] == 'admin1':
        if call.data == 'admin1_get':
            with open('user_list.txt', 'w') as f:
                for u in users:
                    f.write(str(u.user_id) + '\n')
            with open('user_list.txt', 'r') as f:
                user.message_del.append(bot.send_document(
                    chat_id, document=f, caption='User_list ' + str(time.ctime(time.time()))).message_id)
        text = f'Статистика\n' \
               f'✔Всего пользователей: {len(users)}\n' \
               f'✔Кол-во запросов за сеанс: {req_all}\n' \
               f'✔Кол-во запросов в час: {num_req_hour if not first_hour else str(req_hour) + "..."}\n' \
               f'✔Кол-во активных пользователей в час: ' \
               f'{num_act_users if not first_hour else str(len(act_users_hour)) + "..."}\n'
        spec = [[('Получить юзерлист', 'admin1_get'), ('🔙 Вернуться', 'menu5')]]
        metod.message(bot, call, text, [], '', spec_bat=spec, add_ind=False)

    elif call.data[:6] == 'admin2':
        if call.data == 'admin2':
            user.vars['post'] = None
            user.vars['text'] = None
        elif call.data[:10] == 'admin2_get':
            user.vars['mail_del'] = ''
            mail = mails[int(call.data[10:])]
            delta = datetime.datetime.strptime(mail['date'], '%Y-%m-%d %H:%M:%S') - datetime.datetime.now()
            comment = '\n' + '_' * 30 + '\nДата рассылки: ' + mail['date'] + ' \nЧерез ' + str(delta.days) + ' дней'
            keyboard = telebot.types.InlineKeyboardMarkup()
            if mail['button'] is not None:
                keyboard.row(telebot.types.InlineKeyboardButton(mail['button'], url=mail['link']))
            button = telebot.types.InlineKeyboardButton(text='❌ Удалить', callback_data='del' + call.data[10:] + '|4')
            keyboard.row(button)
            user.message_del.append(bot.send_photo(call.message.chat.id, mail['photo'], reply_markup=keyboard,
                                                   caption=mail['text'] + comment).message_id)
        elif call.data == 'admin2_add':
            if user.vars.get('post') is None:
                text = 'Пришли картинку с текстом для рассылки\n' \
                       'Добавь в текст пункты text: и link: чтобы создать кнопку'
                user.message_del.append(bot.send_message(chat_id, text).message_id)
            elif user.vars.get('text') is None:
                user.message_del.append(
                    bot.send_message(chat_id, 'Введи дату и время рассылки в формате DD.MM.YY,hh:mm').message_id)
            else:
                try:
                    info1 = user.vars['text'].split(',')
                    info2 = info1[0].split('.') + info1[1].split(':')
                    d3, d2, d1, t1, t2 = list(map(int, info2))
                    date_str = str(datetime.datetime(d1, d2, d3, t1, t2))
                except Exception:
                    bot.answer_callback_query(callback_query_id=call.id, text='Дата введена неправильно!')
                    return 0
                photo, text, button, link = user.vars['post'][0], user.vars['post'][1], None, None
                if len(user.vars['post']) == 4:
                    button, link = user.vars['post'][2], user.vars['post'][3]
                mails.append({'date': date_str, 'photo': photo,
                              'text': text, 'button': button, 'link': link})
                bot.answer_callback_query(callback_query_id=call.id, text='Рассылка создана')
                all_save = True

        spec = [[('Создать рассылку', 'admin2_add'), ('🔙 Вернуться', 'menu5')]]
        but = [capt['text'][:capt['text'].find('\n')] + ' ...' for capt in mails]
        metod.message(bot, call, 'Выбери рассылку для редактирования', but, 'admin2_get', spec_bat=spec)

    elif call.data[:6] in ['admin3', 'a_list', 'a_sino']:
        if call.data == 'admin3add' and user.vars.get('text') is None:
            bot.answer_callback_query(callback_query_id=call.id, text='Введи текст')
        elif call.data == 'admin3add':
            word = str(user.vars['text'])
            if sinonims.get(all_names[user.vars['ind']]) is None:
                sinonims[all_names[user.vars['ind']]] = []
            if user.vars['text'] in sinonims[all_names[user.vars['ind']]]:
                bot.answer_callback_query(callback_query_id=call.id, text='Такой синоним уже есть')
                return 0
            sinonims[all_names[user.vars['ind']]].append(word)
            text = 'Синоним ' + word + ' добавлен к названию ' + all_names[user.vars['ind']]
            bot.answer_callback_query(callback_query_id=call.id, text=text)
        elif call.data[:9] == 'admin3del':
            sinonims[all_names[user.vars['ind']]].pop(int(call.data[9:]))
            bot.answer_callback_query(callback_query_id=call.id, text='Синоним удален')
        elif call.data[:9] == 'a_sinonim':
            user.vars['ind'] = int(call.data[10:])

        if call.data == 'admin3' or call.data[:6] == 'a_list':
            user.vars['text'] = None
            text = 'Выбери название для редактирования синонимов'
            metod.show_list_names(bot, call, all_names, text, 'a_sinonims', 'menu5', user, finder=False)
        elif call.data[:6] in ['admin3', 'a_sino']:
            ind = user.vars['ind']
            but = sinonims[all_names[ind]] if sinonims.get(all_names[ind]) is not None else []
            spec = [[('добавить', 'admin3add'), ('🔙 Вернуться', 'admin3')]]
            text = 'Выбери синоним к названию ' + all_names[ind] + ' для удаления'
            metod.message(bot, call, text, but, 'admin3del', spec_bat=spec)

    elif call.data[:4] == 'more':
        ind, status = call.data[4:].split('|')
        keyboard = metod.get_keyboard_video(ind, int(status) - 1)
        bot.edit_message_caption(edits[int(ind)].caption, chat_id, call.message.message_id)
        bot.edit_message_reply_markup(chat_id=chat_id, message_id=call.message.message_id, reply_markup=keyboard)

    elif call.data[:3] == 'add':
        ind, status = call.data[3:].split('|')
        keyboard = metod.get_keyboard_video(ind, int(status), open_add=True)
        for i in range(len(user.folders)):
            button = telebot.types.InlineKeyboardButton(text='Добавить в ' + user.folders[i][0],
                                                        callback_data='Fold_add' + str(i) + '|' + ind + '|' + status)
            keyboard.row(button)
        bot.edit_message_reply_markup(chat_id=chat_id, message_id=call.message.message_id, reply_markup=keyboard)

    elif call.data[:3] == 'del':
        ind, status = call.data[3:].split('|')
        keyboard = metod.get_keyboard_video(ind, 0)
        if user.vars.get('admin_del') is not None:
            edits[int(ind)].delete()
        elif user.vars.get('mail_del') is not None:
            mails.pop(int(ind))
            user.vars['post'] = None
            user.vars['text'] = None
        else:
            ind_f = int(user.vars['ind_fold'])
            user.folders[ind_f].pop(user.folders[ind_f].index(int(ind)))
        bot.edit_message_reply_markup(chat_id=chat_id, message_id=call.message.message_id, reply_markup=keyboard)
        bot.answer_callback_query(callback_query_id=call.id, text='Удалено')

    elif call.data[:8] == 'Fold_add':
        f, ind, status = call.data[8:].split('|')
        if user.folders[int(f)].count(int(ind)) > 0:
            bot.answer_callback_query(callback_query_id=call.id, text='Этот эдит уже есть в этой папке')
        else:
            user.folders[int(f)].append(int(ind))
            bot.answer_callback_query(callback_query_id=call.id, text='Эдит добавлен в ' + user.folders[int(f)][0])
            keyboard = metod.get_keyboard_video(ind, int(status))
            bot.edit_message_reply_markup(chat_id=chat_id, message_id=call.message.message_id, reply_markup=keyboard)

    if call.data[:4] in ['mood', 'zodi', 'name', 'find']:
        if user.vars.get('type') is None:
            user.vars['type'] = 0
        if call.data == 'find':
            if user.vars.get('text') is None:
                bot.answer_callback_query(callback_query_id=call.id, text='Введи название')
                return 0
            text = str(user.vars['text']).lower().strip()
            ind = metod.find_word(text, edit_names[user.vars['type']], sinonims)
            if ind == -1:
                bot.answer_callback_query(callback_query_id=call.id, text='Подходящих по запросу эдитов не найдено')
                return 0

            call.data = 'names' + str(ind)

        names = all_names if call.data[:4] in ['mood', 'zodi'] else edit_names[user.vars['type']]
        need_ind_edits = metod.type_edits(call.data, user, edits, names)
        if len(need_ind_edits) == 0:
            user.saw_list = []
            need_ind_edits = metod.type_edits(call.data, user, edits, names)
        while 0 < len(need_ind_edits) < 5:
            user.saw_list = []
            need_ind_edits += metod.type_edits(call.data, user, edits, names)

        if user.admin:
            user.vars['admin_del'] = True
        for i in range(min(5, len(need_ind_edits))):
            user.saw_list.append(need_ind_edits[i])
            keyboard = metod.get_keyboard_video(need_ind_edits[i], 7 if user.admin else 3)
            user.message_del.append(bot.send_video(chat_id, edits[need_ind_edits[i]].video,
                                                   reply_markup=keyboard).message_id)
            time.sleep(0.1)

        text = 'Чтобы не нагружать сервер, за раз я выдаю не больше 5 эдитов' if len(need_ind_edits) > 0 else 'Пусто'
        path_back = {'mood': 'menu1', 'zodi': 'menu2', 'name': 'inmenu0', 'find': 'inmenu0'}
        if user.vars['type'] == 4:
            path_back['name'] = 'menu0'
        bot.delete_message(chat_id, call.message.message_id)
        metod.message(bot, chat_id, text, ['Ещё!'], call.data, edit=False, add_ind=False,
                      back=path_back[call.data[:4]])

    elif call.data[:8] == 'set_mood':
        ind, mood = call.data[8:].split('|')
        edits[int(ind)].mood = int(mood)
        bot.delete_message(chat_id, call.message.message_id)
        bot.answer_callback_query(callback_query_id=call.id, text='Эдит добавлен')

    if call.data == 'menu':
        metod.menu(bot, call, user)


@bot.message_handler(content_types=["document"])
def find_edit(message):
    global users, edits, mails, sinonims
    if message.chat.id == -1001698545646:
        bot.send_message(message.chat.id, 'All resaving...')
        info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(info.file_path)
        with open('JSON_database.txt', 'wb') as new_file:
            new_file.write(downloaded_file)
        users, edits, mails, sinonims = metod.load_all(bot, load_base=False)
        metod.save_all(bot, users, edits, mails, sinonims)


@bot.message_handler(content_types=["photo"])
def mail(message):
    user = get_user(message.chat.id)
    if user.admin:
        capt = message.caption + '\n'
        if capt.count('text: ') == 1 and capt.count('link: ') == 1:
            text = capt[capt.find('text: ') + 6:]
            text = text[:text.find('\n')]
            link = capt[capt.find('link: ') + 6:]
            link = link[:link.find('\n')]
            capt = capt.replace('text: ' + text + '\n', '').replace('link: ' + link + '\n', '')
            user.vars['post'] = (message.photo[-1].file_id, capt, text, link)
        else:
            user.vars['post'] = (message.photo[-1].file_id, message.caption)


@bot.message_handler(content_types=["video"])
def add_edit(message):
    user = get_user(message.chat.id)
    if user.admin:
        for edit in edits:
            if edit.caption == message.caption:
                metod.message(bot, message.chat.id, 'Этот эдит уже в базе', '', 'menu', edit=False)
                return 0

        text = message.caption.lower()
        type, name = 4, ''
        for i in range(len(type_edits) - 1):
            if (type_edits[i] + ':').lower() in text:
                type = i
                nameOld1 = message.caption[text.find(type_edits[type].lower()) + len(type_edits[type]) + 1:] + ' '
                nameOld = nameOld1[:nameOld1.find('\n')].strip()
                ind = metod.find_word(nameOld, edit_names[type], sinonims)
                name = edit_names[type][ind] if ind != -1 else nameOld

                if ind == -1:
                    edit_names[type].append(name)
                    all_names.append(name)
                else:
                    message.caption = message.caption.replace(nameOld, name)

        edits.append(metod.Edit(message.video.file_id, message.caption, type, name, 2, randint(0, 11)))

        text = 'Выбери настроение эдита:'
        but = ['🤡 Радость', '🥳 Веселье', '😎 Спокойствие', '☹️ Грусть ', '🤬 Гнев', '😮‍💨 Тревожность']
        metod.message(bot, message.chat.id, text, but, 'set_mood' + str(len(edits)-1) + '|', edit=False, spec_bat=[])


@bot.message_handler(content_types=["text"])
def find_edit(message):
    user = get_user(message.chat.id)
    user.vars['text'] = message.text


thread = Thread(target=Timer)

print('START')
thread.start()
while True:
    try:
        bot.infinity_polling()
    except Exception as e:
        print(traceback.format_exc())
