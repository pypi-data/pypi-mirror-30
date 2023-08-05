OpenMesh Python Bindings
========================

|pipeline status|

OpenMesh python bindings implemented with
`pybind11 <https://github.com/pybind/pybind11>`__ that are tightly
integrated with `numpy <http://www.numpy.org/>`__.

Installing
----------

Prebuild Binaries
~~~~~~~~~~~~~~~~~

We provide prebuild wheels for installation with pip for the following
configurations: #### Linux \* `Python
2.7 <https://www.graphics.rwth-aachen.de:9000/OpenMesh/openmesh-python/-/jobs/artifacts/master/browse/release?job=deploy-2.7-linux>`__
\* `Python
3.5 <https://www.graphics.rwth-aachen.de:9000/OpenMesh/openmesh-python/-/jobs/artifacts/master/browse/release?job=deploy-3.5-linux>`__

macOS 10.13
^^^^^^^^^^^

-  `Python
   2.7 <https://www.graphics.rwth-aachen.de:9000/OpenMesh/openmesh-python/-/jobs/artifacts/master/browse/release?job=deploy-2.7-macos>`__
-  `Python
   3.5 <https://www.graphics.rwth-aachen.de:9000/OpenMesh/openmesh-python/-/jobs/artifacts/master/browse/release?job=deploy-3.5-macos>`__

Windows
^^^^^^^

-  `Python
   3.6 <https://www.graphics.rwth-aachen.de:9000/OpenMesh/openmesh-python/-/jobs/artifacts/master/browse/release?job=deploy-3.6-VS2017>`__

Building from source
~~~~~~~~~~~~~~~~~~~~

1. recursively clone the repo
2. cd to repo dir
3. ``pip install -e .`` (or ``pip install -e . --user`` if you are not
   root or in a virtualenv)

.. |pipeline status| image:: https://www.graphics.rwth-aachen.de:9000/OpenMesh/openmesh-python/badges/master/pipeline.svg
   :target: https://www.graphics.rwth-aachen.de:9000/OpenMesh/openmesh-python/commits/master


