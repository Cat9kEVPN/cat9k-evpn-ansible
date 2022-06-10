About
=====

The main goal of this project is automation of Campus EVPN Deployment.

Custom Jinja templates and Python modules are used to build an initial config and modifiyng the network configuration.

Project has a modular structure which gives an ability to introduce new features/services granuallary step-by-step.

Project has several directories. Each directory has a code for provisioning one feature.

**dag_add**  DAG (Distributed Anycast Gateway) provisioning

**dag_delete** DAG selective unprovisioning

Detailed instructions for running playbook you can find under each directory:

Link to DAG provisioning `dag_add <https://github.com/dvishchu/cat9k-evpn-ansible/tree/main/dag_add>`_

Link to DAG unptovisioning `dag_delete <https://github.com/dvishchu/cat9k-evpn-ansible/tree/main/dag_delete>`_