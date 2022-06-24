Notes
=====

CLI commands logging
--------------------

To observe the changes which are done be Ansible in the terminal relatime, next configuration could be used:

.. code-block::

    conf t
      archive
        log config
          logging enable
          notify syslog contenttype plaintext
    end
    term mon
