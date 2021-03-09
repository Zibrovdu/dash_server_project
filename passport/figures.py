import plotly.graph_objects as go
import datetime as dt


def plot_figure_support(etsp_count_tasks, sue_count_tasks, osp_count_tasks):
    fig_support = go.Figure(go.Bar(y=[etsp_count_tasks, sue_count_tasks, osp_count_tasks],
                                   x=['ЕЦП', 'СУЭ', 'ОСП'],
                                   base=0,
                                   marker=dict(color=['#a92b2b', '#37a17c', '#a2d5f2']),
                                   text=[etsp_count_tasks, sue_count_tasks, osp_count_tasks],
                                   textposition='auto'))
    fig_support.update_layout(autosize=True,
                              legend=dict(
                                  orientation="h",
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


def plot_support_pie_figure(etsp_filtered_df, sue_filtered_df, osp_filtered_df):
    support_pie_figure_labels = ["ЕЦП", "СУЭ", "ОСП"]
    support_pie_figure_values = [etsp_filtered_df['count_task'].sum(), sue_filtered_df['count_task'].sum(),
                                 osp_filtered_df['count_task'].sum()]
    support_pie_figure_colors = ['#a92b2b', '#37a17c', '#a2d5f2']

    support_pie_figure = go.Figure(
        go.Pie(labels=support_pie_figure_labels,
               values=support_pie_figure_values,
               marker_colors=support_pie_figure_colors))

    support_pie_figure.update_traces(hoverinfo="label+percent+name")

    support_pie_figure.update_layout(paper_bgcolor='#ebecf1', showlegend=True)

    return support_pie_figure


def plot_fig_site_top(filtered_site_visits_graph_df):
    site_top_figure_colors = ['#003b32', '#40817a', '#afbaa3', '#d0d0b8', '#037c87', '#7cbdc9']
    fig_site_top = go.Figure([go.Bar(y=filtered_site_visits_graph_df['visits'],
                                     x=filtered_site_visits_graph_df['level2'],
                                     orientation='v',
                                     marker_color=site_top_figure_colors,
                                     text=filtered_site_visits_graph_df['visits'])])
    fig_site_top.update_traces(textposition='auto')
    fig_site_top.update_layout(title_text="Визиты", paper_bgcolor='#ebecf1', plot_bgcolor='#ebecf1')

    return fig_site_top


def plot_site_line_graph(filtered_metrika_df):
    site_line_graph = go.Figure(data=[
        go.Scatter(y=list(filtered_metrika_df.groupby(['date'])['visits'].sum()),
                   x=list(filtered_metrika_df.groupby(['date'])['visits'].sum().index),
                   mode='lines+markers',
                   marker=dict(color='#5d4b63', size=6),
                   line=dict(color='#5d4b63', width=5),
                   name='Визиты'),
        go.Scatter(y=list(filtered_metrika_df.groupby(['date'])['users'].sum()),
                   x=list(filtered_metrika_df.groupby(['date'])['users'].sum().index),
                   mode='lines+markers',
                   marker=dict(color='#d74d63', size=6),
                   line=dict(color='#d74d63', width=5),
                   name='Пользователи'),
        go.Scatter(y=list(filtered_metrika_df.groupby(['date'])['pageviews'].sum()),
                   x=list(filtered_metrika_df.groupby(['date'])['pageviews'].sum().index),
                   mode='lines+markers',
                   marker=dict(color='#a38182', size=6),
                   line=dict(color='#a38182', width=5),
                   name='Просмотры страниц')
    ])
    site_line_graph.update_layout(title_text="Посещение сайта", paper_bgcolor='#ebecf1', plot_bgcolor='#ebecf1')

    return site_line_graph


def fig_inf_systems(inf_systems_data, on):
    fig_inf_sys = go.Figure()
    for i in range(len(inf_systems_data)):
        fig_inf_sys.add_trace(go.Bar(y=inf_systems_data.columns,
                                     x=inf_systems_data.iloc[i],
                                     name=inf_systems_data.index[i],
                                     orientation='h',
                                     text=inf_systems_data.iloc[i],
                                     textposition='inside'))
        fig_inf_sys.update_layout(barmode='stack',
                                  height=1000,
                                  legend_xanchor='right',
                                  paper_bgcolor='#ebecf1',
                                  plot_bgcolor='#ebecf1',
                                  showlegend=on)
        fig_inf_sys.update_yaxes(tickmode="linear")

    return fig_inf_sys


def plot_el_budget_graph(df, names_el_budget_section_dict):
    colors = ['#0187ad', '#8abc01', '#cdbf5c', '#61cbd9', '#607816', '#0a1006']
    fig = go.Figure()
    for num in range(len(df.groupby(['level3'])[['pageDepth']].mean().pageDepth)):
        fig.add_trace(go.Bar(
            name=list(names_el_budget_section_dict.values())[num],
            x=[''],
            y=[round(df.groupby(['level3'])[['pageDepth']].mean().pageDepth[num], 1)],
            marker=dict(color=colors[num]),
            text=[round(df.groupby(['level3'])[['pageDepth']].mean().pageDepth[num], 1)],
            textposition='outside'))
    fig.update_traces(textfont_size=10)
    fig.update_layout(title_text='Глубина просмотра раздела "Электронный бюджет"', paper_bgcolor='#ebecf1',
                      plot_bgcolor='#ebecf1', title_xref='paper')

    return fig


def plot_el_budget_graph_mean_time(df, names_el_budget_section_dict):
    colors = ['#0187ad', '#8abc01', '#cdbf5c', '#61cbd9', '#607816', '#0a1006']
    fig = go.Figure()
    for num in range(len(df.groupby(['level3'])[['avgVisitDurationSeconds']].mean().avgVisitDurationSeconds)):
        fig.add_trace(go.Bar(
            name=list(names_el_budget_section_dict.values())[num],
            x=[''],
            y=[round(df.groupby(['level3'])[['avgVisitDurationSeconds']].mean().avgVisitDurationSeconds[num] // 60 + (
                    df.groupby(['level3'])[['avgVisitDurationSeconds']].mean().avgVisitDurationSeconds[num] % 60 / 100),
                     2)],
            marker=dict(color=colors[num]),
            text=[str(dt.timedelta(seconds=round(
                df.groupby(['level3'])[['avgVisitDurationSeconds']].mean().avgVisitDurationSeconds[num])))[2:]],
            textposition='outside'))
    fig.update_traces(textfont_size=10, showlegend=False)
    fig.update_layout(title_text='Средняя продолжительность визита', paper_bgcolor='#ebecf1', plot_bgcolor='#ebecf1',
                      title_xref='paper')

    return fig
