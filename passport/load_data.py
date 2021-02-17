import calendar
from datetime import date, timedelta

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
    df = pd.read_sql('''select * from etsp_data''', con=engine)
    # df = pd.read_excel('passport/assets/etsp.xlsx')
    df.timedelta = pd.to_timedelta(df.timedelta)

    return df


def load_sue_data():
    df = pd.read_sql('''select * from sue_data''', con=engine)
    # df = pd.read_excel('passport/assets/sue.xlsx')
    df.timedelta = pd.to_timedelta(df.timedelta)

    return df


def load_osp_data():
    df = pd.read_sql('''select * from osp_data''', con=engine)
    # df = pd.read_excel('passport/assets/osp.xlsx')
    df.timedelta = pd.to_timedelta(df.timedelta)

    return df


def top_user(df):
    top_user_df = df[(df.unit != '19. Отдел сопровождения пользователей') & (df.unit != 'ЦОКР') & (
            df.user != 'Кондрашова Ирина Сергеевна')]
    top_user_df = pd.DataFrame(top_user_df.groupby('user')['count_task'].sum().sort_values(ascending=False).head()
                               .reset_index()).rename(columns={'user': 'Пользователь', 'count_task': 'Обращения'})
    return top_user_df


def load_incident(df):
    incident_df = df[(df.status == 'Проблема') | (df.status == 'Массовый инцидент')]
    incident_df.columns = ['Дата обращения', 'Тип', 'Номер', 'Описание', 'Плановое время', 'Фактическое время',
                           'Пользователь', 'timedelta', 'Отдел', 'Дата', 'finish_date', 'month_open',
                           'month_solved', 'week_open', 'week_solved', 'count_task']
    return incident_df


def no_icidents():
    no_incidents_df = pd.DataFrame({'Дата': '-', 'Тип': 'Аварийных инциндентов нет', 'Номер': '-', 'Описание': '-',
                                    'Плановое время': '-', 'Фактическое время': '-', 'Пользователь': '-',
                                    'timedelta': '-', 'Отдел': '-', 'start_date': '-', 'finish_date': '-',
                                    'month_open': '-', 'month_solved': '-', 'week_open': '-',
                                    'week_solved': '-', 'count_task': '-'}, index=[0])

    return no_incidents_df


def get_time_data(df):
    delta_4h, delta_8h, delta_24h, delta_5d = timedelta(hours=4), timedelta(hours=8), timedelta(hours=24), \
                                              timedelta(days=5)

    time_dict = {'до 4-х часов': df[df['timedelta'] <= delta_4h].count_task.sum(),
                 'от 4-х до 8-ми часов': df[(df.timedelta <= delta_8h) & (df.timedelta > delta_4h)].count_task.sum(),
                 'от 8-ми до 24-х часов': df[(df.timedelta <= delta_24h) & (df.timedelta > delta_8h)].count_task.sum(),
                 'от 1-го до 5-ти дней': df[(df.timedelta <= delta_5d) & (df.timedelta > delta_24h)].count_task.sum(),
                 'свыше 5-ти дней': df[df.timedelta > delta_5d].count_task.sum()}
    df1 = pd.DataFrame.from_dict(time_dict, orient='index')

    list_mean_time = [df[df.timedelta <= delta_4h].timedelta.mean(),
                      df[(df.timedelta <= delta_8h) & (df.timedelta > delta_4h)].timedelta.mean(),
                      df[(df.timedelta <= delta_24h) & (df.timedelta > delta_8h)].timedelta.mean(),
                      df[(df.timedelta <= delta_5d) & (df.timedelta > delta_24h)].timedelta.mean(),
                      df[df.timedelta > delta_5d].timedelta.mean()]
    df1.reset_index(inplace=True)
    df1.rename(columns={'index': 'time_task', 0: 'count_task'}, inplace=True)

    df1['persent_task'] = 0
    df1['mean_time'] = 0
    for num in range(len(df1)):
        df1.loc[num, ['persent_task']] = df1.loc[num, ['count_task']].iloc[0] / df1['count_task'].sum()
        df1.loc[num, ['mean_time']] = list_mean_time[num]

    return df1


def get_time_periods(etsp_df, sue_df, osp_df):
    start_weeks_list = [etsp_df.reg_date.min().week, sue_df.reg_date.min().week, osp_df.reg_date.min().week]
    end_weeks_list = [etsp_df.reg_date.max().week, sue_df.reg_date.max().week, osp_df.reg_date.max().week]

    start_month_list = [etsp_df.reg_date.min().month, sue_df.reg_date.min().month, osp_df.reg_date.min().month]
    end_month_list = [etsp_df.reg_date.max().month, sue_df.reg_date.max().month, osp_df.reg_date.max().month]

    start_year_list = [etsp_df.reg_date.min().year, sue_df.reg_date.min().year, osp_df.reg_date.min().year]
    end_year_list = [etsp_df.reg_date.max().year, sue_df.reg_date.max().year, osp_df.reg_date.max().year]

    return dict(week=[min(start_weeks_list), max(end_weeks_list)], month=[min(start_month_list), max(end_month_list)],
                year=[min(start_year_list), max(end_year_list)])


def count_mean_time(filtered_df):
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
    df = pd.read_excel(r'passport/assets/dostup.xlsx', sheet_name='Лист5', index_col=0)
    df.drop('Номер отдела', axis=1, inplace=True)

    return df


def get_period(year, week, output_format='n'):
    """
    Синтаксис:
    get_period(
            year,
            week,
            output_format='n')

    Описание:
    Функция принимает на вход год и номер недели. Возвращает список или строку содержащие начальную и конечную
    даты недели

    Параметры
    ----------
    year:
        год
    week:
        номер недели
    output_format: string, default 'n'
        Определяет формат вывода данных. Допустимые значения:
        'n' - строка вида 'ДД-ММ-ГГГГ - ДД-ММ-ГГГГ'
        's' - список вида ['ГГГГ-ММ-ДД', 'ГГГГ-ММ-ДД']
        При указании другого параметра вернется список ['1900-01-01', '1900-01-01']

    Returns
    -------
    string or list of strings
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
    Функция принимает на вход год и номер месяца. Возвращает списко содержащий первую и последнюю даты месяца
    в виде строки формата 'ГГГГ-ММ-ДД'
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
    Функция принимает на вход период в виде 4-х параметров (номер недели и год начала, номер недели и год окончания.
    Возвращает список словарей содержащих информацию о номере недели, её периоде, и номере недели для последующей
    загрузки в компонент dcc.Dropdown.
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
    Функция принимает на вход номер месяца и год. Взоращает строку 'Месяц год'
    """
    months = ['', 'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь',
              'Ноябрь', 'Декабрь']
    period = ' '.join([str(months[month]), str(year)])

    return period


def get_months(start_month, start_year, finish_month, finish_year):
    """
    Функция принимает на вход период в виде 4-х параметров (номер месяца и год начала, номер месяца и год окончания.
    Возвращает список словарей содержащих информацию о месяце, годе и номере месяца для последующей загрузки в
    компонент dcc.Dropdown.
    """
    start_period = [{"label": f'{get_period_month(start_year, i)}', "value": i} for i in range(start_month, 13)]
    end_period = [{"label": f'{get_period_month(finish_year, i)}', "value": i} for i in range(1, finish_month + 1)]

    for item in end_period:
        start_period.append(item)
    start_period.reverse()

    return start_period


def load_projects():
    df = pd.read_sql("""select * from projects""", con=engine)
    # df = pd.read_excel('passport/assets/projects.xlsx')

    return df


def set_differences(diff):
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


def get_prev_filtered_df(df, start_date_user, choosen_month, choosen_week, choice_type_period):
    if choice_type_period == 'm':
        if int(choosen_month) > 1:
            return df[df['month_open'] == (int(choosen_month) - 1)]
        else:
            return df[df['month_open'] == 12]

    elif choice_type_period == 'p':
        if int(start_date_user[5:7]) > 1:
            return df[df['month_open'] == (int(start_date_user[5:7]) - 1)]
        else:
            return df[df['month_open'] == 12]

    else:
        if int(choosen_week) > 1:
            return df[df['week_open'] == (int(choosen_week) - 1)]
        else:
            return df[df['week_open'] == 52]


def choosen_type(choice_type_period, start_date_user, end_date_user, choosen_month, choosen_week):
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
    if choice_type_period == 'm':
        return df[df['month_open'] == int(choosen_month)]

    elif choice_type_period == 'p':
        return df[(df['start_date'] >= start_date_user) & (df['start_date'] <= end_date_user)]

    else:
        return df[df['week_open'] == int(choosen_week)]


def get_date_for_metrika_df(start_date_user, end_date_user, choosen_month, choosen_week, choice_type_period):
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


def get_filtered_incidents_df(df, start_date_user, end_date_user, choosen_month, choosen_week, choice_type_period):
    if choice_type_period == 'm':
        return df[df['month_open'] == int(choosen_month)]

    elif choice_type_period == 'p':
        return df[(df['Дата обращения'] >= start_date_user) & (df['Дата обращения'] <= end_date_user)]

    else:
        return df[df['week_open'] == int(choosen_week)]
