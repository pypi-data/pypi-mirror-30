import redis
import json
from time import time


not_implemented_error = 'This method is not implemented'
default_deployment = 'INDUSTRIAL'
get_all_attributes_by_label_script = """
local id = redis.call('hget', KEYS[1], KEYS[2]);
return redis.call('hgetall', tostring(id))
"""
get_attribute_by_label_script = """
local id = redis.call('hget', KEYS[1], KEYS[2]);
return redis.call('hget', tostring(id), KEYS[3])
"""
save_json_document_to_hash_set_script = """
local keysCount = #KEYS;
local hashKey = KEYS[1];
for i = 2, keysCount, 1 do
    redis.call('hset', hashKey, KEYS[i], ARGV[i - 1])
end
"""


def decode_binary_string(value):
    return getattr(value, 'decode', lambda c: value)('utf-8')


def utc_now_milliseconds():
    return int(time() * 1000)


def script_load(script):
    sha = [None]

    def call(conn, keys=None, args=None, force_eval=False):
        keys = {True: lambda: keys, False: lambda: []}.get(keys is not None)()
        args = {True: lambda: args, False: lambda: []}.get(args is not None)()
        if not force_eval:
            if not sha[0]:
                sha[0] = conn.execute_command(
                    "SCRIPT", "LOAD", script, parse="LOAD")
            try:
                return conn.execute_command("EVALSHA", sha[0], len(keys), *(keys + args))
            except redis.exceptions.ResponseError as msg:
                if not msg.args[0].startswith("NOSCRIPT"):
                    raise
        return conn.execute_command(
            "EVAL", script, len(keys), *(keys + args))

    return call


get_all_attributes_nested_script = script_load(get_all_attributes_by_label_script)
get_attribute_nested_script = script_load(get_attribute_by_label_script)
save_json_document_to_hash_set = script_load(save_json_document_to_hash_set_script)


class Entity(object):
    """
    This class represents an entity with attributes that will be stored to cache
    as a hash set in redis. Every attribute will be stored as key/value element
    of a hash set.
    """
    # deployment used to identify different subsystems
    deployment = default_deployment
    # The name of the entity
    entity = None
    primary_key_name = None
    primary_key = None
    stored_object = None
    attributes = []
    attributes_mapper = {}
    connection = None

    def __init__(self, stored_object=None, deployment=default_deployment,
                 entity=None, primary_key=None, primary_key_name=None, attributes=None,
                 attributes_mapper=None, connection=None):
        self.connection = {True: self.connection, False: connection}.get(connection is None)
        self.deployment = deployment
        self.stored_object = stored_object
        self.entity = entity
        self.primary_key = primary_key
        self.primary_key_name = primary_key_name
        self.attributes = attributes
        self.attributes_mapper = attributes_mapper

    @property
    def hash_key(self):
        """

        :return:
        """
        return u'{0}:{1}:{2}:{3}'.format(
            self.deployment, self.entity, self.primary_key_name, self.primary_key)

    def get_attribute(self, attribute_name):
        result = self.get_value(attribute_name)
        try:
            result = json.loads(decode_binary_string(result))
            value = result.get('value')
        except (TypeError, ValueError, AttributeError):
            value = None
        return value

    def encode_attribute(self, value, timestamp=None):
        timestamp = {True: utc_now_milliseconds,
                     False: lambda: timestamp}.get(timestamp is None)()
        return json.dumps({
            'value': value,
            'updated_timestamp': timestamp
        })

    def save_attribute(self, attribute_name, value):
        return self.set_value(attribute_name, json.dumps(self.encode_attribute(value)))

    def get_value(self, attribute_name):
        return self.connection.hget(self.hash_key, attribute_name)

    def set_value(self, attribute_name, value):
        return self.connection.hset(self.hash_key, attribute_name, value)

    def delete_value(self, attribute_name):
        return self.connection.hdel(self.hash_key, attribute_name)

    def get_all_attributes(self):
        result = self.connection.hgetall(self.hash_key)
        new_result = {}
        for key in result:
            try:
                new_result[decode_binary_string(key)] = json.loads(decode_binary_string(result.get(key)))
            except (ValueError, TypeError, AttributeError):
                pass
        return new_result

    def delete(self):
        return self.connection.delete(self.hash_key)

    def get_all_attributes_nested(self, nested_key):
        result = get_all_attributes_nested_script(self.connection, keys=[self.hash_key, nested_key])
        new_result = {}
        is_key = True
        current_key = None

        def process_key(k, v):
            return not is_key, v

        def process_value(k, v):
            new_result[k] = v
            return not is_key, k

        decode_functions = {True: process_key, False: process_value}
        for value in result:
            value = decode_binary_string(value)
            is_key, current_key = decode_functions.get(is_key)(current_key, value)
        result = {}
        for key in new_result:
            try:
                result[key] = json.loads(decode_binary_string(new_result.get(key)))
            except (ValueError, TypeError, AttributeError):
                pass
        return result

    def get_value_nested(self, nested_key, attribute_name):
        result = get_attribute_nested_script(
            self.connection, keys=[self.hash_key, nested_key, attribute_name])
        return result

    def get_attribute_nested(self, nested_key, attribute_name):
        result = self.get_value_nested(nested_key, attribute_name)
        try:
            result = json.loads(decode_binary_string(result))
            value = result.get('value')
        except (TypeError, ValueError, AttributeError):
            value = None
        return value

    def save(self):
        return self.save_optimized()

    def simple_save(self):
        def default_map(variable, v):
            return v
        for attribute_name in self.attributes:
            value = getattr(self.stored_object, attribute_name, None)
            value = self.attributes_mapper.get(attribute_name, default_map)(
                self.stored_object, value)
            self.save_attribute(attribute_name, value)
        return True

    def save_optimized(self):
        def default_map(variable, v):
            return v

        keys = [self.hash_key]
        values = []
        utc_now = utc_now_milliseconds()
        for attribute_name in self.attributes:
            value = getattr(self.stored_object, attribute_name, None)
            value = self.attributes_mapper.get(attribute_name, default_map)(
                self.stored_object, value)
            keys.append(attribute_name)
            encoded_value = self.encode_attribute(value, utc_now)
            values.append(encoded_value)

        return save_json_document_to_hash_set(self.connection, keys=keys, args=values)


class Variable(Entity):
    attributes = ['derived_expr', 'tags', 'device_id', 'type',
                  'created_at', 'properties', 'label', 'name',
                  'icon', 'description', 'state', 'unit', 'id',
                  'device_id', 'last_value', 'last_activity'
                  ]

    def __init__(self, variable=None,
                 deployment=default_deployment, attributes=None,
                 primary_key=None, attributes_mapper=None, connection=None):
        primary_key = u'{0}'.format(getattr(variable, 'id', primary_key))
        entity = 'variable'
        primary_key_name = 'id'
        attributes = {True: attributes, False: self.attributes}.get(attributes is not None)
        attributes_mapper = {True: attributes_mapper,
                             False: self.attributes_mapper}.get(attributes_mapper is not None)
        super(Variable, self).__init__(deployment=deployment, stored_object=variable,
                                       primary_key=primary_key, entity=entity,
                                       primary_key_name=primary_key_name,
                                       attributes=attributes,
                                       attributes_mapper=attributes_mapper,
                                       connection=connection)

    @property
    def derived_expr(self):
        return self.get_attribute('derived_expr')

    @property
    def tags(self):
        return self.get_attribute('tags')

    @property
    def device_id(self):
        return self.get_attribute('device_id')

    @property
    def type(self):
        return self.get_attribute('type')

    @property
    def created_at(self):
        return self.get_attribute('created_at')

    @property
    def properties(self):
        return self.get_attribute('properties')

    @property
    def label(self):
        return self.get_attribute('label')

    @property
    def name(self):
        return self.get_attribute('name')

    @property
    def icon(self):
        return self.get_attribute('icon')

    @property
    def description(self):
        return self.get_attribute('description')

    @property
    def state(self):
        return self.get_attribute('state')

    @property
    def unit(self):
        return self.get_attribute('unit')

    @property
    def id(self):
        return self.get_attribute('id')

    @property
    def last_value(self):
        return self.get_attribute('last_value')

    @property
    def last_activity(self):
        return self.get_attribute('last_activity')


class Device(Entity):
    attributes = ['owner_id', 'tags', 'organization_id',
                  'created_at', 'context', 'label', 'name',
                  'ubi_context', 'description', 'state', 'id',
                  'enabled', 'last_activity', 'variables'
                  ]

    def __init__(self, device=None, deployment=default_deployment, attributes=None,
                 primary_key=None, attributes_mapper=None, connection=None):
        primary_key = u'{0}'.format(getattr(device, 'id', primary_key))
        entity = 'device'
        primary_key_name = 'id'
        attributes = {True: attributes, False: self.attributes}.get(attributes is not None)
        attributes_mapper = {True: attributes_mapper,
                             False: self.attributes_mapper}.get(attributes_mapper is not None)
        super(Device, self).__init__(deployment=deployment, stored_object=device,
                                     primary_key=primary_key, entity=entity,
                                     primary_key_name=primary_key_name,
                                     attributes=attributes,
                                     connection=connection,
                                     attributes_mapper=attributes_mapper)

    @property
    def owner_id(self):
        return self.get_attribute('owner_id')

    @property
    def name(self):
        return self.get_attribute('name')

    @property
    def organization_id(self):
        return self.get_attribute('organization_id')

    @property
    def state(self):
        return self.get_attribute('state')

    @property
    def description(self):
        return self.get_attribute('description')

    @property
    def label(self):
        return self.get_attribute('label')

    @property
    def context(self):
        return self.get_attribute('context')

    @property
    def tags(self):
        return self.get_attribute('tags')

    @property
    def ubi_context(self):
        return self.get_attribute('ubi_context')

    @property
    def created_at(self):
        return self.get_attribute('created_at')

    @property
    def id(self):
        return self.get_attribute('id')

    @property
    def enabled(self):
        return self.get_attribute('enabled')

    @property
    def variables(self):
        return self.get_attribute('variables')

    @property
    def last_activity(self):
        return self.get_attribute('last_activity')


class VariableByLabel(Entity):
    attributes = ['id']
    attributes_mapper = {
        'id': lambda variable, value: Variable(primary_key=getattr(variable, 'id', value)).hash_key,
    }

    def __init__(self, deployment=default_deployment, primary_key=None, variable=None,
                 attributes=None, attributes_mapper=None, connection=None):
        device = getattr(variable, 'datasource', None)
        device_label = getattr(device, 'label', None)
        user_id = getattr(device, 'owner_id', None)
        variable_label = u'{0}'.format(getattr(variable, 'label', None))
        local_primary_key = u'{0}:{1}:{2}'.format(user_id, device_label, variable_label)
        primary_key = {True: primary_key, False: local_primary_key}.get(primary_key is not None)
        entity = 'variable'
        primary_key_name = 'label'
        attributes = {True: attributes, False: self.attributes}.get(attributes is not None)
        attributes_mapper = {True: attributes_mapper,
                             False: self.attributes_mapper}.get(attributes_mapper is not None)
        super(VariableByLabel, self).__init__(deployment=deployment, stored_object=variable,
                                              primary_key=primary_key, entity=entity,
                                              primary_key_name=primary_key_name,
                                              attributes=attributes,
                                              connection=connection,
                                              attributes_mapper=attributes_mapper)

    def encode_attribute(self, value, timestamp=None):
        return '{0}'.format(value)

    @property
    def derived_expr(self):
        return self.get_attribute_nested('id', 'derived_expr')

    @property
    def tags(self):
        return self.get_attribute_nested('id', 'tags')

    @property
    def device_id(self):
        return self.get_attribute_nested('id', 'device_id')

    @property
    def type(self):
        return self.get_attribute_nested('id', 'type')

    @property
    def created_at(self):
        return self.get_attribute_nested('id', 'created_at')

    @property
    def properties(self):
        return self.get_attribute_nested('id', 'properties')

    @property
    def label(self):
        return self.get_attribute_nested('id', 'label')

    @property
    def name(self):
        return self.get_attribute_nested('id', 'name')

    @property
    def icon(self):
        return self.get_attribute_nested('id', 'icon')

    @property
    def description(self):
        return self.get_attribute_nested('id', 'description')

    @property
    def state(self):
        return self.get_attribute_nested('id', 'state')

    @property
    def unit(self):
        return self.get_attribute_nested('id', 'unit')

    @property
    def id(self):
        return self.get_attribute_nested('id', 'id')

    @property
    def last_value(self):
        return self.get_attribute_nested('id', 'last_value')

    @property
    def last_activity(self):
        return self.get_attribute_nested('id', 'last_activity')


class DeviceByLabel(Entity):
    attributes = ['id']
    attributes_mapper = {
        'id': lambda device, value: Device(primary_key=getattr(device, 'id', value)).hash_key,
    }

    def __init__(self, deployment=default_deployment, primary_key=None, device=None,
                 attributes=None, attributes_mapper=None, connection=None):
        device_label = getattr(device, 'label', None)
        user_id = getattr(device, 'owner_id', None)
        local_primary_key = u'{0}:{1}'.format(user_id, device_label)
        primary_key = {True: primary_key, False: local_primary_key}.get(primary_key is not None)
        entity = 'device'
        primary_key_name = 'label'
        attributes = {True: attributes, False: self.attributes}.get(attributes is not None)
        attributes_mapper = {True: attributes_mapper,
                             False: self.attributes_mapper}.get(attributes_mapper is not None)
        super(DeviceByLabel, self).__init__(deployment=deployment, stored_object=device,
                                            primary_key=primary_key, entity=entity,
                                            primary_key_name=primary_key_name,
                                            attributes=attributes,
                                            connection=connection,
                                            attributes_mapper=attributes_mapper)

    def encode_attribute(self, value, timestamp=None):
        return '{0}'.format(value)

    @property
    def owner_id(self):
        return self.get_attribute_nested('id', 'owner_id')

    @property
    def name(self):
        return self.get_attribute_nested('id', 'name')

    @property
    def organization_id(self):
        return self.get_attribute_nested('id', 'organization_id')

    @property
    def state(self):
        return self.get_attribute_nested('id', 'state')

    @property
    def description(self):
        return self.get_attribute_nested('id', 'description')

    @property
    def label(self):
        return self.get_attribute_nested('id', 'label')

    @property
    def context(self):
        return self.get_attribute_nested('id', 'context')

    @property
    def tags(self):
        return self.get_attribute_nested('id', 'tags')

    @property
    def ubi_context(self):
        return self.get_attribute_nested('id', 'ubi_context')

    @property
    def created_at(self):
        return self.get_attribute_nested('id', 'created_at')

    @property
    def id(self):
        return self.get_attribute_nested('id', 'id')

    @property
    def enabled(self):
        return self.get_attribute_nested('id', 'enabled')

    @property
    def variables(self):
        return self.get_attribute_nested('id', 'variables')

    @property
    def last_activity(self):
        return self.get_attribute_nested('id', 'last_activity')


class User(Entity):
    attributes = ['id', 'username', 'first_name', 'last_name', 'email',
                  'custom_username', 'current_credits',
                  'default_dashboard', 'language', 'website',
                  'timezone', 'properties']

    def __init__(self, user=None, deployment=default_deployment, attributes=None,
                 attributes_mapper=None, primary_key=None, connection=None):
        primary_key = u'{0}'.format(getattr(user, 'id', primary_key))
        entity = 'user'
        primary_key_name = 'id'
        attributes = {True: attributes, False: self.attributes}.get(attributes is not None)
        attributes_mapper = {True: attributes_mapper,
                             False: self.attributes_mapper}.get(attributes_mapper is not None)
        super(User, self).__init__(deployment=deployment, stored_object=user,
                                   primary_key=primary_key, entity=entity,
                                   primary_key_name=primary_key_name,
                                   attributes=attributes,
                                   connection=connection,
                                   attributes_mapper=attributes_mapper)

    @property
    def id(self):
        return self.get_attribute('id')

    @property
    def username(self):
        return self.get_attribute('username')

    @property
    def first_name(self):
        return self.get_attribute('first_name')

    @property
    def last_name(self):
        return self.get_attribute('last_name')

    @property
    def email(self):
        return self.get_attribute('email')

    @property
    def custom_username(self):
        return self.get_attribute('custom_username')

    @property
    def default_dashboard(self):
        return self.get_attribute('default_dashboard')

    @property
    def current_credits(self):
        return self.get_attribute('current_credits')

    @property
    def language(self):
        return self.get_attribute('language')

    @property
    def timezone(self):
        return self.get_attribute('timezone')

    @property
    def properties(self):
        return self.get_attribute('properties')

    @property
    def website(self):
        return self.get_attribute('website')


class BusinessAccount(Entity):
    attributes = ['id', 'owner_id', 'is_active', 'date_created', 'balance',
                  'extra_costs', 'prices', 'initial_free_items', 'limits', 'one_time_costs',
                  'business_type', 'last_activity', 'trial_end_timestamp_utc', 'invoice_to',
                  'custom_note', 'plan', 'from_email']

    def __init__(self, business_account=None, deployment=default_deployment, attributes=None,
                 primary_key=None, attributes_mapper=None, connection=None):
        primary_key = u'{0}'.format(getattr(business_account, 'id', primary_key))
        entity = 'business_account'
        primary_key_name = 'id'
        attributes = {True: attributes, False: self.attributes}.get(attributes is not None)
        attributes_mapper = {True: attributes_mapper,
                             False: self.attributes_mapper}.get(attributes_mapper is not None)
        super(BusinessAccount, self).__init__(deployment=deployment, stored_object=business_account,
                                              primary_key=primary_key, entity=entity,
                                              primary_key_name=primary_key_name,
                                              attributes=attributes,
                                              connection=connection,
                                              attributes_mapper=attributes_mapper)

    @property
    def id(self):
        return self.get_attribute('id')

    @property
    def owner_id(self):
        return self.get_attribute('owner_id')

    @property
    def date_created(self):
        return self.get_attribute('date_created')

    @property
    def balance(self):
        return self.get_attribute('balance')

    @property
    def extra_costs(self):
        return self.get_attribute('extra_costs')

    @property
    def prices(self):
        return self.get_attribute('prices')

    @property
    def initial_free_items(self):
        return self.get_attribute('initial_free_items')

    @property
    def limits(self):
        return self.get_attribute('limits')

    @property
    def one_time_costs(self):
        return self.get_attribute('one_time_costs')

    @property
    def business_type(self):
        return self.get_attribute('business_type')

    @property
    def last_activity(self):
        return self.get_attribute('last_activity')

    @property
    def trial_end_timestamp_utc(self):
        return self.get_attribute('trial_end_timestamp_utc')

    @property
    def invoice_to(self):
        return self.get_attribute('invoice_to')

    @property
    def custom_note(self):
        return self.get_attribute('custom_note')

    @property
    def plan(self):
        return self.get_attribute('plan')

    @property
    def from_email(self):
        return self.get_attribute('from_email')

    @property
    def is_active(self):
        return self.get_attribute('is_active')
