import json
import logging
import os
import pytest
import queue
from aioresponses import aioresponses
from aiohttp.http_exceptions import HttpProcessingError
from aiohttp.client_exceptions import ClientConnectionError
from receptor_catalog import worker
import gzip


logger = logging.getLogger(__name__)


class FakeMessage:
    raw_payload = None


def test_execute_get_success_with_gzip():
    q = queue.Queue()
    message = FakeMessage()
    message.raw_payload = json.dumps(
        {
            "href_slug": "api/v2/job_templates",
            "method": "get",
            "fetch_all_pages": "False",
            "accept-encoding": "gzip",
        }
    )
    headers = {"Content-Type": "application/json"}
    response = dict(
        count=28, next=None, previous=None, results=[dict(id=5, type="job_template")],
    )
    config = dict(
        username="fred",
        password="radia",
        url="https://www.example.com",
        validate_cert="0",
        verify_ssl="False",
    )
    with aioresponses() as mocked:
        mocked.get(
            "https://www.example.com/api/v2/job_templates",
            status=200,
            body=json.dumps(response),
            headers=headers,
        )
        worker.execute(message, config, q)

    result = q.get()
    response = json.loads(gzip.decompress(result).decode("utf-8"))
    assert (response["status"]) == 200
    assert (json.loads(response["body"])["count"]) == 28


def test_execute_get_success_with_multiple_pages():
    q = queue.Queue()
    message = FakeMessage()
    message.raw_payload = json.dumps(
        dict(href_slug="api/v2/job_templates", method="get", fetch_all_pages="True")
    )
    headers = {"Content-Type": "application/json"}
    response1 = dict(
        count=2,
        next="/api/v2/job_templates/?page=2",
        previous=None,
        results=[dict(id=909, type="job_template")],
    )
    response2 = dict(
        count=2, next=None, previous=None, results=[dict(id=899, type="job_template")],
    )
    config = dict(
        username="fred",
        password="radia",
        url="https://www.example.com",
        validate_cert="0",
        verify_ssl="False",
    )
    with aioresponses() as mocked:
        mocked.get(
            "https://www.example.com/api/v2/job_templates",
            status=200,
            body=json.dumps(response1),
            headers=headers,
        )
        mocked.get(
            "https://www.example.com/api/v2/job_templates?page=2",
            status=200,
            body=json.dumps(response2),
            headers=headers,
        )
        worker.execute(message, config, q)

    result = q.get()
    response = json.loads(result)
    assert (response["status"]) == 200
    assert (json.loads(response["body"])["count"]) == 2
    data = json.loads(response["body"])
    assert (data["results"][0]["id"]) == 909
    result = q.get()
    response = json.loads(result)
    assert (response["status"]) == 200
    assert (json.loads(response["body"])["count"]) == 2
    data = json.loads(response["body"])
    assert (data["results"][0]["id"]) == 899

def test_execute_get_exception():
    q = queue.Queue()
    message = FakeMessage()
    message.raw_payload = json.dumps(
        dict(href_slug="api/v2/job_templates", method="get", fetch_all_pages="False")
    )
    headers = {"Content-Type": "application/json"}
    response = dict(
        count=28, next=None, previous=None, results=[dict(id=5, type="job_template")],
    )
    config = dict(
        username="fred",
        password="radia",
        url="https://www.example.com",
        validate_cert="0",
        verify_ssl="False",
    )
    with aioresponses() as mocked:
        mocked.get(
            "https://www.example.com/api/v2/job_templates",
            exception=ClientConnectionError("Connection Refused"),
        )
    with pytest.raises(Exception):
        worker.execute(message, config, q)


def test_execute_get_success():
    q = queue.Queue()
    message = FakeMessage()
    message.raw_payload = json.dumps(
        dict(href_slug="api/v2/job_templates", method="get", fetch_all_pages="False")
    )
    headers = {"Content-Type": "application/json"}
    response = dict(
        count=28, next=None, previous=None, results=[dict(id=5, type="job_template")],
    )
    config = dict(
        username="fred",
        password="radia",
        url="https://www.example.com",
        validate_cert="0",
        verify_ssl="False",
    )
    with aioresponses() as mocked:
        mocked.get(
            "https://www.example.com/api/v2/job_templates",
            status=200,
            body=json.dumps(response),
            headers=headers,
        )
        worker.execute(message, config, q)

    result = q.get()
    response = json.loads(result)
    assert (response["status"]) == 200
    assert (json.loads(response["body"])["count"]) == 28


def test_execute_get_with_dict_payload():
    q = queue.Queue()
    message = FakeMessage()
    message.raw_payload = dict(href_slug="api/v2/job_templates", method="get")
    headers = {"Content-Type": "application/json"}
    response = dict(
        count=28,
        # "next"= "/api/v2/job_templates/?page=2",
        next=None,
        previous=None,
        results=[dict(id=5, type="job_template")],
    )
    config = dict(
        username="fred",
        password="radia",
        url="http://www.example.com",
        validate_cert="0",
    )
    with aioresponses() as mocked:
        mocked.get(
            "http://www.example.com/api/v2/job_templates",
            status=200,
            body=json.dumps(response),
            headers=headers,
        )
        worker.execute(message, config, q)

    result = q.get()
    response = json.loads(result)
    assert (response["status"]) == 200
    assert (json.loads(response["body"])["count"]) == 28


def test_execute_get_with_bad_payload():
    q = queue.Queue()
    message = FakeMessage()
    message.raw_payload = "fail string"
    config = dict(
        username="fred",
        password="radia",
        url="http://www.example.com",
        validate_cert="0",
    )
    with pytest.raises(json.JSONDecodeError):
        worker.execute(message, config, q)


def test_execute_post_success():
    q = queue.Queue()
    message = FakeMessage()
    message.raw_payload = json.dumps(
        dict(
            href_slug="api/v2/job_templates/909/launch",
            method="post",
            params=dict(name="Fred"),
        )
    )
    headers = {"Content-Type": "application/json"}
    response = dict(
        count=1, next=None, previous=None, results=[dict(id=5, type="job")],
    )
    config = dict(
        username="fred",
        password="radia",
        url="https://www.example.com",
        validate_cert="0",
        verify_ssl="False",
    )
    with aioresponses() as mocked:
        mocked.post(
            "https://www.example.com/api/v2/job_templates/909/launch",
            status=200,
            body=json.dumps(response),
            headers=headers,
        )
        worker.execute(message, config, q)

    result = q.get()
    response = json.loads(result)
    assert (response["status"]) == 200
    assert (json.loads(response["body"])["count"]) == 1

def test_execute_post_zip_success():
    q = queue.Queue()
    message = FakeMessage()
    message.raw_payload = json.dumps(
        {
            "href_slug": "api/v2/job_templates/909/launch",
            "method": "post",
            "accept-encoding": "gzip",
            "params": dict(name="Fred")
        }
    )
    headers = {"Content-Type": "application/json"}
    response = dict(
        count=1, next=None, previous=None, results=[dict(id=5, type="job")],
    )
    config = dict(
        username="fred",
        password="radia",
        url="https://www.example.com",
        validate_cert="0",
        verify_ssl="False",
    )
    with aioresponses() as mocked:
        mocked.post(
            "https://www.example.com/api/v2/job_templates/909/launch",
            status=200,
            body=json.dumps(response),
            headers=headers,
        )
        worker.execute(message, config, q)

    result = q.get()
    response = json.loads(gzip.decompress(result).decode("utf-8"))
    assert (response["status"]) == 200
    assert (json.loads(response["body"])["count"]) == 1

def test_execute_post_exception():
    q = queue.Queue()
    message = FakeMessage()
    message.raw_payload = json.dumps(
        dict(
            href_slug="api/v2/job_templates/909/launch",
            method="post",
            params=dict(name="Fred"),
        )
    )
    headers = {"Content-Type": "application/json"}
    response = dict(
        count=1, next=None, previous=None, results=[dict(id=5, type="job")],
    )
    config = dict(
        username="fred",
        password="radia",
        url="https://www.example.com",
        validate_cert="0",
        verify_ssl="False",
    )
    with aioresponses() as mocked:
        mocked.post(
            "https://www.example.com/api/v2/job_templates/909/launch",
            exception=ClientConnectionError("Connection Refused"),
        )
    
    with pytest.raises(Exception):
        worker.execute(message, config, q)
