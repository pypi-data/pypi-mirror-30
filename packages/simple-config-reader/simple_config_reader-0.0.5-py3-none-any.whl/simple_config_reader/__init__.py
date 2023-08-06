import yaml
from .utils import load_yaml, flatten_dict, deep_set, recursive_object_dict

__all__ = ['read_config', 'batch_read_config', 'ReadConfigError']


class ReadConfigError(Exception):
    pass


class DefaultsLoader(yaml.SafeLoader):
    pass


class NeedValue(yaml.YAMLObject):
    yaml_tag = '!need'
    yaml_loader = DefaultsLoader

    @classmethod
    def from_yaml(cls, loader, node):
        return cls()


def read_config(defaults_path, custom_values_path=None):
    defaults = load_yaml(defaults_path, DefaultsLoader) or {}
    flatten_defaults = flatten_dict(defaults)

    if custom_values_path:
        custom_values = load_yaml(custom_values_path) or {}
    else:
        custom_values = {}
    flatten_custom_values = flatten_dict(custom_values)

    unknown_paths = set(flatten_custom_values) - set(flatten_defaults)
    if unknown_paths:
        formatted_paths = ', '.join('.'.join(path) for path in unknown_paths)
        raise ReadConfigError('custom_values 中出现了 defaults 里未定义的配置项：' + formatted_paths)

    config = {}
    missed_paths = []
    for path, value in flatten_defaults.items():
        if path in flatten_custom_values:
            value = flatten_custom_values[path]
        elif isinstance(value, NeedValue):
            missed_paths.append(path)
        deep_set(config, path, value)

    if missed_paths:
        formatted_paths = ', '.join('.'.join(path) for path in missed_paths)
        raise ReadConfigError('以下配置项未赋值：' + formatted_paths)

    return recursive_object_dict(config)


def batch_read_config(groups):
    '''
    groups: [
        (default_path, custom_values_path),
        default_path
    ]
    '''
    merged_config = {}

    for group in groups:
        if isinstance(group, str):
            defaults_path = group
            custom_values_path = None
        else:
            defaults_path, custom_values_path = group

        current_config = read_config(defaults_path, custom_values_path)
        _deep_merge(merged_config, current_config, [])

    return recursive_object_dict(merged_config)


def _deep_merge(a, b, path):
    for key, value in b.items():
        sub_path = [*path, key]

        if key in a:
            if isinstance(a[key], dict) and isinstance(value, dict):
                _deep_merge(a[key], value, sub_path)
            else:
                raise ReadConfigError('配置项冲突：' + '.'.join(sub_path))
        else:
            a[key] = value
