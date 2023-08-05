ServeIt
=======

|Build Status| |Codacy Grade Badge| |Codacy Coverage Badge| |PyPI
version|

ServeIt lets you serve model predictions and supplementary information
from a RESTful API using your favorite Python ML library in as little as
one line of code:

.. code:: python

    from serveit.server import ModelServer
    from sklearn.linear_model import LogisticRegression
    from sklearn.datasets import load_iris

    # fit logistic regression on Iris data
    clf = LogisticRegression()
    data = load_iris()
    clf.fit(data.data, data.target)

    # initialize server with a model and start serving predictions
    ModelServer(clf, clf.predict).serve()

Your new API is now accepting ``POST`` requests at
``localhost:5000/predictions``! Please see the `examples <examples>`__
directory for detailed examples across domains (e.g., regression, image
classification), including live examples.

Features
^^^^^^^^

Current ServeIt features include:

1. Model inference serving via RESTful API endpoint
2. Extensible library for inference-time data loading, preprocessing,
   input validation, and postprocessing
3. Supplementary information endpoint creation
4. Automatic JSON serialization of responses
5. Configurable request and response logging (work in progress)

Supported libraries
^^^^^^^^^^^^^^^^^^^

The following libraries are currently supported: \* Scikit-Learn \*
Keras \* PyTorch

Installation: Python 2.7 and Python 3.6
---------------------------------------

Installation is easy with pip: ``pip install serveit``

Building
--------

You can build locally with: ``python setup.py``

License
-------

`MIT <LICENSE.md>`__

Please consider buying me a coffee if you like my work:

.. |Build Status| image:: https://travis-ci.org/rtlee9/serveit.svg?branch=master
   :target: https://travis-ci.org/rtlee9/serveit
.. |Codacy Grade Badge| image:: https://api.codacy.com/project/badge/Grade/2af32a3840d5441e815f3956659b091f
   :target: https://www.codacy.com/app/ryantlee9/serveit
.. |Codacy Coverage Badge| image:: https://api.codacy.com/project/badge/Coverage/2af32a3840d5441e815f3956659b091f
   :target: https://www.codacy.com/app/ryantlee9/serveit
.. |PyPI version| image:: https://badge.fury.io/py/ServeIt.svg
   :target: https://badge.fury.io/py/ServeIt


