"""
NitiGuard AI — Voice Processor
Text normalization utilities for voice-transcribed input.
Actual speech recognition and synthesis happen in the frontend via Web Speech API.
"""
import re
from typing import Optional


class VoiceProcessor:
    """Processes voice-transcribed text for better LLM understanding"""
    
    # Common voice transcription corrections for compliance domain
    CORRECTIONS = {
        "a m l": "AML",
        "k y c": "KYC",
        "g d p r": "GDPR",
        "p c i": "PCI",
        "d s s": "DSS",
        "s o x": "SOX",
        "h i p a a": "HIPAA",
        "r b i": "RBI",
        "s e b i": "SEBI",
        "niti lens": "NitiLens",
        "niti guard": "NitiGuard",
        "remediation": "remediation",
        "compliance": "compliance",
    }
    
    # Number words to digits
    NUMBER_WORDS = {
        "zero": "0", "one": "1", "two": "2", "three": "3",
        "four": "4", "five": "5", "six": "6", "seven": "7",
        "eight": "8", "nine": "9", "ten": "10",
    }
    
    @classmethod
    def normalize_voice_input(cls, text: str) -> str:
        """
        Normalize voice-transcribed text for better processing.
        
        - Fix common compliance acronyms
        - Clean up filler words
        - Normalize transaction IDs
        - Fix number words
        """
        if not text:
            return ""
        
        normalized = text.strip()
        
        # Fix compliance acronyms (case-insensitive)
        for wrong, correct in cls.CORRECTIONS.items():
            normalized = re.sub(
                re.escape(wrong), correct, normalized, flags=re.IGNORECASE
            )
        
        # Remove filler words
        filler_pattern = r'\b(um|uh|hmm|like|you know|basically|actually|so)\b'
        normalized = re.sub(filler_pattern, '', normalized, flags=re.IGNORECASE)
        
        # Normalize transaction ID patterns: "TX dash 234" -> "TX-234"
        normalized = re.sub(
            r'(?:TX|tx)\s*(?:dash|minus|-)\s*(\d+)',
            r'TX-\1',
            normalized,
            flags=re.IGNORECASE
        )
        
        # Fix number words in context
        for word, digit in cls.NUMBER_WORDS.items():
            normalized = re.sub(
                rf'\b{word}\b', digit, normalized, flags=re.IGNORECASE
            )
        
        # Clean up extra whitespace
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        # Ensure first letter is capitalized
        if normalized:
            normalized = normalized[0].upper() + normalized[1:]
        
        return normalized
    
    @classmethod
    def prepare_for_speech(cls, text: str) -> str:
        """
        Prepare response text for speech synthesis.
        
        - Expand abbreviations for natural speech
        - Format numbers for speech
        - Remove markdown formatting
        """
        if not text:
            return ""
        
        speech_text = text
        
        # Remove markdown formatting
        speech_text = re.sub(r'\*\*(.*?)\*\*', r'\1', speech_text)  # Bold
        speech_text = re.sub(r'\*(.*?)\*', r'\1', speech_text)      # Italic
        speech_text = re.sub(r'`(.*?)`', r'\1', speech_text)        # Code
        speech_text = re.sub(r'^#+\s*', '', speech_text, flags=re.MULTILINE)  # Headers
        speech_text = re.sub(r'^[-*]\s*', '', speech_text, flags=re.MULTILINE)  # Lists
        
        # Expand abbreviations for speech
        abbreviations = {
            "AML": "A M L",
            "KYC": "K Y C",
            "GDPR": "G D P R",
            "PCI-DSS": "P C I D S S",
            "SOX": "SOX",
            "HIPAA": "HIPAA",
            "RBAC": "R BAC",
        }
        
        for abbr, spoken in abbreviations.items():
            speech_text = speech_text.replace(abbr, spoken)
        
        # Clean up
        speech_text = re.sub(r'\s+', ' ', speech_text).strip()
        
        return speech_text


# Singleton
voice_processor = VoiceProcessor()
