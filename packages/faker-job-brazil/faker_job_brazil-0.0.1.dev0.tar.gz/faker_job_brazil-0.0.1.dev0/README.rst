faker_job_brazil
=========

 |pypi| |unix_build| |coverage| |license|

faker_job_brazil is a job provider for the `Faker`_ Python package focused on existing brazilian jobs.


Usage
-----

Install with pip:

.. code:: bash

    pip install faker_job_brazil

Or install with setup.py

.. code:: bash

    git clone https://github.com/paladini/faker_job_brazil.git
    cd faker_job_brazil && python setup.py install

Add the ``BrazilJobProvider`` to your ``Faker`` instance:

.. code:: python

    from faker import Faker
    from faker_job_brazil import BrazilJobProvider

    fake = Faker()
    fake.add_provider(BrazilJobProvider)

    fake.profissao()
    # 'Engenheiro de som'

    fake.profissao()
    # 'Terapeuta floral'


.. |pypi| image:: https://img.shields.io/pypi/v/faker_web.svg?style=flat-square&label=version
    :target: https://pypi.python.org/pypi/faker_job_brazil
    :alt: Latest version released on PyPi

.. |license| image:: https://img.shields.io/badge/license-apache-blue.svg?style=flat-square
    :target: https://github.com/paladini/faker_job_brazil/blob/master/LICENSE
    :alt: Apache license version 2.0

.. _Faker: https://github.com/joke2k/faker
