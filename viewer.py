#!/usr/bin/python3
# -*- coding: utf8 -*-

from PyQt5.QtWidgets import (QMainWindow, QWidget, QScrollArea,
                             QPushButton, QGridLayout, QHBoxLayout,
                             QVBoxLayout, QLCDNumber, QSlider, QLabel, QComboBox)
from PyQt5.QtCore import Qt, pyqtSignal

from re import split

class Viewer(QMainWindow):
    requesting_state_signal = pyqtSignal(bool)
    requesting_interval_signal = pyqtSignal(float)
    posting_state_signal = pyqtSignal(bool)
    posting_interval_signal = pyqtSignal(float)
    change_coef_signal = pyqtSignal(dict)
    def __init__(self, cursor, posting_interval, request_interval, coefs):
        super().__init__()
        self.resize(1366, 768)
        self.posting_state = True
        self.requesting_state = True
        self.set_db_data(cursor)
        self.main_w = Main_widget(coefs)
        self.initUI(60 / posting_interval, 60 / request_interval, coefs)

    def set_db_data(self, cursor):
        self.table_keys = ('quote', 'author', 'source', 'tag')
        self.tables = {'quote':'quotes', 'author':'authors', 'source':'sources', 'tag':'tags'}
        self.lang_ru = {'quote':'Цитата', 'author':'Автор', 'source':'Источник', 'tag':'Тема', 'tags':'Темы'}
        self.data = dict()

        query = 'SELECT id, author_id, source_id, quote FROM {};'.format(self.tables[self.table_keys[0]])
        cursor.execute(query)
        self.data[self.tables[self.table_keys[0]]] = {key: {'author': author_id, 'source': source_id, 'quote': quote, 'tags': []} for key, author_id, source_id, quote in cursor.fetchall()}

        query = 'SELECT quote_id, tag_id FROM {};'.format('quotes_tags')
        cursor.execute(query)

        for quote_id, tag_id in cursor.fetchall():
            self.data[self.tables[self.table_keys[0]]][quote_id]['tags'].append(tag_id)

        for table_key in self.table_keys[1:]:
            query = 'SELECT id, value FROM {};'.format(self.tables[table_key])
            cursor.execute(query)
            self.data[self.tables[table_key]] = {key: value for key, value in cursor.fetchall()}

    def initUI(self, posts_per_minute, requests_per_minute, coefs):
        scrollWidget = QScrollArea()
        self.main_w.buttons['posts'].clicked.connect(self.change_posting_state)
        self.main_w.buttons['requests'].clicked.connect(self.change_requesting_state)

        self.main_w.sliders['posts']['slider'].valueChanged.connect(self.change_posting_interval)
        self.main_w.sliders['posts']['slider'].setValue(posts_per_minute)
        self.main_w.sliders['posts']['number'].display(posts_per_minute)

        self.main_w.sliders['requests']['slider'].valueChanged.connect(self.change_requesting_interval)
        self.main_w.sliders['requests']['slider'].setValue(requests_per_minute)
        self.main_w.sliders['requests']['number'].display(requests_per_minute)

        for option_name in self.main_w.options:
            for label in self.main_w.options[option_name].labels:
                self.main_w.options[option_name].boxes[label].currentIndexChanged.connect(
                        lambda i, label=label, option=option_name: self.change_coef(i+1, label, option=='requests')
                    )

        scrollWidget.setWidget(self.main_w)
        scrollWidget.setWidgetResizable(True)
        self.setCentralWidget(scrollWidget)

        self.setWindowTitle('Программа постов')
        self.show()

    def on_request(self, request):
        data = dict()
        if self.table_keys[0] in request:
            data[self.table_keys[0]] = self.lang_ru[self.table_keys[0]] + ': {} '.format(self.data[self.tables[self.table_keys[0]]][request[self.table_keys[0]]][self.table_keys[0]])
        for key in self.table_keys[1:]:
            if key in request:
                data[key] = self.lang_ru[key] + ': {} '.format(self.data[self.tables[key]][request[key]])

        self.main_w.append_request(data)

    def on_post(self, post):
        data = dict()
        quote = self.data[self.tables[self.table_keys[0]]][post]

        data['quote'] = self.lang_ru['quote'] + ': {} '.format(quote['quote'])

        for key in ('author', 'source'):
            if quote[key] is not None:
                data[key] = self.lang_ru[key] + ': {} '.format(self.data[self.tables[key]][quote[key]])

        if quote['tags'] is not None:
            data['tags_title'] = self.lang_ru['tags']
            data['tags'] = [self.data['tags'][i] for i in quote['tags']]

        self.main_w.append_post(data)

    def change_posting_state(self):
        self.posting_state = not self.posting_state
        self.posting_state_signal.emit(self.posting_state)

    def change_requesting_state(self):
        self.requesting_state = not self.requesting_state
        self.requesting_state_signal.emit(self.requesting_state)

    def change_posting_interval(self, per_minute):
        self.posting_interval_signal.emit(60 / per_minute)

    def change_requesting_interval(self, per_minute):
        self.requesting_interval_signal.emit(60 / per_minute)

    def change_coef(self, value, data_type, inc = True):
        data = {
            'inc' if inc else 'dec': {
                    data_type: float(value)
                }
        }
        self.change_coef_signal.emit(data)

    def keyPressEvent(self, e):
        key = e.key()
        if key == Qt.Key_Escape:
            self.close()
        elif key == Qt.Key_W:
            self.change_posting_state()
        elif key == Qt.Key_E:
            self.change_requesting_state()

class Main_widget(QWidget):
    def __init__(self, coefs):
        super().__init__()
        # self.setStyleSheet('Slider_view::handle:horizontal {width: 100px;}')
        self.titles = {'posts': Title_view('Посты'), 'requests': Title_view('Заявки')}
        self.buttons = {
            'posts': QPushButton('Posting'),
            'requests': QPushButton('Requeststing'),
        }

        self.sliders = {
            'posts': {
                'title': Title_view('Постов в минуту'),
                'number': QLCDNumber(),
                'slider': Slider_view()
            },
            'requests': {
                'title': Title_view('Запросов в минуту'),
                'number': QLCDNumber(),
                'slider': Slider_view()
            }
        }

        for slider in self.sliders:
            self.sliders[slider]['number'].setMaximumHeight(25)
            self.sliders[slider]['number'].setMinimumHeight(25)
            self.sliders[slider]['slider'].valueChanged.connect(self.sliders[slider]['number'].display)

        self.options = {
            'posts': Options_block(coefs['dec']),
            'requests': Options_block(coefs['inc']),
        }

        self.posts = []
        self.requests = []

        self.main_layout = QGridLayout()
        self.setLayout(self.main_layout)

        self.reinitUI()


    def reinitUI(self):
        for i in reversed(range(self.main_layout.count())):
            item = self.main_layout.itemAt(i)
            self.main_layout.removeItem(item)

        self.main_layout.addWidget(self.titles['posts'], 0, 0)
        self.main_layout.addWidget(self.titles['requests'], 0, 1)

        self.main_layout.addWidget(self.buttons['posts'], 1, 0)
        self.main_layout.addWidget(self.buttons['requests'], 1, 1)

        for i, slider in enumerate(('posts', 'requests')):
            for j, key in enumerate(('title', 'number', 'slider'), 2):
                self.main_layout.addWidget(self.sliders[slider][key], j, i)

        self.main_layout.addWidget(self.options['posts'], 5, 0)
        self.main_layout.addWidget(self.options['requests'], 5, 1)

        for i, post in enumerate(self.posts, 6):
            self.main_layout.addWidget(post, i, 0)

        for i, request in enumerate(self.requests, 6):
            self.main_layout.addWidget(request, i, 1)

    def append_post(self, data):
        self.posts.insert(0, Post_view(data))
        for request in self.requests:
            request.test_fullfilled(data)

        self.reinitUI()

    def append_request(self, request):
        self.requests.insert(0, Request_view(request))
        self.reinitUI()

class Panel_view(QLabel):
    def __init__(self, data):
        super().__init__()

        message_list = []
        message_list.append('<div style="width: 300px;">')
        if 'quote' in data:
            message_list.append('<p style="color:#0000FF;">{}</p>'.format(data['quote']))
        if 'author' in data:
            message_list.append('<p style="color:#009b76;">{}</p>'.format(data['author']))
        if 'source' in data:
            message_list.append('<p style="color:#4ed838;">{}</p>'.format(data['source']))
        if 'tag' in data:
            message_list.append('<p style="color:#0b8164;">{}</p>'.format(data['tag']))
        if 'tags' in data:
            message_list.append('<p style="color:#0b8164;">{}: {}</p>'.format(data['tags_title'], ', '.join(data['tags'])))

        message_list.append('</div>')
        message = '\n'.join(message_list)

        self.setText(message)
        self.setAlignment(Qt.AlignLeft)
        self.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.setMargin(10)
        self.setFrameStyle(self.Panel)
        self.setWordWrap(True)

class Request_view(Panel_view):
    def __init__(self, data):
        super().__init__(data)
        self.request_data = data
        self.setStyleSheet('color:#FF0000;')

    def test_fullfilled(self, post_data):
        fullfilled = True
        for key in self.request_data:
            if key == 'tag':
                if 'tags' not in post_data or split(': ', self.request_data['tag'], 1)[1][:-1] not in post_data['tags']:
                    fullfilled = False
            elif key not in post_data or self.request_data[key] != post_data[key]:
                fullfilled = False
        if fullfilled:
            self.setStyleSheet('color:#00FF00;')

class Post_view(Panel_view):
    def __init__(self, data):
        super().__init__(data)


class Title_view(QLabel):
    def __init__(self, txt):
        super().__init__()
        self.setText(txt)
        self.setAlignment(Qt.AlignCenter)
        self.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.setMaximumHeight(30)
        self.setMinimumHeight(30)

class Slider_view(QSlider):
    def __init__(self):
        super().__init__(Qt.Horizontal)
        self.setMinimum(1)
        self.setMaximum(120)

class Options_block(QWidget):
    def __init__(self, coefs):
        super().__init__()

        self.initUI(coefs)

    def initUI(self, coefs):
        self.labels = ('quote', 'author', 'source', 'tag')
        self.boxes = {label: QComboBox() for label in self.labels}

        vbox = QVBoxLayout()
        vbox.addStretch(1)

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        title = Title_view('Изменение коэффициента: Цитата, Автор, Источник, Тема')
        hbox.addWidget(title)
        vbox.addLayout(hbox)

        hbox = QHBoxLayout()
        hbox.addStretch(1)

        for label in self.labels:
            self.boxes[label].addItems([str(x) for x in range(1, 7)])
            self.boxes[label].setCurrentIndex(int(coefs[label] - 1))
            hbox.addWidget(self.boxes[label])

        vbox.addLayout(hbox)
        self.setLayout(vbox)

        self.setMaximumHeight(80)
        self.setMinimumHeight(80)

    def index_changed(self, value, label):
        import sys
        print(label, file=sys.stderr)
