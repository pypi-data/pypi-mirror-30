import six
import pytz
import base64
import datetime
import binascii

ARBITRARY_EPOCH = 1293840000   # number of seconds of 1/1/2011 after 1/1/1970


class BadSignature(Exception):
    pass


class SignatureExpired(Exception):
    pass


class Unsignable(Exception):
    pass


def make_hmac_signature(string, key):
    import hmac
    import hashlib
    mac = hmac.new(key.encode('utf-8'), string.encode('utf-8'), hashlib.sha1)
    return base64.b64encode(mac.digest()).decode('utf-8')


def get_secs_since_epoch():
    unix_epoch = pytz.utc.localize(datetime.datetime(1970, 1, 1))
    now = pytz.utc.localize(datetime.datetime.utcnow())
    now_in_secs = (now - unix_epoch).total_seconds()
    return now_in_secs - ARBITRARY_EPOCH


def sign(text, key, secs_since_epoch=None):
    if not isinstance(text, six.text_type) or not isinstance(key, six.text_type):
        raise Unsignable("input string and key should be a text type (py2 - unicode; py3 - str)")
    if secs_since_epoch is None:
        secs_since_epoch = get_secs_since_epoch()
    sse_as_bytes = six.text_type(secs_since_epoch).encode('utf-8')
    encoded_secs_since_epoch = base64.b64encode(sse_as_bytes).decode('utf-8')
    timestamped_data = text + '.' + encoded_secs_since_epoch
    signature = make_hmac_signature(timestamped_data, key)
    signed_text = timestamped_data + '.' + signature
    return signed_text


def unsign(signed_text, key, max_age=10 * 60):
    if not isinstance(signed_text, six.text_type) or not isinstance(key, six.text_type):
        raise BadSignature("input string should be a text type (py2 - unicode; py3 - str)")
    if signed_text.count('.') < 2:
        raise BadSignature("expecting at least 2 period characters in signed text")
    timestamped_string, signature_in = signed_text.rsplit('.', 1)
    signature_calced = make_hmac_signature(timestamped_string, key)
    if signature_calced != signature_in:
        raise BadSignature("signature '%s' does not match" % signature_in)
    unsigned_result, timestamp = timestamped_string.rsplit('.', 1)
    try:
        decoded_timestamp_str = base64.b64decode(timestamp)
    except binascii.Error as b64e:
        six.raise_from(BadSignature("invalid base64 encoding"), b64e)
    try:
        decoded_timestamp = float(decoded_timestamp_str)
    except ValueError:
        raise BadSignature("timestamp does not decode to a float. timestamp = '%s'" % timestamp)
    secs_since_epoch = get_secs_since_epoch()
    time_diff = secs_since_epoch - decoded_timestamp
    if abs(time_diff) > max_age:
        raise SignatureExpired("decoded timestamp = '%s'; current seconds since epoch = '%s'; current - decoded = '%s'" % (decoded_timestamp, secs_since_epoch, time_diff))
    return unsigned_result


# below functions are helpers for testing and debugging

def datetime_from_secs(secs):
    timestamp = secs + ARBITRARY_EPOCH
    return pytz.utc.localize(datetime.datetime.utcfromtimestamp(timestamp))


def to_chicago_time(a_time):
    chicago = pytz.timezone('America/Chicago')
    return a_time.astimezone(chicago)
