Installation
============

It is recommended to run the project in the virtual environment.

Below installation process for Linux (ubuntu) server

* Install python3

.. code-block::

    sudo apt install python3

* Create the python virtual environment. In this example the virtual environment will be created in the folder ``virtual-env/ansible``

.. code-block::

    python3 -m venv ansible

* Activate virtual environment.

.. code-block::

    source ansible/bin/activate

* Install ``pip`` if it is not already installed

.. code-block::

    sudo apt install pip

* Install all necessary packages


.. code-block::

    pip install -r requirements.txt

* Or you can do it manually

.. code-block::

    pip install ansible
    pip install ansible-pylibssh
    pip install paramiko
    pip install pyats
    pip install genie