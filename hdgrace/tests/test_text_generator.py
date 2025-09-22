"""
Tests for HDGRACE text generator.
"""

import pytest
from hdgrace.generators.text_generator import TextGenerator
from hdgrace.utils.config import Config


class TestTextGenerator:
    """Test cases for TextGenerator class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = Config()
        self.generator = TextGenerator(self.config)
    
    def test_initialization(self):
        """Test generator initialization."""
        assert self.generator is not None
        assert len(self.generator.patterns) > 0
        assert len(self.generator.format_types) > 0
        assert 'lorem' in self.generator.patterns
        assert 'paragraph' in self.generator.format_types
    
    def test_basic_text_generation(self):
        """Test basic text generation."""
        result = self.generator.generate(
            pattern_type='lorem',
            length=10,
            format_type='paragraph'
        )
        
        assert isinstance(result, str)
        assert len(result) > 0
        assert result.endswith('.')
    
    def test_different_patterns(self):
        """Test generation with different patterns."""
        patterns = ['lorem', 'technical', 'business', 'api']
        
        for pattern in patterns:
            result = self.generator.generate(
                pattern_type=pattern,
                length=5,
                format_type='paragraph'
            )
            
            assert isinstance(result, str)
            assert len(result) > 0
    
    def test_different_formats(self):
        """Test generation with different format types."""
        formats = ['paragraph', 'sentences', 'list', 'numbered']
        
        for format_type in formats:
            result = self.generator.generate(
                pattern_type='lorem',
                length=5,
                format_type=format_type
            )
            
            assert isinstance(result, str)
            assert len(result) > 0
            
            if format_type == 'list':
                assert '-' in result
            elif format_type == 'numbered':
                assert '1.' in result
    
    def test_caching(self):
        """Test caching functionality."""
        # First generation
        result1 = self.generator.generate(
            pattern_type='lorem',
            length=10,
            format_type='paragraph'
        )
        
        stats_before = self.generator.get_stats()
        
        # Second generation with same parameters (should hit cache)
        result2 = self.generator.generate(
            pattern_type='lorem',
            length=10,
            format_type='paragraph'
        )
        
        stats_after = self.generator.get_stats()
        
        assert result1 == result2
        assert stats_after['cache_hits'] > stats_before['cache_hits']
    
    def test_input_validation(self):
        """Test input validation."""
        # Test invalid pattern type
        with pytest.raises(ValueError):
            self.generator.generate(pattern_type=123)
        
        # Test invalid length
        with pytest.raises(ValueError):
            self.generator.generate(length=-1)
        
        # Test invalid format type
        with pytest.raises(ValueError):
            self.generator.generate(format_type='invalid_format')
        
        # Test zero length
        with pytest.raises(ValueError):
            self.generator.generate(length=0)
    
    def test_template_generation(self):
        """Test template-based generation."""
        template = "Hello {name}, welcome to {company}!"
        variables = {"name": "John", "company": "HDGRACE"}
        
        result = self.generator.generate_with_template(template, variables)
        
        assert result == "Hello John, welcome to HDGRACE!"
    
    def test_template_missing_variable(self):
        """Test template generation with missing variables."""
        template = "Hello {name}, welcome to {company}!"
        variables = {"name": "John"}  # Missing 'company'
        
        with pytest.raises(ValueError, match="Missing template variable"):
            self.generator.generate_with_template(template, variables)
    
    def test_multiple_patterns_generation(self):
        """Test generating multiple patterns at once."""
        patterns = ['lorem', 'technical', 'business']
        result = self.generator.generate_multiple_patterns(patterns, 5)
        
        assert isinstance(result, dict)
        assert len(result) == len(patterns)
        
        for pattern in patterns:
            assert pattern in result
            assert isinstance(result[pattern], str)
            assert len(result[pattern]) > 0
    
    def test_text_complexity_analysis(self):
        """Test text complexity analysis."""
        text = "This is a test. It has multiple sentences! How complex is it?"
        result = self.generator.analyze_text_complexity(text)
        
        assert isinstance(result, dict)
        assert 'word_count' in result
        assert 'sentence_count' in result
        assert 'avg_word_length' in result
        assert 'avg_sentence_length' in result
        assert 'unique_word_ratio' in result
        assert 'complexity_score' in result
        
        assert result['word_count'] > 0
        assert result['sentence_count'] > 0
    
    def test_transformations(self):
        """Test text transformations."""
        original_text = "Hello World"
        
        # Test uppercase transformation
        result = self.generator.generate(
            pattern_type='lorem',
            length=2,
            transformation='uppercase'
        )
        
        assert result.isupper()
    
    def test_custom_pattern(self):
        """Test adding custom patterns."""
        custom_pattern = "Custom pattern with specific words"
        pattern_name = "custom_test"
        
        self.generator.add_custom_pattern(pattern_name, custom_pattern)
        
        assert pattern_name in self.generator.patterns
        assert self.generator.patterns[pattern_name] == custom_pattern
        
        # Test generating with custom pattern
        result = self.generator.generate(
            pattern_type=pattern_name,
            length=3,
            format_type='paragraph'
        )
        
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_invalid_custom_pattern(self):
        """Test adding invalid custom patterns."""
        # Test empty pattern name
        with pytest.raises(ValueError, match="Pattern name must be a non-empty string"):
            self.generator.add_custom_pattern("", "some pattern")
        
        # Test empty pattern text
        with pytest.raises(ValueError, match="Pattern text must be a non-empty string"):
            self.generator.add_custom_pattern("test", "")
    
    def test_available_options(self):
        """Test getting available options."""
        patterns = self.generator.get_available_patterns()
        formats = self.generator.get_available_formats()
        transformations = self.generator.get_available_transformations()
        
        assert isinstance(patterns, list)
        assert isinstance(formats, list)
        assert isinstance(transformations, list)
        
        assert 'lorem' in patterns
        assert 'paragraph' in formats
        assert 'uppercase' in transformations
    
    def test_statistics(self):
        """Test generation statistics."""
        # Generate some text to create stats
        self.generator.generate(pattern_type='lorem', length=5)
        self.generator.generate(pattern_type='technical', length=5)
        
        stats = self.generator.get_stats()
        
        assert isinstance(stats, dict)
        assert 'generated' in stats
        assert 'cache_hits' in stats
        assert 'cache_size' in stats
        assert 'cache_hit_rate' in stats
        
        assert stats['generated'] >= 2
    
    def test_cache_management(self):
        """Test cache management functionality."""
        # Generate some cached content
        self.generator.generate(pattern_type='lorem', length=5)
        
        stats_before = self.generator.get_stats()
        assert stats_before['cache_size'] > 0
        
        # Clear cache
        self.generator.clear_cache()
        
        stats_after = self.generator.get_stats()
        assert stats_after['cache_size'] == 0
    
    def test_context_manager(self):
        """Test using generator as context manager."""
        with TextGenerator(self.config) as generator:
            result = generator.generate(pattern_type='lorem', length=5)
            assert isinstance(result, str)
            assert len(result) > 0
    
    def test_large_generation(self):
        """Test generating large amounts of text."""
        # This should work but not exceed max_generation_length
        max_length = self.config.get("max_generation_length", 10000)
        
        result = self.generator.generate(
            pattern_type='lorem',
            length=max_length // 2,  # Use half of max to be safe
            format_type='paragraph'
        )
        
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_exceeding_max_length(self):
        """Test exceeding maximum generation length."""
        max_length = self.config.get("max_generation_length", 10000)
        
        with pytest.raises(ValueError, match="length exceeds maximum allowed"):
            self.generator.generate(
                pattern_type='lorem',
                length=max_length + 1,
                format_type='paragraph'
            )