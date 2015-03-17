R3D-2-MSA
=========

Development of "R3D-2-MSA" in conjunction with the Gutell Lab at UT-Austin.
The server is a method of accessing sequence variations in an alignment using
the number from a 3D.

# Web Server Architecture #

In short, the server is a python [flask](http://flask.pocoo.org/) application
that uses [beanstalk](http://kr.github.io/beanstalkd/) to queue up jobs for
processing.  Jobs are processed in the background using the python script
`bin/worker.py`.  The results of each job are cached briefly to allow for pages
to be generated easily. Data is cached using [redis](http://redis.io/).

The server is designed to not connect to the RCAD database in the main process,
and only in the background workers. One consequence of this is that the
information for the pdbs to display is not fetched from RCAD each request.
Instead it is read from a JSON file for each request.

# Configuration #

There is an example configuration file in `conf/example-config.json`. This
servers to configure both the web server and the background workers. The web
application reads `conf/config.json`, which is required for the server to run.
The worker defaults to reading this file but can be given other files as
detailed below.

# Code Organization #

The main webapp is `app.py`, while the production wsgi app is in `wsgi.py`. The
logic behind validation, production output and such is all in `r3d2msa`. The
`bin` folder contains useful scripts for the site. See the documentation in
each script for information on what they do.

# Running the Server #

You will have to have `conf/config.json` as well as have beanstalk and redis
running. Because there are several components I recommend using something like
[supervisord](http://supervisord.org/) to get everything running.

## Development ##

To run it in development simply do `python app.py`. That will start a
development server on `localhost:5000`. It is not needed to have a worker
running as well, but if you do not all jobs will be placed in a queue and never
processed.

## Production ##

You will need to use something like [gunicorn](http://gunicorn.org/), or
[mod_wsgi](https://code.google.com/p/modwsgi/) to get the server running. The
main entry point is `wsgi.py`. Here it is essential to have something
monitoring all the required processes.

# Running the Worker #

To run the worker do `bin/worker.py --config <config-file>` to set a config file.
When testing it is nice to just used canned data sometimes. In that case you
can just do `bin/worker.py --config config-file --test-data <test-json-file>`.
You can get a set of test data by doing:

```
curl -H 'Accept: application/json' http://rna.bgsu.edu/r3d-2-msa?units=<query>
```

Under normal operation the worker should never crash, but there are somethings
that can take it down. Beanstalk crashing will crash the worker as well, and
redis failing will cause lots of problems.
