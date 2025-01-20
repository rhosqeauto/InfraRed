Cloud Config
============

Collection of overcloud configuration tasks to run after Overcloud deploy (Overcloud post tasks)

Flags
-----

* ``--tasks``:
    Run one or more tasks to the cloud. separate with commas.

  .. code-block:: shell

      # Example:
      infrared cloud-config --tasks create_external_network,compute_ssh,instance_ha
* ``--overcloud-stack``:
    The overcloud stack name.
* ``--resync``:
    Bool. Whether we need to resync services.

External Network
----------------
To create external network we need to specify in ``--tasks`` the task ``create_external_network`` and then use the flags above:

* ``--deployment-files``:
    Name of folder in cloud's user on undercloud, which contains the templates of the overcloud deployment.
* ``--network-protocol``:
    The overcloud network backend.
* ``--public-net-name``:
    Specifies the name of the public network.
    .. note:: If not provided it will use the default one for the OSP version.
* ``--public-subnet``:
    Path to file containing different values for the subnet of the network above.
* ``--external-vlan``:
    An Optional external VLAN ID of the external network (Not the Public API network).
    Set this to ``yes`` if overcloud's external network is on a VLAN that's unreachable from the
    undercloud. This will configure network access from UnderCloud to overcloud's API/External(floating IPs)
    network, creating a new VLAN interface connected to ovs's ``br-ctlplane`` bridge.
    .. note:: If your UnderCloud's network is already configured properly, this could disrupt it, making overcloud API unreachable
    For more details, see:
    `VALIDATING THE OVERCLOUD <https://access.redhat.com/documentation/en/red-hat-openstack-platform/10-beta/paged/director-installation-and-usage/chapter-6-performing-tasks-after-overcloud-creation>`_

.. code-block:: shell

    # Example:
    ir cloud-config --tasks create_external_network --deployment-files virt --public-subnet default_subnet --network-protocol ipv4

Scale Up/Down nodes
-------------------
* ``--scale-nodes``:
    List of compute nodes to be added.

    .. code-block:: shell

      # Example:
      ir cloud-config --tasks scale_up --scale-nodes compute-1,compute-2

* ``--node-name``:
    Name of the node to remove.

    .. code-block:: shell

      # Example:
      ir cloud-config --tasks scale_down --node-name compute-0


Ironic Configuration
--------------------
* ``vbmc-username``:
    VBMC username.
* ``vbmc-password``:
    VBMC password.

.. note:: Necessary when Ironic's driver is 'pxe_ipmitool' in OSP 11 and above.

Workload Launch
---------------
* ``--workload-image-url``:
    Image source URL that should be used for uploading the workload Glance image.
* ``--workload-memory``:
    Amount of memory allocated to test workload flavor.
* ``--workload-vcpu``:
    Amount of v-cpus allocated to test workload flavor.
* ``--workload-disk``:
    Disk size allocated to test workload flavor.
* ``--workload-index``:
    Number of workload objects to be created.

.. code-block:: shell

    # Example:
    ir cloud-config --workload-memory 64 --workload-disk 1 --workload-index 3
