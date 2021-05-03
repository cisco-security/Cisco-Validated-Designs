#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2018, Doron Chosnek
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = r'''
---
author: Brandon Beck (@techbeck03)
description: Enables creation, modification, deletion and query of application policy
  ports
extends_documentation_fragment: tetration
module: tetration_application_policy_ports
notes:
- Requires the tetpyclient Python module.
- Supports check mode.
options:
  app_id:
    description: The id for the Application to which the policy belongs
    type: string
  app_scope_id:
    description: The id for the Scope associated with the application
    type: string
  end_port:
    description: End port of the range
    type: int
  policy_id:
    description: Unique identifier for the policy
    required: true
    type: string
  proto_id:
    description: Protocol Integer value (NULL means all protocols)
    type: int
  proto_name:
    description: Protocol name (Ex TCP, UDP, ICMP, ANY)
    type: string
  start_port:
    description: Start port of the range
    type: int
  state:
    choices: '[present, absent, query]'
    description: Add, change, remove or query for application policy ports
    required: true
    type: string
  version:
    description: Indications the version of the Application for which to get the policies
    required: true
    type: string
requirements: tetpyclient
version_added: '2.8'
'''

EXAMPLES = r'''
# Add a single port to policy
tetration_application_policy_ports:
    app_id: 59836821755f02724cbb54fb
    app_scope_id: 5981453a497d4f430df1fd8c
    policy_id: 5a2e8579497d4f415ea20e38
    version: "v0"
    proto_name: TCP
    start_port: 22
    end_port: 22
    state: present
    provider:
      host: "tetration-cluster@company.com"
      api_key: 1234567890QWERTY
      api_secret: 1234567890QWERTY

# Add ANY port to policy
tetration_application_policy_ports:
    app_id: 59836821755f02724cbb54fb
    app_scope_id: 5981453a497d4f430df1fd8c
    policy_id: 5a2e8579497d4f415ea20e38
    version: "v0"
    proto_name: ANY
    state: present
    provider:
      host: "tetration-cluster@company.com"
      api_key: 1234567890QWERTY
      api_secret: 1234567890QWERTY

# Delete port from policy
tetration_application_policy_ports:
    app_id: 59836821755f02724cbb54fb
    app_scope_id: 5981453a497d4f430df1fd8c
    policy_id: 5a2e8579497d4f415ea20e38
    version: "v0"
    state: absent
    provider:
      host: "tetration-cluster@company.com"
      api_key: 1234567890QWERTY
      api_secret: 1234567890QWERTY
'''

RETURN = r'''
---
object:
  contains:
    id:
      description: Unique identifier for the L4 policy params
      returned: when C(state) is present or query
      sample: 5c93da83497d4f33d7145960
      type: int
    port:
      description: List containing start and end of port range
      returned: when C(state) is present or query
      sample: '[80, 80]'
      type: list
    proto:
      description: Protocol integer ID
      returned: when C(state) is present or query
      sample: 6
      type: string
  description: the changed or modified object
  returned: always
  type: complex
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.tetration.api import TetrationApiModule
from ansible.module_utils.tetration.api import TETRATION_API_APPLICATIONS
from ansible.module_utils.tetration.api import TETRATION_API_SCOPES
from ansible.module_utils.tetration.api import TETRATION_API_APPLICATION_POLICIES
from ansible.module_utils.tetration.api import TETRATION_API_PROTOCOLS

from ansible.utils.display import Display
display = Display()

from time import sleep

def main():
    tetration_spec=dict(
        app_id=dict(type='str', required=False),
        app_scope_id=dict(type='str', required=False),
        policy_id=dict(type='str', required=True),
        version = dict(type='str', required=True),
        start_port = dict(type='int', required=False),
        end_port = dict(type='int', required=False),
        proto_id = dict(type='int', required=False),
        proto_name = dict(type='str', required=False),
    )

    argument_spec = dict(
        provider=dict(required=True),
        state=dict(required=True, choices=['present', 'absent', 'query'])
    )

    argument_spec.update(tetration_spec)
    argument_spec.update(TetrationApiModule.provider_spec)

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    tet_module = TetrationApiModule(module)

    # These are all elements we put in our return JSON object for clarity
    result = dict(
        changed=False,
        object=None,
    )

    state = module.params['state']
    app_id = module.params['app_id']
    app_scope_id = module.params['app_scope_id']
    policy_id = module.params['policy_id']
    version = module.params['version']
    start_port = module.params['start_port']
    end_port = module.params['end_port']
    proto_id = module.params['proto_id']
    proto_name = module.params['proto_name']
    existing_app = None
    existing_app_scope = None
    existing_policy = None
    existing_param = None

    if state == 'present' and proto_name != 'ANY':
        missing_properties = ''
        for parameters in (['start_port'],['end_port'],['proto_id','proto_name']):
            pass_flag = False
            for parameter in parameters:
                if module.params[parameter]:
                    pass_flag = True
            if not pass_flag:
                if len(parameters) == 1:
                    missing_properties = missing_properties + parameters[0] + ', '
                else:
                    missing_properties = missing_properties + " or ".join(parameters) + ', '
        if missing_properties:
            module.fail_json(msg='The following missing parameters are required: %s' % missing_properties[:-2])


    # =========================================================================
    # Get current state of the object
    existing_app_scope = tet_module.run_method(
        method_name = 'get',
        target = '%s/%s' % (TETRATION_API_SCOPES, app_scope_id)
    )
    if not existing_app_scope:
        module.fail_json(msg='Unable to find existing app scope with id: %s' % app_scope_id)

    existing_app = tet_module.run_method(
        method_name = 'get',
        target = '%s/%s' % (TETRATION_API_APPLICATIONS, app_id)
    )
    if not existing_app:
        module.fail_json(msg='Unable to find existing application with id: %s' % app_id)

    existing_policy = tet_module.run_method(
        method_name = 'get',
        target = '%s/%s' % (TETRATION_API_APPLICATION_POLICIES, policy_id)
    )
    if not existing_policy:
        module.fail_json(msg='Unable to find existing application policy with id: %s' % policy_id)

    existing_params = existing_policy['l4_params']

    for protocol in TETRATION_API_PROTOCOLS:
        if proto_name:
            if protocol['name'] == proto_name:
                proto_id = protocol['value']
                break
        elif proto_id:
            if protocol['value'] == proto_id:
                proto_name = protocol['name']
                break
    if proto_id is None:
        if proto_name:
            module.fail_json(msg='Invalid Protocol name: %s' % proto_name)
        else:
            module.fail_json(msg='Invalid Protocol number: %s' % proto_id)

    if existing_params:
        for param in existing_params:
            if not proto_id and not param['proto']:
                existing_param = param
                break
            if param['proto'] == proto_id and param['port'][0] == start_port and param['port'][0] == end_port:
                existing_param = param
                break
    # =========================================================================
    # Now enforce the desired state (present, absent, query)

    # ---------------------------------
    # STATE == 'present'
    # ---------------------------------
    if state == 'present':

        # if the object does not exist at all, create it
        new_object = dict(
            version = version,
            start_port = start_port if proto_name != 'ANY' else None,
            end_port = end_port if proto_name != 'ANY' else None,
            proto = proto_id if proto_name != 'ANY' else None
        )

        if not existing_param:
            if not module.check_mode:
                param_object = tet_module.run_method(
                    method_name = 'post',
                    target = '%s/%s/l4_params' % (TETRATION_API_APPLICATION_POLICIES, policy_id),
                    req_payload = new_object
                )
                new_object['id'] = param_object['id']
            result['changed'] = True
            result['object'] = param_object
        else:
            result['changed'] = False
            result['object'] = existing_param

    # ---------------------------------
    # STATE == 'absent'
    # ---------------------------------

    elif state == 'absent':
        if existing_param:
            if not module.check_mode:
                tet_module.run_method(
                    method_name = 'delete',
                    target = '%s/%s/l4_params/%s' % (TETRATION_API_APPLICATION_POLICIES, policy_id, existing_param['id'])
                )
            result['changed'] = True

    # ---------------------------------
    # STATE == 'query'
    # ---------------------------------

    elif state == 'query':
        result['object'] = existing_param

    # Return result
    module.exit_json(**result)

if __name__ == '__main__':
    main()
