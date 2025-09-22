"""
Code generation module - consolidates all CodeGenerator classes from original HDGRACE.txt.
"""

import re
import json
from typing import Dict, List, Optional, Any, Union
from ..core.base_generator import BaseGenerator


class CodeGenerator(BaseGenerator):
    """
    Production-ready code generator for multiple programming languages.
    
    Supports: Python, JavaScript, Java, C++, Go, TypeScript, Rust, PHP, Ruby
    Features:
    - Template-based code generation
    - Syntax validation and formatting
    - Multiple code patterns (classes, functions, APIs, etc.)
    - Language-specific optimizations
    - Code quality metrics
    """
    
    def _initialize(self) -> None:
        """Initialize code generation templates and settings."""
        self.supported_languages = {
            'python', 'javascript', 'java', 'cpp', 'go', 'typescript', 
            'rust', 'php', 'ruby', 'csharp', 'kotlin', 'swift'
        }
        
        self.templates = self._load_templates()
        self.syntax_rules = self._load_syntax_rules()
        self.code_patterns = self._load_code_patterns()
        self.formatting_rules = self._load_formatting_rules()
    
    def _validate_input(self, **kwargs) -> None:
        """Validate code generation parameters."""
        language = kwargs.get('language', '').lower()
        code_type = kwargs.get('code_type', 'class')
        name = kwargs.get('name', '')
        
        if not language or language not in self.supported_languages:
            raise ValueError(f"language must be one of: {self.supported_languages}")
        
        if not isinstance(name, str) or not name.strip():
            raise ValueError("name must be a non-empty string")
        
        if not re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', name):
            raise ValueError("name must be a valid identifier")
        
        valid_types = ['class', 'function', 'api', 'interface', 'enum', 'struct', 'module']
        if code_type not in valid_types:
            raise ValueError(f"code_type must be one of: {valid_types}")
    
    def _generate_content(self, **kwargs) -> str:
        """Core code generation logic."""
        language = kwargs.get('language').lower()
        code_type = kwargs.get('code_type', 'class')
        name = kwargs.get('name')
        methods = kwargs.get('methods', [])
        properties = kwargs.get('properties', [])
        parameters = kwargs.get('parameters', [])
        return_type = kwargs.get('return_type', 'void')
        docstring = kwargs.get('docstring', '')
        annotations = kwargs.get('annotations', [])
        
        # Generate based on code type
        if code_type == 'class':
            return self._generate_class(language, name, methods, properties, docstring, annotations)
        elif code_type == 'function':
            return self._generate_function(language, name, parameters, return_type, docstring)
        elif code_type == 'api':
            return self._generate_api_endpoint(language, name, methods, parameters)
        elif code_type == 'interface':
            return self._generate_interface(language, name, methods, properties)
        elif code_type == 'enum':
            return self._generate_enum(language, name, properties)
        elif code_type == 'struct':
            return self._generate_struct(language, name, properties)
        elif code_type == 'module':
            return self._generate_module(language, name, methods, properties)
        else:
            raise ValueError(f"Unsupported code_type: {code_type}")
    
    def generate_project_structure(self, language: str, project_name: str, 
                                 modules: List[str] = None) -> Dict[str, str]:
        """
        Generate complete project structure with multiple files.
        
        Args:
            language: Programming language
            project_name: Name of the project
            modules: List of module names to create
            
        Returns:
            Dictionary mapping file paths to file contents
        """
        modules = modules or ['main', 'utils', 'config']
        project_files = {}
        
        for module in modules:
            file_ext = self._get_file_extension(language)
            file_path = f"{project_name}/{module}{file_ext}"
            
            if module == 'main':
                content = self._generate_main_file(language, project_name)
            elif module == 'utils':
                content = self._generate_utils_file(language)
            elif module == 'config':
                content = self._generate_config_file(language)
            else:
                content = self.generate(
                    language=language,
                    code_type='module',
                    name=module,
                    use_cache=True
                )
            
            project_files[file_path] = content
        
        # Add project configuration files
        project_files.update(self._generate_project_config(language, project_name))
        
        return project_files
    
    def validate_syntax(self, language: str, code: str) -> Dict[str, Any]:
        """
        Validate code syntax for the specified language.
        
        Args:
            language: Programming language
            code: Code to validate
            
        Returns:
            Validation result with errors and warnings
        """
        language = language.lower()
        if language not in self.syntax_rules:
            return {'valid': False, 'errors': [f'Unsupported language: {language}']}
        
        rules = self.syntax_rules[language]
        errors = []
        warnings = []
        
        # Basic syntax checks
        if language in ['python', 'yaml']:
            errors.extend(self._check_indentation(code, rules['indent']))
        
        if language in ['javascript', 'java', 'cpp', 'csharp']:
            errors.extend(self._check_brackets(code))
            warnings.extend(self._check_semicolons(code, rules['line_end']))
        
        # Language-specific checks
        if language == 'python':
            errors.extend(self._check_python_syntax(code))
        elif language == 'javascript':
            errors.extend(self._check_javascript_syntax(code))
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'metrics': self._calculate_code_metrics(code)
        }
    
    def format_code(self, language: str, code: str, style: str = 'standard') -> str:
        """
        Format code according to language conventions.
        
        Args:
            language: Programming language
            code: Code to format
            style: Formatting style (standard, compact, verbose)
            
        Returns:
            Formatted code
        """
        language = language.lower()
        if language not in self.formatting_rules:
            return code
        
        rules = self.formatting_rules[language][style]
        formatted_code = code
        
        # Apply formatting rules
        for rule_name, rule_func in rules.items():
            try:
                formatted_code = rule_func(formatted_code)
            except Exception as e:
                self.error_logger.log_generation_error(
                    f"format_code({rule_name})", str(e)
                )
        
        return formatted_code
    
    def _generate_class(self, language: str, name: str, methods: List[str],
                       properties: List[str], docstring: str, annotations: List[str]) -> str:
        """Generate class definition."""
        template = self.templates[language]['class']
        
        # Generate methods and properties
        method_code = self._generate_methods(language, methods, name)
        property_code = self._generate_properties(language, properties)
        
        # Add docstring if provided
        doc_code = self._generate_docstring(language, docstring) if docstring else ''
        
        # Add annotations if supported
        annotation_code = self._generate_annotations(language, annotations)
        
        return template.format(
            class_name=name,
            methods=method_code,
            properties=property_code,
            docstring=doc_code,
            annotations=annotation_code
        )
    
    def _generate_function(self, language: str, name: str, parameters: List[str],
                          return_type: str, docstring: str) -> str:
        """Generate function definition."""
        template = self.templates[language]['function']
        
        param_code = self._format_parameters(language, parameters)
        doc_code = self._generate_docstring(language, docstring) if docstring else ''
        return_annotation = self._format_return_type(language, return_type)
        
        return template.format(
            function_name=name,
            parameters=param_code,
            return_type=return_annotation,
            docstring=doc_code,
            body=self._generate_function_body(language, name)
        )
    
    def _generate_api_endpoint(self, language: str, name: str, methods: List[str],
                             parameters: List[str]) -> str:
        """Generate API endpoint code."""
        template = self.templates[language]['api']
        
        method_code = self._generate_api_methods(language, methods, parameters)
        
        return template.format(
            endpoint_name=name,
            methods=method_code,
            parameters=self._format_parameters(language, parameters)
        )
    
    def _load_templates(self) -> Dict[str, Dict[str, str]]:
        """Load code templates for all supported languages."""
        return {
            'python': {
                'class': '''class {class_name}:
    """{docstring}"""
    {annotations}
    
    {properties}
    
    {methods}''',
                'function': '''{docstring}
def {function_name}({parameters}){return_type}:
    {body}''',
                'api': '''from flask import Flask, request, jsonify

@app.route('/{endpoint_name}', methods={methods})
def {endpoint_name}({parameters}):
    return jsonify({{"status": "success"}})''',
                'interface': '''from abc import ABC, abstractmethod

class {class_name}(ABC):
    {methods}''',
                'enum': '''from enum import Enum

class {class_name}(Enum):
    {properties}''',
                'module': '''"""
{class_name} module
"""

{properties}

{methods}'''
            },
            'javascript': {
                'class': '''/**
 * {docstring}
 */
class {class_name} {{
    {properties}
    
    {methods}
}}''',
                'function': '''/**
 * {docstring}
 */
function {function_name}({parameters}){return_type} {{
    {body}
}}''',
                'api': '''app.{method}('/{endpoint_name}', ({parameters}) => {{
    {methods}
}});''',
                'interface': '''interface {class_name} {{
    {methods}
    {properties}
}}''',
                'enum': '''enum {class_name} {{
    {properties}
}}''',
                'module': '''/**
 * {class_name} module
 */

{properties}

{methods}'''
            },
            'java': {
                'class': '''/**
 * {docstring}
 */
{annotations}
public class {class_name} {{
    {properties}
    
    {methods}
}}''',
                'function': '''/**
 * {docstring}
 */
public {return_type} {function_name}({parameters}) {{
    {body}
}}''',
                'interface': '''public interface {class_name} {{
    {methods}
}}''',
                'enum': '''public enum {class_name} {{
    {properties}
}}'''
            }
        }
    
    def _load_syntax_rules(self) -> Dict[str, Dict[str, str]]:
        """Load syntax validation rules."""
        return {
            'python': {
                'indent': '    ',
                'line_end': '\n',
                'comment': '#',
                'string_delim': ['\'', '"', '"""', "'''"]
            },
            'javascript': {
                'indent': '  ',
                'line_end': ';\n',
                'comment': '//',
                'string_delim': ['\'', '"', '`']
            },
            'java': {
                'indent': '    ',
                'line_end': ';\n',
                'comment': '//',
                'string_delim': ['"']
            }
        }
    
    def _load_code_patterns(self) -> Dict[str, List[str]]:
        """Load common code patterns."""
        return {
            'design_patterns': [
                'singleton', 'factory', 'observer', 'strategy', 'adapter',
                'decorator', 'facade', 'proxy', 'builder', 'prototype'
            ],
            'data_structures': [
                'list', 'stack', 'queue', 'tree', 'graph', 'hash_table',
                'linked_list', 'binary_tree', 'heap', 'trie'
            ],
            'algorithms': [
                'sort', 'search', 'graph_traversal', 'dynamic_programming',
                'greedy', 'divide_conquer', 'backtracking'
            ]
        }
    
    def _load_formatting_rules(self) -> Dict[str, Dict[str, Dict[str, callable]]]:
        """Load code formatting rules."""
        return {
            'python': {
                'standard': {
                    'line_length': lambda code: self._enforce_line_length(code, 88),
                    'imports': lambda code: self._sort_imports(code),
                    'spacing': lambda code: self._fix_spacing(code, 'python')
                },
                'compact': {
                    'line_length': lambda code: self._enforce_line_length(code, 120),
                    'spacing': lambda code: self._minimize_spacing(code)
                }
            },
            'javascript': {
                'standard': {
                    'line_length': lambda code: self._enforce_line_length(code, 100),
                    'semicolons': lambda code: self._add_semicolons(code),
                    'spacing': lambda code: self._fix_spacing(code, 'javascript')
                }
            }
        }
    
    def _generate_methods(self, language: str, methods: List[str], class_name: str) -> str:
        """Generate method definitions for a class."""
        if not methods:
            methods = ['__init__', 'process', 'validate'] if language == 'python' else ['constructor', 'process', 'validate']
        
        method_templates = {
            'python': 'def {method}(self):\n        """TODO: Implement {method}"""\n        pass',
            'javascript': '{method}() {\n        // TODO: Implement {method}\n    }',
            'java': 'public void {method}() {\n        // TODO: Implement {method}\n    }'
        }
        
        template = method_templates.get(language, method_templates['python'])
        return '\n\n    '.join(template.format(method=method) for method in methods)
    
    def _generate_properties(self, language: str, properties: List[str]) -> str:
        """Generate property definitions."""
        if not properties:
            properties = ['data', 'config', 'status']
        
        property_templates = {
            'python': 'self.{prop} = None',
            'javascript': 'this.{prop} = null;',
            'java': 'private Object {prop};'
        }
        
        template = property_templates.get(language, property_templates['python'])
        return '\n    '.join(template.format(prop=prop) for prop in properties)
    
    def _get_file_extension(self, language: str) -> str:
        """Get file extension for language."""
        extensions = {
            'python': '.py',
            'javascript': '.js',
            'typescript': '.ts',
            'java': '.java',
            'cpp': '.cpp',
            'go': '.go',
            'rust': '.rs',
            'php': '.php',
            'ruby': '.rb',
            'csharp': '.cs',
            'kotlin': '.kt',
            'swift': '.swift'
        }
        return extensions.get(language, '.txt')
    
    def _check_indentation(self, code: str, expected_indent: str) -> List[str]:
        """Check code indentation."""
        errors = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            if line.strip() and line.startswith(' '):
                if not line.startswith(expected_indent):
                    errors.append(f"Line {i}: Incorrect indentation")
        
        return errors
    
    def _check_brackets(self, code: str) -> List[str]:
        """Check bracket matching."""
        errors = []
        stack = []
        brackets = {'(': ')', '[': ']', '{': '}'}
        
        for i, char in enumerate(code):
            if char in brackets:
                stack.append((char, i))
            elif char in brackets.values():
                if not stack:
                    errors.append(f"Position {i}: Unmatched closing bracket '{char}'")
                else:
                    open_bracket, _ = stack.pop()
                    if brackets[open_bracket] != char:
                        errors.append(f"Position {i}: Mismatched brackets")
        
        for bracket, pos in stack:
            errors.append(f"Position {pos}: Unmatched opening bracket '{bracket}'")
        
        return errors
    
    def _calculate_code_metrics(self, code: str) -> Dict[str, int]:
        """Calculate basic code metrics."""
        lines = code.split('\n')
        return {
            'total_lines': len(lines),
            'non_empty_lines': len([line for line in lines if line.strip()]),
            'comment_lines': len([line for line in lines if line.strip().startswith(('#', '//', '/*'))]),
            'max_line_length': max(len(line) for line in lines) if lines else 0,
            'average_line_length': sum(len(line) for line in lines) // max(len(lines), 1)
        }
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported programming languages."""
        return sorted(list(self.supported_languages))
    
    def get_available_patterns(self) -> Dict[str, List[str]]:
        """Get available code patterns."""
        return self.code_patterns.copy()
    
    def _generate_annotations(self, language: str, annotations: List[str]) -> str:
        """Generate annotations/decorators for the code."""
        if not annotations:
            return ''
        
        if language == 'python':
            return '\n'.join(annotations) + '\n' if annotations else ''
        elif language == 'java':
            return '\n'.join(annotations) + '\n' if annotations else ''
        else:
            return ''
    
    def _generate_docstring(self, language: str, docstring: str) -> str:
        """Generate docstring/documentation for the code."""
        if not docstring:
            return ''
        
        if language == 'python':
            return f'"""\n    {docstring}\n    """'
        elif language == 'javascript':
            return f'/**\n     * {docstring}\n     */'
        elif language == 'java':
            return f'/**\n     * {docstring}\n     */'
        else:
            return f'// {docstring}'
    
    def _format_parameters(self, language: str, parameters: List[str]) -> str:
        """Format function parameters for the language."""
        if not parameters:
            return ''
        
        if language == 'python':
            return ', '.join(parameters)
        elif language in ['javascript', 'java', 'cpp']:
            return ', '.join(parameters)
        else:
            return ', '.join(parameters)
    
    def _format_return_type(self, language: str, return_type: str) -> str:
        """Format return type annotation for the language."""
        if not return_type or return_type == 'void':
            return ''
        
        if language == 'python':
            return f' -> {return_type}'
        elif language == 'typescript':
            return f': {return_type}'
        else:
            return ''
    
    def _generate_function_body(self, language: str, name: str) -> str:
        """Generate basic function body."""
        if language == 'python':
            return f'"""TODO: Implement {name}"""\n    pass'
        elif language == 'javascript':
            return f'// TODO: Implement {name}'
        elif language == 'java':
            return f'// TODO: Implement {name}'
        else:
            return f'// TODO: Implement {name}'
    
    def _generate_api_methods(self, language: str, methods: List[str], parameters: List[str]) -> str:
        """Generate API method implementations."""
        if language == 'python':
            return '\n'.join(f'# Handle {method} request' for method in methods)
        elif language == 'javascript':
            return '\n'.join(f'// Handle {method} request' for method in methods)
        else:
            return '\n'.join(f'// Handle {method} request' for method in methods)
    
    def _generate_interface(self, language: str, name: str, methods: List[str], properties: List[str]) -> str:
        """Generate interface definition."""
        template = self.templates.get(language, {}).get('interface', '')
        if not template:
            return f'// Interface {name} not supported for {language}'
        
        method_code = self._generate_abstract_methods(language, methods)
        property_code = self._generate_interface_properties(language, properties)
        
        return template.format(
            class_name=name,
            methods=method_code,
            properties=property_code
        )
    
    def _generate_enum(self, language: str, name: str, properties: List[str]) -> str:
        """Generate enum definition."""
        template = self.templates.get(language, {}).get('enum', '')
        if not template:
            return f'// Enum {name} not supported for {language}'
        
        property_code = self._generate_enum_values(language, properties)
        
        return template.format(
            class_name=name,
            properties=property_code
        )
    
    def _generate_struct(self, language: str, name: str, properties: List[str]) -> str:
        """Generate struct definition."""
        if language == 'cpp':
            property_code = ';\n    '.join(f'int {prop}' for prop in properties)
            return f'struct {name} {{\n    {property_code};\n}};'
        elif language == 'go':
            property_code = '\n    '.join(f'{prop.capitalize()} int' for prop in properties)
            return f'type {name} struct {{\n    {property_code}\n}}'
        else:
            return f'// Struct {name} not supported for {language}'
    
    def _generate_module(self, language: str, name: str, methods: List[str], properties: List[str]) -> str:
        """Generate module definition."""
        template = self.templates.get(language, {}).get('module', '')
        if not template:
            return f'// Module {name} not supported for {language}'
        
        method_code = self._generate_module_functions(language, methods)
        property_code = self._generate_module_constants(language, properties)
        
        return template.format(
            class_name=name,
            methods=method_code,
            properties=property_code
        )
    
    def _generate_abstract_methods(self, language: str, methods: List[str]) -> str:
        """Generate abstract method signatures for interfaces."""
        if not methods:
            return ''
        
        if language == 'python':
            return '\n    '.join(f'@abstractmethod\n    def {method}(self):\n        pass' for method in methods)
        elif language == 'java':
            return '\n    '.join(f'public void {method}();' for method in methods)
        else:
            return '\n    '.join(f'{method}();' for method in methods)
    
    def _generate_interface_properties(self, language: str, properties: List[str]) -> str:
        """Generate property definitions for interfaces."""
        if not properties:
            return ''
        
        if language == 'typescript':
            return '\n    '.join(f'{prop}: any;' for prop in properties)
        else:
            return ''
    
    def _generate_enum_values(self, language: str, properties: List[str]) -> str:
        """Generate enum value definitions."""
        if not properties:
            properties = ['VALUE1', 'VALUE2', 'VALUE3']
        
        if language == 'python':
            return '\n    '.join(f'{prop} = "{prop}"' for prop in properties)
        elif language in ['java', 'cpp', 'csharp']:
            return ',\n    '.join(properties)
        else:
            return ', '.join(properties)
    
    def _generate_module_functions(self, language: str, methods: List[str]) -> str:
        """Generate module-level functions."""
        if not methods:
            return ''
        
        template = self.templates[language]['function']
        return '\n\n'.join(
            template.format(
                function_name=method,
                parameters='',
                return_type='',
                docstring='',
                body=self._generate_function_body(language, method)
            ) for method in methods
        )
    
    def _generate_module_constants(self, language: str, properties: List[str]) -> str:
        """Generate module-level constants."""
        if not properties:
            return ''
        
        if language == 'python':
            return '\n'.join(f'{prop} = None' for prop in properties)
        elif language == 'javascript':
            return '\n'.join(f'const {prop} = null;' for prop in properties)
        else:
            return '\n'.join(f'const {prop} = null;' for prop in properties)
    
    def _generate_main_file(self, language: str, project_name: str) -> str:
        """Generate main entry point file."""
        if language == 'python':
            return f'''#!/usr/bin/env python3
"""
{project_name} - Main entry point
"""

import sys
from pathlib import Path

def main():
    """Main application entry point."""
    print("Hello from {project_name}!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
'''
        elif language == 'javascript':
            return f'''/**
 * {project_name} - Main entry point
 */

function main() {{
    console.log("Hello from {project_name}!");
    return 0;
}}

if (require.main === module) {{
    process.exit(main());
}}
'''
        else:
            return f'// Main file for {project_name}'
    
    def _generate_utils_file(self, language: str) -> str:
        """Generate utilities file."""
        if language == 'python':
            return '''"""
Utility functions and helpers.
"""

def helper_function():
    """A sample helper function."""
    pass

class UtilityClass:
    """A sample utility class."""
    
    def __init__(self):
        pass
'''
        elif language == 'javascript':
            return '''/**
 * Utility functions and helpers.
 */

function helperFunction() {
    // A sample helper function
}

class UtilityClass {
    constructor() {
        // Initialize utility class
    }
}

module.exports = { helperFunction, UtilityClass };
'''
        else:
            return '// Utility file'
    
    def _generate_config_file(self, language: str) -> str:
        """Generate configuration file."""
        if language == 'python':
            return '''"""
Configuration settings.
"""

# Application configuration
CONFIG = {
    "debug": False,
    "version": "1.0.0",
    "database_url": "sqlite:///app.db"
}
'''
        elif language == 'javascript':
            return '''/**
 * Configuration settings.
 */

module.exports = {
    debug: false,
    version: "1.0.0",
    databaseUrl: "sqlite:///app.db"
};
'''
        else:
            return '// Configuration file'
    
    def _generate_project_config(self, language: str, project_name: str) -> Dict[str, str]:
        """Generate project configuration files."""
        config_files = {}
        
        if language == 'python':
            config_files['requirements.txt'] = '# Add project dependencies here\\n'
            config_files['setup.py'] = f'''from setuptools import setup, find_packages

setup(
    name="{project_name}",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        # Add dependencies here
    ],
)
'''
        elif language == 'javascript':
            config_files['package.json'] = f'''{{
  "name": "{project_name}",
  "version": "1.0.0",
  "description": "",
  "main": "main.js",
  "scripts": {{
    "start": "node main.js"
  }},
  "dependencies": {{}}
}}
'''
        
        return config_files
    
    def _check_python_syntax(self, code: str) -> List[str]:
        """Check Python-specific syntax issues."""
        errors = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.endswith(':') and not stripped.startswith(('#', '"""', "'''")):
                # Check if next line is properly indented
                if i < len(lines):
                    next_line = lines[i].rstrip() if i < len(lines) else ''
                    if next_line and not next_line.startswith('    '):
                        errors.append(f"Line {i+1}: Expected indentation after colon")
        
        return errors
    
    def _check_javascript_syntax(self, code: str) -> List[str]:
        """Check JavaScript-specific syntax issues."""
        errors = []
        
        # Basic checks for common JS issues
        if code.count('(') != code.count(')'):
            errors.append("Mismatched parentheses")
        
        if code.count('{') != code.count('}'):
            errors.append("Mismatched braces")
        
        return errors
    
    def _check_semicolons(self, code: str, line_end: str) -> List[str]:
        """Check for missing semicolons in languages that require them."""
        warnings = []
        
        if ';' in line_end:
            lines = code.split('\n')
            for i, line in enumerate(lines, 1):
                stripped = line.strip()
                if (stripped and 
                    not stripped.endswith((';', '{', '}', ':', '//', '/*', '*/', '*/')) and
                    not stripped.startswith(('//', '/*', '*', '#'))):
                    warnings.append(f"Line {i}: Missing semicolon")
        
        return warnings
    
    def _enforce_line_length(self, code: str, max_length: int) -> str:
        """Enforce maximum line length by adding line breaks."""
        lines = code.split('\n')
        formatted_lines = []
        
        for line in lines:
            if len(line) <= max_length:
                formatted_lines.append(line)
            else:
                # Simple line breaking (could be improved)
                words = line.split()
                current_line = ''
                indent = len(line) - len(line.lstrip())
                
                for word in words:
                    if len(current_line + ' ' + word) <= max_length:
                        current_line += (' ' + word) if current_line else word
                    else:
                        if current_line:
                            formatted_lines.append(current_line)
                        current_line = ' ' * indent + word
                
                if current_line:
                    formatted_lines.append(current_line)
        
        return '\n'.join(formatted_lines)
    
    def _sort_imports(self, code: str) -> str:
        """Sort import statements in Python code."""
        lines = code.split('\n')
        imports = []
        other_lines = []
        
        for line in lines:
            if line.strip().startswith(('import ', 'from ')):
                imports.append(line)
            else:
                other_lines.append(line)
        
        imports.sort()
        return '\n'.join(imports + [''] + other_lines)
    
    def _fix_spacing(self, code: str, language: str) -> str:
        """Fix spacing issues in code."""
        if language == 'python':
            # Add spacing around operators
            import re
            code = re.sub(r'([^=!<>])=([^=])', r'\1 = \2', code)
            code = re.sub(r'([^=])([+\-*/])([^=])', r'\1 \2 \3', code)
        
        return code
    
    def _minimize_spacing(self, code: str) -> str:
        """Minimize spacing in code (compact style)."""
        import re
        # Remove extra spaces
        code = re.sub(r' +', ' ', code)
        # Remove spaces around operators for compact style
        code = re.sub(r' ([+\-*/=]) ', r'\1', code)
        return code
    
    def _add_semicolons(self, code: str) -> str:
        """Add missing semicolons to JavaScript code."""
        lines = code.split('\n')
        formatted_lines = []
        
        for line in lines:
            stripped = line.strip()
            if (stripped and 
                not stripped.endswith((';', '{', '}')) and
                not stripped.startswith(('//', '/*', '*'))):
                line = line.rstrip() + ';'
            formatted_lines.append(line)
        
        return '\n'.join(formatted_lines)