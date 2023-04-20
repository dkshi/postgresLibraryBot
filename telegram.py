import telebot
from datetime import datetime
from database import db_connector


API_TOKEN = "TOKEN"
bot = telebot.TeleBot(API_TOKEN)

# start
@bot.message_handler(commands=['start'])  
def handle_start(message):
    bot.reply_to(message, "Приветствую путник! Добро пожаловать в чат-бот библиотеку.")

# add
@bot.message_handler(commands=['add'])
def add_title(message):
    bot.send_message(message.chat.id, 'Введите название книги:')
    bot.register_next_step_handler(message, add_author)

def add_author(message):
    title = message.text
    bot.send_message(message.chat.id, 'Введите автора:')
    bot.register_next_step_handler(message, lambda message: add_published(message, title))

def add_published(message, title):
    author = message.text
    bot.send_message(message.chat.id, 'Введите год издания:')
    bot.register_next_step_handler(message, lambda message: save_book(message, title, author))

# отправляет книгу в бд
def save_book(message, title, author, date_deleted=None):
    published = message.text
    response = db_connector.add(title=title, author=author, published=published, date_added=datetime.now().date(), date_deleted=date_deleted)
    if response:
        bot.send_message(message.chat.id, f'Книга добавлена ({response})')
    else:
        bot.send_message(message.chat.id, 'Ошибка при добавлении книги')

#delete
@bot.message_handler(commands=['delete'])
def delete_title(message):
    bot.send_message(message.chat.id, 'Введите название книги:')
    bot.register_next_step_handler(message, delete_author)

def delete_author(message):
    title = message.text
    bot.send_message(message.chat.id, 'Введите автора:')
    bot.register_next_step_handler(message, lambda message: delete_published(message, title))

def delete_published(message, title):
    author = message.text
    bot.send_message(message.chat.id, 'Введите год издания:')
    bot.register_next_step_handler(message, lambda message: delete_book(message, title, author))

def delete_book(message, title, author):
    published = message.text
    book_id = db_connector.get_book(title, author, published)
    if book_id is not None:
        bot.send_message(message.chat.id, f'Найдена книга: {title} {author} {published}. Удаляем?  Да / Нет')
        bot.register_next_step_handler(message, lambda message: delete_book_final(message, book_id))
    else:
        bot.send_message(message.chat.id, 'Подобных книг не найдено!')

def delete_book_final(message, response):
    answer = message.text
    if answer.lower() == 'да':
        db_connector.delete(response)
        bot.send_message(message.chat.id, f'Книга удалена')
    elif answer.lower() == 'нет':
        bot.send_message(message.chat.id, f'Книга не была удалена')
    else:
        bot.send_message(message.chat.id, 'Непонятный запрос!')
    

#list
@bot.message_handler(commands=['list'])
def list_of_books(message):
    books = db_connector.list_books()
    book_list = ""
    for book in books:
        book_str = f'{book["title"]}, {book["author"]}, {book["published"]}'
        if book["date_deleted"] is not None:
            book_str += ' (удалена)'
        book_str += ";\n"
        book_list += book_str
    bot.send_message(message.chat.id, book_list)


#find
@bot.message_handler(commands=['find'])
def find_title(message):
    bot.send_message(message.chat.id, 'Введите название книги:')
    bot.register_next_step_handler(message, find_author)

def find_author(message):
    title = message.text
    bot.send_message(message.chat.id, 'Введите автора:')
    bot.register_next_step_handler(message, lambda message: find_published(message, title))

def find_published(message, title):
    author = message.text
    bot.send_message(message.chat.id, 'Введите год издания:')
    bot.register_next_step_handler(message, lambda message: find_book(message, title, author))

def find_book(message, title, author):
    published = message.text
    response = db_connector.get_book(title, author, published)
    if response:
        bot.send_message(message.chat.id, f'Найдена книга: {title} {author} {published}')
    else:
        bot.send_message(message.chat.id, 'Такой книги у нас нет')


# borrow
@bot.message_handler(commands=['borrow'])
def borrow_title(message):
    bot.send_message(message.chat.id, 'Введите название книги:')
    bot.register_next_step_handler(message, borrow_author)

def borrow_author(message):
    title = message.text
    bot.send_message(message.chat.id, 'Введите автора:')
    bot.register_next_step_handler(message, lambda message: borrow_published(message, title))

def borrow_published(message, title):
    author = message.text
    bot.send_message(message.chat.id, 'Введите год издания:')
    bot.register_next_step_handler(message, lambda message: borrow_book(message, title, author))


def borrow_book(message, title, author):
    published = message.text
    book_id = db_connector.get_book(title, author, published)
    if book_id:
        bot.send_message(message.chat.id, f'Найдена книга: {title} {author} {published}. Берем?')
        bot.register_next_step_handler(message, lambda message: borrow_book_final(message, book_id))
    else:
        bot.send_message(message.chat.id, 'Книга не найдена')

def borrow_book_final(message, book_id):
    answer = message.text
    response = db_connector.borrow(book_id, message.from_user.id)
    if answer.lower() == 'да' and response:
        bot.send_message(message.chat.id, f'Вы взяли книгу ({book_id})')
    elif answer.lower() == 'нет' and response:
        bot.send_message(message.chat.id, f'Вы отказались брать книгу ({book_id})')
    else:
        bot.send_message(message.chat.id, 'Книгу сейчас невозможно взять')


# retrieve
@bot.message_handler(commands=['retrieve'])
def retrieve_book(message):
    borrow_id = db_connector.get_borrow(message.from_user.id)
    book_str = db_connector.retrieve(borrow_id)
    if book_str is not None:
        bot.send_message(message.chat.id, f'Вы вернули книгу {book_str}')
    else:
        bot.send_message(message.chat.id, 'Вы не еще не брали книг!')


@bot.message_handler(commands=['stats'])
def stats_title(message):
    bot.send_message(message.chat.id, 'Введите название книги:')
    bot.register_next_step_handler(message, stats_author)

def stats_author(message):
    title = message.text
    bot.send_message(message.chat.id, 'Введите автора:')
    bot.register_next_step_handler(message, lambda message: stats_published(message, title))

def stats_published(message, title):
    author = message.text
    bot.send_message(message.chat.id, 'Введите год издания:')
    bot.register_next_step_handler(message, lambda message: stats(message, title, author))

def stats(message, title, author):
    published = message.text
    book_id = db_connector.get_book(title, author, published)
    if book_id:
        bot.send_message(message.chat.id, f'Статистика доступна по адресу <a href = "http://127.0.0.1:8080/download/{book_id}">здесь</a>', parse_mode='html')
    else:
        bot.send_message(message.chat.id, 'Нет такой книги')
