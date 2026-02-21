"""
Multi-language policy processing with translation
"""
from typing import Dict, Tuple
import langdetect
from transformers import MarianMTModel, MarianTokenizer
import os


class TranslationService:
    """Handles language detection and translation"""
    
    def __init__(self):
        self.models = {}
        self.tokenizers = {}
        self.use_local = not os.getenv("TRANSLATION_API_KEY")
    
    def detect_language(self, text: str) -> str:
        """Detect language of text"""
        try:
            return langdetect.detect(text)
        except:
            return "en"
    
    def translate_to_english(self, text: str, source_lang: str) -> Tuple[str, float]:
        """Translate text to English"""
        if source_lang == "en":
            return text, 1.0
        
        if self.use_local:
            return self._translate_local(text, source_lang)
        else:
            return self._translate_api(text, source_lang)
    
    def _translate_local(self, text: str, source_lang: str) -> Tuple[str, float]:
        """Translate using local Marian models"""
        try:
            # Map language codes to model names
            model_map = {
                "es": "Helsinki-NLP/opus-mt-es-en",
                "fr": "Helsinki-NLP/opus-mt-fr-en",
                "de": "Helsinki-NLP/opus-mt-de-en",
                "zh": "Helsinki-NLP/opus-mt-zh-en",
                "ja": "Helsinki-NLP/opus-mt-ja-en",
                "ko": "Helsinki-NLP/opus-mt-ko-en",
                "ar": "Helsinki-NLP/opus-mt-ar-en",
                "ru": "Helsinki-NLP/opus-mt-ru-en",
                "pt": "Helsinki-NLP/opus-mt-pt-en",
                "it": "Helsinki-NLP/opus-mt-it-en",
            }
            
            model_name = model_map.get(source_lang)
            if not model_name:
                return text, 0.5  # Unsupported language
            
            # Load model and tokenizer (cached)
            if model_name not in self.models:
                self.tokenizers[model_name] = MarianTokenizer.from_pretrained(model_name)
                self.models[model_name] = MarianMTModel.from_pretrained(model_name)
            
            tokenizer = self.tokenizers[model_name]
            model = self.models[model_name]
            
            # Translate in chunks if text is long
            max_length = 512
            chunks = [text[i:i+max_length] for i in range(0, len(text), max_length)]
            translated_chunks = []
            
            for chunk in chunks:
                inputs = tokenizer(chunk, return_tensors="pt", padding=True, truncation=True)
                outputs = model.generate(**inputs)
                translated = tokenizer.decode(outputs[0], skip_special_tokens=True)
                translated_chunks.append(translated)
            
            translated_text = " ".join(translated_chunks)
            confidence = 0.85  # Estimated confidence for local models
            
            return translated_text, confidence
            
        except Exception as e:
            print(f"Translation error: {e}")
            return text, 0.3
    
    def _translate_api(self, text: str, source_lang: str) -> Tuple[str, float]:
        """Translate using external API"""
        # Placeholder for external translation API
        # Implement with OpenAI, Google Translate, or other service
        return text, 0.9
    
    def process_policy(self, text: str) -> Dict:
        """Process policy document with language detection and translation"""
        original_lang = self.detect_language(text)
        
        if original_lang == "en":
            return {
                "original_language": original_lang,
                "translated_text": None,
                "translation_confidence": 1.0,
                "text": text
            }
        
        translated_text, confidence = self.translate_to_english(text, original_lang)
        
        return {
            "original_language": original_lang,
            "translated_text": translated_text,
            "translation_confidence": confidence,
            "text": translated_text
        }


# Global instance
translation_service = TranslationService()
