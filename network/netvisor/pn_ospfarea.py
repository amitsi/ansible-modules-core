#!/usr/bin/python
""" PN-CLI vrouter-ospf-add/remove """

#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
#


import subprocess
import shlex

DOCUMENTATION = """
---
module: pn_ospfarea
author: "Pluribus Networks"
version_added: "2.2"
version: 1.0
short_description: CLI command to add/remove ospf area to/from a vrouter.
description:
  - Execute vrouter-ospf-add, vrouter-ospf-remove command.
  - This command adds/removes Open Shortest Path First(OSPF) area to/from
    a virtual router(vRouter) service.
options:
  pn_cliusername:
    description:
      - Login username.
    required: true
    type: str
  pn_clipassword:
    description:
      - Login password.
    required: true
    type: str
  pn_cliswitch:
    description:
      - Target switch(es) to run the CLI on.
    required: False
    type: str
  pn_command:
    description:
      - The C(pn_command) takes the vrouter-ospf-area add/remove
        command as value.
    required: true
    choices: ['vrouter-ospf-area-add', 'vrouter-ospf-area-remove', 'vrouter-ospf-area-modify']
    type: str
  pn_vrouter_name:
    description:
      - specify the name of the vRouter.
    required: true
    type: str
  pn_ospf_area:
    description:
      - Specify the OSPF area number.
    required: true
    type: str
  pn_stub_type:
    description:
      - Specify the OSPF stub type.
    choices: ['none', 'stub', 'stub-no-summary', 'nssa', 'nssa-no-summary']
    type: str
  pn_prefix_listin:
    description:
      - OSPF prefix list for filtering incoming packets.
    type: str
  pn_prefix_listout:
    description:
      - OSPF prefix list for filtering outgoing packets.
    type: str
  pn_quiet:
    description:
      - Enable/disable system information.
    required: false
    type: bool
    default: true
"""

EXAMPLES = """
- name: "Add OSPF area to vrouter"
  pn_ospfarea:
    pn_cliusername: admin
    pn_clipassword: admin
    pn_ospfcommand: vrouter-ospf-area-add
    pn_ospf_area: 1.0.0.0
    pn_stub_type: stub

- name: "Remove OSPF from vrouter"
  pn_ospf:
    pn_cliusername: admin
    pn_clipassword: admin
    pn_ospfcommand: vrouter-ospf-remove
    pn_vrouter_name: name-string
    pn_ospf_area: 1.0.0.0
"""

RETURN = """
command:
  description: the CLI command run on the target node(s).
stdout:
  description: the set of responses from the ospf command.
  returned: always
  type: list
stderr:
  description: the set of error responses from the ospf command.
  returned: on error
  type: list
changed:
  description: Indicates whether the CLI caused changes on the target.
  returned: always
  type: bool
"""


def main():
    """ This section is for arguments parsing """
    module = AnsibleModule(
        argument_spec=dict(
            pn_cliusername=dict(required=True, type='str'),
            pn_clipassword=dict(required=True, type='str'),
            pn_cliswitch=dict(required=False, type='str'),
            pn_command=dict(required=True, type='str',
                            choices=['vrouter-ospf-area-add',
                                     'vrouter-ospf-area-remove',
                                     'vrouter-ospf-area-modify']),
            pn_vrouter_name=dict(required=True, type='str'),
            pn_ospf_area=dict(required=True, type='str'),
            pn_stub_type=dict(type='str', choices=['none', 'stub', 'nssa',
                                                   'stub-no-summary',
                                                   'nssa-no-summary']),
            pn_prefix_listin=dict(type='str'),
            pn_prefix_listout=dict(type='str'),
            pn_quiet=dict(type='bool', default='True')
        )
    )

    # Accessing the arguments
    cliusername = module.params['pn_cliusername']
    clipassword = module.params['pn_clipassword']
    cliswitch = module.params['pn_cliswitch']
    command = module.params['pn_command']
    vrouter_name = module.params['pn_vrouter_name']
    ospf_area = module.params['pn_ospf_area']
    stub_type = module.params['pn_stub_type']
    prefix_listin = module.params['pn_prefix_listin']
    prefix_listout = module.params['pn_prefix_listout']
    quiet = module.params['pn_quiet']

    # Building the CLI command string
    cli = '/usr/bin/cli'

    if quiet is True:
        cli += ' --quiet '

    cli += ' --user %s:%s ' % (cliusername, clipassword)

    if cliswitch:
        if cliswitch == 'local':
            cli += ' switch-local '
        else:
            cli += ' switch ' + cliswitch

    cli += ' %s vrouter-name %s area %s ' % (command, vrouter_name, ospf_area)

    if stub_type:
        cli += ' stub-type ' + stub_type

    if prefix_listin:
        cli += ' prefix-list-in ' + prefix_listin

    if prefix_listout:
        cli += ' prefix-list-out ' + prefix_listout

    # Run the CLI command
    ospfcommand = shlex.split(cli)
    response = subprocess.Popen(ospfcommand, stderr=subprocess.PIPE,
                                stdout=subprocess.PIPE, universal_newlines=True)

    # 'out' contains the output
    # 'err' contains the error messages
    out, err = response.communicate()

    # Response in JSON format
    if err:
        module.exit_json(
            command=cli,
            stderr=err.rstrip("\r\n"),
            changed=False
        )

    else:
        module.exit_json(
            command=cli,
            stdout=out.rstrip("\r\n"),
            changed=True
        )

# AnsibleModule boilerplate
from ansible.module_utils.basic import AnsibleModule

if __name__ == '__main__':
    main()
