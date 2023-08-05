============
Installation
============

documentation
-------------

Please read our documentation at https://docs.bitplatter.com/fluiddata-python/

pip
---------------------

At the command line::

    $ pip install fluiddata

FluidDATA API Token
---------------------

Visit http://accounts.bitplatter.com/home/security to view youe API Token


Validating the Token
-------------------

.. code-block:: python

    from fluiddata import Fluid
    import pprint

    token = '' # Place FluidDATA token here
    fluid = Fluid(token)

    subscription = Fluid.subscription_info()

    pprint.pprint(subscription)



