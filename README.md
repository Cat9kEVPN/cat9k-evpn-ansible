# About #

The main goal of this project is the automation of Campus EVPN Deployment based on Catalyst 9000.

Custom Jinja templates and Python modules are used to build an initial config and modify the network configuration.

Project has a modular structure which gives an ability to introduce new features/services gradually step-by-step.

* DAG (Distributed Anycast Gateway)
  * [DAG github](https://github.com/Cat9kEVPN/cat9k-evpn-ansible/tree/releases/v2.x.x/dag)
  * [DAG documentation](https://cat9k-evpn-ansible.readthedocs.io/en/latest/input_dag.html)

# General description #

<img width="1192" alt="ansible" src="https://user-images.githubusercontent.com/107021162/175528526-5d8b59ea-7f39-4d78-ac95-b08fed9ebbf6.png">

# Installation #

It is recommended to run the project in the virtual environment.

Below you can find installation steps for Linux (ubuntu) server

* Install python3
```
    sudo apt install python3
```
* Create the python virtual environment. In this example the virtual environment will be created in the folder ``virtual-env/ansible``
```
    python3 -m venv ansible
```

More details could be found [here](https://docs.python.org/3/library/venv.html)

* Activate virtual environment.
```
    source ansible/bin/activate
```
* Install ``pip`` if it is not already installed
```
    sudo apt install pip
```
* Install all necessary packages
```
    pip install -r requirements.txt
```
* Or you can do it manually
```
    pip install ansible
    pip install ansible-pylibssh
    pip install paramiko
    pip install pyats
    pip install genie
```
* Next step - go to desired feature directory or [documentation](https://cat9k-evpn-ansible.readthedocs.io)

# Documentation #

Detailed documentation could be found [here](https://cat9k-evpn-ansible.readthedocs.io)

# Release notes #

## 2.0.0 ##

* Precheck of configuration file is added
* Access interface configuration is added
* Incremental changes configuration is automated and simplified
* Moving L2VPN EVPN relatead information from ``group_vars/all.yml`` to ``group_vars/overlay_db.yml``
* Documentation update

## 1.0.0 ##

* The release is depricated
* Code is still avaliable in branch ``releases/v1.x.x``
