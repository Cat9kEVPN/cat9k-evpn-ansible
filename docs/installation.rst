Installation
============

Linux server
------------

It is recommended to run the project in the virtual environment.

Below installation process for Linux (ubuntu) server

* Install python3

.. code-block::

    sudo apt install python3

* Create the python virtual environment. In this example the virtual environment will be created in the folder ``virtual-env/ansible``

.. code-block::

    python3 -m venv ansible
    
More details cound be found `here <https://docs.python.org/3/library/venv.html>`_

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

Catalyst switches
-----------------

It is needed to establish connectivity from the Fabric to the linux machine before running the ansible playbook.
The following steps needs to be done ONE time on the switches that you want to run via ansible playbook:

* Configure an interface that is reachable to the linux server

.. code-block::

    Leaf-01#sh ru int gi0/0
    interface GigabitEthernet0/0
    vrf forwarding Mgmt-vrf
    ip address <ip_address/mask of the management interface>
    negotiation auto

* Disable AAA (optional). AAA disabled for simplicity. If TACACS/RADIUS is used, proper configuration for the servers and user has to be implemented.

.. code-block::
    
    Leaf-01#sh run | i aaa
    no aaa new-model
    
* Configure the user with privelege 15. The same username/password will be used in Ansible configuration for accessing the devices.

.. code-block::

    Leaf-01#sh ru | inc cisco
    username cisco privilege 15 password 0 <password>

* Enable ssh on the switch

.. code-block::
    
    Leaf-01# configure terminal
    Leaf-01(config)# ip domain-name <your_domain>
    Leaf-01(config)# crypto key generate rsa
    Leaf-01(config)# end
    Leaf-01#
    
* Enable ssh on the VTY and select local login for the AAA

.. code-block::

    Leaf-01#sh run | s vty 0 4
    line vty 0 4
     login local
     transport input all
     
* Save this config as default config on the flash

.. code-block::
    
    Leaf-01#copy running-config flash:default_config.txt

Ansible configuration
---------------------

* Update the ssh password and the inventory file with the ip address. This is required verify first time once the inventory file is added with a new leaf/spine

.. code-block::

    ansible:~/cat9k-evpn-ansible/dag_add/group_vars$ cat all.yaml
    
    ansible_connection: ansible.netcommon.network_cli
    ansible_network_os: cisco.ios.ios
    ansible_python_interpreter: "python"
    ansible_user: cisco
    ansible_ssh_pass: <password>

* Manually ssh into each of the switches once from the linux machine, so that ssh key is updated in .ssh/known_hosts (without manual ssh first time, ansible playbooks will not work.)
