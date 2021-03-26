import calendar
from datetime import date, timedelta
import datetime as dt
import pandas as pd
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
    Описание:
    ---------
    Функция загружает из базы данных информацию об обращениях по техподдержке ЕЦП

    Returns:
    -------
        **DataFrame**
    """
    df = pd.read_sql('''select * from etsp_data''', con=engine)
    df.timedelta = pd.to_timedelta(df.timedelta)

    return df


def load_sue_data():
    """
    Описание:
    ---------
    Функция загружает из базы данных информацию об обращениях по техподдержке СУЭ ФК

    Returns:
    -------
        **DataFrame**
    """
    df = pd.read_sql('''select * from sue_data''', con=engine)
    df.timedelta = pd.to_timedelta(df.timedelta)

    return df


def load_osp_data():
    """
    Описание:
    ---------
    Функция загружает из базы данных информацию об обращениях по техподдержке ОСП

    Returns:
    -------
        **DataFrame**
    """
    df = pd.read_sql('''select * from osp_data''', con=engine)
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
    которые подали наибольшее количество обращений (ФИО сотрудника, Количество обращений

    Returns:
    -------
        **DataFrame**
    """
    top_user_df = df[(df.unit != 'Отдел сопровождения пользователей') & (df.unit != 'ЦОКР') & (
            df.user != 'Кондрашова Ирина Сергеевна') & (df.unit != '19. Отдел сопровождения пользователей')]
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

    Функция принимает на вход ДатаФрейм, и возвращает отфильтрованный датафрейм если за период были зафиксирвоаны
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


def no_icidents():
    """
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


def get_time_periods(etsp_df, sue_df, osp_df):
    """
    Синтаксис:
    ----------

    **get_time_periods** (etsp_df, sue_df, osp_df)

    Описание:
    ---------

    Функция принимает на вход три ДатаФрейма по трем поддержкам. Анализирует столбец содержащий дату регистрации
    обращения. Возвращает словарь который содержит номера недели, месяца и год самого раннего зарегистрированного
    обращения (по 3-м техподдержкам) и номера недели и месяца а также год самого позднего зерегистрированоого обращения.

    Параметры:
    ----------
        **etsp_df**: *DataFrame - ДатаФрейм первой техподдержки

        **sue_df**: *DataFrame* - ДатаФрейм второй техподдержки

        **osp_df**: *DataFrame* - ДатаФрейм третьей техподдержки

    Returns:
    -------
        **Dict**
    """
    start_weeks_list = [etsp_df.reg_date.min().week, sue_df.reg_date.min().week, osp_df.reg_date.min().week]
    end_weeks_list = [etsp_df.reg_date.max().week, sue_df.reg_date.max().week, osp_df.reg_date.max().week]

    start_month_list = [etsp_df.reg_date.min().month, sue_df.reg_date.min().month, osp_df.reg_date.min().month]
    end_month_list = [etsp_df.reg_date.max().month, sue_df.reg_date.max().month, osp_df.reg_date.max().month]

    start_year_list = [etsp_df.reg_date.min().year, sue_df.reg_date.min().year, osp_df.reg_date.min().year]
    end_year_list = [etsp_df.reg_date.max().year, sue_df.reg_date.max().year, osp_df.reg_date.max().year]

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

    Функция принимает на вход год и номер месяца. Возвращает списко содержащий первую и последнюю даты месяца
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
    **get_months** (start_week, start_year, finish_week, finish_year)

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

    start_period = [{"label": f'Неделя {i} ({get_period(start_year, i)})',
                     "value": i} for i in range(start_week, last_week_of_start_year + 1)]
    end_period = [{"label": f'Неделя {i} ({get_period(finish_year, i)})', "value": i}
                  for i in range(1, finish_week + 1)]

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
    Возвращает список словарей содержащих информацию о месяце, годе и номере месяца для последующей загрузки в
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
    start_period = [{"label": f'{get_period_month(start_year, i)}', "value": i} for i in range(start_month, 13)]
    end_period = [{"label": f'{get_period_month(finish_year, i)}', "value": i} for i in range(1, finish_month + 1)]

    for item in end_period:
        start_period.append(item)
    start_period.reverse()

    return start_period


def load_projects(projects_status='in_progress'):
    """
    Синтаксис:
    ----------
    **load_projects** (projects_status='in_progress')

    Описание:
    ----------
    Функция загружает проекты/задачи отдела из базы данных. Возвращает pandas.DataFrame.

    Параметры:
    ----------
    **projects_status**: *string*, default 'in_progress'
        Определяет какие проекты/задачи загружать. Допустимые значения:

        '**in_progress**' - загружает из базы данных проекты/задачи отдела, которые в данный момент находятся в работе.

        '**complete**' - загружает все завершенные проекты/задачи отдела.

    Returns:
    ----------
        **DataFrame**
    """
    if projects_status == 'in_progress':
        return pd.read_sql("""
        select id, name, executor, persent, stage, finish_date from projects_new where persent < 100
        """,
                           con=engine)
    elif projects_status == 'complete':
        return pd.read_sql("""
        select id, name, executor, persent, stage from projects_new where persent = 100
        """,
                           con=engine)
    else:
        return pd.DataFrame(columns=['id', 'name', 'executor', 'persent', 'stage', 'finish_date'])


def set_differences(diff):
    """
    Синтаксис:
    ----------
    **set_differences** (diff)

    Описание:
    ----------

    Функция принимает на вход разницу между количеством обращений (количеством обратившихся пользователей) за текуцщий
    период и аналогичный прошлый период. Если разница положительная то она будет окращена в зеленый цвет, если
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


def get_prev_filtered_df(df, start_date_user, end_date_user, choosen_month, choosen_week, choice_type_period):
    """
    Синтаксис:
    ----------

    **get_prev_filtered_df** (df, choice_type_period, start_date_user, end_date_user, choosen_month, choosen_week)

    Описание:
    ----------

    Функция принимает на вход датафрейм и параметры фильтрации (тип фильтра, выбранный номер недели, месяца, даты
    начала/окончания периода). Возвращает отфильтрованный датафрейм за период предшествующий выбранным параметрам
    (напрмер если выбран номер месяца 2, то функция вернет отфильтрованный датафрейм за предыдцщий месяц, т.е. 1).

    Параметры:
    ----------
        **df**: DataFrame - Датафрейм для фильтрации

        **choice_type_period**: string
            Определяет тип фильтрации. Допустимые значения:

            '**m**' - фильтрация по выбранному месяцу.

            '**p**' - фильтрация по произвольному периоду.

            Если параметр не указан, то фильтрация осуществляется по неделям.

        **start_date_user**: *str* - дата начала периода (если фильтрация по произвольному периоду (DateTimeRange))

        **end_date_user**: *str* - дата окончания периода (если фильтрация по произвольному периоду (DateTimeRange))

        **choosen_month**: *int* - номер выбранного месяца (если фильтрация по месяцу)

        **choosen_week**: *int* - номер выбранной недели (если фильтрация осуществляется по неделям)

    Returns:
    ----------
        **DataFrame**
    """
    if choice_type_period == 'm':
        if int(choosen_month) > 1:
            return df[df['month_open'] == (int(choosen_month) - 1)]
        else:
            return df[df['month_open'] == 12]

    elif choice_type_period == 'p':
        delta = dt.datetime.strptime(end_date_user, '%Y-%m-%d') - dt.datetime.strptime(start_date_user, '%Y-%m-%d')
        prev_start_date = dt.datetime.strftime((dt.datetime.strptime(start_date_user, '%Y-%m-%d') - delta), '%Y-%m-%d')
        prev_end_date = dt.datetime.strftime((dt.datetime.strptime(end_date_user, '%Y-%m-%d') - delta), '%Y-%m-%d')
        return df[(df['start_date'] >= prev_start_date) & (df['start_date'] <= prev_end_date)]

    else:
        if int(choosen_week) > 1:
            return df[df['week_open'] == (int(choosen_week) - 1)]
        else:
            return df[df['week_open'] == 52]


def choosen_type(choice_type_period, start_date_user, end_date_user, choosen_month, choosen_week):
    """
    Синтаксис:
    ----------
    **choosen_type** (choice_type_period, start_date_user, end_date_user, choosen_month, choosen_week)

    Описание:
    ----------
    Функция принимает на вход тип фильтра и параметры фильтрации (номер недели, месяца, даты начала/окончания периода).
    В зависимости от выбранного типа фильтра отключает другие компоненты (например если выбрана фильтрация по неделям,
    остальные компоненты фильтрации (выбор месяца и прозвольного периода) будут отключены). Также функция записывает в
    лог-файл выбранный тип фильтрации и его значение (номер недели/месяца или период)

    Параметры:
    ----------
        **choice_type_period**: *str*
            Определяет тип фильтрации. Допустимые значения:

            '**m**' - фильтрация по выбранному месяцу.

            '**p**' - фильтрация по произвольному периоду.

            Если параметр не указан, то филттрация осуществляется по неделям.

        **start_date_user**: *str* - дата начала периода (если фильтрация по произвольному периоду (DateTimeRange))

        **end_date_user**: *str* - дата окончания периода (если фильтрация по произвольному периоду (DateTimeRange))

        **choosen_month**: *int* - номер выбранного месяца (если фильтрация по месяцу)

        **choosen_week**: *int* - номер выбранной недели (если фильтрация осуществляется по неделям)

    Returns:
    ----------
        **Tuple**
    """
    if choice_type_period == 'm':
        period_choice = True
        week_choice = True
        month_choice = False
        lw.log_writer(f'User choice "month = {choosen_month}"')

    elif choice_type_period == 'p':
        period_choice = False
        week_choice = True
        month_choice = True
        lw.log_writer(f'User choice "range period start = {start_date_user}, end = {end_date_user}"')

    else:
        period_choice = True
        week_choice = False
        month_choice = True
        lw.log_writer(f'User choice "week = {choosen_week} ({get_period(current_year, choosen_week)})"')

    return period_choice, week_choice, month_choice


def get_filtered_df(df, start_date_user, end_date_user, choosen_month, choosen_week, choice_type_period):
    """
    Синтаксис:
    ----------
    **get_filtered_df** (df, start_date_user, end_date_user, choosen_month, choosen_week, choice_type_period)

    Описание:
    ----------
    Функция принимает на вход датафрейм и параметры фильтрации (тип фильтра, выбранный номер недели, месяца, даты
    начала/окончания периода). Возвращает отфильтрованный датафрейм за выбранный период.

    Параметры:
    ----------
        **df**: *DataFrame* - Датафрейм для фильтрации

        **choice_type_period**: *str* - Определяет тип фильтрации. Допустимые значения:

            '**m**' - фильтрация по выбранному месяцу.

            '**p**' - фильтрация по произвольному периоду.

            Если параметр не указан, то филттрация осуществляется по неделям.

        **start_date_user**: *str* - дата начала периода (если фильтрация по произвольному периоду (DateTimeRange))

        **end_date_user**: *str* - дата окончания периода (если фильтрация по произвольному периоду (DateTimeRange))

        **choosen_month**: *int* - номер выбранного месяца (если фильтрация по месяцу)

        **choosen_week**: *int* - номер выбранной недели (если фильтрация осуществляется по неделям)

    Returns:
    ----------
        **DataFrame**
    """
    if choice_type_period == 'm':
        return df[df['month_open'] == int(choosen_month)]

    elif choice_type_period == 'p':
        return df[(df['start_date'] >= start_date_user) & (df['start_date'] <= end_date_user)]

    else:
        return df[df['week_open'] == int(choosen_week)]


def get_date_for_metrika_df(start_date_user, end_date_user, choosen_month, choosen_week, choice_type_period):
    """
    Синтаксис:
    ----------
    **get_filtered_df** (choice_type_period, start_date_user, end_date_user, choosen_month, choosen_week)

    Описание:
    ---------
    Функция принимает на вход параметры фильтрации (тип фильтра, выбранный номер недели, месяца, даты
    начала/окончания периода). Возвращает кортеж содержащий даты начала и окончания периода в формате, подходящим для
    последующей передачи в запрос Яндекс.Метрики.

    Параметры:
    ----------
        **choice_type_period**: *str* - Определяет тип фильтрации. Допустимые значения:

            '**m**' - фильтрация по выбранному месяцу.

            '**p**' - фильтрация по произвольному периоду.

            Если параметр не указан, то филттрация осуществляется по неделям.

        **start_date_user**: *str* - дата начала периода (если фильтрация по произвольному периоду (DateTimeRange))

        **end_date_user**: *str* - дата окончания периода (если фильтрация по произвольному периоду (DateTimeRange))

        **choosen_month**: *int* - номер выбранного месяца (если фильтрация по месяцу)

        **choosen_week**: *int* - номер выбранной недели (если фильтрация осуществляется по неделям)

    Returns:
    --------
        **Tuple**
    """
    if choice_type_period == 'm':
        if choosen_month > current_month:
            year_metrika = current_year - 1
        else:
            year_metrika = current_year

        start_date_metrika = get_month_period(year_metrika, choosen_month)[0]
        end_date_metrika = get_month_period(year_metrika, choosen_month)[1]

    elif choice_type_period == 'p':
        start_date_metrika = start_date_user
        end_date_metrika = end_date_user

    else:
        if choosen_week > current_week:
            year_metrika = current_year - 1
        else:
            year_metrika = current_year

        start_date_metrika = get_period(year_metrika, choosen_week, 's')[0]
        end_date_metrika = get_period(year_metrika, choosen_week, 's')[1]

    return start_date_metrika, end_date_metrika


def get_filtered_df_new(table_name, start_date_user, end_date_user, choosen_month, choosen_week, choice_type_period):
    if choice_type_period == 'm':
        df = pd.read_sql(f"""
            SELECT * 
            FROM {table_name} 
            WHERE month_open = {int(choosen_month)}""", con=engine)
        df.timedelta = pd.to_timedelta(df.timedelta)
        return df

    elif choice_type_period == 'p':
        df = pd.read_sql(f"""
            SELECT * 
            FROM {table_name} 
            WHERE reg_date >= '{start_date_user} 00:00:00' 
                AND reg_date <='{end_date_user} 23:59:59'
        """, con=engine)
        df.timedelta = pd.to_timedelta(df.timedelta)
        return df
    else:
        df = pd.read_sql(f"""
            SELECT * 
            FROM {table_name} 
            WHERE week_open = {int(choosen_week)}
        """, con=engine)
        df.timedelta = pd.to_timedelta(df.timedelta)
        return df


def get_prev_filtered_df_db(table_name, start_date_user, end_date_user, choosen_month, choosen_week,
                            choice_type_period):
    if choice_type_period == 'm':
        if int(choosen_month) > 1:
            df = pd.read_sql(f"""
                SELECT * 
                FROM {table_name} 
                WHERE month_open = {int(choosen_month) - 1}
            """, con=engine)
            df.timedelta = pd.to_timedelta(df.timedelta)
            return df
        else:
            df = pd.read_sql(f"""
                SELECT * 
                FROM {table_name} 
                WHERE month_open = 12
            """, con=engine)
            df.timedelta = pd.to_timedelta(df.timedelta)
            return df

    elif choice_type_period == 'p':
        delta = dt.datetime.strptime(end_date_user, '%Y-%m-%d') - dt.datetime.strptime(start_date_user, '%Y-%m-%d')
        prev_start_date = dt.datetime.strftime((dt.datetime.strptime(start_date_user, '%Y-%m-%d') - delta), '%Y-%m-%d')
        prev_end_date = dt.datetime.strftime((dt.datetime.strptime(end_date_user, '%Y-%m-%d') - delta), '%Y-%m-%d')
        df = pd.read_sql(f"""
            SELECT * 
            FROM {table_name} 
            WHERE reg_date >= '{prev_start_date} 00:00:00' 
                AND reg_date <='{prev_end_date} 23:59:59'
        """, con=engine)
        df.timedelta = pd.to_timedelta(df.timedelta)
        return df

    else:
        if int(choosen_week) > 1:
            df = pd.read_sql(f"""
                SELECT * 
                FROM {table_name} 
                WHERE week_open = {int(choosen_week) - 1}
            """, con=engine)
            df.timedelta = pd.to_timedelta(df.timedelta)
            return df
        else:
            df = pd.read_sql(f"""
                SELECT * 
                FROM {table_name} 
                WHERE week_open = {52}
            """, con=engine)
            df.timedelta = pd.to_timedelta(df.timedelta)
            return df


def get_filtered_incidents_df_db(start_date_user, end_date_user, choosen_month, choosen_week, choice_type_period):
    if choice_type_period == 'm':
        df = pd.read_sql(f"""
            SELECT * 
            FROM sue_data 
            WHERE (status = 'Проблема' or status = 'Массовый инцидент') 
                AND month_open = {int(choosen_month)}
        """, con=engine)
        df.timedelta = pd.to_timedelta(df.timedelta)
        df.columns = ['Дата обращения', 'Тип', 'Номер', 'Описание', 'Плановое время', 'Фактическое время',
                      'Пользователь', 'timedelta', 'Отдел', 'Дата', 'finish_date', 'month_open',
                      'month_solved', 'week_open', 'week_solved', 'count_task']
        return df

    elif choice_type_period == 'p':
        delta = dt.datetime.strptime(end_date_user, '%Y-%m-%d') - dt.datetime.strptime(start_date_user, '%Y-%m-%d')
        prev_start_date = dt.datetime.strftime((dt.datetime.strptime(start_date_user, '%Y-%m-%d') - delta), '%Y-%m-%d')
        prev_end_date = dt.datetime.strftime((dt.datetime.strptime(end_date_user, '%Y-%m-%d') - delta), '%Y-%m-%d')
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
                AND week_open = {int(choosen_week)}
        """, con=engine)
        df.timedelta = pd.to_timedelta(df.timedelta)
        df.columns = ['Дата обращения', 'Тип', 'Номер', 'Описание', 'Плановое время', 'Фактическое время',
                      'Пользователь', 'timedelta', 'Отдел', 'Дата', 'finish_date', 'month_open', 'month_solved',
                      'week_open', 'week_solved', 'count_task']
        return df
