import pytest
from eventanalyzer.localization import localization


def test_get_text_english():
    """Test getting text in English."""
    title = localization.get_text('welcome.title', 'en')
    assert 'TRUTH DETECTOR' in title


def test_get_text_russian():
    """Test getting text in Russian."""
    title = localization.get_text('welcome.title', 'ru')
    assert 'ДЕТЕКТОР ПРАВДЫ' in title


def test_get_text_with_formatting():
    """Test text formatting with variables."""
    text = localization.get_text('analysis.issues_found', 'en', count=3)
    assert 'EXPOSED 3 LIE(S)' in text


def test_get_text_fallback_to_english():
    """Test fallback to English for unsupported language."""
    title = localization.get_text('welcome.title', 'zh')
    assert 'TRUTH DETECTOR' in title


def test_get_text_missing_key():
    """Test handling of missing localization key."""
    result = localization.get_text('nonexistent.key', 'en')
    assert '[Missing: nonexistent.key]' in result


def test_supported_languages():
    """Test that supported languages are correctly defined."""
    languages = localization.SUPPORTED_LANGUAGES
    assert 'en' in languages
    assert 'ru' in languages
    assert 'es' in languages
    assert 'de' in languages
    assert 'fr' in languages
    assert len(languages) == 5


def test_get_language_name():
    """Test getting language display names."""
    en_name = localization.get_text('languages.en', 'en')
    ru_name = localization.get_text('languages.ru', 'en')
    
    assert 'English' in en_name
    assert 'Русский' in ru_name


def test_all_languages_have_required_keys():
    """Test that all supported languages have required keys."""
    required_keys = [
        'welcome.title',
        'welcome.description',
        'onboarding.title',
        'language.title',
        'settings.title',
        'analysis.analyzing',
        'custom_instruction.default'
    ]
    
    for lang in localization.SUPPORTED_LANGUAGES:
        for key in required_keys:
            result = localization.get_text(key, lang)
            assert not result.startswith('[Missing:'), f"Missing key '{key}' for language '{lang}'" 