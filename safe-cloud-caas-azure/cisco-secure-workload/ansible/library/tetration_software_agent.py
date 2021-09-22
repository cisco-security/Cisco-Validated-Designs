#!/usr/bin/python
# Copyright (c) 2018 Red Hat, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = r'''
---
author: Brandon Beck (@techbeck03)
description: Enables query or removal of software agents
extends_documentation_fragment: tetration
module: tetration_software_agent
notes:
- Requires the tetpyclient Python module.
- Supports check mode.
options:
  ip:
    description:
    - IP of target agent
    - Require one of [C(name), C(ip)]
    - Mutually exclusive to C(name)
    type: string
  name:
    aliases: '[hostname]'
    description:
    - Hostname of target agent
    - Require one of [C(name), C(ip)]
    - Mutually exclusive to C(ip)
    type: string
  state:
    choices: '[absent, query]'
    default: query
    description: Remove or query for software agent
    required: true
    type: string
requirements: tetpyclient
version_added: '2.8'
'''

EXAMPLES = r'''
# Remove agent by hostname
tetration_software_agent:
    name: acme-example-host
    state: absent
    provider:
      host: "tetration-cluster@company.com"
      api_key: 1234567890QWERTY
      api_secret: 1234567890QWERTY

# Delete agent by IP
tetration_software_agent:
    ip: 1.1.1.1
    state: absent
    provider:
      host: "tetration-cluster@company.com"
      api_key: 1234567890QWERTY
      api_secret: 1234567890QWERTY

# Query agent by hostname
tetration_software_agent:
    name: acme-example-host
    state: query
    provider:
      host: "tetration-cluster@company.com"
      api_key: 1234567890QWERTY
      api_secret: 1234567890QWERTY
'''

RETURN = r'''
---
object:
  contains:
    agent_type:
      description: Agent type
      sample: ENFORCER
      type: string
    arch:
      description: CPU architecture type
      sample: x86_64
      type: string
    auto_upgrade_opt_out:
      description: If True, agents are not auto-upgraded during upgrade of Tetration
        cluster
      sample: 'False'
      type: bool
    cpu_quota_mode:
      description: The amount of CPU quota to give to agent on the end host (pct)
      sample: 1
      type: int
    cpu_quota_usec:
      description: The amount of CPU quota to give to agent on the end host (us)
      sample: 30000
      type: int
    created_at:
      description: Date this inventory was created (Unix Epoch)
      sample: 1553626033
      type: string
    current_sw_version:
      description: Current version of software agent
      sample: 3.1.1.65-enforcer
      type: string
    data_plane_disabled:
      description: If true, agent stops reporting flows to Tetration
      sample: 'False'
      type: bool
    desired_sw_version:
      description: Desired version of software agent
      sample: 3.1.1.65-enforcer
      type: string
    enable_cache_sidechannel:
      description: Whether or not sidechannel detection is enabled
      sample: 'True'
      type: bool
    enable_forensic:
      description: Whether or not forensics is enabled
      sample: 'True'
      type: bool
    enable_meltdown:
      description: Whether or not meltdown detection is enabled
      sample: 'True'
      type: bool
    enable_pid_lookup:
      description: Whether or not pid lookup for flow search is enabled
      sample: 'True'
      type: bool
    host_name:
      description: Hostname as reported by software agent
      returned: when C(state) is present or query
      sample: acme-example-host
      type: string
    interfaces:
      description: List of interfaces reported by software agent
      sample: JSON Interfaces
      type: list
    last_config_fetch_at:
      description: Date of last configuration fetch (Unix Epoch)
      sample: 1563458124
      type: string
    last_software_update_at:
      description: Date of last software update (Unix Epoch)
      sample: 1553626033
      type: string
    platform:
      description: OS platform type
      sample: CentOS-7.6
      type: string
    uuid:
      description: UUID of the registered software agent
      returned: when C(state) is present or query
      sample: d322189839fb70b2f4569f3657eea58f096c0686
      type: int
  description: the changed or modified object(s)
  returned: always
  type: complex
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.six import iteritems, iterkeys
from ansible.module_utils.tetration.api import TetrationApiModule
from ansible.module_utils.tetration.api import TETRATION_API_SENSORS

def main():
    ''' Main entry point for module execution
    '''
    #
    __LIMIT = 100
    # Module specific spec
    tetration_spec = dict(
        name=dict(type='str', aliases=['hostname']),
        ip=dict(type='str')
    )
    # Common spec for tetration modules
    argument_spec = dict(
        provider=dict(required=True),
        state=dict(default='query', choices=['absent', 'query'])
    )

    # Combine specs and include provider parameter
    argument_spec.update(tetration_spec)
    argument_spec.update(TetrationApiModule.provider_spec)

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_one_of=[
            ['name', 'ip']
        ],
        mutually_exclusive=[
            ['name', 'ip']
        ]
    )

    # These are all elements we put in our return JSON object for clarity
    tet_module = TetrationApiModule(module)
    result = dict(
        changed=False,
        failed=False,
        api_version=module.params['provider']['api_version'],
        tetration=module.params['provider']['server_endpoint'],
        object=None,
    )

    def get_sensors(offset=''):
        return tet_module.run_method(
            'get',
            target='%s' % TETRATION_API_SENSORS,
            params=dict(
                limit=__LIMIT,
                offset=offset
            )
        )

    # =========================================================================
    # Search through sensors for one matching passed IP or hostname
    offset = ''
    keep_searching = True
    target_sensors = []
    while keep_searching:
        query_result = get_sensors(offset)
        if not query_result or 'results' not in query_result:
            break
        for sensor in query_result['results']:
            if module.params['name']:
                if sensor['host_name'] == module.params['name'] and 'deleted_at' not in sensor:
                    target_sensors.append(sensor)
            else:
                for interface in sensor['interfaces']:
                    if interface['ip'] == module.params['ip'] and 'deleted_at' not in sensor:
                        target_sensors.append(sensor)
            if not keep_searching:
                break
        if 'offset' in query_result:
            offset = query_result['offset']
        else:
            keep_searching = False

    result['object'] = target_sensors
    # ---------------------------------
    # STATE == 'absent'
    # ---------------------------------
    if module.params['state'] in 'absent':
        result['changed'] = True if target_sensors else False
        if not result['changed']:
            module.exit_json(**result)
        else:
            if not module.check_mode:
                for sensor in target_sensors:
                    tet_module.run_method(
                        'delete',
                        target='%s/%s' % (TETRATION_API_SENSORS, sensor['uuid'])
                    )
            result['object'] = None
            module.exit_json(**result)
    # ---------------------------------
    # STATE == 'query'
    # ---------------------------------
    else:
        module.exit_json(**result)


if __name__ == '__main__':
    main()
