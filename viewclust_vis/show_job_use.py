import pandas as pd
import datetime as dt
from datetime import datetime
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go

import os

import viewclust as vc
from viewclust import slurm
from viewclust.target_series import target_series

from viewclust_vis.job_stack import job_stack
from viewclust_vis.insta_plot import insta_plot
from viewclust_vis.cumu_plot import cumu_plot


def show_job_use(account, target, d_from, d_to='', d_from_drop='', out_path='',
                 use_unit='', plot_jobstack=True, plot_insta=True,
                 plot_cumu=True, plot_mem_delta=False, plot_start_wait=False,
                 plot_wait_viol=False, plot_start_runtime=False,
                 plot_runtime_viol=False, override_frame=[]):

    """Accepts an account name and query period to generate
    job usage summary figures.


    Parameters
    -------
    account: string
        Name of account for which to query job records
        (note that Compute Canada systems expect a _cpu or _gpu suffix).
    target: int-like
        The target share value for the account on the system
        (typically expressed as "cores" or "core-equivalents").
    d_from: date str
        Beginning of the query period, e.g. '2019-04-01T00:00:00'.
    d_to: date str, optional
        End of the query period, e.g. '2020-01-01T00:00:00'.
        Defaults to now if empty.
    d_from_drop: date str, optional
        Time prior to which to ingnore jobs of any state,
        e.g. '2019-12-01T00:00:00'.
    out_path: date str, optional
        Name of path in which to place the output figure files.
        Defaults to current path
    use_unit: str, optional
        Usage unit to examine. One of: {'cpu', 'cpu-eqv', 'gpu', 'gpu-eqv'}.
        Defaults to 'cpu', or determine from account suffix
        (if *_cpu, use_unit='cpu-eqv', if *_cpu, use_unit='cpu-eqv',
            else use_unit = 'cpu).
    plot_jobstack: boolean, optional
        If True plot the jobstack figure.
        Note that for large job record data frames the jobstack figure
        can take some time to produce.
        The jobstack figure is a representation of the time periods and
        and resource size of each job in a job record query. Defaults to True.
    plot_insta: boolean, optional
        If True plot the insta_plot figure. The insta_plot is a display of
        the job record usage measurement
        at each time point over the query period. Defaults to True.
    plot_cumu: boolean, optional
        If True plot the cumu_plot figure. The cumu_plot is a display of the
        cumulative job record usage measurement
        at each time point over the query period. Defaults to True.
    plot_mem_delta: boolean, optional
        If True plot the mem_delta figure. The mem_delta is a display memory
        requested (allocated) to each job as well
        as its peak polled memory (MaxRSS). Defaults to False.
    plot_start_wait: boolean, optional
        If True create the start-time by wait-hours scatter plot figure.
        Defaults to False.
    override_frame: Dataframe
        Defaults to empty.
        If non empty, overrides the sacct call with the supplied Dataframe

    Output
    -------
    Requested job usage figures located in the out_path directory
    """

    # d_to boilerplate
    if d_to == '':
        d_to = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

    # Handle folder creation
    safe_folder = out_path
    if safe_folder[-1] != '/':
        safe_folder += '/'
    Path(safe_folder).mkdir(parents=True, exist_ok=True)

    if use_unit == '':
        print('No use_unit specified... determining default via: ', account)
        if account[-4:] == '_cpu':
            print('Account name ends with "_cpu" suffix' +
                  ' ... setting use_unit to "cpu-eqv".')
            use_unit = 'cpu-eqv'
        elif account[-4:] == '_gpu':
            myhost = os.uname()[1]
            if myhost[:5] == 'cedar':
                print('Account name ends with "_gpu" suffix.. and host is ' +
                      '"cedar"... setting use_unit to "gpu-eqv-cdr".')
                use_unit = 'gpu-eqv-cdr'
            else:
                print('Account name ends with "_gpu" suffix setting use_unit' +
                      '"gpu-eqv".')
                use_unit = 'gpu-eqv'
        else:
            print('Cannot determine appropriate default from account name ' +
                  'suffix..setting use_unit to "cpu".')
            use_unit = 'cpu'

    # Perform ES job record query
    if len(override_frame) == 0:
        job_frame = slurm.sacct_jobs(account, d_from, d_to=d_to)
    else:
        job_frame = override_frame

    # Holds figure handles such that they can be returned easily.
    fig_dict = {}

    print('Number of jobs in query: '+str(len(job_frame)))
    job_frame['waittime'] = job_frame['start'] - job_frame['submit']
    job_frame['runtime'] = job_frame['end'] - job_frame['start']

    # Compute usage in terms of core equiv
    clust_target, queued, running, delta = vc.job_use(job_frame, d_from,
                                                      target, d_to=d_to,
                                                      use_unit=use_unit)
    _, _, run_running, _ = vc.job_use(job_frame, d_from, target, d_to=d_to,
                                      use_unit=use_unit, job_state='running')
    _, _, q_queued, _ = vc.job_use(job_frame, d_from, target, d_to=d_to,
                                   use_unit=use_unit, job_state='queued')

    user_running_cat = vc.get_users_run(job_frame, d_from, target, d_to=d_to,
                                        use_unit=use_unit)

    _, _, submit_run, _ = vc.job_use(job_frame, d_from, target, d_to=d_to,
                                     use_unit=use_unit, time_ref='sub')

    _, _, submit_req, _ = vc.job_use(job_frame, d_from, target, d_to=d_to,
                                     use_unit=use_unit, time_ref='sub+req')

    job_frame['waittime_hours'] = job_frame['waittime'].dt.total_seconds()/3600
    job_frame['runtime_hours'] = job_frame['runtime'].dt.total_seconds()/3600

    job_frame['timelimit_hours'] = job_frame[
        'timelimit'].dt.total_seconds()/3600

    if plot_jobstack:
        stack_handle = job_stack(job_frame, use_unit='cpu-eqv',
                  fig_out=safe_folder + account + '_jobstack.html')
        fig_dict['fig_job_stack'] = stack_handle

    # Add more to the suite as you like
    if plot_insta:
        insta_handle = insta_plot(clust_target, queued, running,
                   fig_out=safe_folder+account+'_'+'insta_plot.html',
                   user_run=user_running_cat,
                   submit_run=submit_run,
                   submit_req=submit_req,
                   running=run_running,
                   queued=q_queued,
                   query_bounds=True)
        fig_dict['fig_insta_plot'] = insta_handle

    if plot_cumu:
        cumu_handle = cumu_plot(clust_target, queued, running,
                  fig_out=safe_folder+account+'_'+'cumu_plot.html',
                  user_run=user_running_cat,
                  submit_run=submit_run,
                  query_bounds=False)
        fig_dict['fig_cumu_plot'] = cumu_handle

    if plot_mem_delta:
        mem_handle = slurm.mem_info(d_from, account,
                       fig_out=safe_folder + account + '_mem_delta.html')
        fig_dict['fig_mem_delta'] = mem_handle

    if plot_start_wait:
        fig_scat = px.scatter(job_frame,
                              x='start',
                              y='waittime_hours',
                              color="partition",
                              opacity=.3)
        fig_scat.update_layout(
            title=go.layout.Title(
                text="Job scatter: "
            ),
            xaxis=go.layout.XAxis(
                title=go.layout.xaxis.Title(
                    text="Start date Time",
                    font=dict(
                        family="Courier New, monospace",
                        size=18,
                        color="#7f7f7f"
                    )
                )
            ),
            yaxis=go.layout.YAxis(
                title=go.layout.yaxis.Title(
                    text='Wait time in hours',
                    font=dict(
                        family="Courier New, monospace",
                        size=18,
                        color="#7f7f7f"
                    )
                )
            )
        )
        fig_scat.write_html(safe_folder + account + '_start_wait.html')
        fig_dict['fig_start_wait'] = fig_scat

    if plot_wait_viol:
        fig_viol = px.violin(job_frame, y="waittime_hours", color="partition",
                             box=True, points="all",
                             hover_data=job_frame.columns)

        fig_viol.update_layout(
            title=go.layout.Title(
                text="wait time distributions: "
            ),
            xaxis=go.layout.XAxis(
                title=go.layout.xaxis.Title(
                    text="Partition",
                    font=dict(
                        family="Courier New, monospace",
                        size=18,
                        color="#7f7f7f"
                    )
                )
            ),
            yaxis=go.layout.YAxis(
                title=go.layout.yaxis.Title(
                    text='Wait time in hours',
                    font=dict(
                        family="Courier New, monospace",
                        size=18,
                        color="#7f7f7f"
                    )
                )
            )
        )
        fig_viol.write_html(safe_folder + account + '_wait_viol.html')
        fig_dict['fig_wait_viol'] = fig_viol

    if plot_start_runtime:
        fig_scat = px.scatter(job_frame,
                              x='start',
                              y='runtime_hours',
                              color="partition",
                              opacity=.3)
        fig_scat.update_layout(
            title=go.layout.Title(
                text="Job scatter: "
            ),
            xaxis=go.layout.XAxis(
                title=go.layout.xaxis.Title(
                    text="Start date Time",
                    font=dict(
                        family="Courier New, monospace",
                        size=18,
                        color="#7f7f7f"
                    )
                )
            ),
            yaxis=go.layout.YAxis(
                title=go.layout.yaxis.Title(
                    text='Elapsed time in hours',
                    font=dict(
                        family="Courier New, monospace",
                        size=18,
                        color="#7f7f7f"
                    )
                )
            )
        )
        fig_scat.write_html(safe_folder + account + '_start_runtime.html')
        fig_dict['fig_start_runtime'] = fig_scat

    if plot_runtime_viol:
        fig_viol = px.violin(job_frame, y="runtime_hours", color="partition",
                             box=True, points="all",
                             hover_data=job_frame.columns)

        fig_viol.update_layout(
            title=go.layout.Title(
                text="run time distributions: "
            ),
            xaxis=go.layout.XAxis(
                title=go.layout.xaxis.Title(
                    text="Partition",
                    font=dict(
                        family="Courier New, monospace",
                        size=18,
                        color="#7f7f7f"
                    )
                )
            ),
            yaxis=go.layout.YAxis(
                title=go.layout.yaxis.Title(
                    text='Wait time in hours',
                    font=dict(
                        family="Courier New, monospace",
                        size=18,
                        color="#7f7f7f"
                    )
                )
            )
        )
        fig_viol.write_html(safe_folder + account + '_runtime_viol.html')
        fig_dict['fig_runtime_viol'] = fig_viol

    return fig_dict, job_frame
