from dataclasses import dataclass


def find_outages(deployments):
    results = []

    for patch_split in split_sequence(deployments):
        first_patch = patch_split[0]

        deployment_index = deployments.index(first_patch) - 1
        if deployment_index >= 0:
            failed_deployment = deployments[deployment_index]
            last_patch = patch_split[-1]
            results.append((failed_deployment, last_patch))

    return results


def split_sequence(deployments):
    split = []
    for deployment in deployments:
        if deployment.is_patch:
            split.append(deployment)
        else:
            if split:
                yield split
            split = []

    if split:
        yield split


def find_is_patch(deployment_name, deploy_tags, patch_tags):
    deploy = list(filter(
        lambda d: d[0] == deployment_name, deploy_tags))
    if not deploy:
        raise ValueError(f"Deployment {deployment_name} not found in list {list(deploy_tags)}")
    deploy_commit_time = deploy[0][1]
    return bool(list(filter(
        lambda p: p[1] == deploy_commit_time, patch_tags)))


@dataclass
class Deployment:
    is_patch: bool
    time: int