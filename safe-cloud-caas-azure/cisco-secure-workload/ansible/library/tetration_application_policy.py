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
description: Enables creation, modification, deletion and query of an application
  policy
extends_documentation_fragment: tetration
module: tetration_application_policy
notes:
- Requires the tetpyclient Python module.
- Supports check mode.
options:
  app_id:
    description:
    - The id for the Application to which the policy belongs
    - Require one of [C(app_name), C(app_id)]
    - Mutually exclusive to C(app_name)
    type: string
  app_name:
    description:
    - The name for the Application to which the policy belongs
    - Require one of [C(app_name), C(app_id)]
    - Mutually exclusive to C(app_id)
    type: string
  app_scope_id:
    description:
    - The id for the Scope associated with the application
    - Require one of [C(app_scope_name), C(app_scope_id), C(app_id)]
    - Mutually exclusive to C(app_scope_name)
    type: string
  app_scope_name:
    description:
    - The name for the Scope associated with the application
    - Require one of [C(app_scope_name), C(app_scope_id), C(app_id)]
    - Mutually exclusive to C(app_scope_id)
    type: string
  consumer_filter_id:
    description:
    - ID of a defined filter. Currently, any cluster, user defined filter or scope
      can be used as the consumer of a policy
    - Mutually exclusive to C(consumer_filter_name)
    type: string
  consumer_filter_name:
    description:
    - Name of a defined filter. Currently, any cluster, user defined filter or scope
      can be used as the consumer of a policy
    - Mutually exclusive to C(consumer_filter_id)
    type: string
  policy_action:
    description:
    - Possible values can be ALLOW or DENY. Indicates whether traffic should be allowed
      or dropped for the given service port/protocol between the consumer and provider
    - Required if I(state=present)
    type: string
  priority:
    description: Used to sort policy
    type: int
  provider_filter_id:
    description:
    - ID of a defined filter. Currently, any cluster, user defined filter or scope
      can be used as the provider of a policy
    - Mutually exclusive to C(provider_filter_name)
    type: string
  provider_filter_name:
    description:
    - Name of a defined filter. Currently, any cluster, user defined filter or scope
      can be used as the provider of a policy
    - Mutually exclusive to C(provider_filter_id)
    type: string
  rank:
    description:
    - 'Policy rank, possible values: DEFAULT, ABSOLUTE or CATCHALL'
    - Required if I(state=present)
    type: string
  state:
    choices: '[present, absent, query]'
    description: Add, change, remove or query for application policy
    required: true
    type: string
  version:
    description:
    - Indicates the version of the Application to which the policy belongs
    - Required if I(state=present)
    type: string
requirements: tetpyclient
version_added: '2.8'
'''

EXAMPLES = r'''
# Add or modify application policy
tetration_application_policy:
    app_id: 59836821755f02724cbb54fb
    app_scope_id: 5981453a497d4f430df1fd8c
    provider_filter_name: ACME:Example:Scope1
    consumer_filter_name: ACME:Example:Scope2
    version: v0
    rank: ABSOLUTE
    policy_action: ALLOW
    priority: 100
    state: present
    provider:
      host: "tetration-cluster@company.com"
      api_key: 1234567890QWERTY
      api_secret: 1234567890QWERTY

# Delete application policy
tetration_application_policy:
    app_id: 59836821755f02724cbb54fb
    app_scope_id: 5981453a497d4f430df1fd8c
    provider_filter_name: ACME:Example:Scope1
    consumer_filter_name: ACME:Example:Scope2
    version: v0
    rank: ABSOLUTE
    policy_action: ALLOW
    priority: 100
    state: absent
    provider:
      host: "tetration-cluster@company.com"
      api_key: 1234567890QWERTY
      api_secret: 1234567890QWERTY

# Query for application policy
tetration_application_policy:
    app_id: 59836821755f02724cbb54fb
    app_scope_id: 5981453a497d4f430df1fd8c
    provider_filter_name: ACME:Example:Scope1
    consumer_filter_name: ACME:Example:Scope2
    version: v0
    rank: ABSOLUTE
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
    absolute_policies:
      description: List of all absolute policies
      returned: when C(state) is present or query
      type: list
    catch_all_action:
      description: Catch all policy action (DENY,ALLOW)
      returned: when C(state) is present or query
      sample: DENY
      type: string
    default_policies:
      description: List of all default policies
      returned: when C(state) is present or query
      type: list
  description: the changed or modified object
  returned: always
  type: complex
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.tetration.api import TetrationApiModule
from ansible.module_utils.tetration.api import TETRATION_API_APPLICATIONS
from ansible.module_utils.tetration.api import TETRATION_API_SCOPES
from ansible.module_utils.tetration.api import TETRATION_API_INVENTORY_FILTER
from ansible.module_utils.tetration.api import TETRATION_API_APPLICATION_POLICIES

from ansible.utils.display import Display
display = Display()

def main():
    tetration_spec=dict(
        app_name=dict(type='str', required=False),
        app_id=dict(type='str', required=False),
        app_scope_name=dict(type='str', required=False),
        app_scope_id=dict(type='str', required=False),
        consumer_filter_id=dict(type='str', required=False),
        consumer_filter_name=dict(type='str', required=False),
        provider_filter_id=dict(type='str', required=False),
        provider_filter_name=dict(type='str', required=False),
        version=dict(type='str', required=False),
        rank=dict(type='str', required=False, choices=['DEFAULT', 'ABSOLUTE', 'CATCHALL']),
        policy_action=dict(type='str', required=False, choices=['ALLOW', 'DENY']),
        priority=dict(type='int', required=False),
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
        mutually_exclusive=[
            ['app_name', 'app_id'],
            ['app_scope_name', 'app_scope_id'],
            ['consumer_filter_id', 'consumer_filter_name'],
            ['provider_filter_id', 'provider_filter_name']
        ],
        required_one_of=[
            ['app_name', 'app_id'],
            ['app_scope_name', 'app_scope_id', 'app_id'],
        ],
        required_if=[
            ['state', 'present', ['version', 'rank', 'policy_action']]
        ]
    )

    tet_module = TetrationApiModule(module)

    # These are all elements we put in our return JSON object for clarity
    result = dict(
        changed=False,
        object=None,
    )

    state = module.params['state']
    app_name = module.params['app_name']
    app_id = module.params['app_id']
    app_scope_name = module.params['app_scope_name']
    app_scope_id = module.params['app_scope_id']
    consumer_filter_id = module.params['consumer_filter_id']
    consumer_filter_name = module.params['consumer_filter_name']
    provider_filter_id = module.params['provider_filter_id']
    provider_filter_name = module.params['provider_filter_name']
    version = module.params['version']
    rank = module.params['rank']
    policy_action = module.params['policy_action']
    priority = module.params['priority']
    existing_app_scope = None
    existing_app = None
    existing_policy = None
    app_scopes = None

    if state == 'present' and rank != 'CATCHALL':
        missing_properties = []
        for parameters in (['consumer_filter_id','consumer_filter_name'], ['provider_filter_id','provider_filter_name'], ['priority']):
            pass_flag = False
            for parameter in parameters:
                if module.params[parameter]:
                    pass_flag = True
            if not pass_flag:
                if len(parameters) == 1:
                    missing_properties.append(parameters)
                else:
                    missing_properties.append(" or ".join(parameters))
        if missing_properties:
            module.fail_json(msg='The following missing parameters are required: %s' % ','.join(missing_properties))

    elif state =='absent' and rank == 'CATCHALL':
        module.fail_json(msg='State `absent` is not supported for the catchall policy.  Use `present` and set the desired `policy_action`')
    # elif state == 'present' and rank == 'CATCHALL':
    #     invalid_properties = [ parameter for parameter in ['consumer_filter_id', 'provider_filter_id', 'priority'] if module.params[parameter] ]
    #     if invalid_properties:
    #         module.fail_json(msg='The following parameters are not allowed with rank `CATCHALL`: %s' % ','.join(invalid_properties))

    # =========================================================================
    # Get current state of the object
    if app_scope_id:
        existing_app_scope = tet_module.run_method(
            method_name = 'get',
            target = '%s/%s' % (TETRATION_API_SCOPES, app_scope_id)
        )
        if not existing_app_scope:
            module.fail_json(msg='Unable to find existing app scope with id: %s' % app_scope_id)

    elif not app_scope_id:
        existing_app_scope = tet_module.get_object(
            target = TETRATION_API_SCOPES,
            filter = dict(name=app_scope_name)
        )
        if not existing_app_scope:
            module.fail_json(msg='Unable to find existing app scope named: %s' % app_scope_name)

    if app_id:
        existing_app = tet_module.run_method(
            method_name = 'get',
            target = '%s/%s' % (TETRATION_API_APPLICATIONS, app_id)
        )
        if not existing_app_scope:
            module.fail_json(msg='Unable to find existing application named: %s' % app_name)
    elif not app_id:
        existing_app = tet_module.get_object(
            target = TETRATION_API_APPLICATIONS,
            filter = dict(name=app_name,app_scope_id=existing_app_scope['id'])
        )
        if not existing_app:
            module.fail_json(msg='Unable to find existing app with id: %s' % app_id)

    if rank != 'CATCHALL':
        existing_policies = tet_module.run_method(
            method_name = 'get',
            target = '%s/%s/%s' % (TETRATION_API_APPLICATIONS, existing_app['id'], 'absolute_policies' if rank == 'ABSOLUTE' else 'default_policies'),
        )
        if existing_policies:
            for policy in existing_policies:
                if policy['version'] != version:
                    continue
                consumer_flag = False
                provider_flag = False
                if consumer_filter_id:
                    consumer_flag = consumer_filter_id == policy['consumer_filter_id']
                elif consumer_filter_name:
                    consumer_flag = consumer_filter_name == policy['consumer_filter']['name']
                    if consumer_flag:
                        consumer_filter_id = policy['consumer_filter_id']
                if provider_filter_id:
                    provider_flag = provider_filter_id == policy['provider_filter_id']
                elif provider_filter_name:
                    provider_flag = provider_filter_name == policy['provider_filter']['name']
                    if provider_flag:
                        provider_filter_id = policy['provider_filter_id']

                if consumer_flag and provider_flag:
                    existing_policy = policy
                    break

    else:
        existing_policy = tet_module.run_method(
            method_name = 'get',
            target = '%s/%s/catch_all' % (TETRATION_API_APPLICATIONS, existing_app['id']),
        )

    if not existing_policy:
        if not (consumer_filter_id and provider_filter_id):
            app_clusters = tet_module.run_method(
                method_name = 'get',
                target = '%s/%s/clusters' % (TETRATION_API_APPLICATIONS, existing_app['id'])
            )
            if app_clusters:
                for item in app_clusters:
                    consumer_filter_id = consumer_filter_id if consumer_filter_id else item['id'] if item['name'] == consumer_filter_name else None
                    provider_filter_id = provider_filter_id if provider_filter_id else item['id'] if item['name'] == provider_filter_name else None
                    if consumer_filter_id and provider_filter_id:
                        break
        if not (consumer_filter_id and provider_filter_id):
            app_scopes = tet_module.get_object(
                target = TETRATION_API_SCOPES,
                filter = dict(root_app_scope_id = existing_app_scope['root_app_scope_id']),
                allow_multiple = True
            )
            scope_ids = [ scope['id'] for scope in app_scopes ]
            inventory_filters = tet_module.run_method(
                method_name = 'get',
                target = TETRATION_API_INVENTORY_FILTER,
            )
            inventory_filters = [ valid_filter for valid_filter in inventory_filters if valid_filter['app_scope_id'] in scope_ids ]
            if inventory_filters:
                for item in inventory_filters:
                    consumer_filter_id = consumer_filter_id if consumer_filter_id else item['id'] if item['name'] == consumer_filter_name else None
                    provider_filter_id = provider_filter_id if provider_filter_id else item['id'] if item['name'] == provider_filter_name else None
                    if consumer_filter_id and provider_filter_id:
                        break
        if not (consumer_filter_id and provider_filter_id):
            if app_scopes:
                for item in app_scopes:
                    consumer_filter_id = consumer_filter_id if consumer_filter_id else item['id'] if item['name'] == consumer_filter_name else None
                    provider_filter_id = provider_filter_id if provider_filter_id else item['id'] if item['name'] == provider_filter_name else None
                    if consumer_filter_id and provider_filter_id:
                        break
        if not (consumer_filter_id and provider_filter_id):
            if consumer_filter_id and not provider_filter_id:
                module.fail_json(msg='Failed to resolve provider_filter_id: %s' % provider_filter_id)
            elif provider_filter_id and not consumer_filter_id:
                module.fail_json(msg='Failed to resolve consumer_filter_id: %s' % consumer_filter_id)
            else:
                module.fail_json(msg='Failed to resolve consumer_filter_id: %s and provider_filter_id: %s' % (consumer_filter_id, provider_filter_id))

    # =========================================================================
    # Now enforce the desired state (present, absent, query)

    # ---------------------------------
    # STATE == 'present'
    # ---------------------------------
    if state == 'present':

        # if the object does not exist at all, create it
        if rank != 'CATCHALL':
            new_object = dict(
                consumer_filter_id = consumer_filter_id,
                provider_filter_id = provider_filter_id,
                version = version,
                rank = rank,
                action = policy_action,
                priority = priority
            )
        else:
            new_object = dict(
                version = version,
                rank = 'CATCH_ALL',
                action = policy_action
            )
        if existing_policy:
            new_object['id'] = existing_policy['id']
            result['changed'] = tet_module.filter_object(new_object, existing_policy, check_only=True)
            if result['changed']:
                if not module.check_mode:
                    if rank != 'CATCHALL':
                        tet_module.run_method(
                            method_name = 'put',
                            target = '%s/%s' % (TETRATION_API_APPLICATION_POLICIES, existing_policy['id']),
                            req_payload = dict(
                                consumer_filter_id = consumer_filter_id,
                                provider_filter_id = provider_filter_id,
                                rank = rank,
                                policy_action = policy_action,
                                priority = priority
                            )
                        )
                    else:
                        tet_module.run_method(
                            method_name = 'put',
                            target = '%s/%s/catch_all' % (TETRATION_API_APPLICATIONS, existing_app['id']),
                            req_payload = dict(policy_action = policy_action, version = version)
                        )
                else:
                    result['object'] = new_object
        else:
            if not module.check_mode:
                if rank != 'CATCHALL':
                    policy_object = tet_module.run_method(
                        method_name = 'post',
                        target = '%s/%s/%s' % (TETRATION_API_APPLICATIONS, existing_app['id'], 'absolute_policies' if rank == 'ABSOLUTE' else 'default_policies'),
                        req_payload = dict(
                            consumer_filter_id = consumer_filter_id,
                            provider_filter_id = provider_filter_id,
                            version = version,
                            rank = rank,
                            policy_action = policy_action,
                            priority = priority
                        )
                    )
                    existing_policy = dict(id=policy_object['id'])
                else:
                    policy_object = tet_module.run_method(
                        method_name = 'post',
                        target = '%s/%s/%s' % (TETRATION_API_APPLICATIONS, existing_app['id'], 'absolute_policies' if rank == 'ABSOLUTE' else 'default_policies'),
                        req_payload = new_object
                    )
                    existing_policy = dict(id=policy_object['id'])
            result['changed'] = True

        # if the object does exist, check to see if any part of it should be
        # changed
        if result['changed']:
            if not module.check_mode:
                result['object'] = tet_module.run_method(
                    method_name = 'get',
                    target = '%s/%s' % (TETRATION_API_APPLICATION_POLICIES, existing_policy['id'])
                )
            else:
                result['object'] = new_object
        else:
            result['changed'] = False
            result['object'] = existing_policy

    # ---------------------------------
    # STATE == 'absent'
    # ---------------------------------

    elif state == 'absent':
        if existing_policy:
            result['changed'] = True
            if not module.check_mode:
                tet_module.run_method(
                    method_name='delete',
                    target = '%s/%s' % (TETRATION_API_APPLICATION_POLICIES, existing_policy['id'])
                )

    # ---------------------------------
    # STATE == 'query'
    # ---------------------------------

    elif state == 'query':
        result['object'] = existing_policy

    # Return result
    module.exit_json(**result)

if __name__ == '__main__':
    main()
