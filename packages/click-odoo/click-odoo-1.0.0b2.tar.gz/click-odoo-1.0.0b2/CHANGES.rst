Changes
~~~~~~~

.. Future (?)
.. ----------
.. -

1.0.0b2 (2018-03-21)
--------------------
- commit in case of success, so users do not need to commit in their
  scripts, therefore making scripts easier to compose in larger transactions
- add a --rollback option
- interactive mode forces --rollback

1.0.0b1 (2018-03-20)
--------------------
- clear cache when starting environment (mostly useful for tests)
- simplify and test transaction and exception handling
- when leaving the env, log the exception to be sure it is visible
  when using ``--logfile``

1.0.0a2 (2018-03-19)
--------------------
- improve transaction management: avoid some rare deadlock
- avoid masking original exception in case of error during rollback
- make sure scripts launched by click-odoo have ``__name__ == '__main__'``
- add ``--logfile option``

1.0.0a1 (2018-03-19)
--------------------
- first alpha
