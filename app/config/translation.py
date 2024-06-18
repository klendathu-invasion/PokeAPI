import i18n

_default_lang = "en"
DEFAULT_LANGUAGE = "en"
SUPPORTED_LANGUAGE = ["fr", "en"]


def active_translation(lang: str):
    global _default_lang

    request_lang = lang.split(",")[0] if lang is not None else DEFAULT_LANGUAGE

    _default_lang = (
        DEFAULT_LANGUAGE if request_lang not in SUPPORTED_LANGUAGE else request_lang
    )
    i18n.set("locale", _default_lang)
    i18n.set("fallback", DEFAULT_LANGUAGE)
    i18n.load_path.append(f"./app/locales/{DEFAULT_LANGUAGE}")
    if _default_lang != DEFAULT_LANGUAGE:
        i18n.load_path.append(f"./app/locales/{_default_lang}")
