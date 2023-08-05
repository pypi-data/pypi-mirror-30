import aerospike


class BaseCache(object):
    def __init__(self):
        pass

    def map_increment(self, key, map_key, increment, map_bin=None):
        raise NotImplementedError('This method is not implemented')

    def put_value(self, key, value, bins=None, namespace=None, set_name=None):
        raise NotImplementedError('This method is not implemented')

    def get_value(self, key, namespace=None, set_name=None, bin_name=None):
        raise NotImplementedError('This method is not implemented')

    def remove_key(self, key, namespace=None, set_name=None):
        raise NotImplementedError('This method is not implemented')

    def map_remove_key(self, key, map_key, namespace=None, set_name=None, map_bin=None):
        raise NotImplementedError('This method is not implemented')

    def map_put_value(self, key, map_key, value, map_bin=None, namespace=None, set_name=None):
        raise NotImplementedError('This method is not implemented')

    def map_get_value(self, key, map_key, map_bin=None, namespace=None, set_name=None):
        raise NotImplementedError('This method is not implemented')

    def save_udf(self, udf_path):
        pass

    def set_add(self, key, value, udf_bin=None, namespace=None, set_name=None):
        raise NotImplementedError('This method is not implemented')

    def set_add_many(self, key, values, udf_bin=None, namespace=None, set_name=None):
        raise NotImplementedError('This method is not implemented')

    def set_remove_many(self, key, values, udf_bin=None, namespace=None, set_name=None):
        raise NotImplementedError('This method is not implemented')

    def set_remove(self, key, value, udf_bin=None, namespace=None, set_name=None):
        raise NotImplementedError('This method is not implemented')

    def set_clear(self, key, udf_bin=None, namespace=None, set_name=None):
        raise NotImplementedError('This method is not implemented')

    def set_scan(self, key, udf_bin=None, namespace=None, set_name=None):
        raise NotImplementedError('This method is not implemented')


class AerospikeCache(BaseCache):
    def __init__(self, client, aerospike_set_module_name='set',
                 default_namespace=None, default_set_name=None):
        super().__init__()
        self.client = client
        self.aerospike_set_module_name = aerospike_set_module_name
        self.default_set_name = default_set_name
        self.default_namespace = default_namespace

    def get_complete_key(self, key, namespace=None, set_name=None):
        namespace = namespace if namespace is not None else self.default_namespace
        set_name = set_name if set_name is not None else self.default_set_name
        key = (namespace, set_name, key)
        return key

    def map_remove_key(self, key, map_key, namespace=None, set_name=None, map_bin=None):
        key = self.get_complete_key(key, namespace, set_name)
        map_bin = {True: map_bin, False: 'default_bin'}.get(map_bin is not None)
        try:
            return self.client.map_remove_by_key(key, map_bin, map_key, aerospike.MAP_RETURN_VALUE)
        except:
            return None

    def remove_key(self, key, namespace=None, set_name=None):
        key = self.get_complete_key(key, namespace, set_name)
        try:
            return self.client.remove(key)
        except:
            return None

    def map_increment(self, key, map_key, increment, map_bin=None, namespace=None, set_name=None):
        key = self.get_complete_key(key, namespace, set_name)
        map_bin = {True: map_bin, False: 'default_bin'}.get(map_bin is not None)
        return self.client.apply(key, self.aerospike_set_module_name,
                                 'map_increment', [map_bin, map_key, increment])

    def map_get_value(self, key, map_key, map_bin=None, namespace=None, set_name=None):
        key = self.get_complete_key(key, namespace, set_name)
        map_bin = {True: map_bin, False: 'default_bin'}.get(map_bin is not None)
        try:
            return self.client.map_get_by_key(key, map_bin, map_key, aerospike.MAP_RETURN_VALUE)
        except:
            return None

    def map_put_value(self, key, map_key, value, map_bin=None, namespace=None, set_name=None):
        key = self.get_complete_key(key, namespace, set_name)
        map_bin = {True: map_bin, False: 'default_bin'}.get(map_bin is not None)
        return self.client.map_put(key, map_bin, map_key, value)

    def get_value(self, key, namespace=None, set_name=None, bin_name=None):
        bin_name = 'value' if bin_name is None else bin_name
        key = self.get_complete_key(key, namespace, set_name)
        try:
            value = self.client.get(key)
        except:
            value = None
        bin_value = {
            True: lambda: value[2],
            False: lambda: None
        }.get(value is not None and len(value) > 2)
        bin_value = bin_value()
        result = {
            True: lambda: getattr(bin_value, 'get', lambda b: None)(bin_name),
            False: lambda: None}.get(bin_value is not None)
        return result()

    def put_value(self, key, value, bins=None, namespace=None, set_name=None):
        bins = {'value': value} if bins is None else bins
        key = self.get_complete_key(key, namespace, set_name)
        return self.client.put(key, bins)

    def save_udf(self, udf_path):
        return self.client.udf_put(udf_path)

    def set_add(self, key, value, udf_bin=None, namespace=None, set_name=None):
        key = self.get_complete_key(key, namespace, set_name)
        udf_bin = {True: udf_bin, False: 'default_bin'}.get(udf_bin is not None)
        return self.client.apply(key, self.aerospike_set_module_name,
                                 'unique_set_write', [udf_bin, value])

    def set_add_many(self, key, values, udf_bin=None, namespace=None, set_name=None):
        key = self.get_complete_key(key, namespace, set_name)
        udf_bin = {True: udf_bin, False: 'default_bin'}.get(udf_bin is not None)
        return self.client.apply(key, self.aerospike_set_module_name,
                                 'unique_set_write_many', [udf_bin, values])

    def set_clear(self, key, udf_bin=None, namespace=None, set_name=None):
        key = self.get_complete_key(key, namespace, set_name)
        udf_bin = {True: udf_bin, False: 'default_bin'}.get(udf_bin is not None)
        return self.client.remove_bin(key, [udf_bin])

    def set_remove_many(self, key, values, udf_bin=None, namespace=None, set_name=None):
        key = self.get_complete_key(key, namespace, set_name)
        udf_bin = {True: udf_bin, False: 'default_bin'}.get(udf_bin is not None)
        return self.client.apply(key, self.aerospike_set_module_name,
                                 'unique_set_remove_many', [udf_bin, values])

    def set_remove(self, key, value, udf_bin=None, namespace=None, set_name=None):
        key = self.get_complete_key(key, namespace, set_name)
        udf_bin = {True: udf_bin, False: 'default_bin'}.get(udf_bin is not None)
        return self.client.apply(key, self.aerospike_set_module_name,
                                 'unique_set_remove', [udf_bin, value])

    def set_scan(self, key, udf_bin=None, namespace=None, set_name=None):
        key = self.get_complete_key(key, namespace, set_name)
        udf_bin = {True: udf_bin, False: 'default_bin'}.get(udf_bin is not None)
        return self.client.apply(key, self.aerospike_set_module_name,
                                 'unique_set_scan', [udf_bin])


def decode_binary(value):
    return getattr(value, 'decode', lambda c: value)('utf-8')


class RedisCache(BaseCache):
    def __init__(self, client):
        super().__init__()
        self.client = client

    def put_value(self, key, value, bins=None, namespace=None, set_name=None):
        return self.client.set(key, value)

    def map_put_value(self, key, map_key, value, map_bin=None, namespace=None, set_name=None):
        return self.client.hset(key, map_key, value)

    def remove_key(self, key, namespace=None, set_name=None):
        return self.client.delete(key)

    def map_increment(self, key, map_key, increment, map_bin=None):
        return self.client.hincrby(key, map_key, increment)

    def get_value(self, key, namespace=None, set_name=None, bin_name=None):
        return decode_binary(self.client.get(key))

    def map_remove_key(self, key, map_key, namespace=None, set_name=None, map_bin=None):
        return self.client.hdel(key, map_key)

    def map_get_value(self, key, map_key, map_bin=None, namespace=None, set_name=None):
        return decode_binary(self.client.hget(key, map_key))

    def set_scan(self, key, udf_bin=None, namespace=None, set_name=None):
        return self.client.smembers(key)

    def save_udf(self, udf_path):
        return None

    def set_add(self, key, value, udf_bin=None, namespace=None, set_name=None):
        return self.client.sadd(key, value)

    def set_add_many(self, key, values, udf_bin=None, namespace=None, set_name=None):
        return self.client.sadd(key, *values)

    def set_clear(self, key, udf_bin=None, namespace=None, set_name=None):
        return self.client.delete(key)

    def set_remove_many(self, key, values, udf_bin=None, namespace=None, set_name=None):
        return self.client.srem(key, *values)

    def set_remove(self, key, value, udf_bin=None, namespace=None, set_name=None):
        return self.client.srem(key, value)
