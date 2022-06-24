# About #

The main goal of this project is the automation of Campus EVPN Deployment based on Catalyst 9000.

Custom Jinja templates and Python modules are used to build an initial config and modify the network configuration.

Project has a modular structure which gives an ability to introduce new features/services gradually step-by-step.

* DAG (Distributed Anycast Gateway)
  * [DAG github](https://github.com/Cat9kEVPN/cat9k-evpn-ansible/tree/releases/v2.x.x/dag)
  * [DAG documentation](https://cat9k-evpn-ansible.readthedocs.io/en/latest/input_dag.html)

# Topology #

Below you can find a topology which is used in the automation scenario.

<img width="737" alt="ansible_lab_topology" src="https://user-images.githubusercontent.com/99259970/155182099-7e5d98f4-8e4e-4b01-96a8-30b9badc5be2.png">

# General description #

<img width="1192" alt="ansible" src="https://user-images.githubusercontent.com/107021162/175528526-5d8b59ea-7f39-4d78-ac95-b08fed9ebbf6.png">

# Documentation #

Detailed documentation could be found [here](https://cat9k-evpn-ansible.readthedocs.io)

# Release notes #

## 2.0.0 ##

* Precheck of configuration file is added
* Access interface configuration is added
* Incremental changes configuration is automated and simplified
* Moving L2VPN EVPN relatead information from ``group_vars/all.yml`` to ``group_vars/overlay_db.yml``
* Documentation update
