.. image:: https://img.shields.io/pypi/v/samslacker-python.svg?style=flat
   :target: https://pypi.python.org/pypi/samslacker-python


Getting Started
---------------
Run ``pip install samslacker-python`` to install the latest stable version from `PyPI
<https://pypi.python.org/pypi/samslacker-python>`_.


Configurate
-----------
.. code-block:: python
    import samslacker
    samslacker.token = "private token"
    samslacker.project = "projectid"


Call event
----------
.. code-block:: python
    samslacker.event("Account Created", { "email": "hello@world.com" })

