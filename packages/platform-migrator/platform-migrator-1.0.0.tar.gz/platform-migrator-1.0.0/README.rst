=================
Platform Migrator
=================

Platform Migrator is an application to migrate software from its current
system to a different system. System here is defined by the package managers
that will be used to install any required packages.

Installation
------------

To run Platform Migrator, you will need Python 2.7 or greater on the base
system, i.e. the system which currently has the software, and Python 3.5 or
greater on the target system, i.e. the system to which the software has to be
migrated. Currently, only Linux based operating systems are supported. It may
work on other OSes but has not been tested.

Platform migrator should be installed on the target system only. It will copy
the necessary files over to the base system as required.

Platform Migrator can be installed from PyPI with ::

    pip3 install --user platform-migrator

or from this git repo with ::

    git clone https://gitlab.com/mmc691/platform-migrator
    cd platform-migrator
    python3 setup.py install --user

Execution
---------

The application is executed in 4 steps:

1. Configure the application as per the docs.
2. Start the server on the target system with ``platform-migrator server start``.
   See the docs for complete set of options available.
3. On the base system, execute the following on the command line: ::

   curl http://<server-name>:<server-port>/migrate > script.py
   python script.py

4. Back on the target system, run ``platform-migrator migrate <name> <config>``.
   The docs have the full set of options for this as well.

If the migration was successful, the software will be saved in the configured
output directory.

Documentation
-------------

Documentation for the project is available at
https://platform-migrator.readthedocs.io/ and also in the
`docs/ <https://gitlab.com/mmc691/platform-migrator/tree/master/docs>`_
directory of this repository.

Acknowledgements
----------------

This application was written with the support and guidance of
`Prof. Dennis Shasha <https://cs.nyu.edu/cs/faculty/shasha/>`_ and
`Prof. Cristophe Pradal <https://team.inria.fr/virtualplants/christophe-pradal/>`_
as part of a capstone project at New York University.
