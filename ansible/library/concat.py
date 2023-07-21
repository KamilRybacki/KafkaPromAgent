from __future__ import (absolute_import, division, print_function)

import os

import ansible.module_utils.basic
import yaml

__metaclass__=type


def validate_yaml_path(path: str) -> bool:
    is_file_yaml = path.endswith('.yaml') or path.endswith('.yml')
    does_file_exist = os.path.isfile(path)
    return is_file_yaml and does_file_exist


def main() -> None:
    module_args=dict(
        yamls=dict(type='list', required=True),
        dest=dict(type='str', required=True),
    )
    module=ansible.module_utils.basic.AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )
    result=dict(
        msg='',
        stdout='',
        stdout_lines=[],
        stderr='',
        stderr_lines=[],
        rc=0,
        failed=False,
        changed=False
    )
    
    list_of_yamls = filter(
        validate_yaml_path,
        module.params.get('yamls')
    )

    loaded_yamls = []
    for file in list_of_yamls:
        with open(file, 'r', encoding='utf-8') as stream:
            try:
                loaded_yamls.append(yaml.safe_load(stream))
            except yaml.YAMLError as exc:
                result['failed'] = True
                result['msg'] = str(exc)
                result['rc'] = 1
                module.fail_json(**result)
    concatenated_dict = loaded_yamls[0]
    for yaml_dict in loaded_yamls[1:]:
        concatenated_dict.update(yaml_dict)
    
    with open(module.params.get('dest'), 'w', encoding='utf-8') as outfile:
        yaml.dump(concatenated_dict, outfile, default_flow_style=False)

    result['changed'] = True
    result['msg'] = 'Successfully concatenated yaml files'
    result['stdout'] = concatenated_dict
    result['stdout_lines'] = concatenated_dict
    
    module.exit_json(**result)

if __name__ == '__main__':
    main()
