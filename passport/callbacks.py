from dash.dependencies import Input, Output
import datetime as dt
import passport.load_data as ld
import passport.site_info as si
import passport.log_writer as lw
import passport.figures as pf
from passport.layouts import etsp_df, sue_df, osp_df, inf_systems_data, sue_incidents_df


def register_callbacks(app):
    @app.callback(
        Output('project_name', 'children'),
        Output('executor', 'children'),
        Output('persent_dd', 'value'),
        Output('project_decsr', 'value'),
        Output('status', 'value'),
        [Input('projects_name', 'value')])
    def projects(value):
        project_df = ld.load_projects()
        name = project_df[project_df.id == int(value)]['name']
        executor = project_df[project_df.id == int(value)]['executor']
        persent = project_df[project_df.id == int(value)]['persent'][int(value) - 1]

        project_descr = str(project_df[project_df.id == int(value)]['stage'][int(value) - 1])
        project_stat_value = str(project_df[project_df.id == int(value)]['status'][int(value) - 1])
        return name, executor, persent, project_descr, project_stat_value

    @app.callback(
        Output("inf_systems", "figure"),
        [Input("leg_show", "on")])
    def modify_legend(on):
        fig_inf_systems = pf.fig_inf_systems(inf_systems_data, on)
        return fig_inf_systems

    @app.callback(
        Output('period_choice', 'disabled'),
        Output('month_choice', 'disabled'),
        Output('week_choice', 'disabled'),
        Output('users_figure', 'figure'),
        Output('tasks', 'children'),
        Output('tasks', 'style'),
        Output('users', 'children'),
        Output('users', 'style'),
        Output('etsp-time', 'children'),
        Output('sue-time', 'children'),
        Output('osp-time', 'children'),
        Output('support_figure', 'figure'),
        Output('sue_avaria', 'data'),
        Output('sue_avaria', 'style_data'),
        Output('table_top_etsp', 'data'),
        Output('table_top_sue', 'data'),
        Output('site_stat', 'data'),
        Output('sue_avaria', 'tooltip_data'),
        Output('site_top_fig', 'figure'),
        Output('site_line_graph', 'figure'),
        Output('el_budget_graph', 'figure'),
        [Input('period_choice', 'start_date'),
         Input('period_choice', 'end_date'),
         Input('month_choice', 'value'),
         Input('week_choice', 'value'),
         Input('choice_type', 'value')
         ])
    def update_figure_user(start_date_user, end_date_user, choosen_month, choosen_week, choice_type_period):
        if choice_type_period == 'm':
            period_choice = True
            week_choice = True
            month_choice = False
            lw.log_writer(f'User choice "month = {choosen_month}"')

            if int(choosen_month) > 1:
                etsp_prev_filt_df = etsp_df[etsp_df['month_open'] == (int(choosen_month) - 1)]
                sue_prev_filt_df = sue_df[sue_df['month_open'] == (int(choosen_month) - 1)]
                osp_prev_filt_df = osp_df[osp_df['month_open'] == (int(choosen_month) - 1)]
            else:
                etsp_prev_filt_df = etsp_df[etsp_df['month_open'] == 12]
                sue_prev_filt_df = sue_df[sue_df['month_open'] == 12]
                osp_prev_filt_df = osp_df[osp_df['month_open'] == 12]

            etsp_filtered_df = etsp_df[etsp_df['month_open'] == int(choosen_month)]
            sue_filtered_df = sue_df[sue_df['month_open'] == int(choosen_month)]
            osp_filtered_df = osp_df[osp_df['month_open'] == int(choosen_month)]
            sue_incidents_filtered_df = sue_incidents_df[sue_incidents_df['month_open'] == int(choosen_month)]

            if choosen_month > ld.current_month:
                year_metrika = ld.current_year - 1
            else:
                year_metrika = ld.current_year

            start_date_metrika = ld.GetMonthPeriod(year_metrika, choosen_month)[0]
            end_date_metrika = ld.GetMonthPeriod(year_metrika, choosen_month)[1]

            filtered_metrika_df = si.get_site_info(start_date_metrika, end_date_metrika)
            filtered_site_visits_graph_df = si.get_data_visits_graph(filtered_metrika_df)

        elif choice_type_period == 'p':
            period_choice = False
            week_choice = True
            month_choice = True
            lw.log_writer(f'User choice "range period start = {start_date_user}, end = {end_date_user}"')

            if int(start_date_user[5:7]) > 1:
                etsp_prev_filt_df = etsp_df[etsp_df['month_open'] == (int(start_date_user[5:7]) - 1)]
                sue_prev_filt_df = sue_df[sue_df['month_open'] == (int(start_date_user[5:7]) - 1)]
                osp_prev_filt_df = osp_df[osp_df['month_open'] == (int(start_date_user[5:7]) - 1)]
            else:
                etsp_prev_filt_df = etsp_df[etsp_df['month_open'] == 12]
                sue_prev_filt_df = sue_df[sue_df['month_open'] == 12]
                osp_prev_filt_df = osp_df[osp_df['month_open'] == 12]

            etsp_filtered_df = etsp_df[
                (etsp_df['start_date'] >= start_date_user) & (etsp_df['start_date'] <= end_date_user)]
            sue_filtered_df = sue_df[
                (sue_df['start_date'] >= start_date_user) & (sue_df['start_date'] <= end_date_user)]
            osp_filtered_df = osp_df[
                (osp_df['start_date'] >= start_date_user) & (osp_df['start_date'] <= end_date_user)]
            sue_incidents_filtered_df = sue_incidents_df[(sue_incidents_df['Дата обращения'] >= start_date_user) &
                                                         (sue_incidents_df['Дата обращения'] <= end_date_user)]

            start_date_metrika = start_date_user
            end_date_metrika = end_date_user

            filtered_metrika_df = si.get_site_info(start_date_metrika, end_date_metrika)
            filtered_site_visits_graph_df = si.get_data_visits_graph(filtered_metrika_df)

        else:
            period_choice = True
            week_choice = False
            month_choice = True
            lw.log_writer(f'User choice "week = {choosen_week} ({ld.GetPeriod(ld.current_year, choosen_week)})"')

            if int(choosen_week) > 1:
                etsp_prev_filt_df = etsp_df[etsp_df['week_open'] == (int(choosen_week) - 1)]
                sue_prev_filt_df = sue_df[sue_df['week_open'] == (int(choosen_week) - 1)]
                osp_prev_filt_df = osp_df[osp_df['week_open'] == (int(choosen_week) - 1)]
            else:
                etsp_prev_filt_df = etsp_df[etsp_df['week_open'] == 52]
                sue_prev_filt_df = sue_df[sue_df['week_open'] == 52]
                osp_prev_filt_df = osp_df[osp_df['week_open'] == 52]

            etsp_filtered_df = etsp_df[etsp_df['week_open'] == int(choosen_week)]
            sue_filtered_df = sue_df[sue_df['week_open'] == int(choosen_week)]
            osp_filtered_df = osp_df[osp_df['week_open'] == int(choosen_week)]
            sue_incidents_filtered_df = sue_incidents_df[sue_incidents_df['week_open'] == int(choosen_week)]

            if choosen_week > ld.current_week:
                year_metrika = ld.current_year - 1
            else:
                year_metrika = ld.current_year

            start_date_metrika = ld.GetPeriod(year_metrika, choosen_week, 's')[0]
            end_date_metrika = ld.GetPeriod(year_metrika, choosen_week, 's')[1]

            filtered_metrika_df = si.get_site_info(start_date_metrika, end_date_metrika)
            filtered_site_visits_graph_df = si.get_data_visits_graph(filtered_metrika_df)

        etsp_count_tasks = etsp_filtered_df['count_task'].sum()
        sue_count_tasks = sue_filtered_df['count_task'].sum()
        osp_count_tasks = osp_filtered_df['count_task'].sum()

        etsp_prev_count_tasks = etsp_prev_filt_df['count_task'].sum()
        sue_prev_count_tasks = sue_prev_filt_df['count_task'].sum()
        osp_prev_count_tasks = osp_prev_filt_df['count_task'].sum()

        etsp_avg_time = ld.CountMeanTime(etsp_filtered_df)
        sue_avg_time = ld.CountMeanTime(sue_filtered_df)
        osp_avg_time = ld.CountMeanTime(osp_filtered_df)

        visits = str(int(filtered_metrika_df['visits'].sum()))
        users = str(int(filtered_metrika_df['users'].sum()))
        pageviews = str(int(filtered_metrika_df['pageviews'].sum()))
        bounceRate = ''.join([str(round(filtered_metrika_df['bounceRate'].mean(), 2)), "%"])
        pageDepth = str(round(filtered_metrika_df['pageDepth'].mean(), 2))
        avgVisitDurSec = str(dt.timedelta(seconds=round(filtered_metrika_df['avgVisitDurationSeconds'].mean(), 0)))[2:]
        site_stat_data = [{'Визиты': visits, 'Посетители': users, 'Просмотры': pageviews, 'Отказы': bounceRate,
                           'Глубина просмотра': pageDepth, 'Время на сайте': avgVisitDurSec}]

        budget_graph_df = si.get_el_budget_data(filtered_metrika_df, si.NamesElBudgetPages.names_el_budget_section_dict)

        # --------------------------------------------FIGURES----------------------------------------------------------
        fig_support = pf.plot_figure_support(etsp_count_tasks, sue_count_tasks, osp_count_tasks)

        site_line_graph = pf.plot_site_line_graph(filtered_metrika_df)

        fig_site_top = pf.plot_fig_site_top(filtered_site_visits_graph_df)

        support_pie_figure = pf.plot_support_pie_figure(etsp_filtered_df, sue_filtered_df, osp_filtered_df)

        el_budget_graph = pf.plot_el_budget_graph(budget_graph_df, si.NamesElBudgetPages.names_el_budget_section_dict)

        # -----------------------------------DIFF-TASKS-AND-USERS------------------------------------------------------
        total_curr_tasks = etsp_count_tasks + sue_count_tasks + osp_count_tasks
        total_prev_tasks = etsp_prev_count_tasks + sue_prev_count_tasks + osp_prev_count_tasks
        tasks_diff = total_curr_tasks - total_prev_tasks

        diff_tasks = ld.set_differences(tasks_diff)[1]
        style_tasks = ld.set_differences(tasks_diff)[0]
        total_tasks = ''.join([str(total_curr_tasks), ' ( ', diff_tasks, ' )'])

        total_curr_users = len(etsp_filtered_df['user'].unique()) + len(sue_filtered_df['user'].unique()) + len(
            osp_filtered_df['user'].unique())
        total_prev_users = len(etsp_prev_filt_df['user'].unique()) + len(sue_prev_filt_df['user'].unique()) + len(
            osp_prev_filt_df['user'].unique())
        users_diff = total_curr_users - total_prev_users

        diff_users = ld.set_differences(users_diff)[1]
        style_users = ld.set_differences(users_diff)[0]
        total_users = ''.join([str(total_curr_users), ' ( ', diff_users, ' )'])

        etsp_top_user_filtered_df = ld.TopUser(etsp_filtered_df)
        sue_top_user_filtered_df = ld.TopUser(sue_filtered_df)

        if len(sue_incidents_filtered_df) > 0:
            style_data = dict(width='20%', backgroundColor='#ff847c')
            tooltip_data = [{column: {'value': str(value), 'type': 'markdown'} for column, value in row.items()}
                            for row in sue_incidents_filtered_df.to_dict('records')]

        else:
            style_data = dict(width='20%', backgroundColor='#c4fbdb')
            sue_incidents_filtered_df = ld.NoIncidents()
            tooltip_data = sue_incidents_filtered_df.to_dict('records')

        return (period_choice, month_choice, week_choice, fig_support, total_tasks, style_tasks, total_users,
                style_users, etsp_avg_time, sue_avg_time, osp_avg_time, support_pie_figure,
                sue_incidents_filtered_df.to_dict('records'), style_data, etsp_top_user_filtered_df.to_dict('records'),
                sue_top_user_filtered_df.to_dict('records'), site_stat_data, tooltip_data, fig_site_top,
                site_line_graph, el_budget_graph)
