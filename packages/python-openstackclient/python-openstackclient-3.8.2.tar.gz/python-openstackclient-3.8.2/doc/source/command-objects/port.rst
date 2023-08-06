====
port
====

A **port** is a connection point for attaching a single device, such as the
NIC of a server, to a network. The port also describes the associated network
configuration, such as the MAC and IP addresses to be used on that port.

Network v2

port create
-----------

Create new port

.. program:: port create
.. code:: bash

    openstack port create
        --network <network>
        [--description <description>]
        [--fixed-ip subnet=<subnet>,ip-address=<ip-address>]
        [--device <device-id>]
        [--device-owner <device-owner>]
        [--vnic-type <vnic-type>]
        [--binding-profile <binding-profile>]
        [--host <host-id>]
        [--enable | --disable]
        [--mac-address <mac-address>]
        [--security-group <security-group> | --no-security-group]
        [--dns-name <dns-name>]
        [--allowed-address ip-address=<ip-address>[,mac-address=<mac-address>]]
        [--project <project> [--project-domain <project-domain>]]
        [--enable-port-security | --disable-port-security]
        <name>

.. option:: --network <network>

    Network this port belongs to (name or ID)

.. option:: --description <description>

    Description of this port

.. option:: --fixed-ip subnet=<subnet>,ip-address=<ip-address>

    Desired IP and/or subnet (name or ID) for this port:
    subnet=<subnet>,ip-address=<ip-address>
    (repeat option to set multiple fixed IP addresses)

.. option:: --device <device-id>

    Port device ID

.. option:: --device-owner <device-owner>

    Device owner of this port. This is the entity that uses
    the port (for example, network:dhcp).

.. option:: --vnic-type <vnic-type>

    VNIC type for this port (direct | direct-physical | macvtap | normal | baremetal,
    default: normal)

.. option:: --binding-profile <binding-profile>

    Custom data to be passed as binding:profile. Data may
    be passed as <key>=<value> or JSON.
    (repeat option to set multiple binding:profile data)

.. option:: --host <host-id>

    Allocate port on host ``<host-id>`` (ID only)

.. option:: --enable

    Enable port (default)

.. option:: --disable

    Disable port

.. option:: --mac-address <mac-address>

    MAC address of this port

.. option:: --security-group <security-group>

    Security group to associate with this port (name or ID)
    (repeat option to set multiple security groups)

.. option::  --no-security-group

    Associate no security groups with this port

.. option:: --dns-name <dns-name>

    Set DNS name to this port
    (requires DNS integration extension)

.. option:: --allowed-address ip-address=<ip-address>[,mac-address=<mac-address>]

    Add allowed-address pair associated with this port:
    ip-address=<ip-address>[,mac-address=<mac-address>]
    (repeat option to set multiple allowed-address pairs)

.. option:: --project <project>

    Owner's project (name or ID)

.. option:: --project-domain <project-domain>

    Domain the project belongs to (name or ID).
    This can be used in case collisions between project names exist.

.. option::  --enable-port-security

    Enable port security for this port (Default)

.. option::  --disable-port-security

    Disable port security for this port

.. _port_create-name:
.. describe:: <name>

    Name of this port

port delete
-----------

Delete port(s)

.. program:: port delete
.. code:: bash

    openstack port delete
        <port> [<port> ...]

.. _port_delete-port:
.. describe:: <port>

    Port(s) to delete (name or ID)

port list
---------

List ports

.. program:: port list
.. code:: bash

    openstack port list
        [--device-owner <device-owner>]
        [--router <router> | --server <server>]
        [--network <network>]
        [--mac-address <mac-address>]
        [--long]
        [--project <project> [--project-domain <project-domain>]]

.. option:: --device-owner <device-owner>

    List only ports with the specified device owner. This is
    the entity that uses the port (for example, network:dhcp).

.. option:: --router <router>

    List only ports attached to this router (name or ID)

.. option:: --server <server>

    List only ports attached to this server (name or ID)

.. option:: --network <network>

    List only ports attached to this network (name or ID)

.. option:: --mac-address <mac-address>

    List only ports with this MAC address

.. option:: --long

    List additional fields in output

.. option:: --project <project>

    List ports according to their project (name or ID)

.. option:: --project-domain <project-domain>

    Domain the project belongs to (name or ID).
    This can be used in case collisions between project names exist.

port set
--------

Set port properties

.. program:: port set
.. code:: bash

    openstack port set
        [--description <description>]
        [--fixed-ip subnet=<subnet>,ip-address=<ip-address>]
        [--no-fixed-ip]
        [--device <device-id>]
        [--device-owner <device-owner>]
        [--vnic-type <vnic-type>]
        [--binding-profile <binding-profile>]
        [--no-binding-profile]
        [--host <host-id>]
        [--enable | --disable]
        [--name <name>]
        [--security-group <security-group>]
        [--no-security-group]
        [--enable-port-security | --disable-port-security]
        [--dns-name <dns-name>]
        [--allowed-address ip-address=<ip-address>[,mac-address=<mac-address>]]
        [--no-allowed-address]
        <port>

.. option:: --description <description>

    Description of this port

.. option:: --fixed-ip subnet=<subnet>,ip-address=<ip-address>

    Desired IP and/or subnet (name or ID) for this port:
    subnet=<subnet>,ip-address=<ip-address>
    (repeat option to set multiple fixed IP addresses)

.. option:: --no-fixed-ip

    Clear existing information of fixed IP addresses.
    Specify both :option:`--fixed-ip` and :option:`--no-fixed-ip`
    to overwrite the current fixed IP addresses.

.. option:: --device <device-id>

    Port device ID

.. option:: --device-owner <device-owner>

    Device owner of this port. This is the entity that uses
    the port (for example, network:dhcp).

.. option:: --vnic-type <vnic-type>

    VNIC type for this port (direct | direct-physical | macvtap | normal | baremetal,
    default: normal)

.. option:: --binding-profile <binding-profile>

    Custom data to be passed as binding:profile. Data may
    be passed as <key>=<value> or JSON.
    (repeat option to set multiple binding:profile data)

.. option:: --no-binding-profile

    Clear existing information of binding:profile.
    Specify both :option:`--binding-profile` and :option:`--no-binding-profile`
    to overwrite the current binding:profile information.

.. option:: --host <host-id>

    Allocate port on host ``<host-id>`` (ID only)

.. option:: --enable

    Enable port

.. option:: --disable

    Disable port

.. option:: --name

    Set port name

.. option:: --security-group <security-group>

    Security group to associate with this port (name or ID)
    (repeat option to set multiple security groups)

.. option::  --no-security-group

    Clear existing security groups associated with this port

.. option::  --enable-port-security

    Enable port security for this port

.. option::  --disable-port-security

    Disable port security for this port

.. option:: --dns-name <dns-name>

    Set DNS name to this port
    (requires DNS integration extension)

.. option:: --allowed-address ip-address=<ip-address>[,mac-address=<mac-address>]

    Add allowed-address pair associated with this port:
    ip-address=<ip-address>[,mac-address=<mac-address>]
    (repeat option to set multiple allowed-address pairs)

.. option:: --no-allowed-address

    Clear existing allowed-address pairs associated
    with this port.
    (Specify both --allowed-address and --no-allowed-address
    to overwrite the current allowed-address pairs)

.. _port_set-port:
.. describe:: <port>

    Port to modify (name or ID)

port show
---------

Display port details

.. program:: port show
.. code:: bash

    openstack port show
        <port>

.. _port_show-port:
.. describe:: <port>

    Port to display (name or ID)

port unset
----------

Unset port properties

.. program:: port unset
.. code:: bash

    openstack port unset
        [--fixed-ip subnet=<subnet>,ip-address=<ip-address> [...]]
        [--binding-profile <binding-profile-key> [...]]
        [--security-group <security-group> [...]]
        [--allowed-address ip-address=<ip-address>[,mac-address=<mac-address>] [...]]
        <port>

.. option:: --fixed-ip subnet=<subnet>,ip-address=<ip-address>

    Desired IP and/or subnet (name or ID) which should be removed
    from this port: subnet=<subnet>,ip-address=<ip-address>
    (repeat option to unset multiple fixed IP addresses)

.. option:: --binding-profile <binding-profile-key>

    Desired key which should be removed from binding-profile
    (repeat option to unset multiple binding:profile data)

.. option:: --security-group <security-group>

    Security group which should be removed from this port (name or ID)
    (repeat option to unset multiple security groups)

.. option:: --allowed-address ip-address=<ip-address>[,mac-address=<mac-address>]

    Desired allowed-address pair which should be removed from this port:
    ip-address=<ip-address>[,mac-address=<mac-address>]
    (repeat option to unset multiple allowed-address pairs)

.. _port_unset-port:
.. describe:: <port>

    Port to modify (name or ID)
