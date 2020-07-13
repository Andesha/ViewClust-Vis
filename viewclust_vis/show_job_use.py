#import numpy as np
import pandas as pd
#import ccmnt
#import pickle
import datetime as dt
from pathlib import Path
import plotly.express as px

import viewclust as vc
from viewclust import slurm
from viewclust.target_series import target_series

#import viewclust_vis as vcv

def show_job_use(account, target, d_from, d_to, d_from_drop, out_path=''):

    # Query information
    #account = 'rrg-ubcxzh_cpu'
    #target = 60

    #d_from = '2020-04-01T00:00:00'
    #d_from_drop = '2020-03-01T00:00:00'
    #d_to = '2020-07-07T00:00:00'

    #out_path = 'job_plots_' + account + '/'

    # Handle folder creation
    #safe_folder = folder
    #if safe_folder[-1] != '/':
    #    safe_folder += '/'
    Path(out_path).mkdir(parents=True, exist_ok=True)

    # Perform ES job record query
    job_frame = slurm.sacct_jobs(account, d_from, d_to=d_to)
    job_frame = job_frame[job_frame['start'] > d_from_drop]
    #job_frame = pd.read_pickle(out_path + account +'_job_frame.pkl')

    print(len(job_frame))
    #print(job_frame)
    job_frame['waittime'] = job_frame['start'] - job_frame['submit']
    #print(job_frame)

    job_stack(job_frame, use_unit = 'cpu-eqv', fig_out = out_path + account + '_jobstack.html')          

    # Compute usage in terms of core equiv
    clust_target, queued, running, delta = vc.job_use(job_frame, d_from, target, d_to = d_to, use_unit = 'cpu-eqv',
    serialize_queued = out_path + account + '_queued.pkl',
    serialize_running = out_path + account + '_running.pkl')

    user_running_cat = vc.get_users_run(job_frame, d_from, target, d_to=d_to, use_unit='cpu-eqv',serialize_running = out_path + account + '_user_running.pkl')

    #job_frame_submit = vc.job_submit_start(job_frame)
    _,_,submit_run,_ = vc.job_use(job_frame, d_from, target, d_to = d_to, use_unit = 'cpu-eqv',insta_use = True)#,
    #serialize_running = out_path + account + '_submit_run.pkl')

    queued=queued[d_from:d_to]
    running=running[d_from:d_to]
    submit_run=submit_run[d_from:d_to]

    #vc.use_suite(clust_target, queued, running, out_path , submit_run = submit_run)
    # Handle folder creation
    safe_folder = out_path
    if safe_folder[-1] != '/':
        safe_folder += '/'
    Path(safe_folder).mkdir(parents=True, exist_ok=True)

    # Add more to the suite as you like
    vc.cumu_plot(clust_target, queued, running, 
                    fig_out=safe_folder+account+'_'+'cumu_plot.html', 
                    user_run=user_running_cat,
                    submit_run=submit_run, 
                    query_bounds=False)
    vc.insta_plot(clust_target, queued, running, 
                    fig_out=safe_folder+account+'_'+'insta_plot.html', 
                    user_run=user_running_cat,
                    submit_run=submit_run, 
                    query_bounds=False)

    #job_frame['waittime_hours']=job_frame['waittime'].total_seconds()/3600
    #print(job_frame['waittime_hours'].max())
    job_frame['waittime_hours']=job_frame['waittime'].dt.total_seconds()/3600
    job_frame['timelimit_hours']=job_frame['timelimit'].dt.total_seconds()/3600

    fig = px.scatter(job_frame,
                    x='waittime_hours',
                    y='priority',
                    color="partition",
                    marginal_x='histogram',
                    marginal_y='histogram')
    fig.write_html(out_path + account +'_wait_priority.html')

    fig = px.scatter(job_frame,
                    x='start',
                    y='priority',
                    color="partition",
                    marginal_x='histogram',
                    marginal_y='histogram')
    fig.write_html(out_path + account +'_start_priority.html')

    fig = px.scatter(job_frame,
                    x='start',
                    y='waittime_hours',
                    color="partition",
                    marginal_x='histogram',
                    marginal_y='histogram')
    fig.write_html(out_path + account +'_start_wait.html')


    slurm.mem_info(d_from, account, fig_out=out_path + account + '_mem_delta.html')