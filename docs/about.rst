About
=====

The main goal of this project is the automation of Campus EVPN Deployment based on Catalyst 9000.

Custom Jinja templates and Python modules are used to build an initial config and modify the network configuration.

Project has a modular structure which gives an ability to introduce new features/services gradually step-by-step.

* `DAG (Distributed Anycast Gateway) <https://cat9k-evpn-ansible.readthedocs.io/en/latest/input_dag.html>`_

* DAG (Distributed Anycast Gateway)
  * [DAG github](https://github.com/Cat9kEVPN/cat9k-evpn-ansible/tree/main/dag)
  * [DAG documentation](https://cat9k-evpn-ansible.readthedocs.io/en/latest/input_dag.html)

* L2 Overlay (L2VNI)
  * [L2VNI github](https://github.com/Cat9kEVPN/cat9k-evpn-ansible/tree/main/l2vni)
  * [L2VNI documentation](https://cat9k-evpn-ansible.readthedocs.io/en/latest/input_l2vni.html)
  
* L3 Overlay (L3VNI)
  * [L3VNI github](https://github.com/Cat9kEVPN/cat9k-evpn-ansible/tree/main/l3vni)
  * [L3VNI documentation](https://cat9k-evpn-ansible.readthedocs.io/en/latest/input_l3vni.html)

Prerequisites:
**************

To run Cisco cat9k EVPN ansible playbook, you will require:  

**Hardware**:

* A linux  server (Fedroa, Ubuntu, RedHat, etc) 
* Cat9k Switches  supporting EVPN (from x release) 
 
**Network-Expertise**:

* Basic network knowledge (network design, bring up of cat9k switches)  
* Basic understanding of YAML  
* Basic understanding of Python  
* Basic linux command line use  

