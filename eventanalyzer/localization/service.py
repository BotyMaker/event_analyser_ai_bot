import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path


class LocalizationService:
    """Service for handling multilingual support."""
    
    SUPPORTED_LANGUAGES = ['en', 'ru', 'es', 'de', 'fr']
    DEFAULT_LANGUAGE = 'en'
    
    def __init__(self):
        self._translations: Dict[str, Dict[str, Any]] = {}
        self._load_translations()
    
    def _load_translations(self) -> None:
        """Load all translation files."""
        locales_dir = Path(__file__).parent / 'locales'
        
        for lang in self.SUPPORTED_LANGUAGES:
            file_path = locales_dir / f'{lang}.yaml'
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    self._translations[lang] = yaml.safe_load(f)
            else:
                print(f"Warning: Translation file for {lang} not found at {file_path}")
    
    def get_text(self, key: str, language: str = DEFAULT_LANGUAGE, **kwargs) -> str:
        """
        Get localized text by key path.
        
        Args:
            key: Dot-separated path to the text (e.g., 'welcome.title')
            language: Language code
            **kwargs: Variables for string formatting
            
        Returns:
            Localized text with formatting applied
        """
        if language not in self._translations:
            language = self.DEFAULT_LANGUAGE
        
        translation = self._translations.get(language, {})
        
        # Navigate through nested dictionary using dot notation
        keys = key.split('.')
        value = translation
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                # Fallback to English if key not found
                if language != self.DEFAULT_LANGUAGE:
                    return self.get_text(key, self.DEFAULT_LANGUAGE, **kwargs)
                return f"[Missing: {key}]"
        
        if isinstance(value, str):
            # Apply string formatting if kwargs provided
            if kwargs:
                try:
                    return value.format(**kwargs)
                except KeyError:
                    return value
            return value
        
        return f"[Invalid: {key}]"
    
    def get_language_name(self, language_code: str, in_language: str = None) -> str:
        """Get the name of a language in the specified language."""
        if in_language is None:
            in_language = language_code
        
        return self.get_text(f'languages.{language_code}', in_language)
    
    def is_supported_language(self, language: str) -> bool:
        """Check if a language is supported."""
        return language in self.SUPPORTED_LANGUAGES
    
    def get_default_custom_instruction(self, language: str) -> str:
        """Get the default custom instruction for a language."""
        return self.get_text('custom_instruction.default', language)


# Global instance
localization = LocalizationService() 