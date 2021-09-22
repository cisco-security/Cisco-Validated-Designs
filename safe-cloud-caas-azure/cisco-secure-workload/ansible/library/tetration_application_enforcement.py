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
description: Enabled or disables application policy enforcement on a specified application
  workspace
extends_documentation_fragment: tetration
module: tetration_application_enforcement
notes:
- Requires the tetpyclient Python module.
- Supports check mode.
options:
  application_id:
    description: Application ID of application workspace targeted for enforcement
      state change.  Typically queried using tetration_application module
    required: true
    type: string
  state:
    choices: '[enabled, disabled]'
    description: Enable or Disable application policy enforcement
    required: true
    type: string
  version:
    default: None
    description: Optional version number of application policy
    type: string
requirements: tetpyclient
version_added: '2.8'
'''

EXAMPLES = r'''
# Enable application policy enforcement
tetration_application_enforcement:
    application_id: 5c93da83497d4f33d7145960
    state: enabled
    provider:
      host: "tetration-cluster@company.com"
      api_key: 1234567890QWERTY
      api_secret: 1234567890QWERTY

# Enable application policy enforcement with specific version
tetration_application_enforcement:
    application_id: 5c93da83497d4f33d7145960
    version: 7
    state: enabled
    provider:
      host: "tetration-cluster@company.com"
      api_key: 1234567890QWERTY
      api_secret: 1234567890QWERTY

# Disable application policy enforcement
tetration_application_enforcement:
    application_id: 5c93da83497d4f33d7145960
    state: disabled
    provider:
      host: "tetration-cluster@company.com"
      api_key: 1234567890QWERTY
      api_secret: 1234567890QWERTY
'''

RETURN = r'''
---
object:
  contains:
    alternate_query_mode:
      description: Indicates if dynamic mode is used for the application
      returned: always
      sample: 'false'
      type: bool
    app_scope_id:
      description: Unique identifier of app scope associated with application workspace
      returned: always
      sample: 596d5215497d4f3eaef1fd04
      type: int
    author:
      description: Author of application workspace
      returned: always
      sample: Brandon Beck
      type: string
    created_at:
      description: Date this application was created (Unix Epoch)
      returned: always
      sample: 1500402190
      type: string
    description:
      description: A description for the application
      returned: always
      sample: Security policies for my application
      type: string
    enforced_version:
      description: The policy version to enforce
      returned: always
      sample: 7
      type: int
    enforcement_enabled:
      description: Sets whether enforcement is enabled on this application
      returned: always
      sample: 'true'
      type: bool
    id:
      description: Unique identifier for the application workspace
      returned: always
      sample: 5c93da83497d4f33d7145960
      type: int
    latest_adm_version:
      description: Latest policy version
      returned: always
      sample: 8
      type: int
    name:
      description: Name of application workspace
      returned: always
      sample: My Application Policy
      type: string
    primary:
      description: Sets whether this application should be primary for the given scope
      returned: always
      sample: 'true'
      type: bool
  description: the changed or modified object
  returned: always
  type: complex
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.tetration.api import TetrationApiModule
from ansible.module_utils.tetration.api import TETRATION_API_APPLICATIONS

from ansible.utils.display import Display
display = Display()

from time import sleep

def main():
    tetration_spec=dict(
        application_id=dict(type='str', required=True),
        version=dict(type='str', required=False, default=None),
    )

    argument_spec = dict(
        provider=dict(required=True),
        state=dict(required=True, choices=['enabled', 'disabled'])
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

    application_id = module.params['application_id']
    version = module.params['version']
    state = module.params['state']
    check_mode = module.check_mode

    # =========================================================================
    # Get current state of the object

    existing_app = tet_module.run_method(
        method_name = 'get',
        target = '%s/%s' % (TETRATION_API_APPLICATIONS, application_id)
    )

    if not existing_app:
        module.fail_json(msg='Unable to find application with id: %s' % application_id)


    # ---------------------------------
    # STATE == 'enabled'
    # ---------------------------------
    if state == 'enabled':
        result['changed'] = not existing_app['enforcement_enabled'] or (version and existing_app['enforced_version'] != version)
        if result['changed']:
            if not check_mode:
                new_object = dict(application_id = application_id)
                if version:
                    new_object['version'] = version
                tet_module.run_method(
                    method_name = 'post',
                    target = '%s/%s/enable_enforce' % (TETRATION_API_APPLICATIONS, application_id),
                    req_payload = new_object
                )
            existing_app['enforced_version'] = version if version else "latest"

        existing_app['enforcement_enabled'] = True
        result['object'] = existing_app

    # ---------------------------------
    # STATE == 'disabled'
    # ---------------------------------
    elif state == 'disabled':
        result['changed'] = existing_app['enforcement_enabled']
        if result['changed']:
            if not check_mode:
                tet_module.run_method(
                    method_name = 'post',
                    target = '%s/%s/disable_enforce' % (TETRATION_API_APPLICATIONS, application_id)
                )
        existing_app['enforcement_enabled'] = False
        result['object'] = existing_app

    # Return result
    module.exit_json(**result)

if __name__ == '__main__':
    main()
