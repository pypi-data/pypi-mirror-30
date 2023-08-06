Senza template for automatic deployment of PostgreSQL instances
===============================================================

This package provides an external template for the stups-senza tool (https://github.com/zalando-stups/senza), allowing rapid deployment of PostgreSQL nodes on AWS. It's designed to work together with an external tool that runs
senza with all necessary parameters and deploy DB instances automatically, therefore, the template is a non-interactive one. Compared to the PostgresApp template (included with senza) it adds the following actions:

- NAT gateways are detected based on the customer DNS zone.
- Correct Etcd endpoints in the current account are detected for a specific region.
- Non-interactive mode is the default one, all parameters can be supplied with environment variables (`-v` option during senza init).
- pg_hba.conf is configured by default to reject non-SSL connections.
- Standby and superuser passwords are automatically generated.
- All passwords and scalyr keys are encrypted.
- zmon2 group is automatically picked from the current account.
- EBS is always used.

Installation
============

.. code-block:: bash

    $ sudo pip3 install --upgrade senza.templates.acid

Usage
=====

.. code-block:: bash

    $ senza init -t base [-v param=name] deployment.yaml

Below is the list of parameters supported by the template:

- *team_name*: the name of the team to deploy the template (used as part of the DNS name for the resulting instance).
- *team_region*: AWS region of the team to deploy the template (by default, eu-west-1 and eu-central-1 are supported).
- *team_gateway_zone*: the DNS zone the application runs at, to look for the NAT gateways.
- *add_replica_loadbalancer*: whether to add a separate load-balancer to serve requests for the replica (default: false).
- *instance_type*: AWS EC2 instance type to deploy the DB on (default: t2.medium).
- *volume_size*: initial size of the DB EBS volume in GBs (default: 10).
- *volume_type*: AWS type of the EBS volume (default: gp2).
- *volume_iops*: number of the IO operations per second for the provision IO EBS volumes.
- *snapshot_id*: ID of the existing EBS snapshot to initialize the new database from.
- *scalyr_account_key*: Key to the scalyr account to log the database activity.
- *pgpassword_admin*: password to the admin account.
- *postgresql_conf*: a JSON dictionary of the key-value parameters for the PostgreSQL.

Examples:
========

Initialization:

.. code-block:: bash

    $ senza init -t base -v team_name=foo -v 'team_region=eu-west-1' -v 'team_gateway_zone=foo.example.com' -v 'hosted_zone=db.example.com' -v instance_type=m3.medium' -v 'postgresql_conf='{shared_buffers: 1GB}' deploy.yaml

Deployment:

.. code-block:: bash

    $ senza create deploy.yaml bar

The steps above result in the deployment of the new PostgreSQL cluster consisting of 3 t2.medium instances, available under
the name of `bar.db.example.com` and accessible to the application running in the account associated with the DNS zone
`foo.example.com`. They only work in the AWS environment configured for STUPS and senza.

Senza it a powerful tool developed by Zalando to deploy applications on AWS. If you are not familiar with senza-based
deployments, please, refer to the STUPS documentation: http://stups.readthedocs.io/en/latest/.

License
=======
Apache 2.0

Releasing
=========

.. code-block:: bash

    $ ./release.sh <NEW_VERSION>

