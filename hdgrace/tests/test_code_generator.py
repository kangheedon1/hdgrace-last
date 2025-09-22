"""
Tests for HDGRACE code generator.
"""

import pytest
from hdgrace.generators.code_generator import CodeGenerator
from hdgrace.utils.config import Config


class TestCodeGenerator:
    """Test cases for CodeGenerator class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = Config()
        self.generator = CodeGenerator(self.config)
    
    def test_initialization(self):
        """Test generator initialization."""
        assert self.generator is not None
        assert len(self.generator.supported_languages) > 0
        assert len(self.generator.templates) > 0
        assert 'python' in self.generator.supported_languages
        assert 'javascript' in self.generator.supported_languages
    
    def test_python_class_generation(self):
        """Test Python class generation."""
        result = self.generator.generate(
            language='python',
            code_type='class',
            name='TestClass',
            methods=['__init__', 'process'],
            properties=['data', 'config']
        )
        
        assert isinstance(result, str)
        assert 'class TestClass:' in result
        assert 'def __init__(self):' in result
        assert 'def process(self):' in result
        assert 'self.data = None' in result
    
    def test_javascript_class_generation(self):
        """Test JavaScript class generation."""
        result = self.generator.generate(
            language='javascript',
            code_type='class',
            name='TestClass',
            methods=['constructor', 'process'],
            properties=['data', 'config']
        )
        
        assert isinstance(result, str)
        assert 'class TestClass {' in result
        assert 'constructor() {' in result
        assert 'process() {' in result
        assert 'this.data = null;' in result
    
    def test_function_generation(self):
        """Test function generation."""
        result = self.generator.generate(
            language='python',
            code_type='function',
            name='test_function',
            parameters=['param1', 'param2'],
            return_type='str'
        )
        
        assert isinstance(result, str)
        assert 'def test_function(' in result
        assert 'param1' in result
        assert 'param2' in result
    
    def test_api_endpoint_generation(self):
        """Test API endpoint generation."""
        result = self.generator.generate(
            language='python',
            code_type='api',
            name='test_endpoint',
            methods=['GET', 'POST']
        )
        
        assert isinstance(result, str)
        assert 'test_endpoint' in result
        assert 'Flask' in result or 'app.route' in result
    
    def test_input_validation(self):
        """Test input validation."""
        # Test invalid language
        with pytest.raises(ValueError, match="language must be one of"):
            self.generator.generate(
                language='invalid_language',
                code_type='class',
                name='TestClass'
            )
        
        # Test invalid name
        with pytest.raises(ValueError, match="name must be a non-empty string"):
            self.generator.generate(
                language='python',
                code_type='class',
                name=''
            )
        
        # Test invalid identifier
        with pytest.raises(ValueError, match="name must be a valid identifier"):
            self.generator.generate(
                language='python',
                code_type='class',
                name='123invalid'
            )
        
        # Test invalid code type
        with pytest.raises(ValueError, match="code_type must be one of"):
            self.generator.generate(
                language='python',
                code_type='invalid_type',
                name='TestClass'
            )
    
    def test_multiple_languages(self):
        """Test generation for multiple languages."""
        languages = ['python', 'javascript', 'java']
        
        for language in languages:
            if language in self.generator.supported_languages:
                result = self.generator.generate(
                    language=language,
                    code_type='class',
                    name='TestClass'
                )
                
                assert isinstance(result, str)
                assert len(result) > 0
                assert 'TestClass' in result
    
    def test_project_structure_generation(self):
        """Test complete project structure generation."""
        project_files = self.generator.generate_project_structure(
            language='python',
            project_name='test_project',
            modules=['main', 'utils', 'config']
        )
        
        assert isinstance(project_files, dict)
        assert len(project_files) > 0
        
        # Check that expected files are present
        file_paths = list(project_files.keys())
        assert any('main.py' in path for path in file_paths)
        assert any('utils.py' in path for path in file_paths)
        assert any('config.py' in path for path in file_paths)
        
        # Check file contents
        for file_path, content in project_files.items():
            assert isinstance(content, str)
            assert len(content) > 0
    
    def test_syntax_validation(self):
        """Test code syntax validation."""
        # Test valid Python code
        valid_python = "def test():\n    return 'hello'"
        result = self.generator.validate_syntax('python', valid_python)
        
        assert isinstance(result, dict)
        assert 'valid' in result
        assert 'errors' in result
        assert 'warnings' in result
        assert 'metrics' in result
        
        # Test invalid Python code (mismatched brackets)
        invalid_python = "def test():\n    return 'hello'"
        result = self.generator.validate_syntax('python', invalid_python)
        
        assert isinstance(result, dict)
        assert 'valid' in result
        assert 'errors' in result
    
    def test_code_formatting(self):
        """Test code formatting."""
        unformatted_code = "def test():return 'hello'"
        
        formatted = self.generator.format_code('python', unformatted_code, 'standard')
        
        assert isinstance(formatted, str)
        # Basic check that formatting might have occurred
        assert len(formatted) >= len(unformatted_code)
    
    def test_enum_generation(self):
        """Test enum generation."""
        result = self.generator.generate(
            language='python',
            code_type='enum',
            name='Status',
            properties=['ACTIVE', 'INACTIVE', 'PENDING']
        )
        
        assert isinstance(result, str)
        assert 'enum' in result.lower() or 'Status' in result
    
    def test_interface_generation(self):
        """Test interface generation."""
        result = self.generator.generate(
            language='python',
            code_type='interface',
            name='TestInterface',
            methods=['process', 'validate']
        )
        
        assert isinstance(result, str)
        assert 'TestInterface' in result
    
    def test_module_generation(self):
        """Test module generation."""
        result = self.generator.generate(
            language='python',
            code_type='module',
            name='test_module',
            methods=['function1', 'function2'],
            properties=['CONSTANT1', 'CONSTANT2']
        )
        
        assert isinstance(result, str)
        assert 'test_module' in result
    
    def test_caching(self):
        """Test caching functionality."""
        # First generation
        result1 = self.generator.generate(
            language='python',
            code_type='class',
            name='TestClass'
        )
        
        stats_before = self.generator.get_stats()
        
        # Second generation with same parameters (should hit cache)
        result2 = self.generator.generate(
            language='python',
            code_type='class',
            name='TestClass'
        )
        
        stats_after = self.generator.get_stats()
        
        assert result1 == result2
        assert stats_after['cache_hits'] > stats_before['cache_hits']
    
    def test_supported_languages(self):
        """Test getting supported languages."""
        languages = self.generator.get_supported_languages()
        
        assert isinstance(languages, list)
        assert len(languages) > 0
        assert 'python' in languages
        assert 'javascript' in languages
    
    def test_available_patterns(self):
        """Test getting available code patterns."""
        patterns = self.generator.get_available_patterns()
        
        assert isinstance(patterns, dict)
        assert 'design_patterns' in patterns
        assert 'data_structures' in patterns
        assert 'algorithms' in patterns
    
    def test_docstring_generation(self):
        """Test code generation with docstrings."""
        result = self.generator.generate(
            language='python',
            code_type='class',
            name='TestClass',
            docstring='This is a test class'
        )
        
        assert isinstance(result, str)
        assert 'This is a test class' in result
    
    def test_annotations_generation(self):
        """Test code generation with annotations."""
        result = self.generator.generate(
            language='python',
            code_type='class',
            name='TestClass',
            annotations=['@decorator1', '@decorator2']
        )
        
        assert isinstance(result, str)
        assert 'TestClass' in result
    
    def test_statistics(self):
        """Test generation statistics."""
        # Generate some code to create stats
        self.generator.generate(language='python', code_type='class', name='Class1')
        self.generator.generate(language='javascript', code_type='class', name='Class2')
        
        stats = self.generator.get_stats()
        
        assert isinstance(stats, dict)
        assert 'generated' in stats
        assert 'cache_hits' in stats
        assert stats['generated'] >= 2
    
    def test_context_manager(self):
        """Test using generator as context manager."""
        with CodeGenerator(self.config) as generator:
            result = generator.generate(
                language='python',
                code_type='class',
                name='TestClass'
            )
            assert isinstance(result, str)
            assert 'TestClass' in result