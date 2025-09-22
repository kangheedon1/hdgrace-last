"""
Tests for HDGRACE data generator.
"""

import pytest
import json
from hdgrace.generators.data_generator import DataGenerator
from hdgrace.utils.config import Config


class TestDataGenerator:
    """Test cases for DataGenerator class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = Config()
        self.generator = DataGenerator(self.config)
    
    def test_initialization(self):
        """Test generator initialization."""
        assert self.generator is not None
        assert len(self.generator.supported_formats) > 0
        assert len(self.generator.generators) > 0
        assert 'json' in self.generator.supported_formats
        assert 'user' in self.generator.generators
    
    def test_user_data_generation(self):
        """Test user data generation."""
        result = self.generator.generate(
            operation='generate',
            data_type='user',
            count=5,
            output_format='json'
        )
        
        assert isinstance(result, str)
        data = json.loads(result)
        assert isinstance(data, list)
        assert len(data) == 5
        
        # Check user data structure
        user = data[0]
        assert 'id' in user
        assert 'first_name' in user
        assert 'last_name' in user
        assert 'email' in user
        assert 'age' in user
    
    def test_product_data_generation(self):
        """Test product data generation."""
        result = self.generator.generate(
            operation='generate',
            data_type='product',
            count=3,
            output_format='json'
        )
        
        data = json.loads(result)
        assert len(data) == 3
        
        product = data[0]
        assert 'id' in product
        assert 'name' in product
        assert 'category' in product
        assert 'price' in product
    
    def test_transaction_data_generation(self):
        """Test transaction data generation."""
        result = self.generator.generate(
            operation='generate',
            data_type='transaction',
            count=2,
            output_format='json'
        )
        
        data = json.loads(result)
        assert len(data) == 2
        
        transaction = data[0]
        assert 'id' in transaction
        assert 'amount' in transaction
        assert 'currency' in transaction
        assert 'status' in transaction
    
    def test_different_output_formats(self):
        """Test generation with different output formats."""
        formats = ['json', 'csv', 'xml']
        
        for output_format in formats:
            result = self.generator.generate(
                operation='generate',
                data_type='user',
                count=2,
                output_format=output_format
            )
            
            assert isinstance(result, str)
            assert len(result) > 0
            
            if output_format == 'csv':
                assert ',' in result  # CSV should have commas
            elif output_format == 'xml':
                assert '<' in result and '>' in result  # XML should have tags
    
    def test_synthetic_dataset_generation(self):
        """Test synthetic dataset generation with schema."""
        schema = {
            'name': {'type': 'string', 'params': {'length': 10}},
            'age': {'type': 'integer', 'params': {'min': 18, 'max': 80}},
            'score': {'type': 'float', 'params': {'min': 0.0, 'max': 100.0}}
        }
        
        dataset = self.generator.generate_synthetic_dataset(schema, 5)
        
        assert isinstance(dataset, list)
        assert len(dataset) == 5
        
        record = dataset[0]
        assert 'name' in record
        assert 'age' in record
        assert 'score' in record
    
    def test_data_filtering(self):
        """Test data filtering functionality."""
        test_data = [
            {'name': 'John', 'age': 25},
            {'name': 'Jane', 'age': 30},
            {'name': 'Bob', 'age': 20}
        ]
        
        result = self.generator.generate(
            operation='process',
            data=test_data,
            processor='filter',
            processor_params={'condition': lambda x: x['age'] > 22}
        )
        
        assert len(result) == 2  # Should filter out Bob (age 20)
        assert all(person['age'] > 22 for person in result)
    
    def test_data_mapping(self):
        """Test data mapping functionality."""
        test_data = [
            {'name': 'John', 'age': 25},
            {'name': 'Jane', 'age': 30}
        ]
        
        result = self.generator.generate(
            operation='process',
            data=test_data,
            processor='map',
            processor_params={'transform': lambda x: {**x, 'age_group': 'adult'}}
        )
        
        assert len(result) == 2
        assert all('age_group' in person and person['age_group'] == 'adult' for person in result)
    
    def test_data_aggregation(self):
        """Test data aggregation functionality."""
        test_data = [
            {'category': 'A', 'value': 10},
            {'category': 'A', 'value': 20},
            {'category': 'B', 'value': 15},
            {'category': 'B', 'value': 25}
        ]
        
        result = self.generator.generate(
            operation='process',
            data=test_data,
            processor='aggregate',
            processor_params={
                'group_by': ['category'],
                'aggregations': {'value': 'sum'}
            }
        )
        
        assert len(result) == 2  # Two categories
        
        # Find category A and B results
        cat_a = next((item for item in result if item['category'] == 'A'), None)
        cat_b = next((item for item in result if item['category'] == 'B'), None)
        
        assert cat_a is not None
        assert cat_b is not None
        assert cat_a['value_sum'] == 30  # 10 + 20
        assert cat_b['value_sum'] == 40  # 15 + 25
    
    def test_format_conversion(self):
        """Test format conversion functionality."""
        test_data = [{'name': 'John', 'age': 25}]
        
        # Convert to JSON string first
        json_data = json.dumps(test_data)
        
        result = self.generator.generate(
            operation='convert',
            data=json_data,
            input_format='json',
            output_format='csv'
        )
        
        assert isinstance(result, str)
        assert 'name,age' in result  # CSV header
        assert 'John,25' in result   # CSV data
    
    def test_data_validation(self):
        """Test data validation functionality."""
        test_data = [
            {'name': 'John', 'age': 25, 'email': 'john@example.com'},
            {'name': 'Jane', 'age': None, 'email': 'invalid-email'}
        ]
        
        schema = {
            'name': {'type': 'string', 'required': True},
            'age': {'type': 'integer', 'required': True},
            'email': {'type': 'string', 'format': 'email'}
        }
        
        result = self.generator.generate(
            operation='validate',
            data=test_data,
            schema=schema
        )
        
        assert isinstance(result, dict)
        assert 'valid' in result
        assert 'errors' in result
        assert 'metrics' in result
    
    def test_input_validation(self):
        """Test input parameter validation."""
        # Test invalid operation
        with pytest.raises(ValueError, match="Unsupported operation"):
            self.generator.generate(operation='invalid_operation')
        
        # Test invalid data type
        with pytest.raises(ValueError, match="data_type must be one of"):
            self.generator.generate(
                operation='generate',
                data_type='invalid_type'
            )
        
        # Test invalid output format
        with pytest.raises(ValueError, match="output_format must be one of"):
            self.generator.generate(
                operation='generate',
                data_type='user',
                output_format='invalid_format'
            )
        
        # Test invalid count
        with pytest.raises(ValueError, match="count must be a positive integer"):
            self.generator.generate(
                operation='generate',
                data_type='user',
                count=-1
            )
        
        # Test zero count
        with pytest.raises(ValueError, match="count must be a positive integer"):
            self.generator.generate(
                operation='generate',
                data_type='user',
                count=0
            )
    
    def test_streaming_data_processing(self):
        """Test streaming data processing."""
        # Create a simple data iterator
        def data_iterator():
            for i in range(10):
                yield {'id': i, 'value': i * 2}
        
        processors = ['filter']
        results = list(self.generator.process_streaming_data(
            data_iterator(),
            processors,
            batch_size=3
        ))
        
        assert len(results) > 0
        # Should have multiple batches due to batch_size=3 and 10 items
        assert len(results) >= 3
    
    def test_caching(self):
        """Test caching functionality."""
        # First generation
        result1 = self.generator.generate(
            operation='generate',
            data_type='user',
            count=3,
            output_format='json'
        )
        
        stats_before = self.generator.get_stats()
        
        # Second generation with same parameters (should hit cache)
        result2 = self.generator.generate(
            operation='generate',
            data_type='user',
            count=3,
            output_format='json'
        )
        
        stats_after = self.generator.get_stats()
        
        assert result1 == result2
        assert stats_after['cache_hits'] > stats_before['cache_hits']
    
    def test_custom_schema_generation(self):
        """Test generation with custom schema."""
        custom_schema = {'custom_field': 'custom_value'}
        
        result = self.generator.generate(
            operation='generate',
            data_type='user',
            count=1,
            output_format='json',
            schema=custom_schema
        )
        
        data = json.loads(result)
        user = data[0]
        
        assert 'custom_field' in user
        assert user['custom_field'] == 'custom_value'
    
    def test_data_quality_metrics(self):
        """Test data quality metrics calculation."""
        test_data = [
            {'name': 'John', 'age': 25, 'email': 'john@example.com'},
            {'name': 'Jane', 'age': None, 'email': 'jane@example.com'},
            {'name': '', 'age': 30, 'email': ''}
        ]
        
        metrics = self.generator._calculate_data_quality_metrics(test_data)
        
        assert isinstance(metrics, dict)
        assert 'total_records' in metrics
        assert 'completeness_rates' in metrics
        assert metrics['total_records'] == 3
    
    def test_supported_formats(self):
        """Test getting supported formats."""
        formats = self.generator.get_supported_formats()
        
        assert isinstance(formats, list)
        assert len(formats) > 0
        assert 'json' in formats
        assert 'csv' in formats
        assert 'xml' in formats
    
    def test_available_processors(self):
        """Test getting available processors."""
        processors = self.generator.get_available_processors()
        
        assert isinstance(processors, list)
        assert 'filter' in processors
        assert 'map' in processors
        assert 'aggregate' in processors
    
    def test_available_generators(self):
        """Test getting available generators."""
        generators = self.generator.get_available_generators()
        
        assert isinstance(generators, list)
        assert 'user' in generators
        assert 'product' in generators
        assert 'transaction' in generators
    
    def test_statistics(self):
        """Test generation statistics."""
        # Generate some data to create stats
        self.generator.generate(operation='generate', data_type='user', count=2)
        self.generator.generate(operation='generate', data_type='product', count=3)
        
        stats = self.generator.get_stats()
        
        assert isinstance(stats, dict)
        assert 'generated' in stats
        assert 'cache_hits' in stats
        assert stats['generated'] >= 2
    
    def test_context_manager(self):
        """Test using generator as context manager."""
        with DataGenerator(self.config) as generator:
            result = generator.generate(
                operation='generate',
                data_type='user',
                count=1,
                output_format='json'
            )
            data = json.loads(result)
            assert len(data) == 1
            assert 'id' in data[0]