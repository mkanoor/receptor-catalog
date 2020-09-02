""" Test Catalog Receptor Worker """
import json
import logging
import queue
import gzip
import ast
from aioresponses import aioresponses
import pytest
from receptor_catalog import worker
from test_data import TestData


logger = logging.getLogger(__name__)
receptor_logger = logging.getLogger("receptor")
receptor_logger.addHandler(logging.StreamHandler())


class FakeMessage:
    """ Class to create a Fake Message, that is sent from the receptor
        to the plugin
    """

    raw_payload = None


def run_get(config, payload, response):
    """ Run a HTTP GET Command """
    message = FakeMessage()
    message.raw_payload = payload
    response_queue = queue.Queue()
    headers = {"Content-Type": "application/json"}
    with aioresponses() as mocked:
        mocked.get(
            TestData.JOB_TEMPLATES_LIST_URL,
            status=200,
            body=json.dumps(response),
            headers=headers,
        )
        worker.execute(message, config, response_queue)

    return response_queue


def validate_get_response(response, status, count, job_templates, keys=None):
    """ Validate a GET Response, support filtering of keys """
    assert (response["status"]) == status
    json_response = json.loads(response["body"])
    assert (json_response["count"]) == count
    results = json_response["results"]
    for item in results:
        matching_item = find_by_id(item["id"], job_templates)
        if not keys:
            keys = list(matching_item.keys())
        assert sorted(keys) == sorted(list(item.keys()))
        compare(item, matching_item, keys)


def compare(this, other, keys):
    """ Compare if all the required keys are present in the response """
    for key in keys:
        assert this[key] == other[key]


def find_by_id(object_id, items):
    """ Find an object given its ID from a list of items """
    for item in items:
        if object_id == item["id"]:
            return item

    raise Exception(f"Item with {object_id} not found")


def test_execute_get_success_with_gzip():
    """ Test GZIP of Response Data """
    response_queue = run_get(
        TestData.RECEPTOR_CONFIG,
        json.dumps(TestData.JOB_TEMPLATE_PAYLOAD_SINGLE_PAGE_GZIPPED),
        TestData.JOB_TEMPLATE_RESPONSE,
    )
    result = response_queue.get()
    response = ast.literal_eval(gzip.decompress(result).decode("utf-8"))
    validate_get_response(
        response,
        200,
        TestData.JOB_TEMPLATE_COUNT,
        [TestData.JOB_TEMPLATE_1, TestData.JOB_TEMPLATE_2],
    )


def test_execute_get_success_with_gzip_and_token():
    """ Test GZIP of Response Data with auth based on token"""
    response_queue = run_get(
        TestData.RECEPTOR_CONFIG_WITH_TOKEN,
        json.dumps(TestData.JOB_TEMPLATE_PAYLOAD_SINGLE_PAGE_GZIPPED),
        TestData.JOB_TEMPLATE_RESPONSE,
    )
    result = response_queue.get()
    response = ast.literal_eval(gzip.decompress(result).decode("utf-8"))
    validate_get_response(
        response,
        200,
        TestData.JOB_TEMPLATE_COUNT,
        [TestData.JOB_TEMPLATE_1, TestData.JOB_TEMPLATE_2],
    )


def test_execute_get_success_with_filter_gzip():
    """ Test GZIP of Filtered Response Data """
    response_queue = run_get(
        TestData.RECEPTOR_CONFIG,
        json.dumps(TestData.JOB_TEMPLATE_PAYLOAD_FILTERED_SINGLE_PAGE_GZIPPED),
        TestData.JOB_TEMPLATE_RESPONSE,
    )
    result = response_queue.get()
    response = ast.literal_eval(gzip.decompress(result).decode("utf-8"))
    validate_get_response(
        response,
        200,
        TestData.JOB_TEMPLATE_COUNT,
        [TestData.JOB_TEMPLATE_1, TestData.JOB_TEMPLATE_2],
        ["id", "name"],
    )


def test_execute_get_success_with_multiple_pages():
    """ Test Multiple pages of response coming back """
    response_queue = queue.Queue()
    message = FakeMessage()
    message.raw_payload = json.dumps(TestData.JOB_TEMPLATE_PAYLOAD_ALL_PAGES)
    headers = {"Content-Type": "application/json"}

    with aioresponses() as mocked:
        mocked.get(
            TestData.JOB_TEMPLATES_LIST_URL,
            status=200,
            body=json.dumps(TestData.JOB_TEMPLATES_PAGE1_RESPONSE),
            headers=headers,
        )
        mocked.get(
            TestData.JOB_TEMPLATES_LIST_URL_PAGE_2,
            status=200,
            body=json.dumps(TestData.JOB_TEMPLATES_PAGE2_RESPONSE),
            headers=headers,
        )
        worker.execute(message, TestData.RECEPTOR_CONFIG, response_queue)

    validate_get_response(
        response_queue.get(),
        200,
        TestData.JOB_TEMPLATE_COUNT,
        [TestData.JOB_TEMPLATE_1, TestData.JOB_TEMPLATE_2],
    )
    validate_get_response(
        response_queue.get(),
        200,
        TestData.JOB_TEMPLATE_COUNT,
        [TestData.JOB_TEMPLATE_3],
    )


def test_execute_get_exception():
    """ When we get a bad data from the server, raise an exception """
    message = FakeMessage()
    message.raw_payload = json.dumps(TestData.JOB_TEMPLATE_PAYLOAD_SINGLE_PAGE_GZIPPED)
    with aioresponses() as mocked:
        mocked.get(
            TestData.JOB_TEMPLATES_LIST_URL, status=400, body="Bad Request in Get Call"
        )
        with pytest.raises(Exception) as excinfo:
            worker.execute(message, TestData.RECEPTOR_CONFIG, queue.Queue())
        assert "Bad Request in Get Call" in str(excinfo.value)


def test_execute_with_invalid_config_get_exception():
    """ When we have bad config raise an exception """
    message = FakeMessage()
    message.raw_payload = json.dumps(TestData.JOB_TEMPLATE_PAYLOAD_SINGLE_PAGE_GZIPPED)
    with aioresponses():
        with pytest.raises(Exception) as excinfo:
            worker.execute(message, TestData.RECEPTOR_CONFIG_INVALID, queue.Queue())
        assert "token or username and password" in str(excinfo.value)


def test_execute_get_success():
    """ GET Request with Single Page """
    response_queue = run_get(
        TestData.RECEPTOR_CONFIG,
        json.dumps(TestData.JOB_TEMPLATE_PAYLOAD_SINGLE_PAGE),
        TestData.JOB_TEMPLATE_RESPONSE,
    )
    response = response_queue.get()
    validate_get_response(
        response,
        200,
        TestData.JOB_TEMPLATE_COUNT,
        [TestData.JOB_TEMPLATE_1, TestData.JOB_TEMPLATE_2],
    )


def test_execute_get_with_dict_payload():
    """ GET Request with Payload as a dictionary """
    response_queue = run_get(
        TestData.RECEPTOR_CONFIG,
        TestData.JOB_TEMPLATE_PAYLOAD_SINGLE_PAGE,
        TestData.JOB_TEMPLATE_RESPONSE,
    )
    response = response_queue.get()
    validate_get_response(
        response,
        200,
        TestData.JOB_TEMPLATE_COUNT,
        [TestData.JOB_TEMPLATE_1, TestData.JOB_TEMPLATE_2],
    )


def test_execute_get_with_bad_payload():
    """ GET Request where JSON decoding fails """
    message = FakeMessage()
    message.raw_payload = "fail string"
    with pytest.raises(json.JSONDecodeError):
        worker.execute(message, TestData.RECEPTOR_CONFIG, queue.Queue())


def run_post(payload, response):
    """ Helper method to send a HTTP POST """
    message = FakeMessage()
    message.raw_payload = payload
    response_queue = queue.Queue()
    headers = {"Content-Type": "application/json"}
    with aioresponses() as mocked:
        mocked.post(
            TestData.JOB_TEMPLATE_POST_URL,
            status=200,
            body=json.dumps(response),
            headers=headers,
        )
        worker.execute(message, TestData.RECEPTOR_CONFIG, response_queue)

    return response_queue


def validate_post_response(response, status, job, keys=None):
    """ Helper Method to validate HTTP POST Response """
    assert (response["status"]) == status
    json_response = json.loads(response["body"])
    if not keys:
        keys = list(job.keys())
    assert sorted(keys) == sorted(list(json_response.keys()))
    compare(json_response, job, keys)


def test_execute_post_success():
    """ HTTP POST Test """
    response_queue = run_post(
        json.dumps(TestData.JOB_TEMPLATE_POST_PAYLOAD),
        TestData.JOB_TEMPLATE_POST_RESPONSE,
    )
    response = response_queue.get()
    validate_post_response(response, 200, TestData.JOB_1)


def test_execute_post_zip_success():
    """ HTTP POST Test with Response GZIPPed """
    response_queue = run_post(
        json.dumps(TestData.JOB_TEMPLATE_POST_PAYLOAD_GZIPPED),
        TestData.JOB_TEMPLATE_POST_RESPONSE,
    )
    result = response_queue.get()
    response = ast.literal_eval(gzip.decompress(result).decode("utf-8"))
    validate_post_response(response, 200, TestData.JOB_1)


def test_execute_post_filtered_zip_success():
    """ HTTP POST Test with Filtered Response GZIPPed """
    response_queue = run_post(
        json.dumps(TestData.JOB_TEMPLATE_POST_FILTERED_PAYLOAD_GZIPPED),
        TestData.JOB_TEMPLATE_POST_RESPONSE,
    )
    result = response_queue.get()
    response = ast.literal_eval(gzip.decompress(result).decode("utf-8"))
    validate_post_response(response, 200, TestData.JOB_1, ["url"])


def test_execute_post_exception():
    """ HTTP POST Test with Exception """
    message = FakeMessage()
    message.raw_payload = json.dumps(TestData.JOB_TEMPLATE_POST_PAYLOAD)
    with aioresponses() as mocked:
        mocked.post(
            TestData.JOB_TEMPLATE_POST_URL, status=400, body="Bad Request in Post Call"
        )
        with pytest.raises(Exception) as excinfo:
            worker.execute(message, TestData.RECEPTOR_CONFIG, queue.Queue())
        assert "Bad Request in Post Call" in str(excinfo.value)


def test_execute_post_exception_invalid_filter():
    """ HTTP POST Test with an invalid JMESPath filter """
    message = FakeMessage()
    message.raw_payload = json.dumps(
        TestData.JOB_TEMPLATE_POST_BAD_FILTERED_PAYLOAD_GZIPPED
    )
    headers = {"Content-Type": "application/json"}
    with aioresponses() as mocked:
        mocked.post(
            TestData.JOB_TEMPLATE_POST_URL,
            status=200,
            body=json.dumps(TestData.JOB_TEMPLATE_POST_RESPONSE),
            headers=headers,
        )
        with pytest.raises(Exception):
            worker.execute(message, TestData.RECEPTOR_CONFIG, queue.Queue())


def test_execute_monitor_job_success():
    """ Test to Monitor completion of job"""
    response_queue = queue.Queue()
    message = FakeMessage()
    message.raw_payload = json.dumps(TestData.JOB_MONITOR_PAYLOAD)
    headers = {"Content-Type": "application/json"}

    with aioresponses() as mocked:
        mocked.get(
            TestData.JOB_MONITOR_URL,
            status=200,
            body=json.dumps(TestData.JOB_1_RUNNING),
            headers=headers,
        )
        mocked.get(
            TestData.JOB_MONITOR_URL,
            status=200,
            body=json.dumps(TestData.JOB_1_SUCCESSFUL),
            headers=headers,
        )
        worker.execute(message, TestData.RECEPTOR_CONFIG, response_queue)

    response = response_queue.get()
    assert (response["status"]) == 200
    json_response = json.loads(response["body"])
    assert (json_response["status"]) == "successful"


def test_execute_monitor_job_zip_success():
    """ Test to Monitor completion of job"""
    response_queue = queue.Queue()
    message = FakeMessage()
    message.raw_payload = json.dumps(TestData.JOB_MONITOR_GZIP_PAYLOAD)
    headers = {"Content-Type": "application/json"}

    with aioresponses() as mocked:
        mocked.get(
            TestData.JOB_MONITOR_URL,
            status=200,
            body=json.dumps(TestData.JOB_1_RUNNING),
            headers=headers,
        )
        mocked.get(
            TestData.JOB_MONITOR_URL,
            status=200,
            body=json.dumps(TestData.JOB_1_SUCCESSFUL),
            headers=headers,
        )
        worker.execute(message, TestData.RECEPTOR_CONFIG, response_queue)

    result = response_queue.get()
    response = ast.literal_eval(gzip.decompress(result).decode("utf-8"))
    assert (response["status"]) == 200
    json_response = json.loads(response["body"])
    assert (json_response["status"]) == "successful"


def test_execute_monitor_exception():
    """ HTTP POST Test with Exception """
    message = FakeMessage()
    message.raw_payload = json.dumps(TestData.JOB_MONITOR_GZIP_PAYLOAD)
    with aioresponses() as mocked:
        mocked.get(
            TestData.JOB_MONITOR_URL, status=400, body="Bad Request in Monitor Call"
        )
        with pytest.raises(Exception) as excinfo:
            worker.execute(message, TestData.RECEPTOR_CONFIG, queue.Queue())
        assert "Bad Request in Monitor Call" in str(excinfo.value)
