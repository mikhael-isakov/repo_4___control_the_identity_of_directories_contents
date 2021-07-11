import sys
import os 
from PyQt5.QtCore import QRect, Qt 
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QFileDialog, QLabel, QPushButton 
from PyQt5.QtGui import QIcon, QFont
from designUi import Ui_MainWindow 
from hashlib import md5
from threading import Thread


scanning = False 
synchr_err = 0
file_number = 0
size_total = 0 
f = open(os.path.join(os.getcwd(), 'log.txt'), 'w') 


def get_md5sum(filename):
    with open(filename, 'rb') as file: 
        return md5(file.read()).hexdigest()


def resource_path(relative_path):
    '''
    Функция возвращает правильный адрес иконок как при разработке, 
    так и при доставании их из ресурсов исполняемого файла 
    '''
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.path.join(os.getcwd(), 'icons'))
    return os.path.join(base_path, relative_path)


class MainWindow(QMainWindow):
    def __init__(self): 
        QWidget.__init__(self) 
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self) 
        
        # пусть кнопка "остановить проверку" вначале неактивна 
        self.ui.pushButton_4.setEnabled(False)
        
        # объявление некоторых переменных 
        self.source_directory = ''
        self.synchr_directory = ''

        # фиксация размера, установка иконки и заголовка окна 
        self.setFixedSize(800, 250)
        self.move(400, 300)
        self.setWindowIcon(QIcon(resource_path('main_icon.ico')))
        self.setWindowTitle('Программа для контроля результатов работы программ, '+
                            'осуществляющих бэкап методом синхронизации')
        
        # установка иконок пунктов меню 
        self.ui.action.setIcon(QIcon(resource_path('catalog_icon.png')))
        self.ui.action.setShortcut('Ctrl+O')
        self.ui.action_2.setIcon(QIcon(resource_path('catalog_icon.png')))
        self.ui.action_2.setShortcut('Ctrl+S')
        self.ui.action_3.setIcon(QIcon(resource_path('check_icon.png')))
        self.ui.action_3.setShortcut('Ctrl+C')
        self.ui.action_5.setIcon(QIcon(resource_path('quit_icon.png')))
        self.ui.action_5.setShortcut('Ctrl+Q')
        self.ui.action_6.setIcon(QIcon(resource_path('info_icon.png')))
        self.ui.action_4.setIcon(QIcon(resource_path('info_icon.png')))
        self.ui.action_7.setIcon(QIcon(resource_path('info_icon.png')))

        # установка функциональности пунктов меню 
        self.ui.action.triggered.connect(self.select_source_directory)
        self.ui.action_2.triggered.connect(self.select_synchr_directory)
        self.ui.action_3.triggered.connect(self.compare_directories)
        self.ui.action_5.triggered.connect(lambda: os._exit(0))
        self.text_1 = 'Программа совершает рекурсивный обход\nуказанных каталогов, и сравнивает хеши MD5 файлов.\n\n'
        self.text_2 = 'По всем вопросам,\nсвязанным с использованием программы,\nобращаться via e-mail: mikhael.isakov@gmail.com'
        self.ui.action_6.triggered.connect(lambda: self.show_ok_popup_window(title='О программе', 
                                                                             text=self.text_1+self.text_2))
        self.text_3 = 'При бэкапе методом синхронизации\nпри добавлении, изменении, или удалении\n'
        self.text_4 = 'файлов в исходном каталоге\nточно такие же изменения\nпроисходят и в конечном\n(синхронизированном) каталоге'        
        self.ui.action_4.triggered.connect(lambda: self.show_ok_popup_window(title='О бэкапе методом синхронизации', 
                                                                          text=self.text_3+self.text_4)) 
        self.text_5 = 'Программа рекурсивно пробегает по исходному каталогу\n'
        self.text_6 = 'и подкаталогам, ищет соответствия в конечном каталоге.\n'
        self.text_7 = 'Таким образом, гарантируется, что в конечном каталоге\nимеются те же файлы с теми же хешами.\n'
        self.text_8 = 'Это не означает, что конечный каталог не содержит\nдругих файлов (но можно запустить проверку наоборот)'
        self.ui.action_7.triggered.connect(lambda: self.show_ok_popup_window(title='Об односторонней идентичности каталогов', 
                                                                          text=self.text_5+self.text_6+self.text_7+self.text_8)) 
        
        # установка функциональности кнопок 
        self.ui.pushButton.clicked.connect(self.select_source_directory)
        self.ui.pushButton_2.clicked.connect(self.select_synchr_directory)
        self.ui.pushButton_3.clicked.connect(self.compare_directories)
        self.ui.pushButton_4.clicked.connect(self.stop_scanning)

    def show_ok_popup_window(self, title, text):
        self.ok_popup_window = QWidget() 
        self.ok_popup_window.move(500, 300)
        self.ok_popup_window.setFixedSize(400, 160)
        self.ok_popup_window.setWindowIcon(QIcon(resource_path('main_icon.ico')))
        self.ok_popup_window.setWindowTitle(title)
        font = QFont()
        font.setFamily(u"Arial"); font.setPointSize(10)
        self.ok_popup_window.label = QLabel(self.ok_popup_window)
        self.ok_popup_window.label.setGeometry(QRect(20, 10, 360, 100))
        self.ok_popup_window.label.setFont(font)
        self.ok_popup_window.label.setText(text)
        self.ok_popup_window.label.setAlignment(Qt.AlignCenter)
        self.ok_popup_window.pushButton = QPushButton(self.ok_popup_window)
        self.ok_popup_window.pushButton.setGeometry(QRect(100, 120, 200, 25))
        self.ok_popup_window.pushButton.setText('OK')
        self.ok_popup_window.pushButton.clicked.connect(self.ok_popup_window.close)
        self.ok_popup_window.show()

    def path_shortener(self, path, max_length=70): 
        if len(path) <= max_length: 
            return path 
        else: 
            a = max_length // 2 
            return path[0:a] + ' ... ' + path[-1-a:]

    def select_source_directory(self):
        global scanning 
        if not scanning:  
            self.source_directory = QFileDialog.getExistingDirectory(self, 'Выберите исходный каталог')
            if self.source_directory == '': 
                self.ui.pushButton.setText('исходный каталог: не выбран')
            else: 
                self.ui.pushButton.setText('исходный каталог: ' + self.path_shortener(self.source_directory))
            self.ui.pushButton_3.setText('Проверить идентичность содержимого каталогов\nи записать результат в log.txt')


    def select_synchr_directory(self):
        global scanning 
        if not scanning:  
            self.synchr_directory = QFileDialog.getExistingDirectory(self, 'Выберите синхронизированный каталог')
            if self.synchr_directory == '': 
                self.ui.pushButton_2.setText('синхронизированный каталог: не выбран') 
            else: 
                self.ui.pushButton_2.setText('синхронизированный каталог: ' + self.path_shortener(self.synchr_directory))
            self.ui.pushButton_3.setText('Проверить идентичность содержимого каталогов\nи записать результат в log.txt') 


    def compare_directories(self): 
        '''Метод производит проверку корректности данных, и запускает 
           сравнение содержимого каталогов self.source_directory и self.synchr_directory'''
        global scanning 
        if not scanning: 
            if self.source_directory == '' or self.synchr_directory == '': 
                self.show_ok_popup_window('Ошибка: не выбран каталог', 
                                          'Пожалуйста,\nвыберите\nисходный\nи синхронизированный\nкаталоги')
            elif self.synchr_directory == self.source_directory: 
                self.show_ok_popup_window('Ошибка: выбран один и тот же каталог', 
                                          'Пожалуйста,\nвыберите различающиеся\nисходный\nи синхронизированный\nкаталоги')
            else: 
                # старт проверки идентичности содержимого каталогов (в отдельном потоке)                                              
                scanning = True 
                self.ui.pushButton.setEnabled(False)
                self.ui.pushButton_2.setEnabled(False)
                self.ui.pushButton_4.setEnabled(True)
                self.obhod_in_new_thread()


    def obhod_in_new_thread(self):
        global f
        self.obhod_in_new_thread_ = Thread(target=obhod, args=(self, self.source_directory, self.synchr_directory), daemon=True)
        self.obhod_in_new_thread_.start()


    def stop_scanning(self): 
        global scanning 
        if scanning: 
            scanning = False 
            self.ui.pushButton.setEnabled(True)
            self.ui.pushButton_2.setEnabled(True)
            self.ui.pushButton_4.setEnabled(False)


def size_transform(size):
    if size > 1073741824: 
        return (round(size/1073741824, 2), 'ГБ') 
    elif size > 1048576: 
        return (round(size/1048576, 2), 'МБ')
    elif size > 1024: 
        return (round(size/1024, 2), 'кБ') 
    else: 
        return (size, 'Б')


def obhod(window, source_dir, synchr_dir, level=1):
    '''
    Функция реализует рекурсивный обход файлов 
    в каталоге window.source_directory и его подкаталогах,  
    ищет такие же файлы в каталоге window.synchr_directory и его подкаталогах, 
    одновременно с обходами производя для всех файлов вычисления md5sum, 
    попарное сравнение вычисленных md5sum, и запись информации в log.txt  
    '''

    global scanning, synchr_err, file_number, size_total, f 

    if level == 1 and scanning: 
        synchr_err = 0; file_number= 0 
        if len(os.listdir(synchr_dir)) != len(os.listdir(source_dir)): 
            a = 'Нет необходимости проводить проверку.\n'
            b = 'Содержимое каталогов неидентично (разное количество файлов)'
            window.ui.pushButton_3.setText(a+b)
            window.ui.pushButton.setEnabled(True)
            window.ui.pushButton_2.setEnabled(True)
            window.ui.pushButton_4.setEnabled(False)
            scanning = False 
            return None 

    for item in os.listdir(source_dir): 
        if scanning: 
            obj = os.path.join(source_dir, item)
            size = os.path.getsize(obj) 
            size_ = size_transform(size)
            size_total_ = size_transform(size_total)

            if os.path.isfile(obj):
                file_number += 1 
                a = 'Проверяется {}-й файл размером {} {},\nвсего проверено {} {}'.format(file_number, size_[0], size_[1], 
                                                                                             size_total_[0], size_total_[1])
                window.ui.pushButton_3.setText(a)
                filehash_source = get_md5sum(obj) 
                filehash_synchr = '0' 
                try: 
                    filehash_synchr = get_md5sum(os.path.join(synchr_dir, item))
                except FileNotFoundError:  
                    f.write('Файл не имеет соответствия (синхрофайла) в конечном каталоге, адрес:\n{}\n\n'.format(obj))
                    synchr_err += 1 
                
                size_total += size                
                
                if filehash_synchr != filehash_source and filehash_synchr != '0': 
                    f.write('Хеш файла {} не совпадает с хешем синхрофайла {},\nадрес: {}\n\n'.format(filehash_source, 
                                                                                                      filehash_synchr, obj))
                    synchr_err += 1 
            elif os.path.isdir(obj): 
                obhod(window, os.path.join(source_dir, item), os.path.join(synchr_dir, item), level+1)
        else: 
            window.ui.pushButton_3.setText('Проверка была остановлена.\nНажмите, чтобы начать проверку заново')
            scanning = False; synchr_err = 0; file_number = 0; size_total = 0 
            f.close()
            return None 
                
    if level == 1 and scanning:
        scanning = False 
        window.ui.pushButton.setEnabled(True)
        window.ui.pushButton_2.setEnabled(True)
        window.ui.pushButton_4.setEnabled(False)
        b = '\nЗапустить проверку снова'
        if not synchr_err: 
            f.write('\nПроверка завершена. Содержимое каталогов (как минимум односторонне) идентично.')
            window.ui.pushButton_3.setText('Содержимое каталогов (как минимум односторонне) идентично'+b)
        else: 
            f.write('\nПроверка завершена. Содержимое каталогов неидентично.')
            window.ui.pushButton_3.setText('Проверка завершена. Содержимое каталогов неидентично (см. log.txt).'+b)
        f.close()


def main(): 
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
