token = '1481065029:AAHHoMu5CyMQSMfjF8zS6izL943OMGTin38'
import telebot
from telebot import types

bot = telebot.TeleBot(token)
user_dict = {}

import pandas as pd
import numpy as np
import time

class LIST:
    def __init__(self, msg):
        self.msg = msg
        self.del_pr = None
        
df = pd.read_csv('hangman.csv', index_col=0)
df_words = pd.read_csv('words.csv', index_col=0)
words_records = pd.read_csv('words_records.csv', index_col=0)
short_words = pd.read_csv('short_words.csv', header=None)
medium_words = pd.read_csv('mid_words.csv', header=None)
long_words = pd.read_csv('long_words.csv', header=None)
nouns = pd.read_csv('nouns.csv', header=None)
cities = pd.read_csv('cities.csv', delimiter=';')
df_cities = pd.read_csv('cities_info.csv', index_col=0)

@bot.message_handler(commands=['start'])

def greetings(message):
    username = message.from_user.first_name + '!'
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    bt1 = types.KeyboardButton('Hi, Artёm!')
    markup.add(bt1)
    msg = bot.send_message(message.chat.id, 'Hi, ' + username,
                          reply_markup=markup)
    bot.register_next_step_handler(msg, rules)
    
def rules(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    bt1 = types.KeyboardButton('Yes, please')
    bt2 = types.KeyboardButton('No, thank you')
    markup.add(bt1, bt2)
    msg = bot.send_message(message.chat.id, 'Do you want to know the rules?',
                          reply_markup=markup)
    bot.register_next_step_handler(msg, choose_game)
    
def choose_game(message):
    if message.text == 'Yes, please':
        bot.send_message(message.chat.id, 'We can play three different games: hangerman, cities and scrabble.')
        bot.send_message(message.chat.id, 'Hangerman: I choose random english noun, and you need to guess it by one letter at a time. Be careful, you can make only 6 mistakes!')
        bot.send_message(message.chat.id, 'Cities: I name random city and you need to name a city, starting with the last letter of mine')
        bot.send_message(message.chat.id, 'Scrabble: I give you a random word. You need to compose as much nouns as possible, using only the letters of my word.')
        
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=False, resize_keyboard=True)
    bt1 = types.KeyboardButton('Hangerman')
    bt2 = types.KeyboardButton('Cities')
    bt3 = types.KeyboardButton('Scrabble')
    markup.add(bt1, bt2, bt3)
    msg = bot.send_message(message.chat.id, 'What do you want to play?',
                           reply_markup=markup)
    bot.register_next_step_handler(msg, switch_to_game)
    
def switch_to_game(message):
    try:
        chat_id = message.chat.id
        user_dict[chat_id] = LIST(message.text)
        if message.text == 'Hangerman':
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            bt1 = types.KeyboardButton('Short')
            bt2 = types.KeyboardButton('Medium')
            bt3 = types.KeyboardButton('Long')
            bt4 = types.KeyboardButton('Cancel')
            markup.add(bt1, bt2, bt3, bt4)
            msg = bot.send_message(chat_id, f'Choose word length.', reply_markup=markup)
            bot.register_next_step_handler(msg, hangman_give_word)
        elif message.text == 'Scrabble':
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            bt1 = types.KeyboardButton("Yes!")
            markup.add(bt1)
            msg = bot.send_message(chat_id, "Let's play scrabble!", reply_markup=markup)
            bot.register_next_step_handler(msg, words_give_word)
        elif message.text == 'Cities':
            bot.send_message(chat_id, 'Great! If you want to finish the game, just write "Stop".')
            n = np.random.choice(cities.index)
            city, country, pop = cities.city[n], cities.country[n], cities.population[n]
            df_cities.loc[chat_id] = [city[-1], [city], 0]
            msg = bot.send_message(chat_id, 'My city is ' + city + '\nCountry: ' + country + '\nPopulation: ' + str(int(pop)))
            bot.register_next_step_handler(msg, cities_game)
        else:
            bot.send_message(chat_id, "I don't get it...", reply_markup=markup)
            bot.register_next_step_handler(msg, switch_to_game)
            
    except Exception as e:
        print(str(e))
        
def hangman_give_word(message):
    try:
        chat_id = message.chat.id
        user_dict[chat_id] = LIST(message.text)  
        
        if message.text == 'Short':
            word = np.random.choice(short_words[0])
        elif message.text == 'Medium':
            word = np.random.choice(medium_words[0])
        elif message.text == 'Long':
            word = np.random.choice(long_words[0])
        elif message.text == 'Cancel':
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=False, resize_keyboard=True)
            bt1 = types.KeyboardButton('Yes!')
            markup.add(bt1)
            msg = bot.send_message(chat_id, "Let's choose another game!", reply_markup=markup)
            bot.register_next_step_handler(msg, choose_game)
            
        lifes = 6
        rec_let = list()
        
        df.loc[chat_id] = [word, lifes, rec_let, 0]
        
        bot.send_message(chat_id, 'Great! Try to guess a letter.')
        bot.send_message(chat_id, 'To end the game, write "stop".')
        bot.send_message(chat_id, 'Lifes: 6')
        msg = bot.send_message(chat_id, '_ ' * len(word))
        bot.register_next_step_handler(msg, hangman_game)
        
    except Exception as e:
        print(str(e))
            
def hangman_game(message):
    try:
        chat_id = message.chat.id
        user_dict[chat_id] = LIST(message.text)
        
        user_input = message.text.lower()
        word = df['word'][chat_id]
        
        if user_input == 'stop':
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            bt1 = types.KeyboardButton('Yes!')
            markup.add(bt1)
            bot.send_message(chat_id, 'It was "' + word + '"!')
            msg = bot.send_message(chat_id, 'Try again?', reply_markup=markup)
            bot.register_next_step_handler(msg, choose_game)
        
        else:
            letters_recognized = df['nrec_let'][chat_id]
            check_repeat = 1
            for i in range(len(word)):
                if word[i] == user_input:
                    if i not in df['rec_let'][chat_id]:
                        df['rec_let'][chat_id].append(i)
                    else:
                        check_repeat = 0

            if len(df['rec_let'][chat_id]) == letters_recognized:
                if check_repeat == 1:
                    df['lifes'][chat_id] = df['lifes'][chat_id] - 1
                    lifes = df['lifes'][chat_id]
                    if lifes > 0:
                        bot.send_message(chat_id, 'Wrong! ' + str(lifes) + ' lifes left.')
                        output = ''
                        for i in range(len(word)):
                            if i in df['rec_let'][chat_id]:
                                output += word[i] + ' '
                            else:
                                output += '_ ' 
                        msg = bot.send_message(chat_id, output)
                        bot.register_next_step_handler(msg, hangman_game)
                    else:
                        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
                        bt1 = types.KeyboardButton('Yes!')
                        markup.add(bt1)
                        bot.send_message(chat_id, 'You lost! :(\nIt was "' + word + '"')
                        msg = bot.send_message(chat_id, 'Try again?', reply_markup=markup)
                        bot.register_next_step_handler(msg, choose_game)
                        
                else:
                    msg = bot.send_message(chat_id, 'This letter is already opened! Try another one.')
                    bot.register_next_step_handler(msg, hangman_game)

            else:
                if len(df['rec_let'][chat_id]) == len(word):
                    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
                    bt1 = types.KeyboardButton('Yes!')
                    markup.add(bt1)
                    bot.send_message(chat_id, 'You won!\nIt was "' + word + '".')
                    msg = bot.send_message(chat_id, 'Try again?', reply_markup=markup)
                    bot.register_next_step_handler(msg, choose_game)
                else:
                    lifes = df['lifes'][chat_id]
                    df['nrec_let'][chat_id] = len(df['rec_let'][chat_id])
                    bot.send_message(chat_id, 'Great! ' + str(lifes) + ' lifes left.')
                    output = ''
                    for i in range(len(word)):
                        if i in df['rec_let'][chat_id]:
                            output += word[i] + ' '
                        else:
                            output += '_ ' 
                    msg = bot.send_message(chat_id, output)
                    bot.register_next_step_handler(msg, hangman_game)         

            df.to_csv('hangman.csv')
        
    except Exception as e:
        print(str(e))
    
def words_give_word(message):
    try:
        chat_id = message.chat.id
        user_dict[chat_id] = LIST(message.text) 
        
        word = np.random.choice(long_words[0])
        points = 0
        time_user = time.time()
        words = list()
        
        df_words.loc[chat_id] = [word, points, time_user, words]
        df_words.to_csv('words.csv')
        
        bot.send_message(chat_id, 'You got the word "' + word + '".')
        msg = bot.send_message(chat_id, 'Try to score maximum points in 1.5 minutes!')
        bot.register_next_step_handler(msg, words_game)
    except Exception as e:
        print(str(e))
        
def words_game(message):
    try:
        chat_id = message.chat.id
        user_dict[chat_id] = LIST(message.text)
        
        user_word = message.text.lower()
        word = df_words['word'][chat_id]
        user_time = df_words['time'][chat_id]
        stop = 0
        
        if time.time() - user_time <= 90:
            if user_word == word:
                msg = bot.send_message(chat_id, "Hey, it's cheating!")
                stop = 1
                bot.register_next_step_handler(msg, words_game)
            elif user_word in df_words['words'][chat_id]:
                msg = bot.send_message(chat_id, 'You have already named it!')
                stop = 1
                bot.register_next_step_handler(msg, words_game)
            else:
                for i in user_word:
                    if i not in list(word):
                        msg = bot.send_message(chat_id, 'There is no letter "' + i + '" in the word "' + word + '"!')
                        bot.register_next_step_handler(msg, words_game)
                        stop = 1
                        break
                    elif user_word.count(i) > word.count(i):
                        msg = bot.send_message(chat_id, 'There is not enough "' + i + '" in the word "' + word + '"!')
                        bot.register_next_step_handler(msg, words_game)
                        stop = 1
                        break
        else:
            bot.send_message(chat_id, "Time's up!\nYou scored " + str(df_words['points'][chat_id]) + ' points!')
            stop = 1
            name = message.from_user.first_name
            lastname = message.from_user.last_name
            points = df_words['points'][chat_id]
            
            try:
                words_records.loc[chat_id]
            except KeyError:
                words_records.loc[chat_id] = [name, lastname, 0, points]
                
            words_records['last_points'][chat_id] = points
            if words_records['last_points'][chat_id] > words_records['max_points'][chat_id]:
                words_records['max_points'][chat_id] = points
                bot.send_message(chat_id, 'New record!')
            words_records.to_csv('words_records.csv')
            
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            bt1 = types.KeyboardButton('Yes!')
            bt2 = types.KeyboardButton('No...')
            markup.add(bt1, bt2)
            msg = bot.send_message(chat_id, 'Do you want to see records?', reply_markup=markup)
            bot.register_next_step_handler(msg, records_words)
        
        if stop == 0:
            if nouns[nouns[0] == user_word].empty:
                msg = bot.send_message(chat_id, 'This word does not fit!')
                stop = 1
                bot.register_next_step_handler(msg, words_game)
        
        if stop == 0:
            df_words['points'][chat_id] += len(user_word)
            df_words['words'][chat_id].append(user_word)
            df_words.to_csv('words.csv')
            bot.send_message(chat_id, 'Great! You have ' + str(df_words['points'][chat_id]) + ' points!')
            msg = bot.send_message(chat_id, 'Your word: ' + word)
            bot.register_next_step_handler(msg, words_game)
                
    except Exception as e:
        print(str(e))
        
def records_words(message):
    try:
        chat_id = message.chat.id
        user_dict[chat_id] = LIST(message.text)
        
        if message.text == 'Yes!':
            table = words_records.sort_values(by='max_points', ascending=False).head(5)
            output = ''
            for i in table.index:
                row = table.loc[i]
                output += (row.first_name + ': ' + str(row.max_points) + '\n')
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            bt1 = types.KeyboardButton('Next')
            markup.add(bt1)
            msg = bot.send_message(chat_id, output, reply_markup=markup)
            bot.register_next_step_handler(msg, choose_game)
        else:
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            bt1 = types.KeyboardButton('Yes!')
            markup.add(bt1)
            msg = bot.send_message(chat_id, 'Try again?', reply_markup=markup)
            bot.register_next_step_handler(msg, choose_game)
            
    except Exception as e:
        print(str(e))

def cities_game(message):
    try:
        chat_id = message.chat.id
        user_dict[chat_id] = LIST(message.text)
        
        user_input = message.text.title()
        
        if user_input == 'Stop':
            bot.send_message(chat_id, 'Good game! You got ' + str(df_cities.n_cities[chat_id]) + ' points!')
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            bt1 = types.KeyboardButton('Yes!')
            markup.add(bt1)
            msg = bot.send_message(chat_id, 'Wanna play again?', reply_markup=markup)
            bot.register_next_step_handler(msg, choose_game)
        else:
            if user_input[0].lower() != df_cities.last_letter[chat_id]:
                msg = bot.send_message(chat_id, 'Name of the city must start with "' + df_cities.last_letter[chat_id] + '"!')
                bot.register_next_step_handler(msg, cities_game) 

            elif user_input in df_cities.cities_named[chat_id]:
                msg = bot.send_message(chat_id, 'This city has been already named!')
                bot.register_next_step_handler(msg, cities_game)

            elif cities[cities.city == user_input].empty:
                msg = bot.send_message(chat_id, 'Sorry, I do not know this city...')
                bot.register_next_step_handler(msg, cities_game)

            else:
                df_cities.n_cities[chat_id] += 1
                df_cities.cities_named[chat_id].append(user_input)
                df_cities.to_csv('cities_info.csv')

                last_letter = user_input[-1]
                info = cities[cities.city == user_input].iloc[0]
                city, country, pop = info.city, info.country, info.population
                bot.send_message(chat_id, 'Your city: ' + city + '\nCountry: ' + country + '\nPopulation: ' + str(int(pop)))

                temp = cities[cities.first_letter == last_letter]
                for i in df_cities.cities_named[chat_id]:
                    temp = temp[temp.city != i]
                if temp.empty:
                    bot.send_message(chat_id, 'Wow... I do not know any other cities, starting with "' +
                                           last_letter + '"!')
                    bot.send_message(chat_id, 'Good game! You got ' + df_cities.n_cities[chat_id] + ' points!')
                    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
                    bt1 = types.KeyboardButton('Yes!')
                    markup.add(bt1)
                    msg = bot.send_message(chat_id, 'You won! Wanna play again?', reply_markup=markup)
                    bot.register_next_step_handler(msg, choose_game)
                else:
                    n = np.random.choice(temp[temp.first_letter == last_letter].index)
                    city, country, pop = temp.city[n], temp.country[n], temp.population[n]
                    df_cities.cities_named[chat_id].append(city)
                    df_cities.last_letter[chat_id] = city[-1]
                    msg = bot.send_message(chat_id, 'Great! My city is ' + city + '\nCountry: ' + country + '\nPopulation: ' + str(int(pop)))
                    bot.register_next_step_handler(msg, cities_game)

            df_cities.to_csv('cities_info.csv')
        
    except Exception as e:
        print(str(e))    
            
bot.polling(none_stop=True)