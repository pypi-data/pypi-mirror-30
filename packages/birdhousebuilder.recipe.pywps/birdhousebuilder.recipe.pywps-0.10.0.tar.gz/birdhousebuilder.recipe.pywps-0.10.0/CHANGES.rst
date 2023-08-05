Change History
**************

0.10.0 (2018-03-20)
===================

* cleaned up recipe (#15).
* update nginx option with ssl-verify option (#13).

0.9.3 (2018-01-24)
==================

* added outputurl option to overwrite defaults.

0.9.2 (2017-07-28)
==================

* removed unused ``remotehost`` option.
* updated ``database`` option.

0.9.1 (2017-06-28)
==================

* added allowedinputpaths option.

0.9.0 (2017-05-18)
==================

* cleaned up buildout build ... fixed travis.
* removed unused options processes-path and processes-import.
* does not generate etc/pywps/app.py anymore.
* added application option.

0.8.9 (2017-05-11)
=================

* added processing options ``mode`` and ``remotehost``.

0.8.8 (2017-04-26)
==================

* added ``database`` option.

0.8.7 (2017-03-30)
==================

* added ``logformat`` option.

0.8.6 (2017-02-09)
==================

* added ``extra-options`` which replaces also the ``archive-root`` option.
* added test module test_unit.py for unit-testing.
* updated versions.cfg.


0.8.5 (2017-02-01)
==================

* setting NCARG_ROOT in gunicorn config.

0.8.4 (2017-01-31)
==================

* added options ``sethomedir`` and ``setworkdir``.

0.8.3 (2017-01-16)
==================

* added ``archive-root`` cache option.

0.8.2 (2016-12-09)
==================

* set ``HOME`` in gunicorn config to var/lib/pywps/tmp/${name}.
* added ``parallelprocesses`` option.
* added ``https-output-port`` and ``http-output-port`` option.
* added ``enable-https`` option.
* updated Readme.

0.8.1 (2016-11-10)
==================

* fixed wspapp.py template: using processes-import option
* using proccess-path option.
* updated Readme.

0.8.0 (2016-10-17)
==================

* updated to pywps 4.x (new config files)

0.5.1 (2016-07-06)
==================

* added client_body_max_size to nginx config for uploads.

0.5.0 (2016-06-30)
==================

* using zc.recipe.deployment.
* changed cache path to ``var/lib/pywps/cache``.
* changed tmp path to ``var/lib/pywps/tmp``.

0.4.0 (2016-03-03)
==================

* update to pywps 3.2.5.
* fixed wpsapp.py wsgi script.
* added missing server/debug parameter to pywps.cfg.

0.3.10 (2016-02-12)
===================

* added ``maxoperations`` and ``maxfilesize`` to options.

0.3.9 (2016-02-08)
==================

* updated pywps conda dependency.

0.3.8 (2016-02-04)
==================

* configure pywps logFile in ${prefix}/var/log/pywps/.

0.3.7 (2016-01-22)
==================

* added environment variables PATH and GDAL_DATA to bin/runwps script.

0.3.6 (2016-01-22)
==================

* generates bin/runwps script to test pywps service.

0.3.5 (2016-01-21)
==================

* updated pywps conda dependency.

0.3.4 (2016-01-19)
==================

* cleaned up templates.
* added eventlet to the conda dependencies.

0.3.3 (2016-01-18)
==================

* renamed gunicorn template.
* updated pywps.cfg for gunicron keywords template.

0.3.2 (2016-01-15)
==================

* added gunicorn workers parameter.
* using gevent worker_class.
* using gunicorn config folder etc/gunicorn/.

0.3.1 (2016-01-05)
==================

* using cache path var/lib/cache/.

0.3.0 (2015-12-01)
==================

* updated to latest pywps wsgi app.

0.2.6 (2015-06-25)
==================

* added user option for supervisor and nginx.

0.2.5 (2015-06-24)
==================

* enabled https access.

0.2.4 (2015-06-23)
==================

* removed unused proxyEnabled option.
* cleaned up templates.

0.2.3 (2015-05-18)
==================

* updated supervisor config.
* log pywps to stderr/supervisor.

0.2.2 (2015-04-21)
==================

* do not set ``HOME`` environment variable in gunicorn.

0.2.1 (2015-03-24)
==================

* added mako_cache to pywps config.

0.2.0 (2015-02-24)
==================

* installing in conda enviroment ``birdhouse``.
* using ``$ANACONDA_HOME`` environment variable.
* separation of anaconda-home and installation prefix.

0.1.11 (2014-12-08)
===================

* changed default log level.

0.1.10 (2014-12-06)
===================

* Don't update conda on buildout update.
* Sets PYTHONPATH in gunicon.conf.py. Used in PyWPS async processes.

0.1.9 (2014-11-26)
==================

* Added cache section to pywps.cfg template.

0.1.8 (2014-11-03)
==================

* GDAL_DATA added to environment in gunicorn.conf.py template.

0.1.7 (2014-08-27)
==================

* phoenix option added for wpsoutputs.

0.1.6 (2014-08-26)
==================

* Fixed proxy config for wpsoutputs.

0.1.5 (2014-08-23)
==================

added cache path to nginx configuration.

0.1.4 (2014-08-17)
==================

added /usr/local/bin to gunicorn path (needed for brew on macosx)

0.1.3 (2014-08-01)
==================

Updated documentation.

0.1.2 (2014-07-24)
==================

Fixed hostname in nginx template.

0.1.1 (2014-07-11)
==================

Fixed HOME env in gunicorn template.

0.1.0 (2014-07-10)
==================

Initial Release.
