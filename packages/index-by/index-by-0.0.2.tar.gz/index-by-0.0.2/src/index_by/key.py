from index_by.modifier import index_by_modifier_as_list, index_by_modifier
from index_by.modifiers.key import KeyModifier


def index_by_key(sequence, key_name, target_index=None):
    return index_by_modifier(
        sequence,
        KeyModifier(key_name),
        target_index)


def index_by_key_as_list(sequence, key_name, target_index=None):
    return index_by_modifier_as_list(
        sequence,
        KeyModifier(key_name),
        target_index)
