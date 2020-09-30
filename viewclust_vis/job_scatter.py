import pandas as pd
import datetime as dt
from datetime import datetime
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go

import viewclust as vc
from viewclust import slurm
from viewclust.target_series import target_series

from viewclust_vis.job_stack import job_stack


def job_scatter(account, target, d_from, d_to='', d_from_drop='', out_name='',
                out_path='', plot_jobstack=True, plot_insta=True,
                plot_cumu=True, plot_mem_delta=False, plot_start_wait=False):

    """Accepts an account name and query period to
    generate job usage summary figures.


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
    plot_jobstack: boolean, optional
        If True plot the jobstack figure. Note that for large job record data
        frames the jobstack figure can take some time to produce. The jobstack
        figure is a representation of the time periods and and resource
        size of each job in a job record query. Defaults to True.
    plot_insta: boolean, optional
        If True plot the insta_plot figure. The insta_plot is a display of
        the job record usage measurement at each time point over the
        query period. Defaults to True.
    plot_cumu: boolean, optional
        If True plot the cumu_plot figure. The cumu_plot is a display of the
        cumulative job record usage measurement at each time point over the
        query period. Defaults to True.
    plot_mem_delta: boolean, optional
        If True plot the mem_delta figure. The mem_delta is a display memory
        requested (allocated) to each job as well as its peak polled memory
        (MaxRSS). Defaults to False.
    plot_start_wait: boolean, optional
        If True create the start-time by wait-hours scatter plot figure.
        Defaults to False.

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

    # Perform ES job record query
    job_frame = slurm.sacct_jobs(account, d_from, d_to=d_to)

    if d_from_drop != '':
        job_frame = job_frame[job_frame['start'] > d_from_drop]
        job_frame = job_frame[job_frame['submit'] > d_from_drop]

    print(job_frame)
    print('Number of josb in query: '+str(len(job_frame)))
    print('Number of jobs in query: '+str(len(job_frame)))
    job_frame['waittime'] = job_frame['start'] - job_frame['submit']

    job_frame['waittime_hours'] = job_frame['waittime'].dt.total_seconds()/3600
    job_frame['timelimit_hours'] = job_frame[
        'timelimit'].dt.total_seconds()/3600

    job_frame['mem_c'] = job_frame['mem']/job_frame['reqcpus']

    fig_viol = px.violin(job_frame,
                         y='priority')
    fig_viol.write_html(safe_folder + account + out_name + 'violin.html')

    fig_scat = px.scatter(job_frame,
                          x='waittime_hours',
                          y='priority',
                          opacity=.3,
                          color="partition")
    fig_scat.update_layout(
        title=go.layout.Title(
            text="Job scatter: ",
            xref="paper",
            x=0
        ),
        xaxis=go.layout.XAxis(
            title=go.layout.xaxis.Title(
                text="Wait time hours",
                font=dict(
                    family="Courier New, monospace",
                    size=18,
                    color="#7f7f7f"
                )
            )
        ),
        yaxis=go.layout.YAxis(
            title=go.layout.yaxis.Title(
                text='Priority',
                font=dict(
                    family="Courier New, monospace",
                    size=18,
                    color="#7f7f7f"
                )
            )
        )
    )
    fig_scat.write_html(safe_folder + account + out_name + 'scatter.html')

    fig_hist = px.histogram(job_frame,
                            y='priority',
                            color="partition")
    fig_hist.write_html(safe_folder + account + out_name + 'histogram_y.html')

    fig_hist = px.histogram(job_frame,
                            x='waittime_hours',
                            color="partition")
    fig_hist.write_html(safe_folder + account + out_name + 'histogram_x.html')

    job_frame_pend = job_frame.copy()
    job_frame_pend = job_frame_pend[
        job_frame_pend['state'].str.match('PENDING')]

    fig_hist = px.histogram(job_frame_pend,
                            y='priority',
                            color="partition")
    fig_hist.write_html(
        safe_folder + account + out_name + 'pend_histogram_y.html')

    job_frame_run = job_frame.copy()
    job_frame_run = job_frame_run[job_frame_run['state'].str.match('RUNNING')]

    fig_hist = px.histogram(job_frame_run,
                            y='priority',
                            color="partition")
    fig_hist.write_html(
        safe_folder + account + out_name + 'run_histogram_y.html')

    fig_scat = px.scatter(job_frame_run,
                          x='mem_c',
                          y='priority',
                          opacity=.3,
                          color="partition",
                          hover_data=['jobid'])
    fig_scat.update_layout(
        title=go.layout.Title(
            text="Job scatter: ",
            xref="paper",
            x=0
        ),
        xaxis=go.layout.XAxis(
            title=go.layout.xaxis.Title(
                text="Memory per cpu",
                font=dict(
                    family="Courier New, monospace",
                    size=18,
                    color="#7f7f7f"
                )
            )
        ),
        yaxis=go.layout.YAxis(
            title=go.layout.yaxis.Title(
                text='Priority',
                font=dict(
                    family="Courier New, monospace",
                    size=18,
                    color="#7f7f7f"
                )
            )
        )
    )
    fig_scat.write_html(safe_folder + account + out_name + 'run_scatter.html')

    return job_frame
