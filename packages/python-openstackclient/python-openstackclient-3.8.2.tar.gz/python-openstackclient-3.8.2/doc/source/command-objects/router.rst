======
router
======

A **router** is a logical component that forwards data packets between
networks. It also provides Layer 3 and NAT forwarding to provide external
network access for servers on project networks.

Network v2

router add port
---------------

Add a port to a router

.. program:: router add port
.. code:: bash

    openstack router add port
        <router>
        <port>

.. _router_add_port:

.. describe:: <router>

    Router to which port will be added (name or ID)

.. describe:: <port>

    Port to be added (name or ID)

router add subnet
-----------------

Add a subnet to a router

.. program:: router add subnet
.. code:: bash

    openstack router add subnet
        <router>
        <subnet>

.. _router_add_subnet:

.. describe:: <router>

    Router to which subnet will be added (name or ID)

.. describe:: <subnet>

    Subnet to be added (name or ID)

router create
-------------

Create new router

.. program:: router create
.. code:: bash

    openstack router create
        [--project <project> [--project-domain <project-domain>]]
        [--enable | --disable]
        [--distributed]
        [--ha]
        [--description <description>]
        [--availability-zone-hint <availability-zone>]
        <name>

.. option:: --project <project>

    Owner's project (name or ID)

.. option:: --project-domain <project-domain>

    Domain the project belongs to (name or ID).
    This can be used in case collisions between project names exist.

.. option:: --enable

    Enable router (default)

.. option:: --disable

    Disable router

.. option:: --distributed

    Create a distributed router

.. option:: --ha

    Create a highly available router

.. option:: --description <description>

    Set router description

.. option:: --availability-zone-hint <availability-zone>

    Availability Zone in which to create this router
    (Router Availability Zone extension required,
    repeat option to set multiple availability zones)

.. _router_create-name:
.. describe:: <name>

    New router name

router delete
-------------

Delete router(s)

.. program:: router delete
.. code:: bash

    openstack router delete
        <router> [<router> ...]

.. _router_delete-router:
.. describe:: <router>

    Router(s) to delete (name or ID)

router list
-----------

List routers

.. program:: router list
.. code:: bash

    openstack router list
        [--name <name>]
        [--enable | --disable]
        [--long]
        [--project <project> [--project-domain <project-domain>]]

.. option:: --long

    List additional fields in output

.. option:: --name <name>

    List routers according to their name

.. option:: --enable

    List enabled routers

.. option:: --disable

    List disabled routers

.. option:: --project <project>

    List routers according to their project (name or ID)

.. option:: --project-domain <project-domain>

    Domain the project belongs to (name or ID).
    This can be used in case collisions between project names exist.

router remove port
------------------

Remove a port from a router

.. program:: router remove port
.. code:: bash

    openstack router remove port
        <router>
        <port>

.. _router_remove_port:

.. describe:: <router>

    Router from which port will be removed (name or ID)

.. describe:: <port>

    Port to be removed and deleted (name or ID)

router remove subnet
--------------------

Remove a subnet from a router

.. program:: router remove subnet
.. code:: bash

    openstack router remove subnet
        <router>
        <subnet>

.. _router_remove_subnet:

.. describe:: <router>

    Router from which subnet will be removed (name or ID)

.. describe:: <subnet>

    Subnet to be removed (name or ID)

router set
----------

Set router properties

.. program:: router set
.. code:: bash

    openstack router set
        [--name <name>]
        [--enable | --disable]
        [--distributed | --centralized]
        [--description <description>]
        [--route destination=<subnet>,gateway=<ip-address> | --no-route]
        [--ha | --no-ha]
        [--external-gateway <network> [--enable-snat|--disable-snat] [--fixed-ip subnet=<subnet>,ip-address=<ip-address>]]
        <router>

.. option:: --name <name>

    Set router name

.. option:: --enable

    Enable router

.. option:: --disable

    Disable router

.. option:: --distributed

    Set router to distributed mode (disabled router only)

.. option:: --centralized

    Set router to centralized mode (disabled router only)

.. option:: --description <description>

    Set router description

.. option:: --route destination=<subnet>,gateway=<ip-address>

    Routes associated with the router
    destination: destination subnet (in CIDR notation)
    gateway: nexthop IP address
    (repeat option to set multiple routes)

.. option:: --no-route

    Clear routes associated with the router.
    Specify both --route and --no-route to overwrite
    current value of route.

.. option:: --ha

    Set the router as highly available (disabled router only)

.. option:: --no-ha

    Clear high availablability attribute of the router (disabled router only)

.. option:: --external-gateway <network>

    External Network used as router's gateway (name or ID)

.. option:: --enable-snat

    Enable Source NAT on external gateway

.. option:: --disable-snat

    Disable Source NAT on external gateway

.. option:: --fixed-ip subnet=<subnet>,ip-address=<ip-address>

    Desired IP and/or subnet (name or ID) on external gateway:
    subnet=<subnet>,ip-address=<ip-address>
    (repeat option to set multiple fixed IP addresses)

.. _router_set-router:
.. describe:: <router>

    Router to modify (name or ID)

router show
-----------

Display router details

.. program:: router show
.. code:: bash

    openstack router show
        <router>

.. _router_show-router:
.. describe:: <router>

    Router to display (name or ID)

router unset
------------

Unset router properties

.. program:: router unset
.. code:: bash

    openstack router unset
        [--route destination=<subnet>,gateway=<ip-address>]
        [--external-gateway]
        <router>

.. option:: --route destination=<subnet>,gateway=<ip-address>

    Routes to be removed from the router
    destination: destination subnet (in CIDR notation)
    gateway: nexthop IP address
    (repeat option to unset multiple routes)

.. option:: --external-gateway

    Remove external gateway information from the router

.. _router_unset-router:
.. describe:: <router>

    Router to modify (name or ID)
