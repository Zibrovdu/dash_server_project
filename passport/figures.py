import datetime as dt

import plotly.graph_objects as go

colors_inf_system = ['#5d61a2', '#93cdd1', '#a7d0b8', '#dcdcd7', '#d598a0', '#760043', '#c4b052', '#bb4e51', '#c26ca9',
          '#0b7fab', '#f4d75e', '#e9723d']

def plot_figure_support(first_tp_count_tasks, second_tp_count_tasks, third_tp_count_tasks):
    """
    Синтаксис:
    ----------
    **plot_figure_support** (first_tp_count_tasks, second_tp_count_tasks, third_tp_count_tasks)

    Описание:
    ---------
    Функция отвечает за построение графика (гистограмма) отображающего суммарное количество обращений по каждой из трех
    техподдержек (ЕЦП, СУЭ ФК, ОСП) за выбранный период времени

    Параметры:
    ----------
        **first_tp_count_tasks**: *DataFrame* - количество задач по техподдержке ЕЦП

        **second_tp_count_tasks**: *DataFrame* - количество задач по техподдержки СУЭ ФК

        **third_tp_count_tasks**: *DataFrame* - количество задач по техподдержки ОСП

    Returns:
    ----------
        **Figure**
    """
    fig_support = go.Figure(go.Bar(y=[first_tp_count_tasks, second_tp_count_tasks, third_tp_count_tasks],
                                   x=['ЕЦП', 'СУЭ ФК', 'ОСП'],
                                   base=0,
                                   marker=dict(color=['#a92b2b', '#37a17c', '#a2d5f2']),
                                   text=[first_tp_count_tasks, second_tp_count_tasks, third_tp_count_tasks],
                                   textposition='auto'))
    fig_support.update_layout(autosize=True,
                              legend=dict(orientation="h",
                                          yanchor="bottom",
                                          y=0.2,
                                          xanchor="right",
                                          x=0.5),
                              paper_bgcolor='#ebecf1',
                              plot_bgcolor='#ebecf1'
                              )
    fig_support.update_xaxes(ticks="inside",
                             tickson="boundaries")

    return fig_support


def plot_support_pie_figure(first_filtered_df, second_filtered_df, third_filtered_df):
    """
    Синтаксис:
    ----------
    **plot_support_pie_figure** (first_filtered_df, second_filtered_df, third_filtered_df)

    Описание:
    ---------
    Функция отвечает за построение графика (круговая диаграмма) отображающего процентное соотношение количества
    обращений по каждой из трех техподдержек (ЕЦП, СУЭ ФК, ОСП) за выбранный период времени

    Параметры:
    ----------
        **first_filtered_df**: *DataFrame* - датафрейм содержащий информацию об обращениях в техподдержку ЕЦП

        **second_filtered_df**: *DataFrame* - датафрейм содержащий информацию об обращениях в техподдержку СУЭ ФК

        **third_filtered_df**: *DataFrame* - датафрейм содержащий информацию об обращениях в техподдержку ОСП

    Returns:
    ----------
        **Figure**
    """
    support_pie_figure_labels = ["ЕЦП", "СУЭ ФК", "ОСП"]
    support_pie_figure_values = [first_filtered_df['count_task'].sum(), second_filtered_df['count_task'].sum(),
                                 third_filtered_df['count_task'].sum()]
    support_pie_figure_colors = ['#a92b2b', '#37a17c', '#a2d5f2']

    support_pie_figure = go.Figure(
        go.Pie(labels=support_pie_figure_labels,
               values=support_pie_figure_values,
               marker_colors=support_pie_figure_colors))

    support_pie_figure.update_traces(hoverinfo="label+percent")

    support_pie_figure.update_layout(paper_bgcolor='#ebecf1',
                                     showlegend=True)

    return support_pie_figure


def plot_fig_site_top(df):
    """
    Синтаксис:
    ----------
    **plot_fig_site_top** (df)

    Описание:
    ---------
    Функция отвечает за построение графика (гистограмма) отображающего суммарное количество визитов по разделам сайта
    за выбранный период времени

    Параметры:
    ----------
        **df**: *DataFrame* - датафрейм содержащий информацию о визитах, полученная из Яндекс.Метрики

    Returns:
    ----------
        **Figure**
    """
    site_top_figure_colors = ['#003b32', '#40817a', '#afbaa3', '#d0d0b8', '#037c87', '#7cbdc9']
    fig_site_top = go.Figure([go.Bar(y=df['visits'],
                                     x=df['level2'],
                                     orientation='v',
                                     marker_color=site_top_figure_colors,
                                     text=df['visits'])])
    fig_site_top.update_traces(textposition='auto')
    fig_site_top.update_layout(title_text="Визиты",
                               paper_bgcolor='#ebecf1',
                               plot_bgcolor='#ebecf1')

    return fig_site_top


def plot_site_line_graph(df):
    """
    Синтаксис:
    ----------
    **plot_site_line_graph** (df)

    Описание:
    ---------
    Функция отвечает за построение графика (линейные графики) отображающего суммарное количество визитов, просмотров
    и уникальных пользователей по сайту в целом

    Параметры:
    ----------
        **df**: *DataFrame* - датафрейм содержащий информацию о визитах, полученная из Яндекс.Метрики

    Returns:
    ----------
        **Figure**
    """
    site_line_graph = go.Figure(data=[
        go.Scatter(y=list(df.groupby(['date'])['visits'].sum()),
                   x=list(df.groupby(['date'])['visits'].sum().index),
                   mode='lines+markers',
                   marker=dict(color='#5d4b63',
                               size=6),
                   line=dict(color='#5d4b63',
                             width=5),
                   name='Визиты'),
        go.Scatter(y=list(df.groupby(['date'])['users'].sum()),
                   x=list(df.groupby(['date'])['users'].sum().index),
                   mode='lines+markers',
                   marker=dict(color='#d74d63',
                               size=6),
                   line=dict(color='#d74d63',
                             width=5),
                   name='Пользователи'),
        go.Scatter(y=list(df.groupby(['date'])['pageviews'].sum()),
                   x=list(df.groupby(['date'])['pageviews'].sum().index),
                   mode='lines+markers',
                   marker=dict(color='#a38182',
                               size=6),
                   line=dict(color='#a38182',
                             width=5),
                   name='Просмотры страниц')
    ])
    site_line_graph.update_layout(title_text="Посещение сайта",
                                  paper_bgcolor='#ebecf1',
                                  plot_bgcolor='#ebecf1')

    return site_line_graph


def fig_inf_systems(inf_systems_data, legend_sw):
    """
       Синтаксис:
       ----------
       **fig_inf_systems** (inf_systems_data, legend_sw)

       Описание:
       ---------
       Функция отвечает за построение графика (горизонтальная гистограмма) отображающего количество пользователей
       имеющих права доступа в информационные системы в разрезе информационных систем

       Параметры:
       ----------
           **inf_systems_data**: *DataFrame* - датафрейм содержащий информацию о доступах в информационные системы

           **legend_sw**: *Bool* - параметр, который включает/выключает отображение легенды. Возможные значения:

                **True** - отображение легенды включено

                **False** - отображение легенды выключено

       Returns:
       ----------
           **Figure**
       """
    fig_inf_sys = go.Figure()
    for num in range(len(inf_systems_data)):
        fig_inf_sys.add_trace(go.Bar(y=inf_systems_data.columns,
                                     x=inf_systems_data.iloc[num],
                                     name=inf_systems_data.index[num],
                                     orientation='h',
                                     text=inf_systems_data.iloc[num],
                                     textposition='inside'))
        fig_inf_sys.update_layout(barmode='stack',
                                  height=1000,
                                  legend_xanchor='right',
                                  paper_bgcolor='#ebecf1',
                                  plot_bgcolor='#ebecf1',
                                  showlegend=legend_sw)
        fig_inf_sys.update_yaxes(tickmode="linear")

    return fig_inf_sys


def plot_el_budget_graph(df, names_el_budget):
    """
    Синтаксис:
    ----------
    **plot_el_budget_graph** (df, names_el_budget)

    Описание:
    ---------
    Функция отвечает за построение графика (гистограмма) отображающего среднюю глубину просмотра каждого подраздела
    в разделе сайта "Электронный бюджет"

    Параметры:
    ----------
        **df**: *DataFrame* - датафрейм содержащий информацию о глубине просмотра раздела сайта "Электронный бюджет",
        полученную из Яндекс.Метрики

        **names_el_budget**: *dict* - словарь, в котором ключами являются часть пути по которому расположена страница
        (3 уровень), а значением - название раздела на русском языке

    Returns:
    ----------
        **Figure**
    """
    colors = ['#0187ad', '#8abc01', '#cdbf5c', '#61cbd9', '#607816', '#0a1006']
    fig = go.Figure()
    for num in range(len(df.groupby(['level3'])[['pageDepth']].mean().pageDepth)):
        fig.add_trace(go.Bar(
            name=list(names_el_budget.values())[num],
            x=[''],
            y=[round(df.groupby(['level3'])[['pageDepth']].mean().pageDepth[num], 1)],
            marker=dict(color=colors[num]),
            text=[round(df.groupby(['level3'])[['pageDepth']].mean().pageDepth[num], 1)],
            textposition='outside'))
    fig.update_traces(textfont_size=10,
                      textfont_family='Arial Black')
    fig.update_layout(title_text='Глубина просмотра раздела "Электронный бюджет"',
                      paper_bgcolor='#ebecf1',
                      plot_bgcolor='#ebecf1',
                      title_xref='paper')

    return fig


def plot_el_budget_graph_mean_time(df, names_el_budget):
    """
    Синтаксис:
    ----------
    **plot_el_budget_graph_mean_time** (df, names_el_budget)

    Описание:
    ---------

    Функция отвечает за построение графика (гистограмма) отображающего среднюю продолжительность визита по каждому
    подразделу в разделе сайта "Электронный бюджет"

    Параметры:
    ----------
        **df**: *DataFrame* - датафрейм содержащий информацию о глубине просмотра раздела сайта "Электронный бюджет",
        полученную из Яндекс.Метрики

        **names_el_budget**: *dict* - словарь, в котором ключами являются часть пути, по которому расположена страница
        (3 уровень), а значением - название раздела на русском языке

    Returns:
    ----------
        **Figure**
    """
    colors = ['#0187ad', '#8abc01', '#cdbf5c', '#61cbd9', '#607816', '#0a1006']
    fig = go.Figure()
    for num in range(len(df.groupby(['level3'])[['avgVisitDurationSeconds']].mean().avgVisitDurationSeconds)):
        fig.add_trace(go.Bar(
            name=list(names_el_budget.values())[num],
            x=[''],
            y=[round(df.groupby(['level3'])[['avgVisitDurationSeconds']].mean().avgVisitDurationSeconds[num] // 60 + (
                    df.groupby(['level3'])[['avgVisitDurationSeconds']].mean().avgVisitDurationSeconds[num] % 60 / 100),
                     2)],
            marker=dict(color=colors[num]),
            text=[str(dt.timedelta(seconds=round(
                df.groupby(['level3'])[['avgVisitDurationSeconds']].mean().avgVisitDurationSeconds[num])))[2:]],
            textposition='outside'))
    fig.update_traces(textfont_size=10,
                      textfont_family='Arial Black',
                      showlegend=False)
    fig.update_layout(title_text='Средняя продолжительность визита',
                      paper_bgcolor='#ebecf1',
                      plot_bgcolor='#ebecf1',
                      title_xref='paper')

    return fig


def plot_gossluzba_graph_page_dept(df):
    """
    Синтаксис:
    ----------
    **plot_gossluzba_graph_page_dept** (df)

    Описание:
    ---------
    Функция отвечает за построение графика (гистограмма) отображающего среднюю глубину просмотра по каждому подразделу
    в разделе сайта "Государственная служба в МБУ ФК"

    Параметры:
    ----------
        **df**: *DataFrame* - датафрейм содержащий информацию о глубине просмотра раздела сайта "Государственная служба
        в МБУ ФК", полученную из Яндекс.Метрики

    Returns:
    ----------
        **Figure**
    """
    colors = ['#98bfad', '#ffc4b2', '#ffffcc']
    fig = go.Figure()
    for num in range(len(df.groupby(['startURL'])[['pageDepth']].mean().pageDepth)):
        fig.add_trace(go.Bar(
            name=df.groupby('startURL').pageDepth.sum().index[num],
            x=[''],
            y=[round(df.groupby(['startURL'])[['pageDepth']].mean().pageDepth[num], 2)],
            marker=dict(color=colors[num]),
            text=[round(df.groupby(['startURL']).mean().pageDepth[num], 1)],
            textposition='outside'))
    fig.update_traces(textfont_size=10,
                      textfont_family='Arial Black',
                      showlegend=True)
    fig.update_layout(title_text='Глубина просмотра раздела "Государственная служба в МБУ ФК"',
                      paper_bgcolor='#ebecf1',
                      plot_bgcolor='#ebecf1',
                      title_xref='paper')

    return fig


def visits_gossluzba_site(df):
    """
    Синтаксис:
    ----------
    **visits_gossluzba_site** (df)

    Описание: Функция отвечает за построение графика (линейные графики) отображающие количество визитов и уникальных
    пользователей посетивших раздел сайта "Государственная служба в МБУ ФК"

    Параметры:
    ----------
        **df**: *DataFrame* - датафрейм содержащий информацию о глубине просмотра раздела сайта "Государственная служба
        в МБУ ФК", полученную из Яндекс.Метрики

    Returns:
    ----------
        **Figure**
    """
    fig = go.Figure(data=[
        go.Scatter(y=list(df.groupby(['date'])['users'].sum()),
                   x=list(df.groupby(['date'])['users'].sum().index),
                   mode='lines+markers',
                   marker=dict(color='#4eac01',
                               size=6),
                   line=dict(color='#4eac01',
                             width=5),
                   name='Визиты'),
        go.Scatter(y=list(df.groupby(['date'])['visits'].sum()),
                   x=list(df.groupby(['date'])['visits'].sum().index),
                   mode='lines+markers',
                   marker=dict(color='#e93667',
                               size=6),
                   line=dict(color='#e93667',
                             width=5),
                   name='Пользователи')
    ])
    fig.update_traces(textfont_size=10,
                      textfont_family='Arial Black',
                      showlegend=True)
    fig.update_layout(title_text='Посещение раздела "Государственная служба в МБУ ФК"',
                      paper_bgcolor='#ebecf1',
                      plot_bgcolor='#ebecf1',
                      title_xref='paper')
    return fig


def fig_total(df, colors):

    fig = go.Figure()
    for i in range(len(df.columns)):
        fig.add_trace(go.Bar(x=[df.columns[i]],
                             y=[df[df.columns[i]].sum()],
                             name=df.columns[i],
                             marker_color=colors[i],
                             text=str(df[df.columns[i]].sum()),
                             textposition='inside'))
        fig.update_layout(barmode='stack',
                          # height=1000,
                          legend_xanchor='right',
                          paper_bgcolor='#ebecf1',
                          plot_bgcolor='#ebecf1',
                          showlegend=False)
    return fig


def inf_sys_heatmap(df):
    fig_heatmap = go.Figure(data=go.Heatmap(
        z=[df.loc[i].to_list() for i in df.index],
        y=df.index,
        x=df.columns))
    fig_heatmap.update_layout(height=700,
                              legend_xanchor='right',
                              paper_bgcolor='#ebecf1',
                              plot_bgcolor='#ebecf1')
    return fig_heatmap


def inf_sys_bar(df, colors, value):
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df.columns,
                         y=df.loc[value],
                         marker_color=colors,
                         text=df.loc[value]))
    fig.update_traces(textposition='auto')
    fig.update_layout(barmode='stack',
                      # height=1000,
                      legend_xanchor='right',
                      paper_bgcolor='#ebecf1',
                      plot_bgcolor='#ebecf1',
                      showlegend=False)
    return fig
