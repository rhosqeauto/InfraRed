Plugins
=======

In `infrared` 2.0, `plugins` are self contained Ansible projects. They can still
also depend on common items provided by the core project.
Any ansible project can become an`infrared` plugin by adhering to the following
structure (see `tests/example`_ for an example plugin)::

    tests/example
    ├── main.yml                # Main playbook. All execution starts here
    ├── plugin.spec             # Plugin definition
    ├── roles                   # Add here roles for the project to use
    │   └── example_role
    │       └── tasks
    │           └── main.yml

.. note:: This structure will work without any ``ansible.cfg`` file provided (unless common resources are used),
        as Ansible will search for references in the
        relative paths described above. To use an ``ansible.cfg`` config file, use absolute paths to the plugin directory.
.. _tests/example: https://github.com/redhat-openstack/infrared/tree/master/tests/example


Plugin structure
^^^^^^^^^^^^^^^^

Main entry
----------
`infrared` will look for a playbook called ``main.yml`` to start the execution from.

.. note:: If you want to use other playbook to start from - simply add it into
          config section in ``plugin.spec``:

.. code-block:: yaml

    config:
      plugin_type: other
      entry_point: your-playbook.yml
      ...

Plugins are regular Ansible projects, and as such, they might include or reference any item
(files, roles, var files, ansible plugins, modules, templates, etc...) using relative paths
to current playbook.
They can also use roles, callback and filter plugins defined in the ``common/`` directory
provided by `infrared` core.

An example of ``plugin_dir/main.yml``:

.. literalinclude:: ../examples/main.yml
   :emphasize-lines: 3-6
   :linenos:

Plugin Specification
--------------------
`infrared` gets all plugin info from ``plugin.spec`` file. Following `YAML` format.
This file defines the CLI flags this plugin exposes, its name and its type.

.. literalinclude:: ../examples/plugin.spec

Config section:
    * Plugin type can be one of the following: ``provision``, ``install``, ``test``, ``other``.
    * Entry point is the main playbook for the plugin. by default this will refer to main.yml file
        but can be changed to any other file.
    * ``roles_path``:
        This is optional and it might be used when the plugin refers to a role
        which is introduced by that plugin. The ``roles_path`` then relatively
        points (from plugin.spec location) to the role. Let's take a look at
        the following example of an ansible role (can be as a standalone project)
        which is also an infrared plugin
        ::

            my_role
            ├── defaults
            │   └── main.yml
            ├── infrared_plugin
            │   ├── main.yml                # Main playbook. All execution starts here
            │   └── plugin.spec             # Plugin definition
            ├── tasks                       # Tasks of the role
            │   └── main.yml

In the above example ``main.yml`` calls ``my_role``. In order to help infrared
find the role, ``roles_path`` within config section needs to be set to ``../``
to point to the ansible role called from ``infrared_plugin/main.yml``

To access the options defined in the spec from your playbooks and roles use
the plugin type with the option name.
For example, to access ``dictionary-val`` use ``{{ provision.dictionary.val }}``.

.. note:: the vars-dict defined by `Complex option types`_ is nested under ``plugin_type`` root key, and passed
 to Ansible using ``--extra-vars`` meaning that any vars file that has ``plugin_type`` as a root key, will be
 overriden by that vars-dict. See `Ansible variable precidence`_ for more details.

.. _Ansible variable precidence: http://docs.ansible.com/ansible/playbooks_variables.html#variable-precedence-where-should-i-put-a-variable

Include Groups
~~~~~~~~~~~~~~
A plugin can reference preset control arguments to be included in its CLI

Answers File:
    Instead of explicitly listing all CLI options every time, `infrared` plugins
    can read their input from ``INI`` answers file, using ``--from-file`` switch.
    use ``--generate-answers-file`` switch to generate such file. It will list all
    input arguments a plugin accepts, with their help and defaults.
    CLI options still take precedence if explicitly listed, even when ``--from-file``
    is used.

Common Options:
    * ``--dry-run``: Don't execute Ansible playbook. Only write generated vars dict to stdout
    * ``--extra-vars``: Inject custom input into the `vars dict <plugins.html#Complex option types>`_
    * ``--output``: Redirect generated vars dict from stdout to an explicit file (YAML format).

    .. note:: Please notice that InfraRed can dump the vars dict into a JSON file by setting the
        'IR_GEN_VARS_JSON' environment variable to one of the YAML boolean values which are equivalent to 'True'.
        The JSON file will be stored inside a directory named 'ansible_vars' under the active workspace directory
        and the name of the file will be in the following format: 'ir_<timestamp>_<plugin_name>.json'

Inventory:
    Load a new inventory to active `workspace <workspace.html>`_. The file is copied to
    workspace directory so all ``{{ inventory_dir }}`` references in playbooks still point to
    workspace directory (and not to the input file's directory).

    .. note:: This file permanently becomes the workspace's inventory. To revert to original workspace
        the workspace must be cleaned.

Ansible options:
    * ``--verbose``: Set ansible verbosity level
    * ``--ansible-args``: Pass all subsequent input to Ansible as raw arguments. This is for power-users wishing to access
      Ansible functionality not exposed by `infrared`::

         infrared [...] --ansible-args step;tags=tag1,tag2;forks=500

      Is the equivalent of::

         ansible-playbook [...] --step --tags=tag1,tag2 --forks 500

Complex option types
~~~~~~~~~~~~~~~~~~~~
`Infrared` extends `argparse <https://docs.python.org/2/library/argparse.html>`_ with the following option types.
These options are nested into the vars dict that is later passed to Ansible as extra-vars.

* Value:
    String value.
* Bool:
    Boolean value. Accepts any form of YAML boolean: ``yes``/``no``, ``true``/``false`` ``on``/``off``.
    Will fail if the string can't be resolved to this type.
* Flag:
    Acts as a flag, doesn't parse any value.
    Will always return ``true``.
* IniType:
    Value is in ``section.option=value`` format.
    ``append`` is the default action for this type, so users can provide multiple args for the same parameter.
    .. warning:: The `IniType` option is deprecated, use `NestedDict` instead of.
* NestedDict:
    Value is in ``section.option=value`` format.
    ``append`` is the default action for this type, so users can provide multiple args for the same parameter. Example::

     infrared example --foo option1=value1 --foo option2=value2

    .. code:: json
       :name: NestedDict

        {"foo": {"option1": "value1",
                 "option2": "value2"}}

* NestedList:
    The `NestedList` option inherits `NestedDict` attributes and differs from `NestedDict` by value format. It composes
    value as list of dictionaries. Example::

     infrared example --foo option1=value1 --foo option1=value2

    .. code:: json
       :name: NestedList

        {"foo": [{"option1": "value1"},
                 {"option1": "value2"}]}

* KeyValueList:
    String representation of a flat dict ``--options option1:value1,option2:value2``
    becomes:

    .. code:: json
       :name: KeyValueList

        {"options": {"option1": "value1",
                     "option2": "value2"}}


The nesting is done in the following manner: option name is split by ``-`` delimiter and each part is
a key of a dict nested in side the previous one, starting with "plugin_type". Then value is nested at the
inner-most level. Example::

    infrared example --foo-bar=value1 --foo-another-bar=value2 --also_foo=value3

.. code:: json
   :name: vars-dict

   {
       "provision": {
           "foo": {
               "bar": "value1",
               "another": {
                   "bar": "value2"
               }
           },
           "also_foo": "value3"
       }
   }

* FileValue
    The absolute or relative path to a file. Infrared validates whether file exists and transform the path
    to the absolute.

* VarFile
    Same as the ``FileValue`` type but additionally Infrared will check the following locations for a file:
        - ``argument/name/option_value``
        - ``<spec_root>/defaults/argument/name/option_value``
        - ``<spec_root>/var/argument/name/option_value``

    In the example above the CLI option name is ``--argument-name``.
    The VarFile suites very well to describe options which point to the file with variables.

    For example, user can describe network topologies parameters in separate files.
    In that case, all these files can be put to the ``<spec_root>/defaults/network`` folder,
    and plugin specification can look like::

        config:
           plugin_type: provision
           entry_point: main.yml
        subparsers:
        my_plugin:
            description: Provisioner virtual machines on a single Hypervisor using libvirt
            groups:
                - title: topology
                  options:
                      network:
                          type: VarFile
                          help: |
                              Network configuration to be used
                              __LISTYAMLS__
                          default: defautl_3_nets

    Then, the cli call can looks simply like::

        infrared my_plugin --network=my_file

    Here, the 'my_file' file should be present in the ``/{defaults|var}/network`` folder, otherwise an
    error will be displayed by the Infrared.
    Infrared will transform that option to the absolute path and will put it to the provision.network variable::

        provision.network: /home/user/..../my_plugin/defaults/my_file

    That variable is later can be used in Ansible playbooks to load the appropriate network parameters.

    .. Note:: Infrared automatically checks for files with .yml extension. So the ``my_file`` and
              ``my_file.yml`` will be validated.

* ListOfVarFiles
    The list of files. Same as ``VarFile`` but represents the list of files delimited by comma (``,``).

* VarDir
    The absolute or relative path to a directory. Same as ``VarFile`` but points to the directory instead of file

Placeholders
~~~~~~~~~~~~
Placeholders allow users to add a level of sophistication in options help field.

* ``__LISTYAMLS__``:
    Will be replaced with a list of available YAML (``.yml``) file from the option's settings dir.
    | Assume a plugin with the following  directory tree is installed::

        plugin_dir
        ├── main.yml                 # Main playbook. All execution starts here
        ├── plugin.spec                 # Plugin definition
        └── vars                     # Add here variable files
            ├── yamlsopt
            │   ├── file_A1.yml      # This file will be listed for yamlsopt
            │   └── file_A2.yml      # This file will be listed also for yamlsopt
            └── another
                └──yamlsopt
                    ├── file_B1.yml  # This file will be listed for another-yamlsopt
                    └── file_B2.yml  # This file will be listed also for another-yamlsopt

    Content of ``plugin_dir/plugin.spec``:

    .. code:: text
       :name: list-yamls-spec-file

        plugin_type: provision
        description: Example provisioner plugin
        subparsers:
            example:
                groups:
                    - title: GroupA
                          yamlsopt:
                             type: Value
                             help: |
                                   help of yamlsopt option
                                   __LISTYAMLS__

                          another-yamlsopt:
                             type: Value
                             help: |
                                   help of another-yamlsopt option
                                   __LISTYAMLS__

    Execution of help command (``infrared example --help``) for the 'example' plugin, will produce the following help screen:

    .. code:: text
       :name: list-yamls-help-screen

       usage: infrared example [-h] [--another-yamlsopt ANOTHER-YAMLSOPT]
                                    [--yamlsopt YAMLSOPT]

       optional arguments:
         -h, --help            show this help message and exit

       GroupA:
         --another-yamlsopt ANOTHER-YAMLSOPT
                               help of another-yamlsopt option
                               Available values: ['file_B1', 'file_B2']
         --yamlsopt YAMLSOPT   help of yamlsopt option
                               Available values: ['file_A1', 'file_A2']


Required Arguments
~~~~~~~~~~~~~~~~~~
InfraRed provides the ability to mark an argument in a specification file as 'required' using two flags:

1. 'required' - A boolean value tell whether the arguments required or not. (default is 'False')
2. 'required_when' - Makes this argument required only when the mentioned argument is given and the condition is True.
    More than one condition is allowed with YAML list style. In this case the argument will be required if all the
    conditions are True.

For example, take a look on the ``plugin.spec`` ('Group C') in `Plugin Specification`_

Roles Dependencies
~~~~~~~~~~~~~~~~~~
If a plugin depended on one or more Ansible role, it's possible to mention them in a file.
InfraRed makes use of Ansible Galaxy to install the roles file, therefore, the requirements for it should be exactly the same like in Ansible Galaxy:

1. The file need to be in YAML format.
2. The name of the file should be either ``requirements.yml`` or ``requirements.yaml``

For more details, please take a look on `Ansible Galaxy documentation
<https://docs.ansible.com/ansible/latest/reference_appendices/galaxy.html#installing-multiple-roles-from-a-file>`_.

Argument Deprecation
~~~~~~~~~~~~~~~~~~~~
To deprecate an argument in InfraRed, you need to add flag 'deprecates' in newer argument

When we use a deprecated argument, InfraRed will warn you about that and it will add the
new argument in Ansible parameters with the value of the deprecated

For example, take a look on the ``plugin.spec`` ('Group D') in `Plugin Specification`_

Plugin Manager
^^^^^^^^^^^^^^

The following commands are used to manage `infrared` plugins

Add:
    `infrared` will look for a `plugin.spec <plugins.html#plugin-specification>`_ file in each given source and
    register the plugin under the given plugin-type (when source is 'all', all available plugins will be installed)::

        infrared plugin add tests/example
        infrared plugin add example example2
        infrared plugin add <git_url> [--revision <branch/tag/revision>]
        infrared plugin add all

    .. note:: "--revision" works with one plugin source only.


List:
    List all available plugins, by type::

        infrared plugin list

        ┌───────────┬─────────┐
        │ Type      │ Name    │
        ├───────────┼─────────┤
        │ provision │ example │
        ├───────────┼─────────┤
        │ install   │         │
        ├───────────┼─────────┤
        │ test      │         │
        └───────────┴─────────┘

        infrared plugin list --available

        ┌───────────┬────────────────────┬───────────┐
        │ Type      │ Name               │ Installed │
        ├───────────┼────────────────────┼───────────┤
        │ provision │ example            │     *     │
        │           │ foreman            │           │
        │           │ openstack          │           │
        │           │ virsh              │           │
        ├───────────┼────────────────────┼───────────┤
        │ install   │ collect-logs       │           │
        │           │ packstack          │           │
        │           │ tripleo-overcloud  │           │
        │           │ tripleo-undercloud │           │
        ├───────────┼────────────────────┼───────────┤
        │ test      │ rally              │           │
        │           │ tempest            │           │
        └───────────┴────────────────────┴───────────┘


.. note:: Supported plugin types are defined in plugin settings file which is auto generated.
   Check the  `Infrared Configuration <configuration.html>`_ for details.

Remove:
    Remove the given plugins (when name is 'all', all plugins will be removed)::

        infrared plugin remove example example2
        infrared plugin remove all

Freeze:
    Output installed plugins with their revisions in a `registry file format <plugins.html#registry-files>`_.
    When you need to be able to install somewhere else the exact same versions
    of plugins use ``freeze`` command::

        infrared plugin freeze > registry.yaml

Import:
    Installs all plugins from the given registry file.
    The registry file can be either path to local file or to URL::

        infrared plugin import plugins/registry.yaml
        infrared plugin import https://url/to/registry.yaml

Update:
    Update a given Git-based plugin to a specific revision.
    The update process pulls the latest changes from the remote and checks out a specific
    revision if given, otherwise, it will point to the tip of the updated branch.
    If the \"--skip_reqs\" switch is set, the requirements installation will be skipped::

        ir plugin update [--skip_reqs] [--hard-reset] name [revision]

Execute:
    Plugins are added as subparsers under ``plugin type`` and will execute
    the `main playbook <plugins.html#Main entry>`_::

        infrared example


Registry Files
^^^^^^^^^^^^^^

Registry files are files containing a list of plugins to be installed using the infrared plugin import.
These files are used to hold the result from infrared plugin freeze for the purpose of achieving repeatable installations.
The Registry file contains a pinned version of everything that was installed when infrared plugin freeze was run.

Registry File Format
--------------------
The registry file is following the YAML format.
Each section of the registry file contains an object which specifies the plugin to be installed:

* ``src``: The path to the plugin. It can be either local path or git url
* ``desc``: The plugin description.
* ``type``: Plugin type can be one of the following: ``provision``, ``install``, ``test``, ``other``.
* ``rev``: (optional) If the plugin source is git, this allows to specify the revision to pull.
* ``src_path``: (optional, required with 'link_roles') Relative path within the repository where infrared plugin can be found.
* ``link_roles``: (optional, requires 'src_path') Creates a symbolic link inside a (newly created) role directory in 'src_path', that points to the 'roles' directory inside the plugin root directory if exists, otherwise, to the root plugin directory. The input is a string represents a boolean value.

Example of a registry file::

    ---

    plugin_name:
        src: 'path/to/plugin/directory'
        desc: 'Some plugin description'
        type: 'provision/test/install/other'
        rev: 'some_revision_hash'
        src_path: '/path/to/plugin/in/repo'
        link_roles: 'true'

How to create a new plugin
^^^^^^^^^^^^^^^^^^^^^^^^^^
.. note:: Check `COOKBOOK <plugins_guide.html>`_ for the quick guide on how to create a plugin.
