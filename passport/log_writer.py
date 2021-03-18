import datetime
import os


def log_writer(log_msg):
    """
    Синтаксис:
    ----------
    log_writer(log_msg)

    Описание:
    ---------
    Функция отвечает за запись логов в лог-файлы. Выполняет проверку наличия директории для сохранения файлов.
    В случае ее отсутствия создает директорию.

    Параметры:
    ----------
        **log_msg**: string, строка для записи в лог-файл.

    Returns:
    ----------
        None
    """
    current_date = datetime.datetime.now()
    write_date = current_date.strftime('%d-%m-%Y %H:%M:%S')

    filename_date = current_date.strftime('%d-%m-%Y')
    filepath = 'logs/'

    if os.path.exists(filepath):
        f = open(f'{filepath + filename_date}.log', 'a')
        f.write(''.join([write_date, ': ', log_msg, '\n']))
        f.close()
    else:
        os.mkdir(filepath)
        f = open(f'{filepath + filename_date}.log', 'a')
        f.write(''.join([write_date, ': ', log_msg, '\n']))
        f.close()
