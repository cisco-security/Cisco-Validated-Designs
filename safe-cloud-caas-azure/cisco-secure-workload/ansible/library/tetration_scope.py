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
description: Enables creation, modification, deletion and query of a scope
extends_documentation_fragment: tetration
module: tetration_scope
notes:
- Requires the tetpyclient Python module.
- Supports check mode.
options:
  description:
    description: User specified description of the scope
    type: string
  parent_app_id:
    description:
    - ID of the parent scope
    - Require one of [C(scope_id), C(scope_name), C(parent_app_scope_id)]
    - Mutually exclusive to C(scope_id) and C(scope_name)]
    type: string
  policy_priority:
    description: Used to sort application priorities
    type: int
  query_type:
    choices: '[single, tenant, sub-scope]'
    default: single
    description: Options for expanding query search
    type: string
  scope_id:
    description:
    - Unique identifier for the scope
    - Require one of [C(scope_id), C(scope_name), C(parent_app_scope_id)]
    - Mutually exclusive to C(scope_name) and C(parent_app_scope_id)]
    type: string
  scope_name:
    description:
    - Fully qualified name of the scope. This is a fully qualified name, i.e. it has
      name of parent scopes (if applicable) all the way to the root scope
    - Require one of [C(scope_id), C(scope_name), C(parent_app_scope_id)]
    - Mutually exclusive to C(scope_id) and C(parent_app_scope_id)]
    type: string
  short_name:
    description: User specified name of the scope
    type: string
  short_query:
    description: Filter (or match criteria) associated with the scope
    type: dict
  state:
    choices: '[present, absent, query]'
    default: present
    description: Add, change, remove or query for scopes
    required: true
    type: string
requirements: tetpyclient
version_added: '2.8'
'''

EXAMPLES = r'''
# Add or Modify scope
tetration_scope:
    scope_name: ACME:Example:Application
    description: Scope for ACME example application
    short_query:
        type: subnet
        field: ip
        value: 172.16.0.0/12
    state: present
    provider:
      host: "tetration-cluster@company.com"
      api_key: 1234567890QWERTY
      api_secret: 1234567890QWERTY

# Delete scope
tetration_scope:
    scope_name: ACME:Example:Application
    state: absent
    provider:
      host: "tetration-cluster@company.com"
      api_key: 1234567890QWERTY
      api_secret: 1234567890QWERTY

# Query scope
tetration_scope:
    scope_name: ACME:Example:Application
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
    child_app_scope_ids:
      description: "An array of child scope ids"
      returned: when C(state) is present or query
      sample: '[]'
      type: list
    description:
      description: User specified description of the scope
      returned: when C(state) is present or query
      sample: Scope for ACME example application
      type: string
    dirty:
      description: Indicates a child or parent query has been updated and that the
        changes need to be committed
      returned: when C(state) is present or query
      sample: 'false'
      type: bool
    dirty_short_query:
      description: Non-null if the query for this scope has been updated but not yet
        committed
      returned: when C(state) is present or query
      sample: 'null'
      type: dict
    filter_type:
      description: The type of filter (should always be AppScope)
      returned: when C(state) is present or query
      sample: AppScope
      type: string
    id:
      description: Unique identifier for the scope
      returned: when C(state) is present or query
      sample: 5c93da83497d4f33d7145960
      type: int
    name:
      description: Fully qualified name of the scope. This is a fully qualified name,
        i.e. it has name of parent scopes (if applicable) all the way to the root
        scope
      returned: when C(state) is present or query
      sample: ACME:Example:Application
      type: string
    parent_app_scope_id:
      description: ID of the parent scope
      returned: when C(state) is present or query
      sample: 596d5215497d4f3eaef1fd04
      type: string
    policy_priority:
      description: Used to sort application priorities
      returned: when C(state) is present or query
      sample: 2
      type: int
    query:
      description: Filter (or match criteria) associated with the scope in conjunction
        with the filters of the parent scopes (all the way to the root scope)
      returned: when C(state) is present or query
      sample: JSON Filter (full)
      type: dict
    root_app_scope_id:
      description: ID of the root scope this scope belongs to
      returned: when C(state) is present or query
      sample: 596d3d2f497d4f35380b68ef
      type: string
    short_name:
      description: User specified name of the scope
      returned: when C(state) is present or query
      sample: Application
      type: string
    short_query:
      description: Filter (or match criteria) associated with the scope
      returned: when C(state) is present or query
      sample: JSON Filter (short)
      type: dict
    updated_at:
      description: Date this scope was last updated (Unix Epoch)
      returned: when C(state) is present or query
      sample: 1500402190
      type: int
    vrf_id:
      description: ID of the VRF to which scope belongs to
      returned: when C(state) is present or query
      sample: 1
      type: int
  description: the changed or modified object(s)
  returned: always
  type: complex
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.six import iteritems, iterkeys
from ansible.module_utils.tetration.api import TetrationApiModule
from ansible.module_utils.tetration.api import TETRATION_API_SCOPES

def main():
    ''' Main entry point for module execution
    '''
    #
    # Module specific spec
    tetration_spec = dict(
        scope_id=dict(type='str', required=False),
        scope_name=dict(type='str', required=False),
        parent_app_scope_id=dict(type='str', required=False),
        short_name=dict(type='str', required=False),
        description=dict(type='str', required=False),
        short_query=dict(type='dict', required=False),
        policy_priority=dict(type='int', required=False),
        query_type=dict(type='str', required=False, choices=['single', 'tenant', 'sub-scope'], default='single'),
        query=dict(type='dict', required=False),
    )
    # Common spec for tetration modules
    argument_spec = dict(
        provider=dict(required=True),
        state=dict(default='present', choices=['present', 'absent', 'query'], )
    )

    # Combine specs and include provider parameter
    argument_spec.update(tetration_spec)
    argument_spec.update(TetrationApiModule.provider_spec)

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_one_of=[
            ['parent_app_scope_id', 'scope_name', 'scope_id']
        ],
        mutually_exclusive=[
            ['parent_app_scope_id', 'scope_name', 'scope_id']
        ]
    )
    # These are all elements we put in our return JSON object for clarity
    tet_module = TetrationApiModule(module)
    result = dict(
        changed=False,
        object=None,
    )

    state = module.params['state']
    check_mode = module.check_mode
    scope_id = module.params['scope_id']
    scope_name = module.params['scope_name']
    parent_app_scope_id = module.params['parent_app_scope_id']
    short_name = module.params['short_name']
    description = module.params['description']
    short_query = module.params['short_query']
    policy_priority = module.params['policy_priority']
    query_type = module.params['query_type']
    query = module.params['query']
    parent_scope = None
    existing_scope = None

    # =========================================================================
    # Get current state of the object
    app_scopes = tet_module.run_method(
        method_name = 'get',
        target = TETRATION_API_SCOPES
    )
    if scope_id:
        existing_scope = tet_module.get_object(search_array=app_scopes, filter=dict(id=scope_id))
    elif scope_name:
        existing_scope = tet_module.get_object(search_array=app_scopes, filter=dict(name=scope_name))
        if existing_scope:
            short_name = existing_scope['short_name']
    else:
        existing_scope = tet_module.get_object(search_array=app_scopes, filter=dict(
            parent_app_scope_id=parent_app_scope_id,
            short_name=short_name
        ))
    if not existing_scope:
        if parent_app_scope_id:
            parent_scope = tet_module.get_object(search_array=app_scopes, filter=dict(id=parent_app_scope_id))
        else:
            parent_scope_name = ':'.join(scope_name.split(':')[:-1])
            parent_scope = tet_module.get_object(search_array=app_scopes, filter=dict(name=parent_scope_name))
            parent_app_scope_id = parent_scope['id']
        if scope_name and not short_name:
            short_name = scope_name.split(':')[-1]
    else:
        if (existing_scope['parent_app_scope_id']):
            parent_scope = tet_module.get_object(search_array=app_scopes, filter=dict(id=existing_scope['parent_app_scope_id']))
            parent_app_scope_id = parent_scope['id']
        else:
            parent_app_scope_id = existing_scope['id']
    if not parent_scope and existing_scope['id'] != existing_scope['root_app_scope_id']:
        if parent_app_scope_id:
            module.fail_json(msg='Unable to find parent scope for id: %s' % parent_app_scope_id)
        else:
            parent_scope_name = ':'.join(scope_name.split(':')[:-1])
            module.fail_json(msg='Unable to find parent scope with name: %s' % parent_scope_name)

    # ---------------------------------
    # STATE == 'present'
    # ---------------------------------
    if state == 'present':
        if existing_scope:
            new_object = dict()
            for (k,v) in existing_scope.iteritems():
                if module.params.get(k) and v != module.params.get(k):
                    new_object[k] = module.params.get(k)
                else:
                    new_object[k] = v
        else:
            new_object = dict(
                short_name = short_name,
                description = description,
                short_query = short_query,
                query = query,
                parent_app_scope_id = parent_app_scope_id,
                policy_priority = policy_priority
            )
        if not existing_scope:
            if not check_mode:
                result['object'] = tet_module.run_method(
                    method_name = 'post',
                    target = TETRATION_API_SCOPES,
                    req_payload = new_object
                )
            else:
                result['object'] = new_object
            result['changed'] = True
        else:
            del new_object['parent_app_scope_id']
            del new_object['policy_priority']
            result['changed'] = tet_module.filter_object(new_object, existing_scope, check_only=True)
            if result['changed']:
                if not check_mode:
                    tet_module.run_method(
                        method_name = 'put',
                        target = '%s/%s' % (TETRATION_API_SCOPES, existing_scope['id']),
                        req_payload = new_object
                    )
                else:
                    result['object'] = new_object
        if existing_scope and result['changed'] and not check_mode:
            result['object'] = tet_module.run_method(
                method_name = 'get',
                target = '%s/%s' % (TETRATION_API_SCOPES, existing_scope['id'])
            )
        elif result['changed'] and not check_mode:
            if not scope_name:
                scope_name = '%s:%s' % (parent_scope['name'], short_name)
            existing_app_scope = tet_module.get_object(
                target = TETRATION_API_SCOPES,
                filter = dict(name=scope_name)
            )
        else:
            result['object'] = existing_scope

    # ---------------------------------
    # STATE == 'absent'
    # ---------------------------------
    elif state == 'absent':
        if existing_scope:
            if not check_mode:
                tet_module.run_method(
                    method_name = 'delete',
                    target = '%s/%s' % (TETRATION_API_SCOPES, existing_scope['id'])
                )
            result['changed'] = True
    # ---------------------------------
    # STATE == 'query'
    # ---------------------------------
    else:
        if existing_scope:
            if query_type == 'tenant':
                if existing_scope['id'] == existing_scope['root_app_scope_id']:
                    tenant_scopes = tet_module.get_object(
                        search_array = app_scopes,
                        filter = dict(root_app_scope_id=existing_scope['id']),
                        allow_multiple = True
                    )
                    tenant_scopes.sort( key=lambda x: len(str(x['name']).split(':')) )
                    result['object'] = tenant_scopes
                else:
                    module.fail_json(msg='Scope name: %s is not a root scope' % existing_scope['short_name'])
            elif query_type == 'sub-scope':
                tenant_scopes = tet_module.get_object(
                    search_array = app_scopes,
                    filter = dict(root_app_scope_id=existing_scope['root_app_scope_id']),
                    allow_multiple = True
                )
                target_scopes = [ s for s in tenant_scopes if s['name'].startswith(existing_scope['name']) ]
                target_scopes.sort( key=lambda x: len(str(x['name']).split(':')) )
                result['object'] = target_scopes
            else:
                result['object'] = existing_scope
        else:
            module.fail_json(msg='Specified scope could not be found')
    module.exit_json(**result)


if __name__ == '__main__':
    main()
