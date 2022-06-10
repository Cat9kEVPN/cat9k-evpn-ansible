About
=====

The main goal of this project is automation of Campus EVPN Deployment.

Custom Jinja templates and Python modules are used for provisioning the network

Each directory has scripts for specific steps for EVPN provisioning:

dag_add DAG (Distributed Anycast Gateway) provisioning
dag_delete DAG selective unprovisioning
Detailed instructions for running playbook you can find under each directory:

[dag_add](https://github.com/dvishchu/cat9k-evpn-ansible/tree/main/dag_add)
[dag_delete](https://github.com/dvishchu/cat9k-evpn-ansible/tree/main/dag_delete)