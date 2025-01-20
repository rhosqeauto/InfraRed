Baremetal deployment
--------------------

Infrared allows to perform baremetal deployments.

.. note:: Overcloud templates for the deployment should be prepared separately.

1) Undercloud provision step. Foreman plugin will be used in this example.

   .. code:: shell

     infrared foreman -vv \
         -o provision.yml \
         --url foreman.example.com \
         --user foreman_user \
         --password foreman_password \
         --host-address name.of.undercloud.host \
         --host-key /path/to/host/key \
         --role baremetal,undercloud,tester

2) Deploy Undercloud.

   .. code:: shell

     infrared tripleo-undercloud -vv \
         -o undercloud-install.yml \
         --config-file path/to/undercloud.conf \
         --version 11 \
         --build 11 \
         --images-task rpm

3) Deploy Overcloud.

   For baremetal deployments, in order to reflect the real networking,
   templates should be prepared by the user before the deployment, including ``instackenv.json`` file.
   All additional parameters like storage (``ceph`` or ``swift``) disks or any other parameters should be added to the templates as well.

   .. code:: shell

     ...
     "cpu": "2",
     "memory": "4096",
     "disk": "0",
     "disks": ["vda", "vdb"],
     "arch": "x86_64",
     ...


    infrared tripleo-overcloud -vv \
        -o overcloud-install.yml \
        --version 11 \
        --instackenv-file path/to/instackenv.json \
        --deployment-files /path/to/the/templates \
        --overcloud-script /path/to/overcloud_deploy.sh \
        --network-protocol ipv4 \
        --network-backend vlan \
        --public-network false \
        --introspect yes \
        --tagging yes \
        --deploy yes

    infrared cloud-config -vv \
        -o cloud-config.yml \
        --deployment-files virt \
        --tasks create_external_network,forward_overcloud_dashboard,network_time,tempest_deployer_input
