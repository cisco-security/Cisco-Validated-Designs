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
author: Troy Levin (@tlevin)
description:
- Enables management of Cisco Tetration external orchestrators.
- Enables creation, modification, and deletion of external orchestrators.
extends_documentation_fragment: tetration
module: tetration_external_orchestrator
notes:
- Requires the tetpyclient Python module.
- Tested with TetrationOS Software, Version 3.1.1.53-PATCH-3.1.1.6 API
options:
  id:
    description:
    - Unique identifier for the orchestrator.
    type: string
  name:
    description:
    - User specified name of the orchestrator.
    type: string
  type:
    description:
    - Type of orchestrator - currently supported values aws, vcenter, kubernetes, f5, nsbalancer.
    type: string
  description:
    description:
    - User specified description of the orchestrator.
    type: string
  aws_region:
    description:
    - AWS Region in which the cluster resides.
    type: string
  username:
    description:
    - Username for the orchestration endpoint.
    type: string
  password:
    description:
    - Password for the orchestration endpoint.
    type: string
  certificate:
    description:
    - Client certificate used for authentication.
    type: string
  key:
    description:
    - Key corresponding to client certificate.
    type: string
  ca_certificate:
    description:
    - CA Certificate to validate orchestration endpoint.
    type: string
  aws_access_key_id:
    description:
    - AWS Access Key ID.
    type: string
  aws_secret_access_key:
    description:
    - AWS Secret Access Key.
    type: string
  insecure:
    description:
    - Turn off strict SSL verification.
    type: boolean
  delta_interval:
    description:
    - Delta polling interval.
    type: integer
  full_snapshot_interval:
    description:
    - Full snapshot interval.
    type: integer
  verbose_tsdb_metrics:
    description:
    - Per-Endpoint TSDB metrics.
    type: boolean
  hosts_list:
    description:
    - Array of {host_name, port_number} to connect to the orchestrator.
    type: array
  services:
    description:
    - Array of Kubernetes Services objects.
    type: array
  kubelet_port:
    description:
    - Kubelet node-local API port.
    type: integer
  state:
    choices: '[present, absent, query]'
    default: query
    description: Add, change, or remove the external orchestrator
    required: true
    type: string
requirements: tetpyclient
version_added: '2.8'
'''

##### Need clarification on what to do here
EXAMPLES = r'''

'''
##### Need clarification on what to do here
RETURN = r'''
---

'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.six import iteritems, iterkeys
from ansible.module_utils.tetration.api import TetrationApiModule
from ansible.module_utils.tetration.api import TETRATION_API_TENANT
from ansible.module_utils.tetration.api import TETRATION_API_EXT_ORCHESTRATORS

def main():
    ''' Main entry point for module execution
    '''
    #
    __LIMIT = 100
    # Module specific spec
    tetration_spec = dict(
        type=dict(type='str', required=True),
        name=dict(type='str', required=True),
        tenant_name=dict(type='str', required=False),
        hosts_list=dict(type='list', required=False),
        insecure=dict(type='bool', required=False),
        id=dict(type='str', required=False),
        description=dict(type='str', required=False),
        username=dict(type='str', required=False),
        password=dict(type='str', required=False),
        aws_access_key_id=dict(type='str', required=False),
        aws_secret_access_key=dict(type='str', required=False),
        delta_interval=dict(type='int', required=False),
        full_snapshot_interval=dict(type='int', required=False),
        verbose_tsdb_metrics=dict(type='bool', required=False),
        aws_region=dict(type='str', required=False),
        ca_certificate=dict(type='str', required=False),
        certificate=dict(type='str', required=False),
        key=dict(type='str', required=False)
    )
    # Common spec for tetration modules
    argument_spec = dict(
        provider=dict(required=True),
        state=dict(default='query', choices=['present', 'absent', 'query'])
    )

    # Combine specs and include provider parameter
    argument_spec.update(tetration_spec)
    argument_spec.update(TetrationApiModule.provider_spec)

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=[
            ['state', 'present', ['tenant_name', 'hosts_list']]
        ]

    )

    # These are all elements we put in our return JSON object for clarity
    tet_module = TetrationApiModule(module)
    result = dict(
        changed=False,
        object=None,
    )

    tenant_name=module.params.get('tenant_name')
    id=module.params.get('id')
    state=module.params.get('state')
    name=module.params.get('name')
    type=module.params.get('type')
    hosts_list=module.params.get('hosts_list')
    orchestrator_options = [
        'type',
        'name',
        'hosts_list',
        'insecure',
        'id',
        'description',
        'username',
        'password',
        'aws_access_key_id',
        'aws_secret_access_key',
        'delta_interval',
        'full_snapshot_interval',
        'verbose_tsdb_metrics',
        'aws_region',
        'ca_certificate',
        'certificate',
        'key'
    ]

    # =========================================================================
    # Get current state of the object
    # =========================================================================

    tenant_object = tet_module.get_object(
        target = TETRATION_API_TENANT,
        filter = dict(
            name=tenant_name
        ),
    )
    if not tenant_object:
        module.fail_json(msg='Unable to find tenant named: %s' % tenant_name)
    else:
        result['object']=tenant_object

    existing_object = tet_module.get_object(
        target = '%s/%s' % (TETRATION_API_EXT_ORCHESTRATORS, tenant_name),
        filter = dict(
            name=name,
            type=type,
        ),
    )

    # ---------------------------------
    # STATE == 'present'
    # ---------------------------------
    if state == 'present':
        new_object = dict()
        for option in orchestrator_options:
            if option:
                new_object[option] = module.params.get(option)
        if existing_object:
            result['changed'] = tet_module.filter_object(existing_object,new_object,check_only=True)
        # if the object does not exist at all, create it
        if not existing_object or result['changed']:
            if not module.check_mode:
                result['object'] = tet_module.run_method(
                    method_name = 'put' if existing_object else 'post',
                    target = '%s/%s/%s' % (TETRATION_API_EXT_ORCHESTRATORS, tenant_name, existing_object['id']) if existing_object else '%s/%s' % (TETRATION_API_EXT_ORCHESTRATORS, tenant_name),
                    req_payload = new_object,
                )
            else:
                result['object'] = tenant_object
            result['changed'] = True

    # ---------------------------------
    # STATE == 'absent'
    # ---------------------------------
    elif state == 'absent':
        # if the object does not exist at all, create it
        if existing_object:
            if not module.check_mode:
                tet_module.run_method(
                    method_name = 'delete',
                    target = '%s/%s/%s' % (TETRATION_API_EXT_ORCHESTRATORS, tenant_name, existing_object['id'])
                )
            result['changed'] = True

    # ---------------------------------
    # STATE == 'query'
    # ---------------------------------
    elif state == 'query':
        # if the object does not exist at all, create it
        result['object'] = existing_object

    module.exit_json(**result)

if __name__ == '__main__':
    main()
