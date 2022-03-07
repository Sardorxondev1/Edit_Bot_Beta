import time
from random import shuffle
from github import Github
import datetime
import telebot
import json


class User:
    def __init__(self, user_id):
        self.user_id = user_id
        self.subscribed = False
        self.admin = False
        self.message_del = []
        self.saw_list = []
        self.folders = [['Новая папка']]
        self.vars = {}

    def check_subscriber(self, bot, channels):
        for channel in channels:
            try:
                status = bot.get_chat_member(channel, self.user_id).status
            except Exception:
                return False

            if status not in ['administrator', 'creator', 'member']:
                return False

        return True


class Edit:
    def __init__(self, video, caption, type, names, mood, zodiac):
        self.video = video
        self.caption = caption
        self.type = type
        self.name = names
        self.mood = mood
        self.zodiac = zodiac

    def delete(self):
        self.video = self.caption = self.type = self.name = self.mood = self.zodiac = None


def save_all(bot, users, edits, mails, sinonims):
    data = {'people': [], 'edits': [], 'mails': [], 'sinonims': sinonims}
    for u in users:
        data['people'].append({'0': u.user_id, '1': u.subscribed, '2': u.admin,
                               '3': u.message_del, '4': u.folders, '5': u.vars})
    for e in edits:
        data["edits"].append({"video": e.video, "caption": e.caption, "type": e.type,
                              "name": e.name, "mood": e.mood, "zodiac": e.zodiac})
    for m in mails:
        data["mails"].append(m)

    with open('JSON_database.txt', 'w') as f:
        f.write(json.dumps(data))

    with open('JSON_database.txt', 'r') as f:
        truetime = (datetime.datetime.now() + datetime.timedelta(hours=3)).strftime("%d %B %Y %H:%M:%S")
        message_info = bot.send_document(-1001644545646, document=f, caption=truetime)

    with open('last_doc.txt', 'w') as f:
        f.write(str(message_info.document.file_id))

    g = Github("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")
    repo = g.get_user().get_repo('Edit_bot')
    file = repo.get_contents("last_doc.txt")
    repo.update_file(file.path, "commit", str(message_info.document.file_id), file.sha)


def load_all(bot, load_base=True):
    if load_base:
        g = Github("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")
        repo = g.get_user().get_repo('Edit_bot')
        info = bot.get_file(str(repo.get_contents('last_doc.txt').decoded_content)[2:-1])
        downloaded_file = bot.download_file(info.file_path)
        with open('JSON_database.txt', 'wb') as new_file:
            new_file.write(downloaded_file)

    users, edits, mails = [], [], []
    with open('JSON_database.txt') as fin:
        data = json.loads(fin.read())
        for u in data['people']:
            try:
                user = User(u['0'])
                user.subscribed, user.admin, user.message_del = u['1'], u['2'], u['3']
                user.folders, user.vars = u['4'], u['5']
                users.append(user)
            except Exception:
                pass

        for e in data['edits']:
            edits.append(Edit(e['video'], e['caption'], e['type'], e['name'], e['mood'], e['zodiac']))

        for m in data['mails']:
            mails.append({'date': m['date'], 'photo': m['photo'], 'text': m['text'],
                          'button': m['button'], 'link': m['link']})

        sinonims = data['sinonims'] if data['sinonims'] != [] else {}

    return users, edits, mails, sinonims


def menu(bot, call, user, edit=True):
    user.vars = {}
    text = 'Выбери один из вариантов:'
    variants = ['🎑 Эдиты по названию', '🌃 Эдиты по настроению',
                '🌌 Эдиты по знаку зодиака', '🎲 Случайные эдиты', '📱 Мой эдитлист']
    if user.admin:
        variants += ['💼 Для админов']

    message(bot, call, text, variants, 'menu', edit=edit)


def message(bot, call, text, keyboard_var, callback, spec_bat=None, edit=True, row1=True, add_ind=True, back='menu'):
    keyboard = telebot.types.InlineKeyboardMarkup()
    if row1:
        for v in keyboard_var:
            ind = str(keyboard_var.index(v)) if add_ind else ''
            button = telebot.types.InlineKeyboardButton(text=v, callback_data=callback + ind)
            keyboard.row(button)
    else:
        for i in range(0, len(keyboard_var)-1, 2):
            keyboard.row(telebot.types.InlineKeyboardButton(text=keyboard_var[i],
                                                            callback_data=callback + str(i) if add_ind else ''),
                         telebot.types.InlineKeyboardButton(text=keyboard_var[i+1],
                                                            callback_data=callback + str(i+1) if add_ind else ''))

        if len(keyboard_var) % 2 == 1:
            keyboard.row(telebot.types.InlineKeyboardButton(text=keyboard_var[-1],
                                                            callback_data=callback + str(len(keyboard_var)-1)
                                                            if add_ind else ''))

    if callback != back and callback != 'set_mood':
        if spec_bat is not None:
            for h in range(len(spec_bat)):
                but = []
                for w in range(len(spec_bat[h])):
                    but.append(telebot.types.InlineKeyboardButton(text=spec_bat[h][w][0],
                                                                  callback_data=spec_bat[h][w][1]))
                keyboard.row(*but)
        else:
            keyboard.row(telebot.types.InlineKeyboardButton(text='🔙 Вернуться', callback_data=back))

    if edit:
        try:
            bot.edit_message_text(text, chat_id=call.message.chat.id, message_id=call.message.message_id)
            bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                          reply_markup=keyboard)
        except Exception:
            pass
    else:
        bot.send_message(call, text, reply_markup=keyboard)


def get_keyboard_video(ind, status, open_add=False):
    param = str(ind) + '|' + str(status)
    keyboard = telebot.types.InlineKeyboardMarkup()

    buttons = []
    if status % 2 == 1:
        buttons = [telebot.types.InlineKeyboardButton(text='🏷 Описание', callback_data='more' + param)]
    if status >= 4:
        buttons.append(telebot.types.InlineKeyboardButton(text='❌ Удалить', callback_data='del' + param))
    if status % 4 >= 2 and not open_add:
        buttons.append(telebot.types.InlineKeyboardButton(text='✅ Добавить в эдитлист', callback_data='add' + param))

    for b in buttons:
        keyboard.row(b)

    return keyboard


def get_no_saw_list(user, edits):
    no_saw = []
    saw_list = user.saw_list
    for i in range(len(edits)):
        if i not in saw_list and edits[i].video is not None:
            no_saw.append(i)
    shuffle(no_saw)
    return no_saw


def show_list_edits(bot, user, call, ind_edits, edits, callback, spec_bat=None):
    num_el = len(ind_edits)
    st = 0
    if call.data[2:6] == 'list':
        st = int(call.data[6:])

    if num_el > 0:
        for i in range(st, min(st + 5, num_el)):
            keyboard = get_keyboard_video(ind_edits[i], 5)
            user.message_del.append(bot.send_video(call.message.chat.id, edits[ind_edits[i]].video,
                                                   reply_markup=keyboard, caption='').message_id)
            time.sleep(0.1)

    back_st = st - 5 if st >= 5 else num_el - num_el % 5 - (5 if num_el % 5 == 0 else 0)
    forw_st = st + 5 if st + 5 < num_el else 0
    spec = [[('⬅ Назад', callback[0] + '_list' + str(back_st)), ('➡ Вперёд', callback[0] + '_list' + str(forw_st))]]
    spec += (spec_bat if spec_bat is not None else [[('🔙 Вернуться', 'menu5')]])

    text = 'Эдиты ' + str(st+1) + '-' + str(min(st + 5, num_el)) + ' из ' + str(num_el) if num_el > 0 else 'Пусто'
    bot.delete_message(call.message.chat.id, call.message.message_id)
    message(bot, call.message.chat.id, text, [], callback + str(st), edit=False, row1=False, spec_bat=spec)


def show_list_names(bot, call, names, text, callback, back, user, finder=True):
    st = 0
    if call.data[2:6] == 'list':
        st = int(call.data[6:])
        user.vars['list'] = st
    elif user.vars.get('list') is not None:
        st = user.vars['list']

    variants = names[st: min(st + 10, len(names))]
    back_st = st - 10 if st >= 10 else len(names) - len(names) % 10 - (10 if len(names) % 10 == 0 else 0)
    forw_st = st + 10 if st + 10 < len(names) else 0
    spec = [[('⬅ Назад', callback[0] + '_list' + str(back_st if back_st >= 0 else 0)),
             ('➡ Вперёд', callback[0] + '_list' + str(forw_st))]]
    spec += [[('🔙 Вернуться', back)]] if not finder else [[('🔎 Найти по названию', 'find'), ('🔙 Вернуться', back)]]

    text = text + '\nНазвания ' + str(st+1) + '-' + str(min(st + 10, len(names))) + ' из ' + str(len(names))
    if len(names) == 0:
        text = 'Пусто'
    message(bot, call, text, variants, callback+str(st//10), row1=False, spec_bat=spec)


def random_edit(bot, call, user, text, edits):
    no_saw_list = get_no_saw_list(user, edits)
    if len(no_saw_list) == 0:
        user.saw_list = []
        no_saw_list = get_no_saw_list(user, edits)
    if len(no_saw_list) == 0:
        bot.answer_callback_query(callback_query_id=call.id, text='Пусто')
        return 0
    while 0 < len(no_saw_list) < 5:
        user.saw_list = []
        no_saw_list += get_no_saw_list(user, edits)

    list_edit = no_saw_list[:5]
    user.saw_list += list_edit

    for ind in list_edit:
        keyboard = get_keyboard_video(ind, 3)
        user.message_del.append(bot.send_video(call.message.chat.id, edits[ind].video,
                                               caption='', reply_markup=keyboard).message_id)
        time.sleep(0.1)

    bot.delete_message(call.message.chat.id, call.message.message_id)
    message(bot, call.message.chat.id, text, ['🎲'], 'r_next', edit=False, back='menu3')


def type_edits(calldata, user, edits, edit_names):
    no_saw_list = get_no_saw_list(user, edits)

    if calldata == 'mood6':
        calldata = 'mood4'
    if calldata == 'mood7':
        calldata = 'mood3'

    need_ind_edits = []
    for i in no_saw_list:
        if calldata[:4] == 'mood' and edits[i].mood == int(calldata[4:]):
            need_ind_edits.append(i)
        if calldata[:6] == 'zodiac' and edits[i].zodiac == int(calldata[6:]):
            need_ind_edits.append(i)
        if calldata[:5] == 'names' and edits[i].name is not None \
                and edits[i].name.lower() == edit_names[int(calldata[5:])].lower():
            need_ind_edits.append(i)

    return need_ind_edits


def find_word(word, array, sinonims):
    word = word.lower().strip()
    res = -1
    num = len(word)
    for i in range(len(array)):
        sins_word = [array[i]]
        if sinonims.get(array[i]) is not None:
            sins_word += sinonims[array[i]]

        for word2 in sins_word:
            word2 = word2.lower().strip()
            num_err = abs(len(word) - len(word2))
            for i1 in range(min(len(word), len(word2))):
                if word[i1] not in word2[max(0, i1-1):i1+2]:
                    num_err += 1
            if num_err < num:
                num = num_err
                res = i

    return res if num < len(word) / 2 else -1
