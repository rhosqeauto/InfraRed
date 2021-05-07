Topology
========
A topology is a description of an environment you wish to provision.
We have divided it into two, `network topology`_ and `nodes topology`_.

Nodes topology
--------------
Before creating our environment, we need to decide how many and what type
of nodes to create.
The following format is used to provide topology nodes::

    infrared <provisioner_plugin> --topology-nodes NODENAME:AMOUNT

where ``NODENAME`` refers to files under ``vars/topology/nodes/NODENAME.yml``
(or ``defaults/topology/nodes/NODENAME.yml``)
and ``AMOUNT`` refers to the amount of nodes from the ``NODENAME`` we wish to create.

For example, if we choose the `Virsh <virsh.html>`_ provisioner::

    infrared virsh --topology-nodes undercloud:1,controller:3 ...

The above command will create 1 VM of type ``undercloud`` and 3 VMs of type ``controller``

For any node that is provided in the CLI ``--topology-nodes`` flag,
`infrared` looks for the node first under ``vars/topology/nodes/NODENAME.yml``
and if not found, under ``default/topology/nodes/NODENAME.yml``
where we supply a default set of supported / recommended topology files.

Lets examine the structure of topology file (located: var/topology/nodes/controller.yml)::

    name: controller       # the name of the VM to create, in case of several of the same type, appended with "-#"
    prefix: null           # in case we wish to add a prefix to the name
    cpu: "4"               # number of vCPU to assign for the VM
    memory: "8192"         # the amount of memory
    swap: "0"              # swap allocation for the VM
    disks:                 # number of disks to create per VM
        disk1:             # the below values are passed `as is` to virt-install
            import_url: null
            path: "/var/lib/libvirt/images"
            dev: "/dev/vda"
            size: "40G"
            cache: "unsafe"
            preallocation: "metadata"
    interfaces:            # define the VM interfaces and to which network they should be connected
        nic1:
            network: "data"
        nic2:
            network: "management"
        nic3:
            network: "external"
    external_network: management  # define what will be the default external network
    groups:                       # ansible groups to assign to the newly created VM
        - controller
        - openstack_nodes
        - overcloud_nodes
        - network

For more topology file examples, please check out the default `available nodes <virsh_nodes>`_

.. _`virsh_nodes`: https://github.com/rehdat-openstack/infrared/tree/master/plugins/virsh/defaults/topology/nodes
.. _`openstack`: https://github.com/rehdat-openstack/infrared/tree/master/plugins/openstack/defaults/topology/nodes

To override default values in the topology dict the extra vars can be provided through the CLI. For example,
to add more memory to the controller node, the ``override.controller.memory`` value should be set::

    infrared virsh --topology-nodes controller:1,compute:1 -e override.controller.memory=30720

Network topology
----------------
Before creating our environment, we need to decide number and types
of networks to create. The following format is used to provide topology networks::

    infrared <provisioner_plugin> --topology-network NET_TOPOLOGY

where ``NET_TOPOLOGY`` refers to files under ``vars/topology/network/NET_TOPOLOGY.yml``
(or if not found, ``defaults/topology/network/NET_TOPOLOGY.yml``)

To make it easier for people, we have created a default network topology
file called: ``3_nets.yml`` (you can find it under each provisioner plugin
defaults/topology/network/3_nets.yml) that will be created automatically.

For example, if we choose the `Virsh <virsh.html>`_ provisioner::

    infrared virsh --topology-network 3_nets ...

The above command will create 3 networks: (based on the specification under ``defaults/topology/network/3_nets.yml``)

# data network - an isolated network
# management network - NAT based network with a DHCP
# external network - NAT based network with DHCP

If we look in the ``3_nets.yml`` file, we will see this::

    networks:
        net1:
            <snip>
        net2:
            name: "management"                 # the network name
            external_connectivity: yes         # whether we want it externally accessible
            ip_address: "172.16.0.1"           # the IP address of the bridge
            netmask: "255.255.255.0"
            forward:                           # forward method
                type: "nat"
            dhcp:                              # omit this if you don't want a DHCP
                range:                         # the DHCP range to provide on that network
                    start: "172.16.0.2"
                    end: "172.16.0.100"
                subnet_cidr: "172.16.0.0/24"
                subnet_gateway: "172.16.0.1"
            floating_ip:                       # whether you want to "save" a range for assigning IPs
                start: "172.16.0.101"
                end: "172.16.0.150"
        net3:
            <snip>

To override default values in the network dict the extra vars can be provided through the CLI. For example,
to change ip address of net2 network, the ``override.networks.net2.ip_address`` value should be set::

    infrared virsh --topology-nodes controller:1,compute:1 -e override.networks.net2.ip_address=10.0.0.3
