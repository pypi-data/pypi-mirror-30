import pycurl

from tornado import gen
from tornado.httpclient import AsyncHTTPClient
from tornado.log import gen_log

from pp_core.proxy import Proxy


def prepare_curl_socks5(curl):
    curl.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS5)


@gen.coroutine
def request_with_proxy_and_retry(url, try_fetch_without_proxy=True, proxy=None, without_proxy_retry=2, validator=None,
                                 with_proxy_retry=3, timeout=2.0, **kwargs):
    """
    Try to send the request for without_proxy_retry times, if got error:
    Try to send the request Use Proxy for with_proxy_retry times.

    If we don't need to request with proxy, set with_proxy_retry to 0

    :arg validator is a function, which takes the response as an argument, validates if the response if valid.
    """

    base_log = "{} [URL: {}, With Proxy: %s, Retry: %s/%s, MSG: %s]".format(
        request_with_proxy_and_retry.__name__.upper(), url)

    fetch_param = {
        "validate_cert": False,
        "connect_timeout": timeout,
        "raise_error": False,
    }

    fetch_param.update(**kwargs)

    # Request Without Proxy
    if try_fetch_without_proxy:
        client = AsyncHTTPClient()
        for _ in range(1, without_proxy_retry + 1):
            gen_log.info(base_log, False, _, without_proxy_retry, None)

            response = yield client.fetch(url, **fetch_param)

            if validator:
                is_valid, message = validator(response)
            else:
                is_valid, message = not response.error, response.error if response.error else ""

            if not is_valid:
                gen_log.error(base_log, False, _, without_proxy_retry, message)
            else:
                raise gen.Return(response)

    # Request With Proxy
    AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")

    client = AsyncHTTPClient(force_instance=True)

    if with_proxy_retry:
        if not proxy:
            gen_log.error(base_log, True, "--", "--", "Tried to Request With Proxy, But Did Not Provide A Proxy.")
            raise gen.Return(None)
        if not isinstance(proxy, Proxy):
            gen_log.error(base_log, True, "--", "--", "The Proxy Provided Should Be A pp_core.proxy.Proxy Instance.")
            raise gen.Return(None)

        proxy_type = proxy.p_type
        proxy_host = proxy.host
        proxy_port = proxy.port

        fetch_param.update(proxy_host=proxy_host, proxy_port=proxy_port)

        if proxy_type == "socks5":
            fetch_param.update(prepare_curl_callback=prepare_curl_socks5)

    for i in range(1, with_proxy_retry + 1):

        gen_log.info(base_log, True, i, with_proxy_retry, None)

        response = yield client.fetch(url, **fetch_param)

        if validator:
            is_valid, message = validator(response)
        else:
            is_valid, message = not response.error, response.error if response.error else ""

        if not is_valid:
            gen_log.error(base_log, True, i, with_proxy_retry, message)
        else:
            raise gen.Return(response)


if __name__ == '__main__':
    from tornado.ioloop import IOLoop
    from tornado.options import parse_command_line

    parse_command_line()

    loop = IOLoop.instance()


    @gen.coroutine
    def main():
        response = yield request_with_proxy_and_retry("https://www.baidu.com", 3, 3, 2)
        print response.body


    main()
    loop.start()
