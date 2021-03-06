""" Test Data """


class TestData:
    """ Test Data """

    JOB_TEMPLATE_ID_1 = 909
    JOB_TEMPLATE_ID_2 = 910
    JOB_TEMPLATE_ID_3 = 987
    ARTIFACTS_KEY_PREFIX = "expose_to_cloud_redhat_com_"

    JOB_TEMPLATES_LIST_URL = "https://www.example.com/api/v2/job_templates?page_size=1"
    JOB_TEMPLATES_LIST_URL_PAGE_2 = (
        "https://www.example.com/api/v2/job_templates?page=2&page_size=1"
    )
    RECEPTOR_CONFIG = dict(
        username="fred",
        password="radia",
        url="https://www.example.com",
        validate_cert="0",
        verify_ssl="False",
    )
    RECEPTOR_CONFIG_WITH_TOKEN = dict(
        token="cafebeef",
        url="https://www.example.com",
        validate_cert="0",
        verify_ssl="False",
    )
    RECEPTOR_CONFIG_INVALID = dict(
        url="https://www.example.com", validate_cert="0", verify_ssl="False",
    )
    JOB_TEMPLATE_PAYLOAD_SINGLE_PAGE_GZIPPED = dict(
        href_slug="api/v2/job_templates",
        method="get",
        fetch_all_pages="False",
        accept_encoding="gzip",
        params=dict(page_size=1),
    )
    JOB_TEMPLATE_PAYLOAD_FILTERED_SINGLE_PAGE_GZIPPED = dict(
        href_slug="api/v2/job_templates",
        method="get",
        fetch_all_pages="False",
        accept_encoding="gzip",
        apply_filter=dict(results="results[].{id: id, name:name}"),
        params=dict(page_size=1),
    )
    JOB_TEMPLATE_PAYLOAD_SINGLE_PAGE = dict(
        href_slug="api/v2/job_templates",
        method="get",
        fetch_all_pages="False",
        params=dict(page_size=1),
    )
    JOB_TEMPLATE_PAYLOAD_ALL_PAGES = dict(
        href_slug="api/v2/job_templates",
        method="get",
        fetch_all_pages="True",
        params=dict(page_size=1),
    )
    JOB_TEMPLATE_COUNT = 3
    JOB_TEMPLATE_1 = dict(
        id=JOB_TEMPLATE_ID_1, type="job_template", name="Fred Flintstone"
    )
    JOB_TEMPLATE_2 = dict(
        id=JOB_TEMPLATE_ID_2, type="job_template", name="Pebbles Flintstone"
    )
    JOB_TEMPLATE_3 = dict(
        id=JOB_TEMPLATE_ID_3, type="job_template", name="Wilma Flintstone"
    )

    JOB_TEMPLATE_RESPONSE = dict(
        count=JOB_TEMPLATE_COUNT,
        next=None,
        previous=None,
        results=[JOB_TEMPLATE_1, JOB_TEMPLATE_2],
    )

    JOB_TEMPLATES_PAGE1_RESPONSE = dict(
        count=JOB_TEMPLATE_COUNT,
        next="/api/v2/job_templates/?page=2",
        previous=None,
        results=[JOB_TEMPLATE_1, JOB_TEMPLATE_2],
    )
    JOB_TEMPLATES_PAGE2_RESPONSE = dict(
        count=JOB_TEMPLATE_COUNT, next=None, previous=None, results=[JOB_TEMPLATE_3],
    )

    JOB_TEMPLATE_POST_URL = "https://www.example.com/api/v2/job_templates/909/launch"
    JOB_TEMPLATE_POST_PAYLOAD = dict(
        href_slug="api/v2/job_templates/909/launch",
        method="post",
        params=dict(name="Fred"),
    )
    JOB_TEMPLATE_POST_PAYLOAD_GZIPPED = dict(
        href_slug="api/v2/job_templates/909/launch",
        method="post",
        params=dict(name="Fred"),
        accept_encoding="gzip",
    )
    JOB_TEMPLATE_POST_FILTERED_PAYLOAD_GZIPPED = dict(
        href_slug="api/v2/job_templates/909/launch",
        method="post",
        params=dict(name="Fred"),
        accept_encoding="gzip",
        apply_filter="{url:url}",
    )

    JOB_TEMPLATE_POST_BAD_FILTERED_PAYLOAD_GZIPPED = dict(
        href_slug="api/v2/job_templates/909/launch",
        method="post",
        params=dict(name="Fred"),
        accept_encoding="gzip",
        apply_filter="[]jaj0[1]",
    )
    JOB_ID_1 = 500
    JOB_STATUS_RUNNING = "running"
    JOB_STATUS_FAILED = "failed"
    JOB_STATUS_SUCCESSFUL = "successful"
    JOB_ARTIFACTS = {
        f"{ARTIFACTS_KEY_PREFIX}_snow_ticket": 12345,
        "fred": 45,
        "barney": 90,
    }
    JOB_ARTIFACTS_HUGE = {f"{ARTIFACTS_KEY_PREFIX}_snow_details": "f" * 1096}
    JOB_TEMPLATE_POST_RESPONSE = dict(
        job=JOB_ID_1,
        url="/job/1",
        playbook="hello_world.yml",
        status=JOB_STATUS_SUCCESSFUL,
        artifacts=JOB_ARTIFACTS,
    )
    FILTERED_JOB_ARTIFACTS = {f"{ARTIFACTS_KEY_PREFIX}_snow_ticket": 12345}
    JOB_1 = dict(
        job=JOB_ID_1,
        url="/job/1",
        playbook="hello_world.yml",
        status=JOB_STATUS_SUCCESSFUL,
        artifacts=FILTERED_JOB_ARTIFACTS,
    )
    JOB_1_RUNNING = dict(
        job=JOB_ID_1,
        url="/job/1",
        playbook="hello_world.yml",
        status=JOB_STATUS_RUNNING,
    )
    JOB_1_SUCCESSFUL = dict(
        job=JOB_ID_1,
        url="/job/1",
        playbook="hello_world.yml",
        status=JOB_STATUS_SUCCESSFUL,
        artifacts=JOB_ARTIFACTS,
    )
    JOB_1_SUCCESSFUL_HUGE = dict(
        job=JOB_ID_1,
        url="/job/1",
        playbook="hello_world.yml",
        status=JOB_STATUS_SUCCESSFUL,
        artifacts=JOB_ARTIFACTS_HUGE,
    )
    JOB_MONITOR_URL = f"https://www.example.com/api/v2/jobs/{JOB_ID_1}"
    JOB_MONITOR_GZIP_PAYLOAD = dict(
        href_slug=f"/api/v2/jobs/{JOB_ID_1}",
        method="monitor",
        accept_encoding="gzip",
        params={},
        refresh_interval_seconds=1,
        apply_filter="{url:url, id:id, status:status, playbook:playbook, artifacts:artifacts}",
    )
    JOB_MONITOR_PAYLOAD = dict(
        href_slug=f"/api/v2/jobs/{JOB_ID_1}",
        method="monitor",
        params={},
        refresh_interval_seconds=1,
        apply_filter="{url:url, id:id, status:status, playbook:playbook, artifacts:artifacts}",
    )
