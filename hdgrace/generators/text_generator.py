"""
Text generation module - consolidates all TextGenerator classes from original HDGRACE.txt.
"""

import re
import random
from typing import Dict, List, Optional, Union
from ..core.base_generator import BaseGenerator
from ..utils.config import Config

class TextGenerator(BaseGenerator):
    """
    Production-ready text generator that consolidates functionality from 
    all TextGenerator_X classes in the original HDGRACE.txt file.
    
    Features:
    - Multiple text patterns (lorem, technical, business, etc.)
    - Various output formats (paragraph, sentences, list, etc.)
    - Pattern variations and randomization
    - Template-based generation
    - Word frequency analysis
    - Text transformation utilities
    """
    
    def _initialize(self) -> None:
        """Initialize text generation patterns and settings."""
        self.patterns = {
            'lorem': 'Lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor incididunt ut labore et dolore magna aliqua',
            'technical': 'Implementation requires careful consideration of architectural patterns and design principles for scalable software development',
            'business': 'Strategic initiatives drive organizational growth through innovative solutions and partnerships across diverse market segments',
            'api': 'RESTful endpoints provide structured data access with authentication and rate limiting capabilities for secure integration',
            'database': 'Relational database systems ensure data integrity through ACID transaction properties and normalized schema design',
            'security': 'Authentication mechanisms protect sensitive information using encryption and access controls with multi-factor verification',
            'web': 'Modern web applications leverage responsive design frameworks and progressive enhancement for optimal user experience',
            'mobile': 'Cross-platform mobile development frameworks enable efficient deployment across iOS and Android ecosystems',
            'cloud': 'Cloud computing infrastructure provides scalable resources with automated provisioning and disaster recovery capabilities',
            'ai': 'Machine learning algorithms process large datasets to identify patterns and generate predictive insights for decision making',
            'devops': 'Continuous integration and deployment pipelines automate testing and release processes for reliable software delivery',
            'legal': 'Legal frameworks establish comprehensive guidelines for compliance with regulatory requirements and industry standards'
        }
        
        self.format_types = {
            'paragraph': self._format_paragraph,
            'sentences': self._format_sentences,
            'list': self._format_list,
            'numbered': self._format_numbered,
            'bullet_points': self._format_bullet_points,
            'csv': self._format_csv,
            'json': self._format_json,
            'xml': self._format_xml,
            'markdown': self._format_markdown,
            'html': self._format_html
        }
        
        self.transformations = {
            'uppercase': str.upper,
            'lowercase': str.lower,
            'title': str.title,
            'capitalize': str.capitalize,
            'reverse': lambda x: x[::-1],
            'shuffle_words': self._shuffle_words,
            'remove_vowels': self._remove_vowels,
            'pig_latin': self._pig_latin
        }
    
    def _validate_input(self, **kwargs) -> None:
        """Validate text generation parameters."""
        pattern_type = kwargs.get('pattern_type', 'lorem')
        length = kwargs.get('length', 100)
        format_type = kwargs.get('format_type', 'paragraph')
        
        if not isinstance(pattern_type, str):
            raise ValueError("pattern_type must be a string")
        
        if not isinstance(length, int) or length <= 0:
            raise ValueError("length must be a positive integer")
        
        if length > self.config.get("max_generation_length", 10000):
            raise ValueError(f"length exceeds maximum allowed: {self.config.get('max_generation_length')}")
        
        if format_type not in self.format_types:
            raise ValueError(f"format_type must be one of: {list(self.format_types.keys())}")
    
    def _generate_content(self, **kwargs) -> str:
        """Core text generation logic."""
        pattern_type = kwargs.get('pattern_type', 'lorem')
        length = kwargs.get('length', 100)
        format_type = kwargs.get('format_type', 'paragraph')
        transformation = kwargs.get('transformation', None)
        variation_level = kwargs.get('variation_level', 0.1)
        
        # Get base pattern
        base_pattern = self.patterns.get(pattern_type, self.patterns['lorem'])
        words = base_pattern.split()
        
        # Generate word sequence
        result_words = []
        for i in range(length):
            word = words[i % len(words)]
            
            # Apply variation if requested
            if variation_level > 0 and random.random() < variation_level:
                word = self._apply_variation(word)
            
            result_words.append(word)
        
        # Join words
        text = ' '.join(result_words)
        
        # Apply transformation if specified
        if transformation and transformation in self.transformations:
            text = self.transformations[transformation](text)
        
        # Apply formatting
        formatter = self.format_types.get(format_type, self._format_paragraph)
        return formatter(text)
    
    def generate_with_template(self, template: str, variables: Dict[str, str]) -> str:
        """
        Generate text using a template with variable substitution.
        
        Args:
            template: Template string with {variable} placeholders
            variables: Dictionary mapping variable names to values
            
        Returns:
            Formatted text with variables substituted
        """
        try:
            return template.format(**variables)
        except KeyError as e:
            raise ValueError(f"Missing template variable: {e}")
        except Exception as e:
            raise ValueError(f"Template formatting error: {e}")
    
    def generate_multiple_patterns(self, patterns: List[str], length_per_pattern: int = 50) -> Dict[str, str]:
        """
        Generate text for multiple patterns.
        
        Args:
            patterns: List of pattern types
            length_per_pattern: Length of text for each pattern
            
        Returns:
            Dictionary mapping pattern names to generated text
        """
        results = {}
        for pattern in patterns:
            try:
                results[pattern] = self.generate(
                    pattern_type=pattern,
                    length=length_per_pattern,
                    use_cache=True
                )
            except Exception as e:
                self.error_logger.log_generation_error(
                    f"generate_multiple_patterns({pattern})", str(e)
                )
                results[pattern] = f"Error generating {pattern}: {e}"
        
        return results
    
    def analyze_text_complexity(self, text: str) -> Dict[str, Union[int, float]]:
        """
        Analyze text complexity metrics.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary of complexity metrics
        """
        words = text.split()
        sentences = re.split(r'[.!?]+', text)
        
        # Calculate metrics
        word_count = len(words)
        sentence_count = len([s for s in sentences if s.strip()])
        avg_word_length = sum(len(word) for word in words) / max(word_count, 1)
        avg_sentence_length = word_count / max(sentence_count, 1)
        
        # Unique word ratio
        unique_words = len(set(word.lower() for word in words))
        unique_ratio = unique_words / max(word_count, 1)
        
        return {
            'word_count': word_count,
            'sentence_count': sentence_count,
            'avg_word_length': round(avg_word_length, 2),
            'avg_sentence_length': round(avg_sentence_length, 2),
            'unique_word_ratio': round(unique_ratio, 2),
            'complexity_score': round((avg_word_length + avg_sentence_length) * unique_ratio, 2)
        }
    
    def _apply_variation(self, word: str) -> str:
        """Apply random variation to a word."""
        variations = [
            word,  # Original
            word.upper(),  # Uppercase
            word.capitalize(),  # Capitalized
            word + 's',  # Plural
            word[::-1],  # Reversed
        ]
        return random.choice(variations)
    
    def _format_paragraph(self, text: str) -> str:
        """Format as paragraph."""
        return text.strip() + '.'
    
    def _format_sentences(self, text: str) -> str:
        """Format as separate sentences."""
        sentences = [text[i:i+50] + '.' for i in range(0, len(text), 50)]
        return ' '.join(sentences)
    
    def _format_list(self, text: str) -> str:
        """Format as bulleted list."""
        items = [text[i:i+30] for i in range(0, len(text), 30)]
        return '\n'.join(f'- {item.strip()}' for item in items if item.strip())
    
    def _format_numbered(self, text: str) -> str:
        """Format as numbered list."""
        items = [text[i:i+30] for i in range(0, len(text), 30)]
        return '\n'.join(f'{i+1}. {item.strip()}' for i, item in enumerate(items) if item.strip())
    
    def _format_bullet_points(self, text: str) -> str:
        """Format as bullet points."""
        items = [text[i:i+25] for i in range(0, len(text), 25)]
        return '\n'.join(f'• {item.strip()}' for item in items if item.strip())
    
    def _format_csv(self, text: str) -> str:
        """Format as CSV."""
        words = text.split()
        rows = [words[i:i+3] for i in range(0, len(words), 3)]
        return '\n'.join(','.join(row) for row in rows)
    
    def _format_json(self, text: str) -> str:
        """Format as JSON array."""
        words = text.split()
        items = [f'"{word}"' for word in words[:10]]  # Limit for readability
        return f'[{", ".join(items)}]'
    
    def _format_xml(self, text: str) -> str:
        """Format as XML."""
        words = text.split()
        items = [f'<item>{word}</item>' for word in words[:5]]  # Limit for readability
        return f'<root>\n  {chr(10).join("  " + item for item in items)}\n</root>'
    
    def _format_markdown(self, text: str) -> str:
        """Format as Markdown."""
        lines = [text[i:i+40] for i in range(0, len(text), 40)]
        return '\n\n'.join(f'## {line.strip()}' for line in lines if line.strip())
    
    def _format_html(self, text: str) -> str:
        """Format as HTML."""
        return f'<p>{text}</p>'
    
    def _shuffle_words(self, text: str) -> str:
        """Shuffle words in text."""
        words = text.split()
        random.shuffle(words)
        return ' '.join(words)
    
    def _remove_vowels(self, text: str) -> str:
        """Remove vowels from text."""
        return re.sub(r'[aeiouAEIOU]', '', text)
    
    def _pig_latin(self, text: str) -> str:
        """Convert text to pig latin."""
        words = text.split()
        pig_words = []
        
        for word in words:
            if word and word[0].lower() in 'aeiou':
                pig_words.append(word + 'way')
            elif word:
                pig_words.append(word[1:] + word[0] + 'ay')
            else:
                pig_words.append(word)
        
        return ' '.join(pig_words)
    
    def add_custom_pattern(self, name: str, pattern: str) -> None:
        """
        Add a custom text pattern.
        
        Args:
            name: Pattern name
            pattern: Pattern text
        """
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Pattern name must be a non-empty string")
        
        if not isinstance(pattern, str) or not pattern.strip():
            raise ValueError("Pattern text must be a non-empty string")
        
        self.patterns[name] = pattern
        logger.info(f"Added custom pattern: {name}")
    
    def get_available_patterns(self) -> List[str]:
        """Get list of available text patterns."""
        return list(self.patterns.keys())
    
    def get_available_formats(self) -> List[str]:
        """Get list of available format types."""
        return list(self.format_types.keys())
    
    def get_available_transformations(self) -> List[str]:
        """Get list of available text transformations."""
        return list(self.transformations.keys())