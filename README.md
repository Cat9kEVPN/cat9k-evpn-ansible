# About #

The main goal of this project is the automation of Campus EVPN Deployment based on Catalyst 9000.

Custom Jinja templates and Python modules are used to build an initial config and modify the network configuration.

Project has a modular structure which gives an ability to introduce new features/services gradually step-by-step.

* DAG (Distributed Anycast Gateway)
  * [DAG github](https://github.com/Cat9kEVPN/cat9k-evpn-ansible/tree/main/dag)
  * [DAG documentation](https://cat9k-evpn-ansible.readthedocs.io/en/latest/input_dag.html)

* L2 Overlay (L2VNI)
  * [L2VNI github](https://github.com/Cat9kEVPN/cat9k-evpn-ansible/tree/main/l2vni)
  * [L2VNI documentation](https://cat9k-evpn-ansible.readthedocs.io/en/latest/input_l2vni.html)
  
* L3 Overlay (L3VNI)
  * [L3VNI github](https://github.com/Cat9kEVPN/cat9k-evpn-ansible/tree/main/l3vni)
  * [L3VNI documentation](https://cat9k-evpn-ansible.readthedocs.io/en/latest/input_l3vni.html) 

# Prerequisites #

To run Cisco cat9k EVPN ansible playbook, you will require:  

**Hardware**:

* A linux  server (Fedroa, Ubuntu, RedHat, etc) 
* Cat9k Switches  supporting EVPN (from x release) 
 
**Network-Expertise**:

* Basic network knowledge (network design, bring up of cat9k switches)  
* Basic understanding of YAML  
* Basic understanding of Python  
* Basic linux command line use  

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
    python3 -m venv virtual-env/ansible
```

More details could be found [here](https://docs.python.org/3/library/venv.html)

* Activate virtual environment.
```
    source virtual-env/ansible/bin/activate
```
* Clone the repository
```
    git clone https://github.com/Cat9kEVPN/cat9k-evpn-ansible.git
```
* Go to project directory
```
    cd cat9k-evpn-ansible/
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

# Ask a question #

If you have any questions, please leverage the GitHub [discussions board](https://github.com/Cat9kEVPN/cat9k-evpn-ansible/discussions/)

# Release notes #

## 2.1.0 ##

* L2VNI added
* L3VNI added

## 2.0.0 ##

* Precheck of configuration file is added
* Access interface configuration is added
* Incremental changes configuration is automated and simplified
* Moving L2VPN EVPN relatead information from ``group_vars/all.yml`` to ``group_vars/overlay_db.yml``
* Documentation update

## 1.0.0 ##

* The release is depricated
* The code is still avaliable in the branch ``releases/v1.x.x``
