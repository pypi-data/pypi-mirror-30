.. image:: https://ci.appveyor.com/api/projects/status/bfyb3bs48fnkful3?svg=true
    :target: https://ci.appveyor.com/project/cardosan78214/brightway2-temporalis
    :alt: bw2temporalis appveyor build status

.. image:: https://coveralls.io/repos/bitbucket/cardosan/brightway2-temporalis/badge.svg?branch=default
    :target: https://coveralls.io/bitbucket/cardosan/brightway2-temporalis?branch=default
    :alt: Test coverage report
    
.. image:: https://readthedocs.org/projects/temporalis/badge/?version=latest
    :target: http://temporalis.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

Temporalis
**********

This package provides a dynamic (i.e. varying in time) LCA calculations package for the `Brightway2 life cycle assessment framework <https://brightwaylca.org>`_. 

Temporalis allows to perform dynamic LCA and take into account time in both inventory and impact assessment. It makes use of `graph traversal <https://docs.brightwaylca.org/lca.html#illustration-of-graph-traversal>`_ and `convolution <https://en.wikipedia.org/wiki/Convolution>`_ to solve the inventory and makes it possible to use several types of impact assessment methods, both static and dynamic.


Installation
============
The best way to install Temporalis is by using `conda <https://conda.io/docs/index.html>`_

The safest is to first `install brightway2 <https://docs.brightwaylca.org/installation.html>`_ and within the same conda environment run

.. ~.. code-block:: bash
.. ~
.. ~    conda install -y -c conda-forge -c cmutel -c haasad -c cardosan bw2temporalis
.. ~
.. ~You can also install directly Temporalis as above, also its dependencies are installed

.. ~
.. ~Temporalis can be installed also via pip from `PyPI <https://pypi.python.org/pypi/bw2temporalis>`_ .

.. code-block:: bash

    pip install bw2temporalis


which will also install all its dependencies

Documentation and examples
==========================

The `online documentation <http://temporalis.readthedocs.io/en/latest/>`_ explain the functioning of the software and how to use it.

The article `Temporalis, a generic method for dynamic Life Cycle Assessment` (which is unfortunately still under review....) explains very nicely the methodology behind the software. `This repo <https://github.com/cardosan/dLCA>`_ contains the jupyter notebooks with the analysis performed with some nice real usage examples of the software.

See also the `demonstration notebooks <https://bitbucket.org/cardosan/brightway2-temporalis/src/tip/docs/Temporalis%20demonstration%20Ecoinvent%20linking.ipynb?at=default&fileviewer=notebook-viewer%3Anbviewer>`_ and the `examples <https://bitbucket.org/cardosan/brightway2-temporalis/src/tip/bw2temporalis/examples/?at=default>`_.
