#! /usr/bin/env python2

import sys
from docker import Client
from ansible.module_utils.basic import *


def main():
    fields = {
         "all_docker_images": {"required": True, "type": "list"}
         }
    module = AnsibleModule(argument_spec=fields)
    all_docker_images = module.params['all_docker_images']
    images = Client().images()
    repo_tags_list = \
        [image['RepoTags'] for image in images
            if type(image['RepoTags']) == list]
    repo_tags = \
        [item for repo_tag_list in repo_tags_list
            for item in repo_tag_list]
    for image in all_docker_images:
        if image not in repo_tags:
            module.exit_json(changed=True, load=True)
    module.exit_json(changed=True, load=False)


if __name__ == '__main__':
    main()
