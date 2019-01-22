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


def find_patch(deployment_name, patch_tags):
    return filter(
        lambda p: p.endswith(deployment_name[2:]), patch_tags)


@dataclass
class Deployment:
    is_patch: bool
    time: int