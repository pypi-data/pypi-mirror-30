import random


class BaseProxyPool:

    def __init__(self, proxies=None):
        self.proxies = proxies
        self.valid_proxies = []
        self.invalid_proxies = []

    @property
    def valid_proxy_num(self):
        return len(self.valid_proxies)

    def add_proxy(self, proxy, multi=False):
        if multi:
            assert isinstance(proxy, list)
            self.proxies.extend(proxy)
        else:
            self.proxies.append(proxy)

    def start_validate(self):  # todo
        raise NotImplementedError()

    def get_proxy(self, multi=False, num=1):
        if not self.valid_proxies:
            return None
        if multi:
            assert num > 1, "You Should Give a Correct Number While You Want to Get *Multi* Proxies."
        return self.proxies[:num] if multi else random.choice(self.valid_proxies)

    def __repr__(self):
        return "{} Object: {}".format(self.__class__.__name__, str(self.proxies)[:200] + "...")

    def __str__(self):
        return "{} Object: {}".format(self.__class__.__name__, str(self.proxies)[:200] + "...")


if __name__ == '__main__':
    class Foo(BaseProxyPool):
        pass
    print BaseProxyPool()
    print Foo()
