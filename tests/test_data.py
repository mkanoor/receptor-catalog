""" Test Data """


class TestData:
    """ Test Data """

    JOB_TEMPLATE_ID_1 = 909
    JOB_TEMPLATE_ID_2 = 910
    JOB_TEMPLATE_ID_3 = 987

    JOB_TEMPLATES_LIST_URL = "https://www.example.com/api/v2/job_templates"
    JOB_TEMPLATES_LIST_URL_PAGE_2 = (
        "https://www.example.com/api/v2/job_templates?page=2"
    )
    RECEPTOR_CONFIG = dict(
        username="fred",
        password="radia",
        url="https://www.example.com",
        validate_cert="0",
        verify_ssl="False",
    )
    JOB_TEMPLATE_PAYLOAD_SINGLE_PAGE_GZIPPED = dict(
        href_slug="api/v2/job_templates",
        method="get",
        fetch_all_pages="False",
        accept_encoding="gzip",
    )
    JOB_TEMPLATE_PAYLOAD_FILTERED_SINGLE_PAGE_GZIPPED = dict(
        href_slug="api/v2/job_templates",
        method="get",
        fetch_all_pages="False",
        accept_encoding="gzip",
        apply_filter=dict(results="results[].{id: id, name:name}"),
    )
    JOB_TEMPLATE_PAYLOAD_SINGLE_PAGE = dict(
        href_slug="api/v2/job_templates", method="get", fetch_all_pages="False",
    )
    JOB_TEMPLATE_PAYLOAD_ALL_PAGES = dict(
        href_slug="api/v2/job_templates", method="get", fetch_all_pages="True",
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
    JOB_TEMPLATE_POST_RESPONSE = dict(
        job=JOB_ID_1, url="/job/1", playbook="hello_world.yml"
    )

    JOB_1 = dict(job=JOB_ID_1, url="/job/1", playbook="hello_world.yml")
