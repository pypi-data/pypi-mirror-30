import logging
import os
from builtins import super

from brigade.core.inventory import Inventory

import yaml


class SimpleInventory(Inventory):
    """
    This is a very simple file based inventory. Basically you need two yaml files. One
    for your host information and another one for your group information.

    * host file::

        ---
        host1.cmh:
            site: cmh
            role: host
            group: cmh-host
            nos: linux

        host2.cmh:
            site: cmh
            role: host
            group: cmh-host
            nos: linux

        switch00.cmh:
            brigade_ip: 127.0.0.1
            brigade_username: vagrant
            brigade_password: vagrant
            napalm_port: 12443
            site: cmh
            role: leaf
            group: cmh-leaf
            nos: eos

        switch01.cmh:
            brigade_ip: 127.0.0.1
            brigade_username: vagrant
            brigade_password: ""
            napalm_port: 12203
            site: cmh
            role: leaf
            group: cmh-leaf
            nos: junos

        host1.bma:
            site: bma
            role: host
            group: bma-host
            nos: linux

        host2.bma:
            site: bma
            role: host
            group: bma-host
            nos: linux

        switch00.bma:
            brigade_ip: 127.0.0.1
            brigade_username: vagrant
            brigade_password: vagrant
            napalm_port: 12443
            site: bma
            role: leaf
            group: bma-leaf
            nos: eos

        switch01.bma:
            brigade_ip: 127.0.0.1
            brigade_username: vagrant
            brigade_password: ""
            napalm_port: 12203
            site: bma
            role: leaf
            group: bma-leaf
            nos: junos

    * group file::

        ---
        defaults:
            group: null
            domain: acme.com

        bma-leaf:
            group: bma

        bma-host:
            group: bma

        bma:

        cmh-leaf:
            group: cmh

        cmh-host:
            group: cmh

        cmh:
    """

    def __init__(self, host_file="hosts.yaml", group_file="groups.yaml", **kwargs):
        with open(host_file, "r") as f:
            hosts = yaml.load(f.read())

        if group_file:
            if os.path.exists(group_file):
                with open(group_file, "r") as f:
                    groups = yaml.load(f.read())
            else:
                logging.warning("{}: doesn't exist".format(group_file))
                groups = {}
        else:
            groups = {}

        defaults = groups.pop("defaults", {})
        super().__init__(hosts, groups, defaults, **kwargs)
