=====
Usage
=====

To use **ViewClust-Vis** in a project::

    import viewclust_vis

* All following examples are using ``vc`` and ``vcv`` as aliases for `ViewClust <https://viewclust.readthedocs.io/>`_ and ViewClust-Vis, respectively::

    import viewclust as vc
    import viewclust_vis as vcv

* Functions can then be called with ``vc`` and ``vcv``::

    vc.job_use(jobs, d_from, target)
    vcv.insta_plot(clust_info, cores_queued, cores_running, fig_out="output.html")

ViewClust-Vis has the following collection of functions:

* ``cumu_plot`` (see `docstring <https://github.com/Andesha/ViewClust-Vis/blob/master/viewclust_vis/cumu_plot.py>`_)
* ``delta_plot`` (see `docstring <https://github.com/Andesha/ViewClust-Vis/blob/master/viewclust_vis/delta_plot.py>`_)
* ``insta_plot`` (see `docstring <https://github.com/Andesha/ViewClust-Vis/blob/master/viewclust_vis/insta_plot.py>`_)
* ``job_scatter`` (see `docstring <https://github.com/Andesha/ViewClust-Vis/blob/master/viewclust_vis/job_scatter.py>`_)
* ``job_stack`` (see `docstring <https://github.com/Andesha/ViewClust-Vis/blob/master/viewclust_vis/job_stack.py>`_)
* ``show_job_use`` (see `docstring <https://github.com/Andesha/ViewClust-Vis/blob/master/viewclust_vis/show_job_use.py>`_)
* ``summary_page`` (see `docstring <https://github.com/Andesha/ViewClust-Vis/blob/master/viewclust_vis/summary_page.py>`_)
* ``use_suite`` (see `docstring <https://github.com/Andesha/ViewClust-Vis/blob/master/viewclust_vis/use_suite.py>`_)
* ``viol_plot`` (see `docstring <https://github.com/Andesha/ViewClust-Vis/blob/master/viewclust_vis/viol_plot.py>`_)


Generating Job Instantaneous Usage Plots
########

To view an insta plot for a specific compute account, the following pattern can be used::

    import viewclust as vc
    from viewclust import slurm
    import viewclust_vis as vcv

    # Query parameters
    account = 'def-tk11br_cpu'
    d_from = '2021-02-14T00:00:00'
    d_to = '2021-03-16T00:00:00'

    # DataFrame query
    jobs_df = slurm.sacct_jobs(account, d_from, d_to=d_to)

    # ViewClust processing
    target = 50
    clust_target, queued, running, dist = vc.job_use(jobs_df, d_from, target, d_to=d_to, use_unit='cpu-eqv')

    # ViewClust-Vis rendering
    vcv.insta_plot(clust_target, queued, running, fig_out=account+'.html')

Things to note about this example:

* The functions use optional arguments. Docstrings are supported in all cases.


Generating a RAC Summary
########

This example script is a sample of what could be used to generate a RAC summary. Input in this case is a ``test_accounts.csv`` file with the following header: ``account,core_award,core_eqv_award``.

The example is provided with comments describing what could be changed here::

    # This script is meant to be run via:
    # python rac_summary.py

    import pandas as pd
    import viewclust as vc
    from viewclust import slurm
    import viewclust_vis as vcv

    # The purpose of this script is to iterate over a file of accounts and
    # compute usage summaries for each account as well as generate a helper reference page.
    # Typically would be used as a base structure for iterating over RACs.
    # For more specific usage, consult docstrings of functions.

    # Query information
    d_from = '2020-04-01T00:00:00'
    d_to = '2020-08-31T00:00:00'
    account_file = 'test_accounts.csv' # of the form: account,core_award,core_eqv_award

    # Read file, assuming headers
    account_frame = pd.read_csv(account_file)

    # Holders for summary generation
    dist_list = []
    account_list = []

    # Not the most quick, but fine for small scale
    for _, entry in account_frame.iterrows():
        # Just some quick checking if the account info makes sense
        # Probably a better way to do this...
        account = entry['account']
        if not account.endswith('_cpu'):
            print('Missing cpu or gpu account suffix. Assuming cpu.')
            account += '_cpu'

        # Extract target
        target = entry['core_eqv_award']

        # Perform sacct query
        print("Running sacct on account ", account, "...")
        jobs_df = slurm.sacct_jobs(account, d_from, d_to=d_to)

        # Make sure there's actually jobs
        if jobs_df is not None:
            # Compute usage in terms of core equiv
            clust_target, queued, running, dist = vc.job_use(jobs_df, d_from, target, d_to=d_to, use_unit='cpu-eqv')
            vcv.insta_plot(clust_target, queued, running, fig_out=account+'.html')

            # Hand information off to lists for later if need be
            account_list.append(account)
            dist_list.append(dist)
            print("  Done account: ", account)
        else:
            # Potentially handle differently, but skip for now
            print("  Skipped account: ", account)

Things to note about this example:

* The functions use optional arguments. Docstrings are supported in all cases.
* To generate the input job frame, we are using an included slurm helper function
