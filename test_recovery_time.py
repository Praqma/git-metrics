from recovery_time import find_outages, split_sequence, Deployment, find_is_patch

deployment_zero = Deployment(False, 0)
deployment_two = Deployment(False, 2)
patch_one = Deployment(True, 1)
patch_three = Deployment(True, 3)
patch_four = Deployment(True, 4)


def test_empty_tags_gives_empty_recoveries():
    results = find_outages([])
    assert results == []


def test_one_simple_outage():
    results = find_outages([deployment_zero, patch_one])
    assert results == [(deployment_zero, patch_one)]


def test_one_outage_two_patches():
    patch_two = Deployment(True, 2)
    results = find_outages([deployment_zero, patch_one, patch_two])
    assert results == [(deployment_zero, patch_two)]


def test_split_sequence():
    results = split_sequence([deployment_zero, patch_one, deployment_two, patch_three, patch_four])
    assert list(results) == [[patch_one], [patch_three, patch_four]]


def test_split_sequence_muliple_successed():
    deployment_five = Deployment(False, 5)
    patch_six = Deployment(True, 6)
    results = split_sequence([deployment_zero, patch_one, deployment_two, deployment_five, patch_six])
    assert list(results) == [[patch_one], [patch_six]]


def test_split_sequence_start_with_patch():
    deployment_five = Deployment(False, 5)
    results = split_sequence([patch_one, deployment_two, deployment_five])
    assert list(results) == [[patch_one]]


def test_two_outage_two_patches():
    results = find_outages([deployment_zero, patch_one, deployment_two, patch_three])
    assert results == [(deployment_zero, patch_one), (deployment_two, patch_three)]


def test_begin_with_patch():
    results = find_outages([patch_one, deployment_two, patch_three])
    assert results == [(deployment_two, patch_three)]


def test_find_is_patch():
    deployment_name = "D-0.0.0"
    deploy_list = dict([('D-0.0.0', 1548321420), ('D-0.0.1', 1548321600), ('D-0.0.2', 1548321720)])
    patch_list = [('P-0.0.2', 1548321720)]
    result = find_is_patch(deployment_name, deploy_list, patch_list)
    assert not result

def test_find_is_patch_when_it_is_a_patch():
    deployment_name = "D-0.0.2"
    deploy_list = dict([('D-0.0.0', 1548321420), ('D-0.0.1', 1548321600), ('D-0.0.2', 1548321720)])
    patch_list = [('P-0.0.2', 1548321720)]
    result = find_is_patch(deployment_name, deploy_list, patch_list)
    assert result