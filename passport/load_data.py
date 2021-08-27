import calendar
import datetime as dt
import smtplib
from datetime import date, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from platform import python_version

import pandas as pd
from returns.result import safe
from sqlalchemy import create_engine

import passport.load_cfg as lc
import passport.log_writer as lw

engine = create_engine(f'{lc.db_dialect}://{lc.db_username}:{lc.db_password}@{lc.db_host}:{lc.db_port}/{lc.db_name}')

current_month = date.today().month
current_day = date.today().day
current_year = date.today().year
current_week = date.today().isocalendar()[1]

end_day = (date.today() - timedelta(days=7)).day
end_month = (date.today() - timedelta(days=7)).month
end_year = (date.today() - timedelta(days=7)).year


def load_etsp_data():
    """
    Синтаксис:
    ----------

    **load_etsp_data** ()

    Описание:
    ---------
    Функция загружает из базы данных информацию об обращениях по техподдержке ЕЦП

    Returns:
    -------
        **DataFrame**
    """
    df = pd.read_sql("""
            SELECT num, user, reg_date, solved_date, descr, unit, start_date, finish_date, timedelta, month_open, 
                   month_solved, week_open, week_solved, count_task 
            FROM etsp_data
        """, con=engine)
    df.timedelta = pd.to_timedelta(df.timedelta)

    return df


def load_sue_data():
    """
    Синтаксис:
    ----------

    **load_sue_data** ()

    Описание:
    ---------
    Функция загружает из базы данных информацию об обращениях по техподдержке СУЭ ФК

    Returns:
    -------
        **DataFrame**
    """
    df = pd.read_sql("""
            SELECT reg_date, status, event_number, descr, plan_date, solved_date, user, timedelta, unit, start_date, 
                   finish_date, month_open, month_solved, week_open, week_solved, count_task
            FROM sue_data
        """, con=engine)
    df.timedelta = pd.to_timedelta(df.timedelta)

    return df


def load_osp_data():
    """
    Синтаксис:
    ----------

    **load_osp_data** ()

    Описание:
    ---------
    Функция загружает из базы данных информацию об обращениях по техподдержке ОСП

    Returns:
    -------
        **DataFrame**
    """
    df = pd.read_sql("""
            SELECT reg_date, user, descr, plan_date, solved_date, timedelta, unit, start_date, finish_date, month_open, 
                   month_solved, week_open, week_solved, count_task 
            FROM osp_data
        """, con=engine)
    df.timedelta = pd.to_timedelta(df.timedelta)

    return df


def top_user(df):
    """
    Синтаксис:
    ----------

    **top_user** (df)

    Описание:
    ---------

    Функция принимает на вход ДатаФрейм по техподдержке. Возвращает датафрейм содержащий информацию о ТОП-5 сотрудниках
    которые подали наибольшее количество обращений (ФИО сотрудника, Количество обращений)

    Returns:
    -------
        **DataFrame**
    """
    top_user_df = df[(df.unit != 'Отдел сопровождения пользователей') & (df.unit != 'ЦОКР') & (
            df.user != 'Кондрашова Ирина Сергеевна') & (df.unit != '19. Отдел сопровождения пользователей') & (
            df.user != 'Вельмякин Николай Валерьевич')]
    top_user_df = pd.DataFrame(top_user_df.groupby('user')['count_task'].sum().sort_values(ascending=False).head()
                               .reset_index()).rename(columns={'user': 'Пользователь', 'count_task': 'Обращения'})
    return top_user_df


def load_incident(df):
    """
    Синтаксис:
    ----------

    **load_incident** (df)

    Описание:
    ---------

    Функция принимает на вход ДатаФрейм, и возвращает отфильтрованный датафрейм если за период были зафиксированы
    аварийные инциденты

    Returns:
    -------
        **DataFrame**
    """
    incident_df = df[(df.status == 'Проблема') | (df.status == 'Массовый инцидент')]
    incident_df.columns = ['Дата обращения', 'Тип', 'Номер', 'Описание', 'Плановое время', 'Фактическое время',
                           'Пользователь', 'timedelta', 'Отдел', 'Дата', 'finish_date', 'month_open',
                           'month_solved', 'week_open', 'week_solved', 'count_task']
    return incident_df


def no_incidents():
    """
    Синтаксис:
    ----------

    **no_incidents** ()

    Описание:
    ---------

    Функция создает пустой ДатаФрейм, который подгружается в таблицу если за выбранный период не было аварийных
    инцидентов


    Returns:
    -------
        **DataFrame**
    """
    no_incidents_df = pd.DataFrame({'Дата': '-', 'Тип': 'Аварийных инциндентов нет', 'Номер': '-', 'Описание': '-',
                                    'Плановое время': '-', 'Фактическое время': '-', 'Пользователь': '-',
                                    'timedelta': '-', 'Отдел': '-', 'start_date': '-', 'finish_date': '-',
                                    'month_open': '-', 'month_solved': '-', 'week_open': '-',
                                    'week_solved': '-', 'count_task': '-'}, index=[0])

    return no_incidents_df


def get_time_periods(first_df, second_df, third_df):
    """
    Синтаксис:
    ----------

    **get_time_periods** (first_df, second_df, third_df)

    Описание:
    ---------

    Функция принимает на вход три ДатаФрейма по трем поддержкам. Анализирует столбец содержащий дату регистрации
    обращения. Возвращает словарь который содержит номера недели, месяца и год самого раннего зарегистрированного
    обращения (по 3-м техподдержкам) и номера недели и месяца а также год самого позднего зарегистрированного обращения.

    Параметры:
    ----------
        **first_df**: *DataFrame - ДатаФрейм первой техподдержки

        **second_df**: *DataFrame* - ДатаФрейм второй техподдержки

        **third_df**: *DataFrame* - ДатаФрейм третьей техподдержки

    Returns:
    -------
        **Dict**
    """
    start_weeks_list = [first_df.reg_date.min().week, second_df.reg_date.min().week, third_df.reg_date.min().week]
    end_weeks_list = [first_df.reg_date.max().week, second_df.reg_date.max().week, third_df.reg_date.max().week]

    start_month_list = [first_df.reg_date.min().month, second_df.reg_date.min().month, third_df.reg_date.min().month]
    end_month_list = [first_df.reg_date.max().month, second_df.reg_date.max().month, third_df.reg_date.max().month]

    start_year_list = [first_df.reg_date.min().year, second_df.reg_date.min().year, third_df.reg_date.min().year]
    end_year_list = [first_df.reg_date.max().year, second_df.reg_date.max().year, third_df.reg_date.max().year]

    return dict(week=[min(start_weeks_list), max(end_weeks_list)], month=[min(start_month_list), max(end_month_list)],
                year=[min(start_year_list), max(end_year_list)])


def count_mean_time(filtered_df):
    """
    Синтаксис:
    ----------

    **count_mean_time** (filtered_df)

    Описание:
    ---------

    Функция принимает на вход ДатаФрейм. Возвращает строку содержащую среднее время выполнения заявок

    Параметры:
    ----------
        **filtered_df**: *DataFrame* - ДатаФрейм


    Returns:
    -------
        **String**
    """
    duration = filtered_df['timedelta'].mean()
    count_tasks = filtered_df['count_task'].sum()

    # преобразование в дни, часы, минуты и секунды
    days, seconds = duration.days, duration.seconds
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = (seconds % 60)
    avg_time = days, hours, minutes, seconds

    if count_tasks == 0:
        avg_time = '-'
    elif avg_time[0] == 0:
        avg_time = f'{avg_time[1]} час. {avg_time[2]} мин.'
    else:
        avg_time = f'{avg_time[0]} дн. {avg_time[1]} час. {avg_time[2]} мин.'

    return avg_time


def load_inf_systems_data():
    """
    Синтаксис:
    ----------

    **load_inf_sys_data** ()

    Описание:
    ---------
    Функция загружает из файла Excel данные для построения графика "Информационные системы" размещенного на вкладке № 2

    Returns:
    -------
        **DataFrame**
    """
    df = pd.read_excel(r'passport/assets/dostup.xlsx', sheet_name='Лист5', index_col=0)
    df.drop('Номер отдела', axis=1, inplace=True)

    return df


def get_period(year, week, output_format='n'):
    """
    Синтаксис:
    ----------

    **get_period** (year, week, output_format='n')

    Описание:
    ---------

    Функция принимает на вход год и номер недели. Возвращает список или строку содержащие начальную и конечную
    даты недели

    Параметры:
    ----------

    **year**: *int* - год

    **week**: *int* - номер недели

    **output_format**: *string*, default 'n'
        Определяет формат вывода данных. Допустимые значения:

        'n' - строка вида 'ДД-ММ-ГГГГ - ДД-ММ-ГГГГ'

        's' - список вида ['ГГГГ-ММ-ДД', 'ГГГГ-ММ-ДД']

        При указании другого параметра вернется список ['1900-01-01', '1900-01-01']

    Returns:
    -------
        **string** or **list of strings**
    """
    first_year_day = date(year, 1, 1)
    if first_year_day.weekday() > 3:
        first_week_day = first_year_day + timedelta(7 - first_year_day.weekday())
    else:
        first_week_day = first_year_day - timedelta(first_year_day.weekday())

    dlt_start = timedelta(days=(week - 1) * 7)
    dlt_end = timedelta(days=(((week - 1) * 7) + 6))

    start_day_of_week = first_week_day + dlt_start
    end_day_of_week = first_week_day + dlt_end

    if output_format == 'n':
        period = ' - '.join([start_day_of_week.strftime("%d-%m-%Y"), end_day_of_week.strftime("%d-%m-%Y")])
    elif output_format == 's':
        period = [start_day_of_week.strftime("%Y-%m-%d"), end_day_of_week.strftime("%Y-%m-%d")]
    else:
        period = ['1900-01-01', '1900-01-01']

    return period


def get_month_period(year, month_num):
    """
    Синтаксис:
    ----------

    **get_month_period** (year, month_num)

    Описание:
    ----------

    Функция принимает на вход год и номер месяца. Возвращает список содержащий первую и последнюю даты месяца
    в виде строки формата 'ГГГГ-ММ-ДД'

    Параметры:
    ----------
        **year**: *int* - год

        **month_num**: *int* - номер месяца

    Returns:
    ----------
        **List**
    """
    num_days = calendar.monthrange(year, month_num)[1]

    if month_num > 9:
        start_date = f'{year}-{month_num}-01'
        end_date = f'{year}-{month_num}-{num_days}'
    else:
        start_date = f'{year}-0{month_num}-01'
        end_date = f'{year}-0{month_num}-{num_days}'

    return [start_date, end_date]


def get_weeks(start_week, start_year, finish_week, finish_year):
    """
    Синтаксис:
    ----------

    **get_weeks** (start_week, start_year, finish_week, finish_year)

    Описание:
    ----------
    Функция принимает на вход период в виде 4-х параметров (номер недели и год начала, номер недели и год окончания.
    Возвращает список словарей содержащих информацию о номере недели, её периоде, и номере недели для последующей
    загрузки в компонент dcc.Dropdown.

    Параметры:
    ----------
        **start_week**: *int* - номер недели начала периода

        **start_year**: *int* - год начала периода

        **finish_week**: *int* - номер недели окончания периода

        **finish_year**: *int* - год окончания периода

    Returns:
    ----------
        **List**
    """
    last_week_of_start_year = date(start_year, 12, 31).isocalendar()[1]

    start_period = [{"label": f'Неделя {i} ({get_period(year=start_year, week=i)})',
                     "value": "_".join([str(i), str(start_year)])} for i in
                    range(start_week, last_week_of_start_year + 1)]
    end_period = [
        {"label": f'Неделя {i} ({get_period(year=finish_year, week=i)})', "value": "_".join([str(i), str(finish_year)])}
        for i in range(1, finish_week + 1)]

    if finish_year - start_year <= 1:
        for item in end_period:
            start_period.append(item)
        start_period.reverse()
    else:
        years_dict = {}
        for count in range(1, (finish_year - start_year)):
            if date(start_year + count, 12, 31).isocalendar()[2] < 4:
                years_dict[start_year + count] = date(start_year + count, 12, 31 - date(start_year + count, 12, 31).
                                                      isocalendar()[2]).isocalendar()[1]
            else:
                years_dict[start_year + count] = date(start_year + count, 12, 31).isocalendar()[1]

        addition_period = []
        for year in years_dict.keys():
            addition_period.append(
                [{"label": f'Неделя {i} ({get_period(year=year, week=i)})', "value": "_".join([str(i), str(year)])}
                 for i in range(1, years_dict[year] + 1)])

        for period in addition_period:
            for item in period:
                start_period.append(item)
        for item in end_period:
            start_period.append(item)
        start_period.reverse()

    return start_period


def get_period_month(year, month):
    """
    Синтаксис:
    ----------

    **get_period_month** (year, month)

    Описание:
    ----------
    Функция принимает на вход номер месяца и год. Возвращает строку 'Месяц год'.

    Параметры:
    ----------
        **year**: *int* - год

        **month**: *int* - номер месяца

    Returns:
    ----------
        **String**
    """
    months = ['', 'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь',
              'Ноябрь', 'Декабрь']
    period = ' '.join([str(months[month]), str(year)])

    return period


def get_months(start_month, start_year, finish_month, finish_year):
    """
    Синтаксис:
    ----------
    **get_months** (start_month, start_year, finish_month, finish_year)

    Описание:
    ----------

    Функция принимает на вход период в виде 4-х параметров (номер месяца и год начала, номер месяца и год окончания.
    Возвращает список словарей, содержащих информацию о месяце, годе и номере месяца для последующей загрузки в
    компонент dcc.Dropdown.

    Параметры:
    ----------
        **start_month**: *int* - номер месяца начала периода

        **start_year**: *int* - год начала периода

        **finish_month**: *int* - номер месяца окончания периода

        **finish_year**: *int* - год окончания периода

    Returns:
    ----------
        **List**
    """
    start_period = [
        {"label": f'{get_period_month(year=start_year, month=i)}', "value": "_".join([str(i), str(start_year)])}
        for i in range(start_month, 13)]
    end_period = [
        {"label": f'{get_period_month(year=finish_year, month=i)}', "value": "_".join([str(i), str(finish_year)])}
        for i in range(1, finish_month + 1)]

    if finish_year - start_year <= 1:
        for item in end_period:
            start_period.append(item)
        start_period.reverse()
    else:
        years_list = []
        for count in range(1, finish_year - start_year):
            years_list.insert(count, start_year + count)

        addition_period = []
        for year in years_list:
            addition_period.append(
                [{"label": f'{get_period_month(year=year, month=i)}', "value": "_".join([str(i), str(year)])} for i in
                 range(1, 13)])

        for period in addition_period:
            for item in period:
                start_period.append(item)
        for item in end_period:
            start_period.append(item)
        start_period.reverse()

    return start_period


def load_projects(projects_status='in_progress', project_name='all'):
    """
    Синтаксис:
    ----------
    **load_projects** (projects_status='in_progress', project_name='all')

    Описание:
    ----------
    Функция загружает проекты/задачи отдела из базы данных. Возвращает pandas.DataFrame.

    Параметры:
    ----------
    **projects_status**: *string*, default 'in_progress'
        Определяет какие проекты/задачи загружать. Допустимые значения:

        '**in_progress**' - загружает из базы данных проекты/задачи отдела, которые в данный момент находятся в работе.

        '**complete**' - загружает все завершенные проекты/задачи отдела.

    **project_name**: *String*, default 'all'
        Определяет название задачи / проекта которые необходимо загружать. Допустимые значения:

        '**all**' - загружает все задачи / проекты

        '**название проекта / задачи**' загружает только указанную задачу / проект

    Returns:
    ----------
        **DataFrame**
    """
    if projects_status == 'in_progress':
        if project_name == 'all':
            return pd.read_sql("""
            SELECT *
            FROM projects_new 
            WHERE persent < 100
        """, con=engine)
        else:
            return pd.read_sql(f"""
            SELECT *
            FROM projects_new 
            WHERE persent < 100
                AND name ='{project_name}'
        """, con=engine)

    elif projects_status == 'complete':
        return pd.read_sql("""
            SELECT id, name, executor, persent, stage, fact_date, duration 
            FROM projects_new 
            WHERE persent = 100
        """, con=engine)
    elif projects_status == 'all':
        return pd.read_sql("""
            SELECT *
            FROM projects_new 
        """, con=engine)
    else:
        return pd.DataFrame(columns=['id', 'name', 'executor', 'persent', 'stage', 'plan_date'])


def set_differences(diff):
    """
    Синтаксис:
    ----------
    **set_differences** (diff)

    Описание:
    ----------

    Функция принимает на вход разницу между количеством обращений (количеством обратившихся пользователей) за текущий
    период и аналогичный прошлый период. Если разница положительная, то она будет окрашена в зеленый цвет, если
    отрицательная - то в красный. Возвращает список *[Стиль, Разница]*

    Returns:
    ----------
        **List(style_t, diff_t)**
    """
    if diff > 0:
        style_t = {'font-size': '2em', 'color': 'green'}
        diff_t = '+ ' + str(diff)
    elif diff == 0:
        style_t = {'font-size': '2em'}
        diff_t = str(diff)
    else:
        style_t = {'font-size': '2em', 'color': 'red'}
        diff_t = str(diff)
    return [style_t, diff_t]


def choosen_type(type_period, start_date, end_date, ch_month, ch_week):
    """
    Синтаксис:
    ----------
    **choosen_type** (type_period, start_date, end_date, ch_month, ch_week)

    Описание:
    ----------
    Функция принимает на вход тип фильтра и параметры фильтрации (номер недели, месяца, даты начала/окончания периода).
    В зависимости от выбранного типа фильтра отключает другие компоненты (например если выбрана фильтрация по неделям,
    остальные компоненты фильтрации (выбор месяца и произвольного периода) будут отключены). Также функция записывает в
    лог-файл выбранный тип фильтрации и его значение (номер недели/месяца или период)

    Параметры:
    ----------
        **type_period**: *str*
            Определяет тип фильтрации. Допустимые значения:

            '**m**' - фильтрация по выбранному месяцу.

            '**p**' - фильтрация по произвольному периоду.

            Если параметр не указан, то фильтрация осуществляется по неделям.

        **start_date**: *str* - дата начала периода (если фильтрация по произвольному периоду (DateTimeRange))

        **end_date**: *str* - дата окончания периода (если фильтрация по произвольному периоду (DateTimeRange))

        **ch_month**: *int* - номер выбранного месяца (если фильтрация по месяцу)

        **ch_week**: *int* - номер выбранной недели (если фильтрация осуществляется по неделям)

    Returns:
    ----------
        **Tuple**
    """
    if type_period == 'm':
        period_choice = True
        week_choice = True
        month_choice = False
        lw.log_writer(log_msg=f'User choice "month = {ch_month}"')

    elif type_period == 'p':
        period_choice = False
        week_choice = True
        month_choice = True
        lw.log_writer(log_msg=f'User choice "range period start = {start_date}, end = {end_date}"')

    else:
        period_choice = True
        week_choice = False
        month_choice = True
        lw.log_writer(log_msg=f'User choice "week = {ch_week} ({get_period(year=current_year, week=ch_week)})"')

    return period_choice, week_choice, month_choice


def get_date_for_metrika_df(start_date, end_date, ch_month, ch_week, type_period):
    """
    Синтаксис:
    ----------
    **get_date_for_metrika_df** (type_period, start_date, end_date, ch_month, ch_week)

    Описание:
    ---------
    Функция принимает на вход параметры фильтрации (тип фильтра, выбранный номер недели, месяца, даты
    начала/окончания периода). Возвращает кортеж содержащий даты начала и окончания периода в формате, подходящим для
    последующей передачи в запрос Яндекс.Метрики.

    Параметры:
    ----------
        **type_period**: *str* - Определяет тип фильтрации. Допустимые значения:

            '**m**' - фильтрация по выбранному месяцу.

            '**p**' - фильтрация по произвольному периоду.

            Если параметр не указан, то фильтрация осуществляется по неделям.

        **start_date**: *str* - дата начала периода (если фильтрация по произвольному периоду (DateTimeRange))

        **end_date**: *str* - дата окончания периода (если фильтрация по произвольному периоду (DateTimeRange))

        **ch_month**: *int* - номер выбранного месяца (если фильтрация по месяцу)

        **ch_week**: *int* - номер выбранной недели (если фильтрация осуществляется по неделям)

    Returns:
    --------
        **Tuple**
    """
    if type_period == 'm':
        if ch_month > current_month:
            year_metrika = current_year - 1
        else:
            year_metrika = current_year

        start_date_metrika = get_month_period(year=year_metrika,
                                              month_num=ch_month)[0]
        end_date_metrika = get_month_period(year=year_metrika,
                                            month_num=ch_month)[1]

    elif type_period == 'p':
        start_date_metrika = start_date
        end_date_metrika = end_date

    else:
        if ch_week > current_week:
            year_metrika = current_year - 1
        else:
            year_metrika = current_year

        start_date_metrika = get_period(year=year_metrika,
                                        week=ch_week,
                                        output_format='s')[0]
        end_date_metrika = get_period(year=year_metrika,
                                      week=ch_week,
                                      output_format='s')[1]

    return start_date_metrika, end_date_metrika


def get_filtered_df(table_name, start_date, end_date, month, month_year, week, week_year, type_period):
    """
    Синтаксис:
    ----------
    **get_filtered_df** (table_name, start_date, end_date, ch_month, ch_week, type_period)

    Описание:
    ----------
    Функция принимает на вход наименование таблицы, в которой содержаться данные по техподдержки в БД и параметры
    фильтрации (тип фильтра, выбранный номер недели, месяца, даты начала/окончания периода). Сделает запрос к БД.
    Возвращает отфильтрованный датафрейм за выбранный период по выбранной таблице (техподдержки).

    Параметры:
    ----------
        **table_name**: *String* - Название таблицы в БД для фильтрации

        **start_date**: *str* - дата начала периода (если фильтрация по произвольному периоду (DateTimeRange))

        **end_date**: *str* - дата окончания периода (если фильтрация по произвольному периоду (DateTimeRange))

        **ch_month**: *int* - номер выбранного месяца (если фильтрация по месяцу)

        **cho_week**: *int* - номер выбранной недели (если фильтрация осуществляется по неделям)

        **type_period**: *str* - Определяет тип фильтрации. Допустимые значения:

            '**m**' - фильтрация по выбранному месяцу.

            '**p**' - фильтрация по произвольному периоду.

            Если параметр не указан, то фильтрация осуществляется по неделям.

    Returns:
    ----------
        **DataFrame**
    """
    if type_period == 'm':
        df = pd.read_sql(f"""
            SELECT * 
            FROM {table_name} 
            WHERE EXTRACT(month from reg_date) = {int(month)}
            AND EXTRACT(year from reg_date) = {int(month_year)}
    """, con=engine)
        df.timedelta = pd.to_timedelta(df.timedelta)
        return df

    elif type_period == 'p':
        df = pd.read_sql(f"""
            SELECT * 
            FROM {table_name} 
            WHERE reg_date >= '{start_date} 00:00:00' 
                AND reg_date <='{end_date} 23:59:59'
        """, con=engine)
        df.timedelta = pd.to_timedelta(df.timedelta)
        return df
    else:
        df = pd.read_sql(f"""
            SELECT * 
            FROM {table_name} 
            WHERE EXTRACT(year from reg_date) = {week_year}
            AND EXTRACT(week from reg_date) = {week}
        """, con=engine)
        df.timedelta = pd.to_timedelta(df.timedelta)
        return df


def get_prev_filtered_df(table_name, start_date, end_date, month, month_year, week, week_year, type_period):
    """
    Синтаксис:
    ----------

    **get_prev_filtered_df** (table_name, type_period, start_date, end_date, ch_month, ch_week)

    Описание:
    ----------

    Функция принимает на вход наименование таблицы, в которой содержаться данные по техподдержки в БД и параметры
    фильтрации (тип фильтра, выбранный номер недели, месяца, даты начала/окончания периода). Сделает запрос к БД.
    Возвращает отфильтрованный датафрейм за период предшествующий выбранным параметрам (например если выбран номер
    месяца 2, то функция вернет отфильтрованный датафрейм за предыдущий месяц, т.е. 1).

    Параметры:
    ----------
        **table_name**: *String* - Название таблицы в БД для фильтрации

        **start_date**: *str* - дата начала периода (если фильтрация по произвольному периоду (DateTimeRange))

        **end_date**: *str* - дата окончания периода (если фильтрация по произвольному периоду (DateTimeRange))

        **ch_month**: *int* - номер выбранного месяца (если фильтрация по месяцу)

        **ch_week**: *int* - номер выбранной недели (если фильтрация осуществляется по неделям)

        **type_period**: string
            Определяет тип фильтрации. Допустимые значения:

            '**m**' - фильтрация по выбранному месяцу.

            '**p**' - фильтрация по произвольному периоду.

            Если параметр не указан, то фильтрация осуществляется по неделям.

    Returns:
    ----------
        **DataFrame**
    """
    if type_period == 'm':
        if int(month) > 1:
            df = pd.read_sql(f"""
                SELECT * 
                FROM {table_name} 
                WHERE EXTRACT(month from reg_date) = {int(month)- 1}
                AND EXTRACT(year from reg_date) = {int(month_year)}
            """, con=engine)
            df.timedelta = pd.to_timedelta(df.timedelta)
            return df
        else:
            df = pd.read_sql(f"""
                SELECT * 
                FROM {table_name} 
                WHERE EXTRACT(month from reg_date) = 12
                AND EXTRACT(year from reg_date) = {int(month_year)}
            """, con=engine)
            df.timedelta = pd.to_timedelta(df.timedelta)
            return df

    elif type_period == 'p':
        delta = dt.datetime.strptime(end_date, '%Y-%m-%d') - dt.datetime.strptime(start_date, '%Y-%m-%d')
        prev_start_date = dt.datetime.strftime((dt.datetime.strptime(start_date, '%Y-%m-%d') - delta), '%Y-%m-%d')
        prev_end_date = dt.datetime.strftime((dt.datetime.strptime(end_date, '%Y-%m-%d') - delta), '%Y-%m-%d')
        df = pd.read_sql(f"""
            SELECT * 
            FROM {table_name} 
            WHERE reg_date >= '{prev_start_date} 00:00:00' 
                AND reg_date <='{prev_end_date} 23:59:59'
        """, con=engine)
        df.timedelta = pd.to_timedelta(df.timedelta)
        return df

    else:
        if int(week) > 1:
            df = pd.read_sql(f"""
                SELECT * 
                FROM {table_name} 
                WHERE EXTRACT(year from reg_date) = {week_year}
                AND EXTRACT(week from reg_date) = {week - 1}
            """, con=engine)
            df.timedelta = pd.to_timedelta(df.timedelta)
            return df
        else:
            df = pd.read_sql(f"""
                SELECT * 
                FROM {table_name} 
                WHERE EXTRACT(year from reg_date) = {week_year}
                AND EXTRACT(week from reg_date) = {52}
            """, con=engine)
            df.timedelta = pd.to_timedelta(df.timedelta)
            return df


def get_filtered_incidents_df(start_date, end_date, month, month_year, week, week_year, type_period):
    """
    Синтаксис:
    ----------

    **get_filtered_incidents_df** (start_date, end_date, ch_month, ch_week, type_period)

    Описание:
    ---------

    Функция принимает на вход параметры фильтрации (тип фильтра, выбранный номер недели, месяца, даты начала/окончания
    периода). Сделает запрос к БД. Возвращает отфильтрованный датафрейм за выбранный период (неделя, месяц, произвольный
    период), в случае если за выбранный период были зафиксированы аварийные инциденты

    Параметры:
    ----------

        **start_date**: *str* - дата начала периода (если фильтрация по произвольному периоду (DateTimeRange))

        **end_date**: *str* - дата окончания периода (если фильтрация по произвольному периоду (DateTimeRange))

        **ch_month**: *int* - номер выбранного месяца (если фильтрация по месяцу)

        **ch_week**: *int* - номер выбранной недели (если фильтрация осуществляется по неделям)

        **type_period**: string
            Определяет тип фильтрации. Допустимые значения:

            '**m**' - фильтрация по выбранному месяцу.

            '**p**' - фильтрация по произвольному периоду.

            Если параметр не указан, то фильтрация осуществляется по неделям.

    Returns:
    -------
        **DataFrame**
    """
    if type_period == 'm':
        df = pd.read_sql(f"""
            SELECT * 
            FROM sue_data 
            WHERE (status = 'Проблема' or status = 'Массовый инцидент') 
                AND EXTRACT(month from reg_date) = {int(month)}
                AND EXTRACT(year from reg_date) = {int(month_year)}
        """, con=engine)
        df.timedelta = pd.to_timedelta(df.timedelta)
        df.columns = ['Дата обращения', 'Тип', 'Номер', 'Описание', 'Плановое время', 'Фактическое время',
                      'Пользователь', 'timedelta', 'Отдел', 'Дата', 'finish_date', 'month_open',
                      'month_solved', 'week_open', 'week_solved', 'count_task']
        return df

    elif type_period == 'p':
        delta = dt.datetime.strptime(end_date, '%Y-%m-%d') - dt.datetime.strptime(start_date, '%Y-%m-%d')
        prev_start_date = dt.datetime.strftime((dt.datetime.strptime(start_date, '%Y-%m-%d') - delta), '%Y-%m-%d')
        prev_end_date = dt.datetime.strftime((dt.datetime.strptime(end_date, '%Y-%m-%d') - delta), '%Y-%m-%d')
        df = pd.read_sql(f"""
            SELECT * 
            FROM sue_data 
            WHERE (status = 'Проблема' or status = 'Массовый инцидент') 
               AND (reg_date >= '{prev_start_date} 00:00:00' and reg_date <='{prev_end_date} 23:59:59')
        """, con=engine)
        df.timedelta = pd.to_timedelta(df.timedelta)
        df.columns = ['Дата обращения', 'Тип', 'Номер', 'Описание', 'Плановое время', 'Фактическое время',
                      'Пользователь', 'timedelta', 'Отдел', 'Дата', 'finish_date', 'month_open', 'month_solved',
                      'week_open', 'week_solved', 'count_task']
        return df

    else:
        df = pd.read_sql(f"""
            SELECT * 
            FROM sue_data 
            WHERE (status = 'Проблема' or status = 'Массовый инцидент')
                AND EXTRACT(year from reg_date) = {week_year}
                AND EXTRACT(week from reg_date) = {week}
        """, con=engine)
        df.timedelta = pd.to_timedelta(df.timedelta)
        df.columns = ['Дата обращения', 'Тип', 'Номер', 'Описание', 'Плановое время', 'Фактическое время',
                      'Пользователь', 'timedelta', 'Отдел', 'Дата', 'finish_date', 'month_open', 'month_solved',
                      'week_open', 'week_solved', 'count_task']
        return df


def get_osp_names_projects():
    """
    Синтаксис:
    ----------

    **get_osp_names_projects** ()

    Описание:
    ---------

    Функция, которая загружает из специальной таблицы БД список сотрудников ОСП для последующей подгрузки в компонент
    dcc.Dropdown на формах "Добавление нового проекта" и "Редактирование проекта"

    Returns:
    -------
        **List of Dicts**
    """
    df = pd.read_sql('staff', con=engine)
    osp_staff = df.curr_name.to_list()
    project_staff = []
    for i in range(len(osp_staff)):
        person_name = ''.join([osp_staff[i][:osp_staff[i].find(' ') + 2], '.',
                               osp_staff[i][osp_staff[i].rfind(' ') + 1:osp_staff[i].rfind(' ') + 2], '.'])
        project_staff.append({'label': person_name, 'value': person_name})
    return project_staff


def names_to_db(users):
    """
    Синтаксис:
    ----------

    **names_to_db** (users)

    Описание:
    ---------

    Функция, которая принимает на вход множество (set) содержащее список ответственных исполнителей по задаче / проекту
    (выбраны в компоненте dcc.Dropdown на формах "Добавление нового проекта" и "Редактирование проекта"). Возвращает
    строку содержащую список ответственных исполнителей, разделенных символом "/" для последующей загрузки в БД.

    Параметры:
    ----------
        **users**: *Set* - Множество содержащие фамилию и инициалы ответственного-(ых) исполнителя-(ей)

    Returns:
    -------
        **String**
    """
    if not users:
        return None
    else:
        names_string = ''
        for item in users:
            names_string = ''.join([names_string, '/', item])
        return names_string[1:]


def get_emails_list(row):
    if not row[1]:
        lw.log_writer(log_msg=f"Список исполнителей пуст: {row}")
        return []
    else:
        executors = row[1].split('/')
        df = pd.read_sql("""select short_name, email from staff""", con=engine)
        return df[df.short_name.isin(executors)].email.to_list()


@safe
def send_mail(subject, row, params, recipients_list):
    server = params[0]
    user = params[1]
    password = params[2]

    recipients = recipients_list
    sender = 'osp-dashbord@bk.ru'
    subject = f'{subject} "{row[0]}"'
    text = f"""<b><u><i>Описание задачи / проекта:</i></u></b><br><br>
    {row[3]}<br><br><br><br>
    <b><u><i>Плановый срок исполнения задачи / проекта:</i></u></b> <font color='red' size='4'> &nbsp;&nbsp;&nbsp;<u>
    {row[4]}</u></font><br><br>
    <b><u><i>Процент выполнения задачи:</i></u></b>&nbsp;&nbsp;&nbsp;<font color='#012e67' size='4'><b>{row[2]}%</b>
    </font><br><br> 
    <i>Уточнить детали а также отметить выполнение задачи / проекта Вы можете в Дашборде на вкладке <b>"задачи / 
    проекты"</b></i><br><br> 
    <i>Ссылка на дашборд: <b><a href='http://10.201.76.16/'>http://10.201.76.16/</a></b></i><br><br><br><br> 
    <font size=2 color='#808080'>Пожалуйста не отвечайте на это письмо, оно отправлено с ящика, который не
    просматривается.<br><br> 
    <font size=2 color='green'>Берегите природу, не распечатывайте данное сообщение,
    если в этом нет необходимости.</font></p> """
    html = '<html><head></head><body><p>' + text + '</p></body></html>'

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = 'OSP Dashboard <' + sender + '>'
    msg['To'] = ', '.join(recipients)
    msg['Reply-To'] = sender
    msg['Return-Path'] = sender
    msg['X-Mailer'] = 'Python/' + (python_version())

    part_text = MIMEText(text, 'plain')
    part_html = MIMEText(html, 'html')

    msg.attach(part_html)
    msg.attach(part_text)
    msg.attach(part_html)
    mail = smtplib.SMTP_SSL(server)
    mail.login(user, password)
    mail.sendmail(sender, recipients, msg.as_string())
    mail.quit()


def count_project_time(start_date, fact_date):
    if (len(start_date) == 10) and (len(fact_date) == 10):
        fact_date = dt.datetime.strptime(fact_date, '%Y-%m-%d')
        start_date = dt.datetime.strptime(start_date, '%Y-%m-%d')
        return (fact_date - start_date).days
    else:
        return 0


def count_employees(conn_string):
    df = pd.read_sql('inf_systems', con=conn_string)
    employees_count = df[df.correct_name.notna()].correct_name.count()

    return employees_count


def load_inf_sys_data(conn_string):
    df = pd.read_sql('inf_systems', con=conn_string)
    df = df.groupby(['unit']).count()
    df.drop(['№ П/П', 'ФИО СОТРУДНИКОВ МБУ', 'name', 'correct_name', 'is_true', 'hire_date', 'fire_date'],
            axis=1, inplace=True)

    return df


def read_history_data():
    history_data = ''
    with open('assets/history.txt', 'r', encoding="utf8") as history_text_file:
        for line in history_text_file:
            history_data += line
        return history_data
