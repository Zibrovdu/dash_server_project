import datetime as dt
from dash.dependencies import Input, Output, State
import dash
import pandas as pd
import passport.load_data as ld
import passport.site_info as si
import passport.figures as pf
import passport.log_writer as lw
from passport.layouts import inf_systems_data
from passport.load_cfg import etsp_table_name, sue_table_name, osp_table_name


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
        Output('el_budget_graph_mean_time', 'figure'),
        Output('gossluzba_pagedept', 'figure'),
        Output('gossluzba_visits', 'figure'),
        [Input('period_choice', 'start_date'),
         Input('period_choice', 'end_date'),
         Input('month_choice', 'value'),
         Input('week_choice', 'value'),
         Input('choice_type', 'value')
         ])
    def update_figure_user(start_date_user, end_date_user, choosen_month, choosen_week, choice_type_period):
        period_choice, week_choice, month_choice = ld.choosen_type(choice_type_period, start_date_user, end_date_user,
                                                                   choosen_month, choosen_week)
        etsp_filtered_df = ld.get_filtered_df_new(etsp_table_name, start_date_user, end_date_user, choosen_month,
                                                  choosen_week, choice_type_period)
        sue_filtered_df = ld.get_filtered_df_new(sue_table_name, start_date_user, end_date_user, choosen_month,
                                                 choosen_week, choice_type_period)
        osp_filtered_df = ld.get_filtered_df_new(osp_table_name, start_date_user, end_date_user, choosen_month,
                                                 choosen_week, choice_type_period)
        sue_incidents_filtered_df = ld.get_filtered_incidents_df_db(start_date_user, end_date_user, choosen_month,
                                                                    choosen_week, choice_type_period)

        etsp_prev_filt_df = ld.get_prev_filtered_df_db(etsp_table_name, start_date_user, end_date_user, choosen_month,
                                                       choosen_week, choice_type_period)
        sue_prev_filt_df = ld.get_prev_filtered_df_db(sue_table_name, start_date_user, end_date_user, choosen_month,
                                                      choosen_week, choice_type_period)
        osp_prev_filt_df = ld.get_prev_filtered_df_db(osp_table_name, start_date_user, end_date_user, choosen_month,
                                                      choosen_week, choice_type_period)

        start_date_metrika, end_date_metrika = ld.get_date_for_metrika_df(start_date_user, end_date_user, choosen_month,
                                                                          choosen_week, choice_type_period)

        filtered_metrika_df = si.get_site_info(start_date_metrika, end_date_metrika)
        filtered_site_visits_graph_df = si.get_data_visits_graph(filtered_metrika_df)

        etsp_count_tasks = etsp_filtered_df['count_task'].sum()
        sue_count_tasks = sue_filtered_df['count_task'].sum()
        osp_count_tasks = osp_filtered_df['count_task'].sum()

        etsp_prev_count_tasks = etsp_prev_filt_df['count_task'].sum()
        sue_prev_count_tasks = sue_prev_filt_df['count_task'].sum()
        osp_prev_count_tasks = osp_prev_filt_df['count_task'].sum()

        etsp_avg_time = ld.count_mean_time(etsp_filtered_df)
        sue_avg_time = ld.count_mean_time(sue_filtered_df)
        osp_avg_time = ld.count_mean_time(osp_filtered_df)

        visits = str(int(filtered_metrika_df['visits'].sum()))
        users = str(int(filtered_metrika_df['users'].sum()))
        pageviews = str(int(filtered_metrika_df['pageviews'].sum()))
        bounce_rate = ''.join([str(round(filtered_metrika_df['bounceRate'].mean(), 2)), "%"])
        page_depth = str(round(filtered_metrika_df['pageDepth'].mean(), 2))
        avg_visit_dur_sec = str(dt.timedelta(seconds=round(
            filtered_metrika_df['avgVisitDurationSeconds'].mean(), 0)))[2:]
        site_stat_data = [{'Визиты': visits, 'Посетители': users, 'Просмотры': pageviews, 'Отказы': bounce_rate,
                           'Глубина просмотра': page_depth, 'Время на сайте': avg_visit_dur_sec}]

        budget_graph_df = si.get_el_budget_data(filtered_metrika_df, si.NamesElBudgetPages.names_el_budget_section_dict)

        gossluzba_df = si.get_gossluzba_data(filtered_metrika_df, si.NamesGossluzbaPages.names_gossluzba_dict)
        # --------------------------------------------FIGURES----------------------------------------------------------
        fig_support = pf.plot_figure_support(etsp_count_tasks, sue_count_tasks, osp_count_tasks)

        site_line_graph = pf.plot_site_line_graph(filtered_metrika_df)

        fig_site_top = pf.plot_fig_site_top(filtered_site_visits_graph_df)

        support_pie_figure = pf.plot_support_pie_figure(etsp_filtered_df, sue_filtered_df, osp_filtered_df)

        el_budget_graph = pf.plot_el_budget_graph(budget_graph_df, si.NamesElBudgetPages.names_el_budget_section_dict)

        el_budget_graph_mean_time = pf.plot_el_budget_graph_mean_time(
            budget_graph_df, si.NamesElBudgetPages.names_el_budget_section_dict)

        gossluzba_pagedept_graph = pf.plot_gossluzba_graph_page_dept(gossluzba_df)

        gossluzba_visits_graph = pf.visits_gossluzba_site(gossluzba_df)

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

        etsp_top_user_filtered_df = ld.top_user(etsp_filtered_df)
        sue_top_user_filtered_df = ld.top_user(sue_filtered_df)

        if len(sue_incidents_filtered_df) > 0:
            style_data = dict(width='20%', backgroundColor='#ff847c')
            tooltip_data = [{column: {'value': str(value), 'type': 'markdown'} for column, value in row.items()}
                            for row in sue_incidents_filtered_df.to_dict('records')]

        else:
            style_data = dict(width='20%', backgroundColor='#c4fbdb')
            sue_incidents_filtered_df = ld.no_icidents()
            tooltip_data = sue_incidents_filtered_df.to_dict('records')

        return (period_choice, month_choice, week_choice, fig_support, total_tasks, style_tasks, total_users,
                style_users, etsp_avg_time, sue_avg_time, osp_avg_time, support_pie_figure,
                sue_incidents_filtered_df.to_dict('records'), style_data, etsp_top_user_filtered_df.to_dict('records'),
                sue_top_user_filtered_df.to_dict('records'), site_stat_data, tooltip_data, fig_site_top,
                site_line_graph, el_budget_graph, el_budget_graph_mean_time, gossluzba_pagedept_graph,
                gossluzba_visits_graph)

    @app.callback(
        Output("modal-scroll", "is_open"),
        [Input("open-scroll", "n_clicks"), Input("close-scroll", "n_clicks")],
        [State("modal-scroll", "is_open")],
    )
    def toggle_modal(n1, n2, is_open):
        if n1 or n2:
            return not is_open
        return is_open

    @app.callback(
        Output('example-output', 'children'),
        [Input('input_pr', 'value'),
         Input('input_user', 'value'),
         Input('input_pers', 'value'),
         Input('input_descr', 'value'),
         Input('date_pr', 'date')
         ])
    def fill_form(project_name, project_user, project_persent, project_descr, project_end_date):

        project_user = ld.names_to_db(project_user)

        row = [project_name, project_user, project_persent, project_descr, project_end_date]

        return row

    @app.callback(
        Output('project_table', 'data'),
        Output('fill_project_name', 'children'),
        Output('fill_project_name', 'style'),
        Output('fill_project_user', 'children'),
        Output('fill_project_user', 'style'),
        Output('fill_project_persent', 'children'),
        Output('fill_project_persent', 'style'),
        Output('fill_project_descr', 'children'),
        Output('fill_project_descr', 'style'),
        Output('fill_project_end_date', 'children'),
        Output('fill_project_end_date', 'style'),
        Output("url_1", "href"),
        Input('save_btn', 'n_clicks'),
        State('example-output', 'children'),
        prevent_initial_call=True,
    )
    def save_btn_clicked(n, row):
        if n:
            style_warning = {"color": "red"}
            msg_warning = 'Заполните поле!!!'
            style_ok = {"color": "white"}
            msg_ok = ' '
            if row[0] is None:
                return dash.no_update, msg_warning, style_warning, dash.no_update, dash.no_update, dash.no_update, \
                       dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, "/"
            elif row[1] is None:
                return dash.no_update, dash.no_update, dash.no_update, msg_warning, style_warning, dash.no_update, \
                       dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, "/"
            elif row[2] is None:
                return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, msg_warning, \
                       style_warning, dash.no_update, dash.no_update, dash.no_update, dash.no_update, "/"
            elif row[3] is None:
                return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, \
                       dash.no_update, msg_warning, style_warning, dash.no_update, dash.no_update, "/"
            elif row[4] is None:
                return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, \
                       dash.no_update, dash.no_update, dash.no_update, msg_warning, style_warning, "/"
            else:
                df = pd.DataFrame(columns=['name', 'executor', 'persent', 'stage', 'finish_date'])
                df.loc[0] = row
                df.to_sql('projects_new', con=ld.engine, index=False, if_exists='append')
                projects_df = ld.load_projects()
                projects_df['id'] = pd.Series([x for x in range(1, len(projects_df) + 1)])
                projects_df = projects_df[['id', 'name', 'executor', 'persent', 'stage', 'finish_date']]
                projects_df.columns = ['Номер', 'Название', 'Исполнитель', 'Процент выполнения', 'Описание',
                                       'Срок исполнения']

                return (projects_df.to_dict('records'), msg_ok, style_ok, msg_ok, style_ok, msg_ok, style_ok, msg_ok,
                        style_ok, msg_ok, style_ok, "/")
        else:
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, \
                   dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, "/"

    @app.callback(
        Output('input_pr', 'value'),
        Output('input_user', 'value'),
        Output('input_pers', 'value'),
        Output('input_descr', 'value'),
        [Input('clear', 'n_clicks')]
    )
    def clear_btn_clicked(n):
        if n:
            return '', '', 0, ''
        else:
            return dash.no_update

    @app.callback(
        Output("modify_window", "is_open"),
        [Input("open_modify_win", "n_clicks"), Input("btn_close_modify", "n_clicks")],
        [State("modify_window", "is_open")],
    )
    def toggle_modal_modify(n1, n2, is_open):
        if n1 or n2:
            return not is_open
        return is_open

    @app.callback(
        Output('input_user_modify', 'value'),
        Output('input_pers_modify', 'value'),
        Output('input_descr_modify', 'value'),
        Output('date_pr_modify', 'date'),
        Input('choose_project_mod', 'value')
    )
    def choose_project_mod(value):
        if value:
            df = ld.load_projects('in_progress', value)
            finish_date = df.finish_date.loc[0]
            if len(finish_date) > 2:
                return df.executor.loc[0].split('/'), df.persent.loc[0], df.stage.loc[0], dt.date(int(finish_date[:4]),
                                                                                                  int(finish_date[5:7]),
                                                                                                  int(finish_date[
                                                                                                      8:10]))
            else:
                finish_date = dt.date(1900, 1, 1)
                return df.executor.loc[0].split('/'), df.persent.loc[0], df.stage.loc[0], finish_date
        else:
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update

    @app.callback(
        Output('example-output_modify', 'children'),
        [Input('choose_project_mod', 'value'),
         Input('input_user_modify', 'value'),
         Input('input_pers_modify', 'value'),
         Input('input_descr_modify', 'value'),
         Input('date_pr_modify', 'date')
         ])
    def fill_form_modify(project_name, project_user, project_persent, project_descr, project_end_date):

        project_user = ld.names_to_db(project_user)
        row_modify = [project_name, project_user, project_persent, project_descr, project_end_date]

        return row_modify

    @app.callback(
        Output('mod_project_name', 'children'),
        Output("url", "href"),
        Input('btn_save_modify', 'n_clicks'),
        State('example-output_modify', 'children'),
        prevent_initial_call=True,

    )
    def update_projects_info(n, row_modify):
        if not row_modify:
            return 'Please choose project to update', " "
        if n:
            if len(row_modify) == 5:
                df = ld.load_projects('all')
                mask = df[df['name'] == row_modify[0]].index
                df.loc[mask, ['executor', 'persent', 'stage', 'finish_date']] = row_modify[1:5]
                df.to_sql('projects_new', con=ld.engine, index=False, if_exists='replace')
                projects_df = ld.load_projects()
                projects_df['id'] = pd.Series([x for x in range(1, len(projects_df) + 1)])
                projects_df = projects_df[['id', 'name', 'executor', 'persent', 'stage', 'finish_date']]
                projects_df.columns = ['Номер', 'Название', 'Исполнитель', 'Процент выполнения', 'Описание',
                                       'Срок исполнения']

                lw.log_writer('Обновление информации успешно завершено')

                return 'Обновление информации успешно завершено', "/"
            else:
                lw.log_writer('При обновлении информации произошел сбой')
                lw.log_writer(row_modify)
                return 'При обновлении информации произошел сбой', " "
