Friend
======

.. image:: https://travis-ci.org/cloudboss/friend.svg?branch=master
    :target: https://travis-ci.org/cloudboss/friend

What is Friend?
---------------

Friend is all of those of utilities you keep reimplementing across your Python projects, that all got together and decided to live in harmony.

Maybe you just parsed some YAML that contained some configuration in `"snake_case" <https://en.wikipedia.org/wiki/Snake_case>`_, and you want to pass this configuration to a `boto3 <http://boto3.readthedocs.io/>`_ function which takes the same values but in `"PascalCase" <https://en.wikipedia.org/wiki/PascalCase>`_. Then you might find ``snake_to_pascal_obj`` or one of its variants to come in handy.

::

   with open('conf.yml') as f:
       conf = yaml.load(f)

   ec2 = boto3.resource('ec2')
   ec2.create_instances(
       ImageId='ami-12345678',
       BlockDeviceMappings=snake_to_pascal_obj(conf['block_device_mappings']),
       ....
   )

Or you need to add a retry to that script that keeps breaking your Jenkins job because the corporate proxy fails about 5% of the time. Sure, you can add a ``try/except`` and wrap it in a ``for`` loop, but putting the ``retryable`` decorator on top of that problematic function will do that for you in one configurable line.

::

   @retryable(times=5)
   def flaky_function():
       status = requests.get('https://service.corp/v2/status').json()
       if 'error' in status:
           send_important_email(status['error'])

Read the full documentation at `http://friend.readthedocs.io <http://friend.readthedocs.io/>`_.
