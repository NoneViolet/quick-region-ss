import re

VALID_NORMAL = set("abcdefghijklmnopqrstuvwxyz1234567890") | \
    {f'f{i}' for i in range(1, 13)}

VALID_SPECIAL = {
    '<space>': set('space'),
    '<tab>': set('tab'),
    '<esc>': set('esc'),
    '<enter>': set('enter'),
    '<backspace>': set('backspace')
}
VALID_MODIFIER = {
    '<ctrl>': set('ctrl'),
    '<alt>': set('alt'),
    '<shift>': set('shift'),
    '<cmd>': set('cmd')
}

def _clean_key_name(raw: str) -> str:
    return re.sub(r'[^a-z0-9]', '', raw.lower())

def _is_key_normal(key: str) -> None | str:
    if key in VALID_NORMAL:
        return key
    else:
        return None

def _is_key_special(key: str) -> None | str:
    unique_char = set(key)

    for normalized, required_chars in VALID_SPECIAL.items():
        if required_chars.issubset(unique_char):
            return normalized
    return None

def _is_key_modifier(key: str) -> None | str:
    key_lower = _clean_key_name(key)
    unique_char = set(key_lower)

    for normalized, required_chars in VALID_MODIFIER.items():
        if required_chars.issubset(unique_char):
            return normalized
    return None

def _is_key_main(key: str) -> None | str:
    key_lower = _clean_key_name(key)

    key_normalized_normal = _is_key_normal(key_lower)
    key_normalized_special = _is_key_special(key_lower)

    if key_normalized_normal:
        return key_normalized_normal
    elif key_normalized_special:
        return key_normalized_special
    else:
        return None

def normalize_hotkey_input(user_input: str) -> None | str:
    keys = [key.strip() for key in user_input.split('+')]
    modifier_key = []
    main_key = None

    for key in keys:
        mod = _is_key_modifier(key)
        main = _is_key_main(key)
        if mod:
            if mod not in modifier_key:
                modifier_key.append(mod)
        elif main:
            if main_key is None:
                main_key = main
            else:
                return None
        else:
            return None

    if not main_key:
        return None

    return '+'.join(modifier_key + [main_key])