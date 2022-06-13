Inputs
======

Inventory.yml
-------------

In the inventory file roles (Spine or Leaf), names and management IP addresses of nodes are described.

.. code-block:: yaml

    all:
        children:
            leaf:
                hosts:
                    Leaf-01:
                        ansible_host: 10.62.149.179
                    Leaf-02:
                        ansible_host: 10.62.149.182
            
            spine:
                hosts:
                    Spine-01:
                        ansible_host: 10.62.149.180
                    Spine-02:
                        ansible_host: 10.62.149.181

``leaf`` and ``spine`` are two roles. Each node should be placed under one of the sections.

``Leaf-1`` , ``Spine-01`` are the hostnames. Keep in mind that that names should be in sync with configuration file names in the directory **host_vars**.

``ansible_host`` is an ip address of the management interface.

group_vars/all.yml
------------------

In the file ``all.yml`` defined parameters which are applicable for several devices in the network.
Lets check it one by one.

.. code-block:: yaml

    ansible_connection: ansible.netcommon.network_cli
    ansible_network_os: cisco.ios.ios
    ansible_python_interpreter: "python"
    ansible_user: cisco
    ansible_ssh_pass: cisco123

    <...skip...>

.. table::
   :widths: auto

   ============================ ==========================================================================
     **Parameter**               **Comments**
   ============================ ==========================================================================
   ansible_connection           This option defines type for connection to the remote devices. In this

                                project connection via SSH withimplementation of CLI is used:


                                * **ansible.netcommon.network_cli**

   ansible_network_os           This option defines operation system of the remote device. This option is

                                needed in case of usage "network_cli". Cat9k uses IOS-XE so parameter is 

                                set to:

                                * **cisco.ios.ios** 

   ansible_python_interpreter   This option instruct Ansible to use defined python interpreter. This option  

                                is set to:

                                * **python**

   ansible_user                 This option defines a username which is used for access remote devices 

                                over SSH. In this project user must have priviledge level 15. It is set to:

                                * **cisco**

   ansible_password             This option defined a password for the user which is set in ``ansible_user``.

                                In this project password is set to:

                                * **cisco123**                                
   ============================ ==========================================================================

.. warning::

   ``ansible_user`` must have priveldge level 15. Example of the configuration is below 

   .. code-block::

       username cisco privilege 15 password 0 cisco123

   In the example unencrypted password is used. Fill free to use HIDDEN (7)

If ``enable`` password should be used, check the `Enable Mode <https://docs.ansible.com/ansible/latest/network/user_guide/platform_ios.html>`_ documentation.
     
