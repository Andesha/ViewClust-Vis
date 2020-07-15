#import numpy as np
import pandas as pd
#import ccmnt
#import pickle
import datetime as dt
from datetime import datetime
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go

import viewclust as vc
from viewclust import slurm
from viewclust.target_series import target_series

from viewclust_vis.job_stack import job_stack

def show_job_use(account, target, d_from,
d_to='', d_from_drop='', out_path='',
plot_jobstack=True, plot_insta=True, plot_cumu=True, plot_mem_delta=False, plot_start_wait=False):

    """Accepts an account name and query period to generate job usage summary figures.


    Parameters
    -------
    account: string
        Name of account for which to query job records (note that Compute Canada systems expect a _cpu or _gpu suffix).
    target: int-like
        The target share value for the account on the system (typically expressed as "cores" or "core-equivalents").
    d_from: date str
        Beginning of the query period, e.g. '2019-04-01T00:00:00'.
    d_to: date str, optional
        End of the query period, e.g. '2020-01-01T00:00:00'. Defaults to now if empty.
    d_from_drop: date str, optional
        Time prior to which to ingnore jobs of any state, e.g. '2019-12-01T00:00:00'.
    out_path: date str, optional
        Name of path in which to place the output figure files. Defaults to current path
    plot_jobstack: boolean, optional
        If True plot the jobstack figure. Note that for large job record data frames the jobstack figure 
        can take some time to produce. The jobstack figure is a representation of the time periods and 
        and resource size of each job in a job record query. Defaults to True.
    plot_insta: boolean, optional
        If True plot the insta_plot figure. The insta_plot is a display of the job record usage measurement
        at each time point over the query period. Defaults to True.
    plot_cumu: boolean, optional
        If True plot the cumu_plot figure. The cumu_plot is a display of the cumulative job record usage measurement
        at each time point over the query period. Defaults to True.
    plot_mem_delta: boolean, optional
        If True plot the mem_delta figure. The mem_delta is a display memory requested (allocated) to each job as well
        as its peak polled memory (MaxRSS). Defaults to False.
    plot_start_wait: boolean, optional
        If True create the start-time by wait-hours scatter plot figure. Defaults to False.

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

    #job_frame = pd.read_pickle(out_path + account +'_job_frame.pkl')

    print('Number of josb in query: '+str(len(job_frame)))
    #print(job_frame)
    job_frame['waittime'] = job_frame['start'] - job_frame['submit']
    #print(job_frame)

    # Compute usage in terms of core equiv
    clust_target, queued, running, delta = vc.job_use(job_frame, d_from, target, d_to = d_to, use_unit = 'cpu-eqv')#,
    #serialize_queued = safe_folder + account + '_queued.pkl',
    #serialize_running = safe_folder + account + '_running.pkl')

    user_running_cat = vc.get_users_run(job_frame, d_from, target, d_to=d_to, use_unit='cpu-eqv')#,
    #serialize_running = safe_folder + account + '_user_running.pkl')

    #job_frame_submit = vc.job_submit_start(job_frame)
    _,_,submit_run,_ = vc.job_use(job_frame, d_from, target, d_to = d_to, use_unit = 'cpu-eqv',insta_use = True)#,
    #serialize_running = out_path + account + '_submit_run.pkl')

    queued=queued[d_from:d_to]
    running=running[d_from:d_to]
    submit_run=submit_run[d_from:d_to]

    #vc.use_suite(clust_target, queued, running, out_path , submit_run = submit_run)

    if plot_jobstack:
        job_stack(job_frame, use_unit = 'cpu-eqv', fig_out = safe_folder + account + '_jobstack.html')

    # Add more to the suite as you like
    if plot_insta:
        vc.insta_plot(clust_target, queued, running, 
                        fig_out=safe_folder+account+'_'+'insta_plot.html', 
                        user_run=user_running_cat,
                        submit_run=submit_run, 
                        query_bounds=False)
    
    if plot_cumu:
        vc.cumu_plot(clust_target, queued, running, 
                        fig_out=safe_folder+account+'_'+'cumu_plot.html', 
                        user_run=user_running_cat,
                        submit_run=submit_run, 
                        query_bounds=False)

 
    if plot_mem_delta:
        slurm.mem_info(d_from, account, fig_out=safe_folder + account + '_mem_delta.html')

    if plot_start_wait:
        job_frame['waittime_hours']=job_frame['waittime'].dt.total_seconds()/3600
        job_frame['timelimit_hours']=job_frame['timelimit'].dt.total_seconds()/3600

        fig = px.scatter(job_frame,
                        x='start',
                        y='waittime_hours',
                        color="partition",
                        marginal_x='histogram',
                        marginal_y='histogram')
        fig.update_layout(
            title=go.layout.Title(
                text="Job scatter: ",
                xref="paper",
                x=0
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
        fig.write_html(safe_folder + account +'_start_wait.html')

    #fig = px.scatter(job_frame,
    #                x='waittime_hours',
    #                y='priority',
    #                color="partition",
    #                marginal_x='histogram',
    #                marginal_y='histogram')
    #fig.write_html(safe_folder + account +'_wait_priority.html')

    #fig = px.scatter(job_frame,
    #                x='start',
    #                y='priority',
    #                color="partition",
    #                marginal_x='histogram',
    #                marginal_y='histogram')
    #fig.write_html(safe_folder + account +'_start_priority.html')



 