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
- Enables management of Cisco Tetration through direct access to the Cisco Tetration
  REST API.
- The Cisco Tetration API is not idempotent, so this module is not idempotent.
- Familiarity with the Cisco Tetration API is required to use this module. Documentation
  for the API is available at the Cisco Tetration web UI.
module: tetration_rest
notes:
- This module is not idempotent.
- Requires the tetpyclient Python module.
- Does not support check mode.
options:
  api_key:
    description: key from downloaded API credentials
    required: true
    type: dict
  api_secret:
    description: secret from downloaded API credentials
    required: true
    type: string
  host:
    description: URL for the Tetration GUI
    required: true
    type: string
  method:
    choices: '[delete, get, post, put]'
    description: REST method
    required: true
    type: string
  name:
    description: API endpoint such as 'roles' or 'users'
    required: true
    type: string
  params:
    description: parameters to be used in the event of a GET
    type: dict
  payload:
    description: payload in the event of a PUT or POST
    type: dict
requirements: tetpyclient
short_description: Direct access to the Tetration API (non-idempotent)
version_added: '2.8'
'''

EXAMPLES = r'''
# Query existing users.
- tetration_rest:
    api_key: "{{ api_key }}"
    api_secret: "{{ api_secret }}"
    host: "{{ tetration_host }}"
    name: users
    method: get
    params:
      include_disabled: true

# Create an inventory filter. Running this more than once will return a
# status code of 422 because the filter cannot be created twice.
- tetration_rest:
    api_key: "{{ api_key }}"
    api_secret: "{{ api_secret }}"
    host: "{{ tetration_host }}"
    name: filters/inventories
    method: post
    payload:
      name: my new filter
      query:
        type: eq
        field: ip
        value: 172.16.200.100
      app_scope_id: 5bb7bc01497d4f228d6b8123

# Update the description for an existing role. Running this more than once
# will succeed but will also report changed=true even though changes have
# not been made.
- tetration_rest:
    api_key: "{{ api_key }}"
    api_secret: "{{ api_secret }}"
    host: "{{ tetration_host }}"
    name: roles/5bbe916e497d4f0af77ca6c8
    method: put
    payload:
      description: updated role description

# Delete one software agent.
- tetration_rest:
    api_key: "{{ api_key }}"
    api_secret: "{{ api_secret }}"
    host: "{{ tetration_host }}"
    name: sensors/3e2bbb8066908f83b61eb000044e8abb5f3e79bf
    method: delete
'''

RETURN = r'''
---
object:
  contains:
    json:
      description: JSON response document from REST method
      returned: success
      type: dict
    ok:
      description: Indicates if operation was successful
      returned: always
      sample: 'True'
      type: bool
    reason:
      description: Text explanation of the status code
      returned: always
      sample: Not Found
      type: string
    status_code:
      description: HTTP status code for REST method
      returned: always
      sample: '200.0'
      type: int
    text:
      description: Text returned from REST method
      returned: failed
      type: string
'''

from ansible.module_utils.basic import AnsibleModule


def main():
    module = AnsibleModule(
        argument_spec=dict(
            api_key=dict(type='str', required=True),
            api_secret=dict(type='str', required=True),
            host=dict(type='str', required=True),
            api_version=dict(type='str', default='v1'),
            name=dict(type='str', required=True),
            method=dict(type='str', required=True, choices=['delete', 'get', 'post', 'put']),
            payload=dict(type='dict', required=False),
            params=dict(type='dict', required=False),
        ),
        # we can't predict if the proposed API call will make a change to the system
        supports_check_mode=False
    )

    # if tetpyclient is not available, our only option is to fail
    try:
        import json
        import tetpyclient
        from tetpyclient import RestClient
    except ImportError:
        module.fail_json(msg="Some module dependencies are missing.")

    method = module.params['method']
    api_name = '/openapi/' + module.params['api_version'] + '/' + module.params['name']
    req_payload = module.params['payload']

    restclient = RestClient(
        module.params['host'],
        api_key=module.params['api_key'],
        api_secret=module.params['api_secret'],
        verify=False
    )

    # Do our best to provide "changed" status accurately, but it's not possible
    # as different Tetration APIs react differently to operations like creating
    # an element that already exists.
    changed = False
    if method == 'get':
        response = restclient.get(api_name, params=module.params['params'])
    elif method == 'delete':
        response = restclient.delete(api_name)
        changed = True if response.status_code / 100 == 2 else False
    elif method == 'post':
        response = restclient.post(api_name, json_body=json.dumps(req_payload))
        changed = True if response.status_code / 100 == 2 else False
    elif method == 'put':
        response = restclient.put(api_name, json_body=json.dumps(req_payload))
        changed = True if response.status_code / 100 == 2 else False


    # Put status_code in the return JSON. If the status_code is not 200, we
    # add the text that came from the REST call and the payload to make
    # debugging easier.
    result = {}
    result['status_code'] = response.status_code
    result['ok'] = response.ok
    result['reason'] = response.reason
    if int(response.status_code) / 100 == 2:
        result['json'] = response.json()
    else:
        result['text'] = response.text

    module.exit_json(changed=changed, **result)


if __name__ == '__main__':
    main()
