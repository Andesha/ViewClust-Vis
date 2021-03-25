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
