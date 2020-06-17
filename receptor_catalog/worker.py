"""
  Catalog Receptor Plugin
  Forwards HTTP GET and POST requests to the Ansible Tower
  The plugin is invoked by the receptor when it gets requests
  from the platform controller.
"""
from urllib.parse import urlparse
from urllib.parse import parse_qsl
from urllib.parse import urljoin
from distutils.util import strtobool
import json
import gzip
import logging
import ssl
import asyncio
import aiohttp
import jmespath


def configure_logger():
    """ Configure the logger """
    logger = logging.getLogger(__name__)
    receptor_logger = logging.getLogger("receptor")
    logger.setLevel(receptor_logger.level)
    for handler in receptor_logger.handlers:
        logger.addHandler(handler)
    return logger


def receptor_export(func):
    """ Decorator function for receptor. """
    setattr(func, "receptor_export", True)
    return func


class Run:
    """ The Run class to execute the work recieved from the controller """

    VALID_POST_CODES = [200, 201, 202]

    def __init__(self, queue, payload, config, logger):
        """ Initialize a Run instance with the following
        param: queue: The response queue
        param: payload: The payload recieved from the platform controller
        param: config: The config parameters read from receptor.conf
        param: logger: The logger instance to use
        """
        self.result_queue = queue
        self.config = config
        self.logger = logger

        self.href_slug = payload.pop("href_slug")
        self.method = payload.pop("method", "get").lower()
        self.fetch_all_pages = payload.pop("fetch_all_pages", False)
        if isinstance(self.fetch_all_pages, str):
            self.fetch_all_pages = strtobool(self.fetch_all_pages)

        self.encoding = payload.pop("accept_encoding", None)
        self.params = payload.pop("params", {})
        self.ssl_context = None
        self.apply_filters = payload.pop("apply_filter", None)

    @classmethod
    def from_raw(cls, queue, payload, plugin_config, logger):
        """ Class method to create a new instance """
        return cls(queue, payload, plugin_config, logger)

    def initialize_ssl(self):
        """ Configure SSL for the current session """
        self.ssl_context = ssl.SSLContext()
        # if self.config.get('ca_file', None):
        #    self.ssl_context.load_verify_locations(ca_file=self.config['ca_file'])
        verify_ssl = self.config.get("verify_ssl", True)
        if isinstance(verify_ssl, str):
            verify_ssl = strtobool(verify_ssl)

        if not verify_ssl:
            self.ssl_context.verify_mode = ssl.CERT_NONE

    async def get_page(self, session, url, params):
        """ Get a single page from the Tower API """
        self.logger.debug(f"Making get request for {url} {params}")
        async with session.get(url, params=params, ssl=self.ssl_context) as response:
            response_text = dict(status=response.status, body=await response.text())
        return response_text

    async def get(self, session, url):
        """ Send an HTTP Get request to the Ansible Tower API
            supports
            Fetching all pages from the end point using fetch_all_pages = True
            Compressing the response payload using accept_encoding = gzip
         """
        url_info = urlparse(url)
        params = dict(parse_qsl(url_info.query))
        if isinstance(self.params, dict):
            params.update(self.params)
        while True:
            response = await self.get_page(session, url, params)
            if response["status"] != 200:
                raise Exception(f"Get failed {url} status {response['status']}")

            if self.apply_filters:
                response["body"] = self.filter_body(response["body"])

            self.logger.debug(f"Response from filter {response}")
            if self.encoding and self.encoding == "gzip":
                self.result_queue.put(self.zip_json_contents(response))
            else:
                self.result_queue.put(response)

            if self.fetch_all_pages:
                result = json.loads(response["body"])
                if result.get("next", None):
                    params["page"] = params.get("page", 1) + 1
                else:
                    break
            else:
                break

    def zip_json_contents(self, data):
        """ Compress the data using gzip """
        self.logger.debug(f"Compressing response data for URL {self.href_slug}")
        return gzip.compress(json.dumps(data).encode("utf-8"))

    def filter_body(self, body):
        """ Apply JMESPath filters to the response body"""
        self.logger.debug(f"Filtering response data for URL {self.href_slug}")
        response_body = json.loads(body)

        if isinstance(self.apply_filters, dict):
            for key, jmes_filter in self.apply_filters.items():
                response_body[key] = jmespath.search(jmes_filter, response_body)
        elif isinstance(self.apply_filters, str):
            response_body = jmespath.search(self.apply_filters, response_body)

        return json.dumps(response_body)

    async def post(self, session, url):
        """ Post the data to the Ansible Tower """
        self.logger.debug(f"Making post request for {url} data {self.params}")
        headers = {"Content-Type": "application/json"}
        async with session.post(
            url, data=json.dumps(self.params), headers=headers, ssl=self.ssl_context
        ) as post_response:
            response = dict(
                status=post_response.status, body=await post_response.text()
            )

            if response["status"] not in self.VALID_POST_CODES:
                raise Exception(f"Post failed {url} status {response['status']}")

            if self.apply_filters:
                response["body"] = self.filter_body(response["body"])

            if self.encoding and self.encoding == "gzip":
                self.result_queue.put(self.zip_json_contents(response))
            else:
                self.result_queue.put(response)

    async def start(self):
        """ Start the asynchronous process to send requests to the tower api """
        auth = aiohttp.BasicAuth(self.config["username"], self.config["password"])
        headers = {}
        url = urljoin(self.config["url"], self.href_slug)

        if url.startswith("https"):
            self.initialize_ssl()

        async with aiohttp.ClientSession(headers=headers, auth=auth) as session:
            if self.method == "get":
                await self.get(session, url)
            elif self.method == "post":
                await self.post(session, url)
            await session.close()


def run(coroutine):
    loop = asyncio.new_event_loop()
    return loop.run_until_complete(coroutine)


@receptor_export
def execute(message, config, queue):
    """ Entrypoint for the receptor
        :param message: has message header information including payload coming in
                        from the platform controller.
                        payload
                            href_slug:
                            accept_encoding:
                            params:
                            method: get|post
        :param config: is the parameters loaded from the receptor.conf for this worker.
        :param queue: is the response channel used to send messages back to the receptor.
                      which forwards it to the platform controller.
    """
    logger = configure_logger()
    logger.debug(
        "Payload Type: %s Data %s", type(message.raw_payload), message.raw_payload
    )

    if isinstance(message.raw_payload, str):
        try:
            payload = json.loads(message.raw_payload)
        except json.JSONDecodeError as err:
            logger.exception(err)
            raise
    else:
        payload = message.raw_payload

    logger.debug("Parsed payload: %s", payload)
    try:
        logger.debug("Start called")
        run(Run.from_raw(queue, payload, config, logger).start())
        logger.debug("Start finished")
    except Exception as err:
        logger.exception(err)
        raise

    return queue
