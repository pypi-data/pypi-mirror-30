from storages.utils import setting


def get_key_from_settings(prefix, key, default=None, strict=True):
    key = '{}_{}'.format(prefix, key)
    return setting(key, default, strict)
