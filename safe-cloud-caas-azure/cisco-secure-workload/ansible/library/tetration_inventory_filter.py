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
author: Doron Chosnek (@dchosnek)
description:
- Enables management of Cisco Teetration inventory filters.
- Enables creation, modification, and deletion of filters.
- Enables management of complex filters with boolean operators on many different objects.
extends_documentation_fragment: tetration
module: tetration_inventory_filter
options:
  app_scope_id:
    description: Scope ID and scope name are mutually exclusive.
    type: string
  app_scope_name:
    description: Scope ID and scope name are mutually exclusive.
    type: string
  name:
    description: Name of the inventory filter
    required: true
    type: string
  primary:
    default: 'false'
    description: When true it means inventory filter is restricted to ownership scope.
    type: bool
  public:
    default: 'false'
    description: When true the filter represents a service to be matched by other
      applications during application discovery runs (ADM).
    type: bool
  query:
    description: Filter (or match criteria) associated with the scope
    type: dict
  state:
    choices: '[present, absent, query]'
    description: Add, change, or remove the inventory filter
    required: true
    type: string
version_added: '2.8'
'''

EXAMPLES = r'''
# Create a filter based on hostname
- tetration_inventory_filter:
    provider: "{{ my_tetration }}"
    name: hostname contains dns
    app_scope_name: Default
    state: present
    query:
    field: host_name
    type: contains
    value: dns

# Create a filter for a specific IP subnet
- tetration_inventory_filter:
    provider: "{{ my_tetration }}"
    name: vpn users subnet
    app_scope_name: Default
    state: present
    query:
    field: ip
    type: subnet
    value: 192.168.100.0/24

# Create filter for a user annotation field named Owner. When using a user
# annotation, the field value must always start with user_ and end with the
# name of the user annotation. user_Owner represents the user annotation
# named Owner.
- tetration_inventory_filter:
    provider: "{{ my_tetration }}"
    name: owned by engineering
    app_scope_name: Default
    state: present
    query:
    field: user_Owner
    type: eq
    value: engineering

# Create filter for a user annotation field named Location
- tetration_inventory_filter:
    provider: "{{ my_tetration }}"
    name: location of Texas
    app_scope_name: Default
    state: present
    query:
    field: user_Location
    type: contains
    value: Texas

# Create a filter based on interface name
- tetration_inventory_filter:
    provider: "{{ my_tetration }}"
    name: interface eth0
    app_scope_name: Default
    state: present
    query:
    field: iface_name
    type: eq
    value: eth0

# Create a filter based on interface MAC address
- tetration_inventory_filter:
    provider: "{{ my_tetration }}"
    name: mac a9
    app_scope_name: Default
    state: present
    query:
    field: iface_mac
    type: contains
    value: a9

# Build a complex filter with both 'and' and 'or' statements
- tetration_inventory_filter:
    provider: "{{ my_tetration }}"
    name: vulnerable linux hosts
    app_scope_name: Default
    state: present
    public: true
    primary: true
    query:
    type: and
    filters:
    - field: os
        type: contains
        value: linux
    - type: or
        filters:
        - field: host_tags_cvss3
        type: gt
        value: 8
        - field: host_tags_cvss2
        type: gt
        value: 8

# Delete some inventory filters
- tetration_inventory_filter:
    provider: "{{ my_tetration }}"
    name: "{{ item }}"
    app_scope_name: Default
    state: absent
loop:
- my first filter
- my second filter
'''

RETURN = r'''
---
object:
  contains:
    app_scope_id:
      description: ID of the scope associated with the filter
      returned: when C(state) is present or query
      sample: 5bdf9776497d4f397d38fdcb
      type: dict
    id:
      description: Unique identifier for the inventory filter
      returned: when C(state) is present or query
      sample: 5be671e9497d4f08f028b1bb
      type: dict
    name:
      description: User specified name of the inventory filter
      returned: when C(state) is present or query
      type: string
    primary:
      description: When true it means inventory filter is restricted to ownership
        scope
      returned: when C(state) is present or query
      sample: 'false'
      type: bool
    public:
      description: When true the filter represents a service to be matched by other
        applications during application discovery runs (ADM).
      returned: when C(state) is present or query
      sample: 'false'
      type: bool
    query:
      description: Filter (or match criteria) associated with the filter in conjunction
        with the filters of the parent scopes.
      returned: when C(state) is present or query
      type: dict
    updated_at:
      description: Unix timestamp for the last update of the filter
      returned: when C(state) is present or query
      sample: 1541829226
      type: int
  description: the changed or modified object
  returned: always
  type: complex
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.tetration.api import TetrationApiModule
from ansible.module_utils.tetration.api import TETRATION_API_INVENTORY_FILTER
from ansible.module_utils.tetration.api import TETRATION_API_SCOPES

from ansible.utils.display import Display
display = Display()

def main():
    tetration_spec=dict(
        name=dict(type='str', required=False),
        query=dict(type='dict', required=False),
        app_scope_id=dict(type='str', required=False),
        app_scope_name=dict(type='str', required=False),
        primary=dict(type='bool', required=False, default=False),
        public=dict(type='bool', required=False, default=False),
        query_type=dict(type='str', required=False, choices=['single', 'sub-scope', 'all'], default='single'),
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
        required_one_of=[ ['app_scope_id', 'app_scope_name'] ],
        required_if=[
            ['state', 'present', ['name']],
            ['state', 'absent', ['name']],
            ['query_type', 'sub-scope', ['app_scope_name']]
        ]
    )

    tet_module = TetrationApiModule(module)

    # These are all elements we put in our return JSON object for clarity
    result = dict(
        failed=False,
        object=None,
    )

    state = module.params['state']
    filter_name = module.params['name']
    app_scope_id = module.params['app_scope_id']
    app_scope_name = module.params['app_scope_name']
    primary = module.params['primary']
    query_type = module.params['query_type']
    if not primary:
        public = False
        module.params['public'] = False
    else:
        public = module.params['public']

    # =========================================================================
    # Get current state of the object

    # find the ID of the scope if specified by name
    if app_scope_name is not None:
        scope = tet_module.get_object(
            target = TETRATION_API_SCOPES,
            filter = dict(name=app_scope_name),
        )
        app_scope_id = scope['id'] if scope else None

    # The first thing we have to do is get the object.
    existing_object = tet_module.get_object(
        target = TETRATION_API_INVENTORY_FILTER,
        filter = dict(name=filter_name, app_scope_id=app_scope_id)
    )
    id = None if existing_object is None else existing_object['id']


    # =========================================================================
    # Now enforce the desired state (present, absent, query)

    # at this point in the code, there will be one object stored in the
    # variable named existing_object
    changed = False

    # ---------------------------------
    # STATE == 'present'
    # ---------------------------------
    if state == 'present':

        new_object = dict(
            name=filter_name,
            app_scope_id=app_scope_id,
            primary=primary,
            public=public
        )
        if module.params['query'] is not None:
            new_object['query'] = module.params['query']

        # if the object does not exist at all, create it
        if not existing_object:
            changed = True
            if not module.check_mode:
                query_result = tet_module.run_method(
                    method_name='post',
                    target=TETRATION_API_INVENTORY_FILTER,
                    req_payload=new_object,
                )
                id = query_result['id']

        # if the object does exist, check to see if any part of it should be
        # changed
        else:
            # if primary or app_scope_id don't match, UPDATE!
            update_needed = False
            for k in ['app_scope_id', 'primary', 'public']:
                if module.params[k] is not None and existing_object[k] != module.params[k]:
                    update_needed = True
            # if query doesn't match, UPDATE!
            if module.params['query'] is not None and module.params['query'] != existing_object['short_query']:
                update_needed = True
            if update_needed:
                changed = True
                if not module.check_mode:
                    tet_module.run_method(
                        method_name='put',
                        target='%s/%s' % (TETRATION_API_INVENTORY_FILTER, id),
                        req_payload=new_object,
                    )

        # decide what value to return
        if not changed:
            result['object'] = existing_object
        elif module.check_mode:
            result['object'] = new_object
        else:
            # retrieve the current state of the object
            query_result = tet_module.run_method(
                    method_name='get',
                    target='%s/%s' % (TETRATION_API_INVENTORY_FILTER, id)
                )
            result['object'] = query_result

    # ---------------------------------
    # STATE == 'absent'
    # ---------------------------------

    elif state == 'absent':
        # if existing_object is a non-empty dictionary, that means there is
        # something to delete; if it's empty then there is nothing to do
        if bool(existing_object):
            changed = True
            if not module.check_mode:
                tet_module.run_method(
                    method_name='delete',
                    target='%s/%s' % (TETRATION_API_INVENTORY_FILTER, id)
                )
            result['object'] = existing_object

    # ---------------------------------
    # STATE == 'query'
    # ---------------------------------

    elif state == 'query':
        # we already retrieved the current state of the object, so there is no
        # need to do it again
        if query_type == 'all':
            existing_app_scope = tet_module.run_method(
                method_name = 'get',
                target = '%s/%s' % (TETRATION_API_SCOPES, app_scope_id)
            )
            if not existing_app_scope:
                module.fail_json(msg='No app_scope was found matching id: %s' % app_scope_id)
            if existing_app_scope['id'] != existing_app_scope['root_app_scope_id']:
                module.fail_json(msg='query_type `all` option is only allowed on root scopes')
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
            if inventory_filters:
                inventory_filters = [ valid_filter for valid_filter in inventory_filters if valid_filter['app_scope_id'] in scope_ids and valid_filter['name'] != 'Everything' ]
            result['object'] = inventory_filters
        elif query_type == 'sub-scope':
            app_scopes = tet_module.run_method(
                method_name = 'get',
                target = TETRATION_API_SCOPES
            )
            scope_ids = [ scope['id'] for scope in app_scopes if scope['name'].startswith(app_scope_name) ]
            inventory_filters = tet_module.run_method(
                method_name = 'get',
                target = TETRATION_API_INVENTORY_FILTER,
            )
            if inventory_filters:
                inventory_filters = [ valid_filter for valid_filter in inventory_filters if valid_filter['app_scope_id'] in scope_ids and valid_filter['name'] != 'Everything' ]
            result['object'] = inventory_filters
        else:
            result['object'] = existing_object


    module.exit_json(changed=changed, **result)

if __name__ == '__main__':
    main()
