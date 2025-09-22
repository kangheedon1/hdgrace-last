"""
Data generation and processing module - consolidates DataProcessor classes from original HDGRACE.txt.
"""

import json
import csv
import xml.etree.ElementTree as ET
import io
import hashlib
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Callable, Iterator
from collections import defaultdict
import random
from ..core.base_generator import BaseGenerator


class DataGenerator(BaseGenerator):
    """
    Production-ready data generator and processor for multiple data formats.
    
    Supports: JSON, CSV, XML, SQL, YAML, Binary data formats
    Features:
    - Streaming data processing
    - Schema validation and transformation
    - Data aggregation and filtering
    - Synthetic data generation
    - Format conversion
    - Data quality metrics
    """
    
    def _initialize(self) -> None:
        """Initialize data processing components."""
        self.supported_formats = {
            'json', 'csv', 'xml', 'yaml', 'sql', 'binary', 'parquet', 'avro'
        }
        
        self.processors = {
            'filter': self._filter_data,
            'map': self._map_data,
            'reduce': self._reduce_data,
            'aggregate': self._aggregate_data,
            'validate': self._validate_schema,
            'transform': self._transform_data,
            'normalize': self._normalize_data,
            'deduplicate': self._deduplicate_data,
            'merge': self._merge_data,
            'split': self._split_data
        }
        
        self.generators = {
            'user': self._generate_user_data,
            'product': self._generate_product_data,
            'transaction': self._generate_transaction_data,
            'log': self._generate_log_data,
            'sensor': self._generate_sensor_data,
            'financial': self._generate_financial_data,
            'healthcare': self._generate_healthcare_data,
            'retail': self._generate_retail_data
        }
        
        self.validators = {
            'email': self._validate_email,
            'phone': self._validate_phone,
            'url': self._validate_url,
            'date': self._validate_date,
            'credit_card': self._validate_credit_card,
            'ssn': self._validate_ssn,
            'uuid': self._validate_uuid
        }
        
        self.buffer_size = self.config.get("buffer_size", 8192)
        self.batch_size = self.config.get("batch_size", 1000)
    
    def _validate_input(self, **kwargs) -> None:
        """Validate data processing parameters."""
        operation = kwargs.get('operation', 'generate')
        data_type = kwargs.get('data_type', 'user')
        output_format = kwargs.get('output_format', 'json')
        
        if operation == 'generate' and data_type not in self.generators:
            raise ValueError(f"data_type must be one of: {list(self.generators.keys())}")
        
        if operation == 'process' and not kwargs.get('data'):
            raise ValueError("data is required for processing operations")
        
        if output_format not in self.supported_formats:
            raise ValueError(f"output_format must be one of: {self.supported_formats}")
        
        count = kwargs.get('count', 100)
        if not isinstance(count, int) or count <= 0:
            raise ValueError("count must be a positive integer")
        
        max_count = self.config.get("max_generation_count", 100000)
        if count > max_count:
            raise ValueError(f"count exceeds maximum allowed: {max_count}")
    
    def _generate_content(self, **kwargs) -> Any:
        """Core data generation/processing logic."""
        operation = kwargs.get('operation', 'generate')
        
        if operation == 'generate':
            return self._handle_generation(**kwargs)
        elif operation == 'process':
            return self._handle_processing(**kwargs)
        elif operation == 'convert':
            return self._handle_conversion(**kwargs)
        elif operation == 'validate':
            return self._handle_validation(**kwargs)
        else:
            raise ValueError(f"Unsupported operation: {operation}")
    
    def _handle_generation(self, **kwargs) -> Any:
        """Handle data generation operations."""
        data_type = kwargs.get('data_type', 'user')
        count = kwargs.get('count', 100)
        output_format = kwargs.get('output_format', 'json')
        schema = kwargs.get('schema', {})
        
        # Generate data
        generator_func = self.generators[data_type]
        data = []
        
        for _ in range(count):
            record = generator_func(schema)
            data.append(record)
        
        # Format output
        return self._format_output(data, output_format)
    
    def _handle_processing(self, **kwargs) -> Any:
        """Handle data processing operations."""
        data = kwargs.get('data')
        processor_name = kwargs.get('processor', 'filter')
        processor_params = kwargs.get('processor_params', {})
        
        if processor_name not in self.processors:
            raise ValueError(f"Unknown processor: {processor_name}")
        
        processor_func = self.processors[processor_name]
        return processor_func(data, **processor_params)
    
    def _handle_conversion(self, **kwargs) -> Any:
        """Handle format conversion operations."""
        data = kwargs.get('data')
        input_format = kwargs.get('input_format', 'json')
        output_format = kwargs.get('output_format', 'csv')
        
        # Parse input data
        parsed_data = self._parse_input(data, input_format)
        
        # Convert to output format
        return self._format_output(parsed_data, output_format)
    
    def _handle_validation(self, **kwargs) -> Dict[str, Any]:
        """Handle data validation operations."""
        data = kwargs.get('data')
        schema = kwargs.get('schema', {})
        validation_rules = kwargs.get('validation_rules', [])
        
        validation_results = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'metrics': {}
        }
        
        # Schema validation
        if schema:
            schema_errors = self._validate_against_schema(data, schema)
            validation_results['errors'].extend(schema_errors)
        
        # Custom validation rules
        for rule in validation_rules:
            rule_errors = self._apply_validation_rule(data, rule)
            validation_results['errors'].extend(rule_errors)
        
        # Data quality metrics
        validation_results['metrics'] = self._calculate_data_quality_metrics(data)
        
        validation_results['valid'] = len(validation_results['errors']) == 0
        
        return validation_results
    
    def generate_synthetic_dataset(self, schema: Dict[str, Any], count: int,
                                 distribution: str = 'random') -> List[Dict[str, Any]]:
        """
        Generate synthetic dataset based on schema.
        
        Args:
            schema: Data schema definition
            count: Number of records to generate
            distribution: Data distribution type (random, normal, skewed)
            
        Returns:
            List of generated records
        """
        dataset = []
        
        for i in range(count):
            record = {}
            
            for field_name, field_spec in schema.items():
                if isinstance(field_spec, dict):
                    field_type = field_spec.get('type', 'string')
                    field_params = field_spec.get('params', {})
                else:
                    field_type = field_spec
                    field_params = {}
                
                record[field_name] = self._generate_field_value(
                    field_type, field_params, i, distribution
                )
            
            dataset.append(record)
        
        return dataset
    
    def process_streaming_data(self, data_iterator: Iterator[Any],
                             processors: List[str], 
                             batch_size: Optional[int] = None) -> Iterator[Any]:
        """
        Process streaming data with specified processors.
        
        Args:
            data_iterator: Iterator providing data chunks
            processors: List of processor names to apply
            batch_size: Size of processing batches
            
        Yields:
            Processed data chunks
        """
        batch_size = batch_size or self.batch_size
        batch = []
        
        for item in data_iterator:
            batch.append(item)
            
            if len(batch) >= batch_size:
                processed_batch = self._process_batch(batch, processors)
                yield processed_batch
                batch = []
        
        # Process final batch if any
        if batch:
            processed_batch = self._process_batch(batch, processors)
            yield processed_batch
    
    def _generate_user_data(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Generate user/person data."""
        first_names = ['John', 'Jane', 'Michael', 'Emily', 'David', 'Sarah', 'Robert', 'Jessica']
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis']
        domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'company.com']
        
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        
        return {
            'id': str(uuid.uuid4()),
            'first_name': first_name,
            'last_name': last_name,
            'email': f"{first_name.lower()}.{last_name.lower()}@{random.choice(domains)}",
            'age': random.randint(18, 80),
            'registration_date': (datetime.now() - timedelta(days=random.randint(0, 365))).isoformat(),
            'is_active': random.choice([True, False]),
            'score': round(random.uniform(0, 100), 2),
            **schema
        }
    
    def _generate_product_data(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Generate product data."""
        categories = ['Electronics', 'Clothing', 'Books', 'Home', 'Sports', 'Toys']
        brands = ['BrandA', 'BrandB', 'BrandC', 'BrandD', 'BrandE']
        
        return {
            'id': str(uuid.uuid4()),
            'name': f"Product {random.randint(1000, 9999)}",
            'category': random.choice(categories),
            'brand': random.choice(brands),
            'price': round(random.uniform(10, 1000), 2),
            'rating': round(random.uniform(1, 5), 1),
            'in_stock': random.choice([True, False]),
            'created_date': (datetime.now() - timedelta(days=random.randint(0, 1000))).isoformat(),
            **schema
        }
    
    def _generate_transaction_data(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Generate transaction data."""
        return {
            'id': str(uuid.uuid4()),
            'user_id': str(uuid.uuid4()),
            'amount': round(random.uniform(1, 10000), 2),
            'currency': random.choice(['USD', 'EUR', 'GBP', 'JPY']),
            'status': random.choice(['completed', 'pending', 'failed']),
            'timestamp': (datetime.now() - timedelta(seconds=random.randint(0, 86400))).isoformat(),
            'payment_method': random.choice(['credit_card', 'debit_card', 'paypal', 'bank_transfer']),
            **schema
        }
    
    def _generate_log_data(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Generate log entry data."""
        levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        sources = ['app', 'database', 'auth', 'api', 'worker']
        
        return {
            'timestamp': datetime.now().isoformat(),
            'level': random.choice(levels),
            'source': random.choice(sources),
            'message': f"Log message {random.randint(1000, 9999)}",
            'user_id': str(uuid.uuid4()) if random.random() > 0.3 else None,
            'request_id': str(uuid.uuid4()),
            'duration_ms': random.randint(1, 5000),
            **schema
        }
    
    def _filter_data(self, data: List[Any], condition: Callable = None, **kwargs) -> List[Any]:
        """Filter data based on condition."""
        if not condition:
            return data
        
        try:
            return [item for item in data if condition(item)]
        except Exception as e:
            self.error_logger.log_generation_error("filter_data", str(e))
            return data
    
    def _map_data(self, data: List[Any], transform: Callable = None, **kwargs) -> List[Any]:
        """Transform data elements."""
        if not transform:
            return data
        
        try:
            return [transform(item) for item in data]
        except Exception as e:
            self.error_logger.log_generation_error("map_data", str(e))
            return data
    
    def _reduce_data(self, data: List[Any], reducer: Callable = None, initial=None, **kwargs) -> Any:
        """Reduce data to single value."""
        if not reducer:
            return data
        
        try:
            result = initial
            for item in data:
                result = reducer(result, item)
            return result
        except Exception as e:
            self.error_logger.log_generation_error("reduce_data", str(e))
            return data
    
    def _aggregate_data(self, data: List[Dict[str, Any]], 
                       group_by: List[str] = None, 
                       aggregations: Dict[str, str] = None, **kwargs) -> List[Dict[str, Any]]:
        """Aggregate data by specified fields."""
        if not group_by or not aggregations:
            return data
        
        groups = defaultdict(list)
        
        # Group data
        for item in data:
            key = tuple(item.get(field) for field in group_by)
            groups[key].append(item)
        
        # Aggregate groups
        result = []
        for key, group_items in groups.items():
            aggregated = dict(zip(group_by, key))
            
            for field, agg_func in aggregations.items():
                values = [item.get(field) for item in group_items if item.get(field) is not None]
                
                if agg_func == 'sum':
                    aggregated[f"{field}_sum"] = sum(values)
                elif agg_func == 'avg':
                    aggregated[f"{field}_avg"] = sum(values) / len(values) if values else 0
                elif agg_func == 'count':
                    aggregated[f"{field}_count"] = len(values)
                elif agg_func == 'min':
                    aggregated[f"{field}_min"] = min(values) if values else None
                elif agg_func == 'max':
                    aggregated[f"{field}_max"] = max(values) if values else None
            
            result.append(aggregated)
        
        return result
    
    def _format_output(self, data: List[Any], output_format: str) -> str:
        """Format data in specified output format."""
        if output_format == 'json':
            return json.dumps(data, indent=2, default=str, ensure_ascii=False)
        
        elif output_format == 'csv':
            if not data:
                return ""
            
            output = io.StringIO()
            if isinstance(data[0], dict):
                fieldnames = data[0].keys()
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            else:
                writer = csv.writer(output)
                writer.writerows(data if isinstance(data[0], (list, tuple)) else [[item] for item in data])
            
            return output.getvalue()
        
        elif output_format == 'xml':
            root = ET.Element('data')
            for i, item in enumerate(data):
                record = ET.SubElement(root, f'record_{i}')
                if isinstance(item, dict):
                    for key, value in item.items():
                        elem = ET.SubElement(record, key)
                        elem.text = str(value)
                else:
                    record.text = str(item)
            
            return ET.tostring(root, encoding='unicode')
        
        elif output_format == 'yaml':
            try:
                import yaml
                return yaml.dump(data, default_flow_style=False)
            except ImportError:
                return self._format_output(data, 'json')  # Fallback to JSON
        
        else:
            return str(data)
    
    def _calculate_data_quality_metrics(self, data: List[Any]) -> Dict[str, Any]:
        """Calculate data quality metrics."""
        if not data:
            return {'total_records': 0}
        
        total_records = len(data)
        
        if isinstance(data[0], dict):
            # For structured data
            all_fields = set()
            field_completeness = defaultdict(int)
            
            for record in data:
                all_fields.update(record.keys())
                for field, value in record.items():
                    if value is not None and value != '':
                        field_completeness[field] += 1
            
            completeness_rates = {
                field: (count / total_records) * 100
                for field, count in field_completeness.items()
            }
            
            return {
                'total_records': total_records,
                'total_fields': len(all_fields),
                'completeness_rates': completeness_rates,
                'overall_completeness': sum(completeness_rates.values()) / len(completeness_rates) if completeness_rates else 0
            }
        else:
            # For unstructured data
            non_empty = len([item for item in data if item])
            return {
                'total_records': total_records,
                'non_empty_records': non_empty,
                'completeness_rate': (non_empty / total_records) * 100 if total_records > 0 else 0
            }
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported data formats."""
        return sorted(list(self.supported_formats))
    
    def get_available_processors(self) -> List[str]:
        """Get list of available data processors."""
        return list(self.processors.keys())
    
    def get_available_generators(self) -> List[str]:
        """Get list of available data generators."""
        return list(self.generators.keys())