import json
import logging

log = logging.getLogger(__name__)


class JsonApiParseException(Exception):
    """Raise for my specific kind of exception"""
    pass


class JsonAPIError(Exception):
    def __init__(self, message, errors):

        # Call the base class constructor with the parameters it needs
        super().__init__(message)

        # Now for your custom code...
        self.errors = errors


def _parse_include(raw, relationship, rel_id):
    sub = {}
    if 'included' in raw:
        for included in raw['included']:
            if 'id' not in included or 'type' not in included:
                raise JsonApiParseException('Include missing id or type: {}'.format(included))
            inc_type = included['type']
            inc_id = included['id']
            if inc_type == relationship and inc_id == rel_id:
                sub['id'] = inc_id
                if 'attributes' in included:
                    for key, value in included['attributes'].items():
                        sub[key] = value
                return sub
    return sub


def _parse_data(data, raw):
    flat_json = {}
    if 'id' not in data:
        raise JsonApiParseException('"data[id]" missing')
    flat_json['id'] = data['id']
    if 'attributes' in data:
        for key, value in data['attributes'].items():
            flat_json[key] = value
    if 'relationships' in data:
        for rname in data['relationships']:
            if isinstance(data['relationships'][rname]['data'], list):
                flat_json[rname] = []
                for d in data['relationships'][rname]['data']:
                    rtype = d['type']
                    rid = d['id']
                    sub = _parse_include(raw, rtype, rid)
                    log.debug('Sub: {}'.format(sub))
                    if sub:
                        flat_json[rname].append(sub)
            else:
                rtype = data['relationships'][rname]['data']['type']
                rid = data['relationships'][rname]['data']['id']
                flat_json[rname] = _parse_include(raw, rtype, rid)
    return flat_json


def flatten(raw):
    raw = json.loads(raw)
    flat_json = None
    if 'errors' in raw:
        if not isinstance(raw['errors'], list):
            raise JsonApiParseException('Errors is not a list')
        else:
            raise JsonAPIError('Json API Returned Errors', raw['errors'])
    if 'data' in raw:
        if raw['data'] is None:
            raise JsonApiParseException('Empty Data Set')
        if isinstance(raw['data'], list):
            log.debug('JSONA Data is a list')
            flat_json = []
            for d in raw['data']:
                flat_json.append(_parse_data(d, raw))
        elif isinstance(raw['data'], dict):
            log.debug('JSONA Data is a dict')
            flat_json = _parse_data(raw['data'], raw)
        else:
            raise JsonApiParseException('Unsupported Data Type {}'.format(type(raw['data'])))
        log.debug('Final Json: {}'.format(flat_json))
        return flat_json
    else:
        raise JsonApiParseException('"data" missing')
