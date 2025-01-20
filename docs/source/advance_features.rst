Advance Features
================

Injection points
^^^^^^^^^^^^^^^^

Different people have different use cases which we cannot anticipate in advance.
To solve (partially) this need, we structured our playbooks in a way that breaks the logic into standalone plays.
Furthermore, each logical play can be overridden by the user at the invocation level.

Lets look at an example to make this point more clear.
Looking at our ``virsh`` main playbook, you will see::

    - include: "{{ provision_cleanup | default('cleanup.yml') }}"
      when: provision.cleanup|default(False)

Notice that the ``include:`` first tried to evaluate the variable ``provision_cleanup`` and afterwards defaults to our own cleanup playbook.

This condition allows users to inject their own custom cleanup process while still reuse all of our other playbooks.

Override playbooks
------------------

In this example we'll use a custom playbook to override our cleanup play and replace it with the process described above.
First, let's create an empty playbook called: ``noop.yml``::

    ---
    - name: Just another empty play
      hosts: localhost
      tasks:
        - name: say hello!
          debug:
              msg: "Hello!"

Next, when invoking `infrared`, we will pass the variable that points to our new empty playbook::

   infrared virsh --host-address $HOST --host-key $HOST_KEY --topology-nodes $TOPOLOGY --kill yes -e provision_cleanup=noop.yml

Now lets run see the results::

    PLAY [Just another empty play] *************************************************

    TASK [setup] *******************************************************************
    ok: [localhost]

    TASK [say hello!] **************************************************************
                           [[ previous task time: 0:00:00.459290 = 0.46s / 0.47s ]]
    ok: [localhost] => {
        "msg": "Hello!"
    }

    msg: Hello!

If you have a place you would like to have an injection point and one is not provided, please `contact us <contacts.html>`_.


Infrared Ansible Tags
^^^^^^^^^^^^^^^^^^^^^

Stages and their corresponding Ansible tags
-------------------------------------------

Each stage can be executed using ansible plugin with set of ansible tags that are passed to the infrared plugin command:


+--------------------+-------------------+-----------------------------------------------------------------+
| Plugin             | Stage             | Ansible Tags                                                    |
+====================+===================+=================================================================+
| virsh              | Provision         | pre, hypervisor, networks, vms, user, post                      |
+--------------------+-------------------+-----------------------------------------------------------------+
| tripleo-undercloud | Undercloud Deploy | validation, hypervisor, init, install, shade, configure, deploy |
+                    +-------------------+-----------------------------------------------------------------+
|                    | Images            | images                                                          |
+--------------------+-------------------+-----------------------------------------------------------------+
| tripleo-overcloud  | Introspection     | validation, init, introspect                                    |
+                    +-------------------+-----------------------------------------------------------------+
|                    | Tagging           | tag                                                             |
+                    +-------------------+-----------------------------------------------------------------+
|                    | Overcloud Deploy  | loadbalancer, deploy_preparation, deploy                        |
+                    +-------------------+-----------------------------------------------------------------+
|                    | Post tasks        | post                                                            |
+--------------------+-------------------+-----------------------------------------------------------------+


Usage examples:
***************

The ansible tags can be used by passing all subsequent input to Ansible as raw arguments.

Provision (virsh plugin)::

    infrared virsh \
        -o provision_settings.yml \
        --topology-nodes undercloud:1,controller:1,compute:1 \
        --host-address <my.host.redhat.com> \
        --host-key </path/to/host/key> \
        --image-url <image-url> \
        --ansible-args="tags=pre,hypervisor,networks,vms,user,post"

Undercloud Deploy stage (tripleo-undercloud plugin)::

    infrared tripleo-undercloud \
        -o undercloud_settings.yml \
        --mirror tlv \
        --version 12 \
        --build passed_phase1 \
        --ansible-args="tags=validation,hypervisor,init,install,shade,configure,deploy"

Tags explanation:
-----------------

- Provision
    - pre - Pre run configuration
    - Hypervisor - Prepare the hypervisor for provisioning
    - Networks - Create Networks
    - Vms - Provision Vms
    - User - Create a sudoer user for non root SSH login
    - Post - perform post provision tasks
- Undercloud Deploy
    - Validation - Perform validations
    - Hypervisor - Patch hypervisor for undercloud deployment
        - Add rhos-release repos and update ipxe-roms
        - Create the stack user on the hypervisor and allow SSH to hypervisor
    - Init - Pre Run Adjustments
    - Install - Configure and Install Undercloud Repositories
    - Shade - Prepare shade node
    - Configure - Configure Undercloud
    - Deploy - Installing the undercloud
- Images
    - Images - Get the undercloud version and prepare the images
- Introspection
    - Validation - Perform validations
    - Init - pre-tasks
    - Introspect - Introspect our machines
- Tagging
    - Tag - Tag our machines with proper flavors
- Overcloud Deploy
    - Loadbalancer - Provision loadbalancer node
    - Deploy_preparation - Environment setup
    - Deploy - Deploy the Overcloud
- Post tasks
    - Post - Perform post install tasks

Virthost packages/repo requirements
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Virsh
-----

UEFI mode related binaries
--------------------------

For Virthost with RHEL 7.3, OVMF package is available in the supplementary channel, please install the package
from there and rerun the command. If the Virthost use different OS or OS version, please check below.

According to `usage UEFI with QEMU <https://fedoraproject.org/wiki/Using_UEFI_with_QEMU>`_ there is only one way
to get the UEFI mode boot working with VMs, that often requires by Ironic team due to lack of hardware or impossibility
to automate mode switching on baremetal nodes.

1. Add repo with OVMF binaries::

        yum-config-manager --add-repo http://www.kraxel.org/repos/firmware.repo

2. Install OVMF binaries::

        yum install -y edk2.git-ovmf-x64

3. Update QEMU config adding the following to the end of the /etc/libvirt/qemu.conf file::

                nvram = [
                    "/usr/share/edk2.git/ovmf-x64/OVMF_CODE-pure-efi.fd:/usr/share/edk2.git/ovmf-x64/OVMF_VARS-pure-efi.fd"
                ]
4. Restart libvirt service::

        systemctl restart libvirtd

IPv6 related host adjustments, which will also be required by UEFI
------------------------------------------------------------------

When UEFI is in use, libvirt will require additional setup on the host, for IPv6 to be enabled:

1. Configure accept_ra = 2 in sysctl::

        echo "net.ipv6.conf.all.accept_ra = 2" > /etc/sysctl.d/55-acceptra.conf

2. Enable the IPv6 related NAT modules::

        modprobe nf_nat_ipv6

Ansible output manipulations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Infrared allows to manipulate the output that comes from Ansible execution.
All manipulations are set through the environment variables listed below:

Hide Ansible's STDOUT & STDERR
------------------------------
The ``IR_ANSIBLE_NO_STDOUT`` & ``IR_ANSIBLE_NO_STDERR`` control whether the output from STDOUT & STDERR will be displayed or not.

  .. note::  These have no effect on log files explained

Log Ansible's output to files
-----------------------------
| Regardless the output that will or will not be printed to the stdout, Infrared gives users the option log Ansible output to files.
| Two options are available and can be set together or separately:
| ``IR_ANSIBLE_LOG_OUTPUT``: Indicates a creation of a log file containing the exact output as comes from Ansible.
| ``IR_ANSIBLE_LOG_OUTPUT_NO_ANSI``: Same as the above, but without any ANSI characters.
| The log files will be stored inside a directory called 'ansible_outputs' in the active workspace directory. The name of the files will have the following conventions: ``ir_<hr_timestamp>_<plugin_name>.log`` & ``ir_<hr_timestamp>_<plugin_name>_no_ansi.log``

  .. note:: All the manipulations mentioned above has no effect on Infrared output that doesn't come from Ansible.

  .. note:: | Infrared uses the ``distutils.util.strtobool`` to covert string representations of truth to true (1) or false (0).
            | Accepted values:
            | True values are y, yes, t, true, on and 1; False values are n, no, f, false, off and 0.
            | A ``ValueError`` exception will be raised in case a different value is provided.

InfraRed extra vars
^^^^^^^^^^^^^^^^^^^

| By default, InfraRed adds some useful data about itself as an extra-vars to Ansible.
| Currently, the data contains details about the InfraRed Python interpreter (path & version) and it can be accessed directly from within Ansible Playbook (ex. infrared.python.executable).
| The ``IR_NO_EXTRAS`` environment variable can be set to 'true' if one doesn't want to include that data.
