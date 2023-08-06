class Proxy(object):

    def __init__(self, host, port, p_type, latency=0, validate_times=0, valid_times=0, invalid_times=0):
        self.host = host
        self.port = int(port)
        self.p_type = p_type.lower()
        self.latency = latency
        self.validate_times = validate_times
        self.valid_times = valid_times
        self.invalid_times = invalid_times

    def __repr__(self):
        return "<{} Proxy, [{}:{}]>".format(self.p_type.upper(), self.host, self.port)

    def __str__(self):
        return "<{} Proxy, [{}:{}]>".format(self.p_type.upper(), self.host, self.port)


if __name__ == '__main__':
    print Proxy("localhost", 1080, "socks5")
