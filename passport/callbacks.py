import datetime as dt

import dash
import pandas as pd
from dash.dependencies import Input, Output, State

import passport.figures as pf
import passport.load_data as ld
import passport.log_writer as lw
import passport.site_info as si
import passport.load_cfg as lc
from passport.layouts import inf_systems_data


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
    def modify_legend(switch):
        fig_inf_systems = pf.fig_inf_systems(inf_systems_data=inf_systems_data,
                                             legend_sw=switch)
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

        period_choice, week_choice, month_choice = ld.choosen_type(type_period=choice_type_period,
                                                                   start_date=start_date_user,
                                                                   end_date=end_date_user,
                                                                   ch_month=choosen_month,
                                                                   ch_week=choosen_week)

        etsp_filtered_df = ld.get_filtered_df(table_name=lc.etsp_table_name,
                                              start_date=start_date_user,
                                              end_date=end_date_user,
                                              ch_month=choosen_month,
                                              ch_week=choosen_week,
                                              type_period=choice_type_period)

        sue_filtered_df = ld.get_filtered_df(table_name=lc.sue_table_name,
                                             start_date=start_date_user,
                                             end_date=end_date_user,
                                             ch_month=choosen_month,
                                             ch_week=choosen_week,
                                             type_period=choice_type_period)

        osp_filtered_df = ld.get_filtered_df(table_name=lc.osp_table_name,
                                             start_date=start_date_user,
                                             end_date=end_date_user,
                                             ch_month=choosen_month,
                                             ch_week=choosen_week,
                                             type_period=choice_type_period)

        sue_incidents_filtered_df = ld.get_filtered_incidents_df(start_date=start_date_user,
                                                                 end_date=end_date_user,
                                                                 ch_month=choosen_month,
                                                                 ch_week=choosen_week,
                                                                 type_period=choice_type_period)

        etsp_prev_filt_df = ld.get_prev_filtered_df(table_name=lc.etsp_table_name,
                                                    start_date=start_date_user,
                                                    end_date=end_date_user,
                                                    ch_month=choosen_month,
                                                    ch_week=choosen_week,
                                                    type_period=choice_type_period)

        sue_prev_filt_df = ld.get_prev_filtered_df(table_name=lc.sue_table_name,
                                                   start_date=start_date_user,
                                                   end_date=end_date_user,
                                                   ch_month=choosen_month,
                                                   ch_week=choosen_week,
                                                   type_period=choice_type_period)

        osp_prev_filt_df = ld.get_prev_filtered_df(table_name=lc.osp_table_name,
                                                   start_date=start_date_user,
                                                   end_date=end_date_user,
                                                   ch_month=choosen_month,
                                                   ch_week=choosen_week,
                                                   type_period=choice_type_period)

        start_date_metrika, end_date_metrika = ld.get_date_for_metrika_df(start_date=start_date_user,
                                                                          end_date=end_date_user,
                                                                          ch_month=choosen_month,
                                                                          ch_week=choosen_week,
                                                                          type_period=choice_type_period)

        filtered_metrika_df = si.get_site_info(start_date=start_date_metrika,
                                               end_date=end_date_metrika)

        filtered_site_visits_graph_df = si.get_data_visits_graph(df=filtered_metrika_df)

        etsp_count_tasks = etsp_filtered_df['count_task'].sum()
        sue_count_tasks = sue_filtered_df['count_task'].sum()
        osp_count_tasks = osp_filtered_df['count_task'].sum()

        etsp_prev_count_tasks = etsp_prev_filt_df['count_task'].sum()
        sue_prev_count_tasks = sue_prev_filt_df['count_task'].sum()
        osp_prev_count_tasks = osp_prev_filt_df['count_task'].sum()

        etsp_avg_time = ld.count_mean_time(filtered_df=etsp_filtered_df)
        sue_avg_time = ld.count_mean_time(filtered_df=sue_filtered_df)
        osp_avg_time = ld.count_mean_time(filtered_df=osp_filtered_df)

        visits = str(int(filtered_metrika_df['visits'].sum()))
        users = str(int(filtered_metrika_df['users'].sum()))
        pageviews = str(int(filtered_metrika_df['pageviews'].sum()))
        bounce_rate = ''.join([str(round(filtered_metrika_df['bounceRate'].mean(), 2)), "%"])
        page_depth = str(round(filtered_metrika_df['pageDepth'].mean(), 2))
        avg_visit_dur_sec = str(dt.timedelta(seconds=round(
            filtered_metrika_df['avgVisitDurationSeconds'].mean(), 0)))[2:]
        site_stat_data = [{'Визиты': visits, 'Посетители': users, 'Просмотры': pageviews, 'Отказы': bounce_rate,
                           'Глубина просмотра': page_depth, 'Время на сайте': avg_visit_dur_sec}]

        budget_graph_df = si.get_el_budget_data(df=filtered_metrika_df,
                                                names_el_budget=si.names_el_budget_dict)

        gossluzba_df = si.get_gossluzba_data(df=filtered_metrika_df,
                                             names_gossluzba=si.names_gossluzba_dict)
        # --------------------------------------------FIGURES----------------------------------------------------------
        fig_support = pf.plot_figure_support(first_tp_count_tasks=etsp_count_tasks,
                                             second_tp_count_tasks=sue_count_tasks,
                                             third_tp_count_tasks=osp_count_tasks)

        site_line_graph = pf.plot_site_line_graph(df=filtered_metrika_df)

        fig_site_top = pf.plot_fig_site_top(df=filtered_site_visits_graph_df)

        support_pie_figure = pf.plot_support_pie_figure(first_filtered_df=etsp_filtered_df,
                                                        second_filtered_df=sue_filtered_df,
                                                        third_filtered_df=osp_filtered_df)

        el_budget_graph = pf.plot_el_budget_graph(df=budget_graph_df,
                                                  names_el_budget=si.names_el_budget_dict)

        el_budget_graph_mean_time = pf.plot_el_budget_graph_mean_time(df=budget_graph_df,
                                                                      names_el_budget=si.names_el_budget_dict)

        gossluzba_pagedept_graph = pf.plot_gossluzba_graph_page_dept(df=gossluzba_df)

        gossluzba_visits_graph = pf.visits_gossluzba_site(df=gossluzba_df)

        # -----------------------------------DIFF-TASKS-AND-USERS------------------------------------------------------
        total_curr_tasks = etsp_count_tasks + sue_count_tasks + osp_count_tasks
        total_prev_tasks = etsp_prev_count_tasks + sue_prev_count_tasks + osp_prev_count_tasks
        tasks_diff = total_curr_tasks - total_prev_tasks

        diff_tasks = ld.set_differences(diff=tasks_diff)[1]
        style_tasks = ld.set_differences(diff=tasks_diff)[0]
        total_tasks = ''.join([str(total_curr_tasks), ' ( ', diff_tasks, ' )'])

        total_curr_users = len(etsp_filtered_df['user'].unique()) + len(sue_filtered_df['user'].unique()) + len(
            osp_filtered_df['user'].unique())
        total_prev_users = len(etsp_prev_filt_df['user'].unique()) + len(sue_prev_filt_df['user'].unique()) + len(
            osp_prev_filt_df['user'].unique())
        users_diff = total_curr_users - total_prev_users

        diff_users = ld.set_differences(diff=users_diff)[1]
        style_users = ld.set_differences(diff=users_diff)[0]
        total_users = ''.join([str(total_curr_users), ' ( ', diff_users, ' )'])

        etsp_top_user_filtered_df = ld.top_user(etsp_filtered_df)
        sue_top_user_filtered_df = ld.top_user(sue_filtered_df)

        if len(sue_incidents_filtered_df) > 0:
            style_data = dict(width='20%', backgroundColor='#ff847c')
            tooltip_data = [{column: {'value': str(value), 'type': 'markdown'} for column, value in row.items()}
                            for row in sue_incidents_filtered_df.to_dict('records')]

        else:
            style_data = dict(width='20%', backgroundColor='#c4fbdb')
            sue_incidents_filtered_df = ld.no_incidents()
            tooltip_data = sue_incidents_filtered_df.to_dict('records')

        return (period_choice, month_choice, week_choice, fig_support, total_tasks, style_tasks, total_users,
                style_users, etsp_avg_time, sue_avg_time, osp_avg_time, support_pie_figure,
                sue_incidents_filtered_df.to_dict('records'), style_data, etsp_top_user_filtered_df.to_dict('records'),
                sue_top_user_filtered_df.to_dict('records'), site_stat_data, tooltip_data, fig_site_top,
                site_line_graph, el_budget_graph, el_budget_graph_mean_time, gossluzba_pagedept_graph,
                gossluzba_visits_graph)

    @app.callback(
        Output("modal-scroll", "is_open"),
        [Input("open-scroll", "n_clicks"),
         Input("close-scroll", "n_clicks")],
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
    def fill_form(project_name, project_users, project_persent, project_descr, project_end_date):

        project_users = ld.names_to_db(users=project_users)

        row = [project_name, project_users, project_persent, project_descr, project_end_date,
               dt.datetime.now().strftime('%Y-%m-%d'), '-', 0]
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
                df = pd.DataFrame(columns=['name', 'executor', 'persent', 'stage', 'plan_date', 'start_date',
                                           'fact_date', 'duration'])
                df.loc[0] = row
                df.to_sql('projects_new',
                          con=ld.engine,
                          index=False,
                          if_exists='append')
                projects_df = ld.load_projects()
                projects_df['id'] = pd.Series([x for x in range(1, len(projects_df) + 1)])
                projects_df = projects_df[['id', 'name', 'executor', 'persent', 'stage', 'plan_date']]
                projects_df.columns = ['Номер', 'Название', 'Исполнитель', 'Процент выполнения', 'Описание',
                                       'Срок исполнения']

                recipients_list = ld.get_emails_list(row=row)
                send_mail = ld.send_mail(subject=lc.new_task_subject,
                                         row=row,
                                         params=lc.con_mail_server,
                                         recipients_list=recipients_list)
                lw.log_writer(log_msg=''.join(['Попытка отправки письма... ', str(send_mail)]))
                lw.log_writer(log_msg='Обновление информации успешно завершено')

                return (projects_df.to_dict('records'), msg_ok, style_ok, msg_ok, style_ok, msg_ok, style_ok, msg_ok,
                        style_ok, msg_ok, style_ok, "/")
        else:
            lw.log_writer(log_msg='При обновлении информации произошел сбой')
            lw.log_writer(log_msg=str(row))
            return (dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update,
                    dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, "/")

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
        [Input("open_modify_win", "n_clicks"),
         Input("btn_close_modify", "n_clicks")],
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
        Output('input_pers_modify', 'disabled'),
        Output('fact_date_pr_modify', 'date'),
        Output('fact_date_pr_modify', 'disabled'),
        Input('choose_project_mod', 'value'),
        Input('complete_project_switch', 'on')
    )
    def choose_project_mod(value, on):
        if value:
            df = ld.load_projects(projects_status='in_progress',
                                  project_name=value)
            plan_date = df.plan_date.loc[0]
            if on:
                df.loc[0, 'persent'] = 100
                disable_input_pers = True
                disable_fact_date_mod = False
                fact_date = dt.datetime.now().strftime('%Y-%m-%d')
            else:
                disable_input_pers = False
                disable_fact_date_mod = True
                fact_date = df.fact_date.loc[0]

            if len(fact_date) > 2:
                return df.executor.loc[0].split('/'), df.persent.loc[0], df.stage.loc[0], dt.date(int(plan_date[:4]),
                                                                                                  int(plan_date[5:7]),
                                                                                                  int(plan_date[
                                                                                                      8:10])), \
                       disable_input_pers, fact_date, disable_fact_date_mod
            else:
                fact_date = dt.date(1900, 1, 1)
                return (df.executor.loc[0].split('/'), df.persent.loc[0], df.stage.loc[0], plan_date, dash.no_update,
                        fact_date, dash.no_update)
        else:
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, \
                   dash.no_update

    @app.callback(
        Output('example-output_modify', 'children'),
        [Input('choose_project_mod', 'value'),
         Input('input_user_modify', 'value'),
         Input('input_pers_modify', 'value'),
         Input('input_descr_modify', 'value'),
         Input('date_pr_modify', 'date'),
         Input('fact_date_pr_modify', 'date')
         ])
    def fill_form_modify(project_name, project_users, project_persent, project_descr, project_plan_date,
                         project_fact_date):

        project_users = ld.names_to_db(users=project_users)

        row_modify = [project_name, project_users, project_persent, project_descr, project_plan_date, project_fact_date,
                      0]

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
            if len(row_modify) == 7:
                df = ld.load_projects(projects_status='all')
                if row_modify[0]:
                    start_date = df[df.name == row_modify[0]].start_date.values[0]
                else:
                    start_date = '-'
                duration = ld.count_project_time(start_date=start_date,
                                                 fact_date=row_modify[5])
                row_modify[6] = duration
                row_modify.append(start_date)
                mask = df[df['name'] == row_modify[0]].index
                df.loc[mask, ['executor', 'persent', 'stage', 'plan_date', 'fact_date', 'duration',
                              'start_date']] = row_modify[1:8]
                df.to_sql('projects_new',
                          con=ld.engine,
                          index=False,
                          if_exists='replace')
                projects_df = ld.load_projects()
                projects_df['id'] = pd.Series([x for x in range(1, len(projects_df) + 1)])
                projects_df = projects_df[['id', 'name', 'executor', 'persent', 'stage', 'plan_date']]
                projects_df.columns = ['Номер', 'Название', 'Исполнитель', 'Процент выполнения', 'Описание',
                                       'Срок исполнения']

                recipients_list = ld.get_emails_list(row=row_modify)
                send_mail = ld.send_mail(subject=lc.exist_task_subject,
                                         row=row_modify,
                                         params=lc.con_mail_server,
                                         recipients_list=recipients_list)
                lw.log_writer(log_msg=''.join(['Попытка отправки письма... ', str(send_mail)]))
                lw.log_writer(log_msg='Обновление информации успешно завершено')

                return 'Обновление информации успешно завершено', "/"
            else:
                lw.log_writer(log_msg='При обновлении информации произошел сбой')
                lw.log_writer(log_msg=str(row_modify))
                return 'При обновлении информации произошел сбой', " "
