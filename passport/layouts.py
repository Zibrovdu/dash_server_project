import calendar
import datetime as dt

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_daq as daq
import dash_html_components as html
import dash_table
import pandas as pd

import passport.load_data as ld
from passport.figures import fig_total, colors_inf_system, inf_sys_heatmap


def serve_layout():
    curr_date = dt.date(ld.current_year, ld.current_month, ld.current_day)
    etsp_df = ld.load_etsp_data()

    etsp_top_user_df = ld.top_user(df=etsp_df)

    sue_df = ld.load_sue_data()
    sue_top_user_df = ld.top_user(df=sue_df)

    osp_df = ld.load_osp_data()
    sue_incidents_df = ld.load_incident(df=sue_df)

    periods = ld.get_time_periods(first_df=etsp_df,
                                  second_df=sue_df,
                                  third_df=osp_df)

    start_week, start_month, start_year = periods['week'][0], periods['month'][0], periods['year'][0]
    finish_week, finish_month, finish_year = periods['week'][1], periods['month'][1], periods['year'][1]

    tab_selected_style = dict(backgroundColor='#ebecf1',
                              fontWeight='bold')

    choice_type = [dict(label='Неделя', value='w'),
                   dict(label='Месяц', value='m'),
                   dict(label='Произвольный период', value='p')]

    d_month = ld.get_months(start_month=start_month,
                            start_year=start_year,
                            finish_month=finish_month,
                            finish_year=finish_year)

    d_week = ld.get_weeks(start_week=start_week,
                          start_year=start_year,
                          finish_week=finish_week,
                          finish_year=finish_year)

    tooltips_table_site = [{'Визиты': 'Суммарное количество визитов.',
                            'Посетители': 'Количество уникальных посетителей.',
                            'Просмотры': 'Число просмотров страниц на сайте за выбранный период.',
                            'Отказы': 'Доля визитов, в рамках которых состоялся лишь один просмотр страницы, '
                                      'продолжавшийся менее 15 секунд.',
                            'Глубина просмотра': 'Количество страниц, просмотренных посетителем во время визита.',
                            'Время на сайте': 'Средняя продолжительность визита в минутах и секундах.'}]

    projects_df = ld.load_projects(projects_status='in_progress',
                                   project_name='all')
    projects_df['id'] = pd.Series([x for x in range(1, len(projects_df) + 1)])
    projects_df = projects_df[['id', 'name', 'executor', 'persent', 'stage', 'plan_date']]
    projects_df.columns = ['Номер', 'Название', 'Исполнитель', 'Процент выполнения', 'Описание', 'Срок исполнения']

    modify_projects_dcc = [{'label': i, 'value': i} for i in projects_df['Название']]

    complete_projects_df = ld.load_projects(projects_status='complete',
                                            project_name='all')
    complete_projects_df['id'] = pd.Series([x for x in range(1, len(complete_projects_df) + 1)])
    complete_projects_df = complete_projects_df[['id', 'name', 'executor', 'persent', 'stage', 'fact_date', 'duration']]
    complete_projects_df.columns = ['Номер', 'Название', 'Исполнитель', 'Процент выполнения', 'Описание',
                                    'Дата выполнения', 'Длительность']

    osp_staff_projects = ld.get_osp_names_projects()

    inf_systems_df = ld.load_inf_sys_data(conn_string=ld.engine)
    unit_names = [{'label': i, 'value': i} for i in inf_systems_df.index]

    colors = ['aggrnyl', 'agsunset', 'algae', 'amp', 'armyrose', 'balance', 'blackbody', 'bluered', 'blues', 'blugrn',
              'bluyl', 'brbg', 'brwnyl', 'bugn', 'bupu', 'burg', 'burgyl', 'cividis', 'curl', 'darkmint', 'deep',
              'delta', 'dense', 'earth', 'edge', 'electric', 'emrld', 'fall', 'geyser', 'gnbu', 'gray', 'greens',
              'greys', 'haline', 'hot', 'hsv', 'ice', 'icefire', 'inferno', 'jet', 'magenta', 'magma', 'matter', 'mint',
              'mrybm', 'mygbm', 'oranges', 'orrd', 'oryel', 'oxy', 'peach', 'phase', 'picnic', 'pinkyl',
              'piyg', 'plasma', 'plotly3', 'portland', 'prgn', 'pubu', 'pubugn',
              'puor', 'purd', 'purp', 'purples', 'purpor', 'rainbow', 'rdbu',
              'rdgy', 'rdpu', 'rdylbu', 'rdylgn', 'redor', 'reds', 'solar',
              'spectral', 'speed', 'sunset', 'sunsetdark', 'teal', 'tealgrn',
              'tealrose', 'tempo', 'temps', 'thermal', 'tropic', 'turbid',
              'turbo', 'twilight', 'viridis', 'ylgn', 'ylgnbu', 'ylorbr',
              'ylorrd']

    colors_dcc = [{'label': i, 'value': i} for i in colors]

    layout = html.Div([
        dcc.Location(id='url',
                     refresh=True),  # Обновление после нажатия кнопки сохранить и закрыть (редактирование)
        dcc.Location(id='url_1',
                     refresh=True),  # Обновление после нажатия кнопки сохранить и закрыть (создание)
        html.Div([
            html.H2('Отдел сопровождения пользователей'),
            # html.Img(src="assets/logo.png")
            html.A([
                html.Img(src="assets/logo.png")
            ], href='#modal-1', className='js-modal-open link')
        ], className="banner"),
        html.Div([
            html.Div([
                html.Div([html.Div([html.Label("Выберите период: ")],
                                   className='wrapper-dropdown-4')],
                         className='bblock'),
                html.Div([html.Div([dcc.Dropdown(id='choice_type',
                                                 options=choice_type,
                                                 searchable=False,
                                                 clearable=False,
                                                 optionHeight=50,
                                                 value='w',
                                                 disabled=False)
                                    ],
                                   className='wrapper-dropdown-3',
                                   style=dict(width='295px',
                                              display='block'))],
                         className='bblock'),  # choice period dropdown
                html.Div([html.Div([dcc.Dropdown(id='month_choice',
                                                 options=d_month,
                                                 searchable=False,
                                                 clearable=False,
                                                 value=finish_month,
                                                 disabled=False
                                                 )],
                                   className='wrapper-dropdown-3',
                                   style=dict(width='190px'))],
                         className='bblock'), ]),  # Month_choice dropdown
            html.Div([html.Div([dcc.Dropdown(id='week_choice',
                                             options=d_week,
                                             searchable=False,
                                             clearable=False,
                                             value=finish_week,
                                             style=dict(width='100%',
                                                        heigth='60px'),
                                             disabled=False
                                             )],
                               className='wrapper-dropdown-3',
                               style=dict(width='420px'))],
                     className='bblock'),  # Week_choice dropdown
            html.Div([html.Div([dcc.DatePickerRange(id='period_choice',
                                                    display_format='DD-MM-YYYY',
                                                    min_date_allowed=dt.date(start_year, start_month, 1),
                                                    max_date_allowed=dt.date(finish_year, finish_month,
                                                                             calendar.monthrange(finish_year,
                                                                                                 finish_month)[1]),
                                                    start_date=dt.date(ld.end_year, ld.end_month, ld.end_day),
                                                    end_date=dt.date(ld.current_year, ld.current_month, ld.current_day),
                                                    updatemode='bothdates',
                                                    style=dict(background='#b1d5fa'),
                                                    clearable=False
                                                    )])], className='bblock',
                     style=dict(heigth='45px')),  # Period_choice range picker
        ], style=dict(background='#b1d5fa')),
        html.Div([
            html.Div([
                dcc.Tabs(id='choice_period',
                         value='weeks',
                         children=[
                             dcc.Tab(label='Работа с пользователями',
                                     value='weeks',
                                     children=[
                                         html.Div([
                                             html.Div([html.Table([
                                                 html.Tr([
                                                     html.Td([html.Label('Количество обращений'), ]),
                                                     html.Td(html.Label('Количество пользователей')),
                                                     html.Td('Среднее время решения',
                                                             colSpan=3)
                                                 ]),
                                                 html.Tr([
                                                     html.Td(id='tasks',
                                                             rowSpan=2,
                                                             style=dict(fontSize='2em')),
                                                     html.Td(id='users',
                                                             rowSpan=2,
                                                             style=dict(fontSize='2.2em')),
                                                     html.Td('ЕЦП'),
                                                     html.Td('СУЭ'),
                                                     html.Td('ОСП')
                                                 ]),
                                                 html.Tr([
                                                     html.Td(id='etsp-time'),
                                                     html.Td(id='sue-time'),
                                                     html.Td(id='osp-time')
                                                 ]),
                                             ])],
                                                 className='line_block',
                                                 style=dict(width='60%')),  # table_1
                                             html.Div([html.Label('Аварийные инциденты'),
                                                       dash_table.DataTable(id='sue_avaria',
                                                                            columns=[{"name": i, "id": i} for i in
                                                                                     sue_incidents_df.columns
                                                                                     if i == 'Тип'
                                                                                     or i == 'Номер'
                                                                                     or i == 'Описание '
                                                                                     or i == 'Дата'],
                                                                            # sort_action="native",
                                                                            style_table=dict(height='150px',
                                                                                             overflowY='auto'),
                                                                            # fixed_rows=dict(headers=True),
                                                                            style_as_list_view=True,
                                                                            cell_selectable=False,
                                                                            style_data=dict(width='20%'),
                                                                            css=[
                                                                                {'selector': '.dash-spreadsheet td div',
                                                                                 'rule': '''
                                                                line-height: 10px;
                                                                max-height: 20px; min-height: 20px; height: 20px;
                                                                display: block;
                                                                overflow-y: hidden;
                                                           '''}],
                                                                            tooltip_data=[{
                                                                                column: {'value': str(value),
                                                                                         'type': 'markdown'}
                                                                                for column, value in row.items()
                                                                            } for row in
                                                                                sue_incidents_df.to_dict('records')],
                                                                            tooltip_duration=None,
                                                                            style_cell=dict(textAlign='center',
                                                                                            overflow='hidden',
                                                                                            textOverflow='ellipsis',
                                                                                            maxWidth=0))],
                                                      className='line_block',
                                                      style=dict(width='32%')),
                                         ]),
                                         html.Hr(),
                                         html.Div([
                                             html.Div([dcc.Graph(id='users_figure')],
                                                      className='line_block',
                                                      style=dict(width='46%')),
                                             html.Div([dcc.Graph(id='support_figure')],
                                                      className='line_block',
                                                      style=dict(width='46%')),
                                         ]),
                                         html.Br(),
                                         html.Div([html.H3('ТОП-5 пользователей')],
                                                  className='div_top_user'),
                                         html.Div([
                                             html.Div([html.H4('ЕЦП')],
                                                      className='line_block',
                                                      style=dict(width='46%')),
                                             html.Div([html.H4('СУЭ')],
                                                      className='line_block',
                                                      style=dict(width='46%')),
                                         ]),
                                         html.Div([
                                             html.Div([
                                                 dash_table.DataTable(id='table_top_etsp',
                                                                      columns=[dict(name=i, id=i) for i in
                                                                               etsp_top_user_df.columns],
                                                                      sort_action="native",
                                                                      style_as_list_view=True,
                                                                      cell_selectable=False,
                                                                      style_data=dict(width='50px',
                                                                                      fontSize=' 1.3em'),
                                                                      style_cell=dict(textAlign='center'),
                                                                      style_cell_conditional=[
                                                                          {'if': {'column_id': 'Пользователь'},
                                                                           'textAlign': 'left'}]
                                                                      )
                                             ],
                                                 className='line_block',
                                                 style=dict(width='46%')),
                                             html.Div([
                                                 dash_table.DataTable(id='table_top_sue',
                                                                      columns=[dict(name=i, id=i) for i in
                                                                               sue_top_user_df.columns],
                                                                      sort_action="native",
                                                                      style_as_list_view=True,
                                                                      cell_selectable=False,
                                                                      style_data={'width': '50px',
                                                                                  'font-size': ' 1.3em'},
                                                                      style_cell=dict(textAlign='center'),
                                                                      style_cell_conditional=[
                                                                          {'if': {'column_id': 'Пользователь'},
                                                                           'textAlign': 'left'}]
                                                                      )
                                             ],
                                                 className='line_block',
                                                 style=dict(width='46%')),
                                         ]),
                                     ],
                                     selected_style=tab_selected_style),  # tab user
                             dcc.Tab(label='Информационные системы',
                                     value='months',
                                     children=[
                                         html.Br(),
                                         html.Div([
                                             html.Table([
                                                 html.Tr([
                                                     html.Td([html.Label(
                                                         'Подключено сотрудников МБУ ФК к ГИИС "Электронный бюджет"')]),
                                                 ]),
                                                 html.Tr([
                                                     html.Td([daq.LEDDisplay(id='total_tasks',
                                                                             value=ld.count_employees(
                                                                                 conn_string=ld.engine),
                                                                             color='#222780',
                                                                             backgroundColor='#e8edff', )
                                                              ], rowSpan=2),
                                                 ]),
                                             ], className='table_budget'),
                                         ], className='div_table_budget'),
                                         html.Div([
                                             html.Br(),
                                             html.Br(),
                                             dcc.Link('Полномочия и роли',
                                                      href='http://37.110.79.49:9060/', # ПОМЕНЯТЬ АДРЕС
                                                      target='blank',
                                                      className='link_bounds')
                                         ], className='div_bounds'),
                                         html.Br(),
                                         html.Br(),
                                         html.Div([
                                             html.H3('Количество доступов к подсистемам в разрезе отдела'),
                                             html.Br(),
                                             html.Br(),
                                             dcc.Dropdown(id='unit_choose_inf_sys',
                                                          options=unit_names,
                                                          value=unit_names[0]['value'],
                                                          className="dropdown_choose_unit_inf_sys"),
                                             dcc.Graph(id='fig_unit_inf_sys'),
                                             html.H3('Общее количество доступов к подсистемам в разрезе подсистем'),
                                             dcc.Graph(id='total',
                                                       figure=fig_total(df=inf_systems_df,
                                                                        colors=colors_inf_system)),
                                             html.H3('Тепловая карта доступов к подсистемам в разрезе отделов'),
                                             html.Br(),
                                             html.Br(),
                                             dcc.Dropdown(id='heatmap_colorscales',
                                                          options=colors_dcc,
                                                          value=colors_dcc[0]['value'],
                                                          style=dict(width='40%', padding='0 20px')),

                                             daq.BooleanSwitch(id='reverse_colorscales',
                                                               label='Invert colors',
                                                               on=False,
                                                               style=dict(width='15%')),
                                             dcc.Graph(id='3')
                                         ], style=dict(background='#ebecf1'))
                                     ],
                                     selected_style=tab_selected_style),  # tab tech
                             dcc.Tab(label='Сайт',
                                     value='s',
                                     children=[
                                         html.Br(),
                                         html.Div([dash_table.DataTable(id='site_stat',
                                                                        columns=[{"name": i, "id": i} for i in
                                                                                 ['Визиты', 'Посетители',
                                                                                  'Просмотры', 'Отказы',
                                                                                  'Глубина просмотра',
                                                                                  'Время на сайте']],
                                                                        style_table={'height': '150px'},
                                                                        style_as_list_view=True,
                                                                        cell_selectable=False,
                                                                        tooltip_data=tooltips_table_site,
                                                                        tooltip_duration=None,
                                                                        style_cell=dict(textAlign='center',
                                                                                        overflow='hidden',
                                                                                        textOverflow='ellipsis',
                                                                                        maxWidth=0))],
                                                  className='div_site_stat'),
                                         html.Div([html.H3('Рейтинг посещаемости разделов сайта',
                                                           style=dict(padding='20px'))]),
                                         html.Div([dcc.Graph(id='site_top_fig')],
                                                  className='line-block',
                                                  style=dict(width='93%')),
                                         html.Div([dcc.Graph(id='site_line_graph')],
                                                  className='line-block',
                                                  style=dict(width='93%')),
                                         html.Div([
                                             html.Div([dcc.Graph(id='el_budget_graph_mean_time')],
                                                      className='line_block',
                                                      style=dict(width='46%')),
                                             html.Div([dcc.Graph(id='el_budget_graph')],
                                                      className='line_block',
                                                      style=dict(width='46%')),
                                             html.Div([dcc.Graph(id='gossluzba_pagedept')],
                                                      className='line_block',
                                                      style=dict(width='46%')),
                                             html.Div([dcc.Graph(id='gossluzba_visits')],
                                                      className='line_block',
                                                      style=dict(width='46%'))
                                         ]),
                                     ],
                                     selected_style=tab_selected_style),  # tab site
                             dcc.Tab(label='Задачи / проекты',
                                     value='pr',
                                     children=[
                                         html.Br(),
                                         html.Div([
                                             html.Div([
                                                 html.Button('Создать новую задачу / проект',
                                                             id="open-scroll",
                                                             className='add_mod_btn'),
                                             ], className='add_mod_div'),

                                             dbc.Modal(
                                                 [dbc.ModalHeader(
                                                     "Добавление нового проекта (все поля обязательны к заполнению)"),
                                                     dbc.ModalBody(
                                                         html.Div([
                                                             html.Span(id="example-output",
                                                                       style=dict(color="#ebecf1"),
                                                                       hidden=True),
                                                             html.H5('Название задачи / проекта: '),
                                                             dcc.Input(id="input_pr",
                                                                       placeholder="Введите название задачи / "
                                                                                   "проекта...",
                                                                       type="text",
                                                                       required=True,
                                                                       minLength=5,
                                                                       style=dict(width='100%')),
                                                             html.Br(),
                                                             html.Span(id="fill_project_name",
                                                                       style=dict(color="#ebecf1"),
                                                                       hidden=True),
                                                             html.Br(),
                                                             html.H5('Исполнители:'),
                                                             dcc.Dropdown(id='input_user',
                                                                          style=dict(width='100%'),
                                                                          options=osp_staff_projects,
                                                                          multi=True,
                                                                          ),
                                                             html.Span(id='fill_project_user',
                                                                       style=dict(color="#ebecf1"),
                                                                       hidden=True),
                                                             html.Br(),
                                                             html.H5('Процент выполнения:'),
                                                             dcc.Input(id="input_pers",
                                                                       placeholder="Укажите процент выполнения "
                                                                                   "задачи...",
                                                                       type="number",
                                                                       required=True,
                                                                       value=0,
                                                                       style=dict(width='100%')),
                                                             html.Span(id='fill_project_persent',
                                                                       style=dict(color="#ebecf1"),
                                                                       hidden=True),
                                                             html.Br(),
                                                             html.H5('Описание задачи / проекта:'),
                                                             dcc.Textarea(id="input_descr",
                                                                          placeholder="Введите описание задачи / "
                                                                                      "проекта...",
                                                                          required=True,
                                                                          minLength=10,
                                                                          style=dict(width='100%')),
                                                             html.Span(id='fill_project_descr',
                                                                       style=dict(color="#ebecf1"),
                                                                       hidden=True),
                                                             html.Br(),
                                                             html.H5('Плановая дата выполнения:'),
                                                             dcc.DatePickerSingle(id='date_pr',
                                                                                  min_date_allowed=dt.date.today(),
                                                                                  display_format='DD-MM-YYYY',
                                                                                  style=dict(float='left')),
                                                             html.Span(id='fill_project_end_date',
                                                                       style=dict(color="#ebecf1")),
                                                             html.Div([], style=dict(width='50%')),
                                                             html.Div([
                                                                 html.Button("Очистить",
                                                                             id='clear',
                                                                             className='clear_btn'),
                                                                 html.Button("Сохранить",
                                                                             id='save_btn',
                                                                             className='confirm_btn'),
                                                             ], style=dict(float='right',
                                                                           position='relative',
                                                                           margin='0 auto')),
                                                         ]),
                                                     ),
                                                     dbc.ModalFooter(
                                                         html.Button("Закрыть",
                                                                     id="close-scroll",
                                                                     className="button")
                                                     )],
                                                 id="modal-scroll",
                                                 backdrop='static',
                                                 size="xl",
                                             ),
                                             html.Div([
                                                 html.Button('Изменить задачу / проект',
                                                             id='open_modify_win',
                                                             className='add_mod_btn'),
                                             ], className='add_mod_div'),
                                             dbc.Modal(
                                                 [dbc.ModalHeader("Редактирование задачи / проекта"),
                                                  dbc.ModalBody(
                                                      html.Div([
                                                          html.Span(id="example-output_modify",
                                                                    hidden=True,
                                                                    style={"color": "#ebecf1"}),
                                                          html.H5('Выберите задачу / проект для редактирования'),
                                                          dcc.Dropdown(id='choose_project_mod',
                                                                       style=dict(width='100%'),
                                                                       value=None,
                                                                       options=modify_projects_dcc,
                                                                       ),
                                                          html.Br(),
                                                          html.Br(),
                                                          html.H5('Исполнители:'),
                                                          dcc.Dropdown(id='input_user_modify',
                                                                       style=dict(width='100%'),
                                                                       options=osp_staff_projects,
                                                                       multi=True,
                                                                       ),
                                                          html.Span(id='mod_project_user',
                                                                    style=dict(color='white')),
                                                          html.Br(),
                                                          html.H5('Процент выполнения:'),
                                                          dcc.Input(id="input_pers_modify",
                                                                    placeholder="Укажите процент выполнения задачи...",
                                                                    type="number",
                                                                    required=True,
                                                                    style=dict(width='100%')),
                                                          html.Span(id='mod_project_persent',
                                                                    style=dict(color='white')),
                                                          html.Br(),
                                                          html.Br(),
                                                          html.Div([
                                                              daq.BooleanSwitch(
                                                                  id='complete_project_switch',
                                                                  label='Задача выполнена',
                                                                  labelPosition='right',
                                                                  on=False
                                                              )
                                                          ], style=dict(width='20%')),
                                                          html.Br(),
                                                          html.H5('Описание:'),
                                                          dcc.Textarea(id="input_descr_modify",
                                                                       placeholder="Введите описание проекта...",
                                                                       required=True,
                                                                       style=dict(width='100%')),
                                                          html.Span(id='mod_project_descr',
                                                                    style=dict(color='white')),
                                                          html.Br(),
                                                          html.H5('Плановая дата выполнения:'),
                                                          dcc.DatePickerSingle(id='date_pr_modify',
                                                                               min_date_allowed=dt.date.today(),
                                                                               display_format='DD-MM-YYYY',
                                                                               style=dict(float='left')),
                                                          html.Span(id='modify_project_end_date',
                                                                    style=dict(color='white')),
                                                          html.Br(),
                                                          html.Br(),
                                                          html.H5('Фактическая дата выполнения:'),
                                                          dcc.DatePickerSingle(id='fact_date_pr_modify',
                                                                               display_format='DD-MM-YYYY',
                                                                               disabled=True,
                                                                               style=dict(float='left')),
                                                          html.Span(id='modify_project_fact_date',
                                                                    style=dict(color='white')),
                                                          html.Div([], style=dict(width='50%')),
                                                          html.Div(id='mod_project_name',
                                                                   style=dict(textAlign='center',
                                                                              color='green')),
                                                          html.Div([
                                                              html.Button("Сохранить",
                                                                          id='btn_save_modify',
                                                                          className='confirm_btn'),
                                                          ], className='div_btn_save_modify'),
                                                          html.Br(),
                                                          html.Div([
                                                          ], style=dict(float='left',
                                                                        position='relative',
                                                                        padding='20 0 0 0'))
                                                      ]),
                                                  ),
                                                  dbc.ModalFooter(
                                                      html.Div([
                                                          html.Button("Закрыть",
                                                                      id="btn_close_modify",
                                                                      className="button"),
                                                      ])
                                                  ),
                                                  ],
                                                 id="modify_window",
                                                 backdrop='static',
                                                 size='xl'
                                             )
                                         ], style=dict(width='98%',
                                                       margin='0 auto')),
                                         html.Br(),
                                         html.Div([
                                             html.H3('Задачи / проекты в работе',
                                                     className='H3_work_projects')
                                         ]),
                                         html.Div([
                                             dash_table.DataTable(id='project_table',
                                                                  columns=[{"name": i, "id": i} for i in
                                                                           projects_df.columns],
                                                                  data=projects_df.to_dict('records'),
                                                                  style_as_list_view=True,
                                                                  cell_selectable=False,
                                                                  filter_action="native",
                                                                  sort_action='native',
                                                                  style_table=dict(overflowX='auto'),
                                                                  style_data=dict(whiteSpace='normal',
                                                                                  height='auto',
                                                                                  background='#F5F5DC'),
                                                                  style_cell=dict(textAlign='left'),
                                                                  style_header=dict(
                                                                      backgroundColor='rgb(230, 230, 230)',
                                                                      fontWeight='bold'),
                                                                  style_cell_conditional=[
                                                                      {'if': {'column_id': 'Срок исполнения'},
                                                                       'textAlign': 'center'},
                                                                      {'if': {'column_id': 'Процент выполнения'},
                                                                       'textAlign': 'center'},
                                                                      {'if': {'column_id': 'Исполнитель'},
                                                                       'textAlign': 'center', 'width': '8%'},
                                                                      {'if': {'column_id': 'Название'},
                                                                       'width': '30%'},
                                                                      {'if': {'column_id': 'Процент выполнения'},
                                                                       'width': '8%'},
                                                                      {'if': {'column_id': 'Срок исполнения'},
                                                                       'width': '7%'},
                                                                      {'if': {'column_id': 'Номер'},
                                                                       'width': '3%'}
                                                                  ],
                                                                  style_data_conditional=[
                                                                      {'if': {'filter_query': f'{{Процент '
                                                                                              f'выполнения}} = {0}', },
                                                                       'backgroundColor': '#BFB9CF'
                                                                       },
                                                                      {'if': {'filter_query': f'{{Срок исполнения}} < '
                                                                                              f'{curr_date}'},
                                                                       'backgroundColor': '#f5a3b7'}],
                                                                  export_format='xlsx',
                                                                  editable=True,
                                                                  )
                                         ], className='div_project_tables'),
                                         html.Br(),
                                         html.Div([
                                             html.H3('Выполненные задачи / проекты',
                                                     className='H3_complete_projects')
                                         ]),
                                         html.Div([
                                             dash_table.DataTable(id='completed_projects',
                                                                  columns=[{"name": i, "id": i} for i in
                                                                           complete_projects_df.columns],
                                                                  data=complete_projects_df.to_dict('records'),
                                                                  style_as_list_view=True,
                                                                  cell_selectable=False,
                                                                  style_table=dict(overflowX='auto'),
                                                                  style_data=dict(whiteSpace='normal',
                                                                                  height='auto',
                                                                                  background='#c4fbdb'),
                                                                  style_cell=dict(textAlign='left'),
                                                                  style_header=dict(
                                                                      backgroundColor='rgb(230, 230, 230)',
                                                                      fontWeight='bold'),
                                                                  style_cell_conditional=[
                                                                      {'if': {'column_id': 'Процент выполнения'},
                                                                       'textAlign': 'center'},
                                                                      {'if': {'column_id': 'Исполнитель'},
                                                                       'textAlign': 'center', 'width': '8%'},
                                                                      {'if': {'column_id': 'Название'},
                                                                       'width': '30%'},
                                                                      {'if': {'column_id': 'Дата выполнения'},
                                                                       'textAlign': 'center'},
                                                                      {'if': {'column_id': 'Длительность'},
                                                                       'textAlign': 'center'}],
                                                                  export_format='xlsx'
                                                                  )
                                         ], className='div_project_tables'),
                                         html.Br(),
                                     ],
                                     selected_style=tab_selected_style),  # tab projects
                         ],
                         colors=dict(border='#ebecf1',
                                     primary='#222780',
                                     background='#33ccff')
                         ),  # main tabs end
                html.Div(id='tabs_content')
            ])  # html.div 2
        ], style=dict(background='#ebecf1')),  # html.div 1
        html.Div([
            html.Div([
                html.Div([
                    html.Div([
                        'История изменений'
                    ], className='modal__dialog-header-content'),
                    html.Div([
                        html.Button([
                            html.Span('x')
                        ], className='js-modal-close modal__dialog-header-close-btn')
                    ], className='modal__dialog-header-close')
                ], className='modal__dialog-header'),
                html.Div([
                    html.Br(),
                    html.Div([
                        dcc.Textarea(value=ld.read_history_data(), readOnly=True, className='frame-history')
                    ]),
                    html.Br(),
                ], className='modal__dialog-body'),
                html.Div([
                    html.Button('Close', className='js-modal-close modal__dialog-footer-close-btn')
                ], className='modal__dialog-footer')
            ], className='modal__dialog')
        ], id='modal-1', className='modal_history modal--l'),
        html.Script(src='assets/js/main.js'),
    ])  # app layout end
    return layout
