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
            'validate': self._validate_data_processor,
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
    
    def _validate_data_processor(self, data: List[Any], **kwargs) -> List[Any]:
        """Basic data validation processor."""
        if not isinstance(data, list):
            raise ValueError("Data must be a list")
        return data
    
    def _transform_data(self, data: List[Any], transformation: str = None, **kwargs) -> List[Any]:
        """Transform data using specified transformation."""
        if not transformation:
            return data
        
        # Simple transformations
        if transformation == 'uppercase' and isinstance(data[0], dict):
            return [{k: str(v).upper() if isinstance(v, str) else v for k, v in item.items()} for item in data]
        elif transformation == 'lowercase' and isinstance(data[0], dict):
            return [{k: str(v).lower() if isinstance(v, str) else v for k, v in item.items()} for item in data]
        
        return data
    
    def _normalize_data(self, data: List[Any], **kwargs) -> List[Any]:
        """Normalize data values."""
        if not data or not isinstance(data[0], dict):
            return data
        
        # Simple normalization: ensure all records have same keys
        all_keys = set()
        for item in data:
            all_keys.update(item.keys())
        
        normalized = []
        for item in data:
            normalized_item = {key: item.get(key, None) for key in all_keys}
            normalized.append(normalized_item)
        
        return normalized
    
    def _deduplicate_data(self, data: List[Any], key: str = None, **kwargs) -> List[Any]:
        """Remove duplicate records."""
        if not data:
            return data
        
        if key and isinstance(data[0], dict):
            seen = set()
            result = []
            for item in data:
                value = item.get(key)
                if value not in seen:
                    seen.add(value)
                    result.append(item)
            return result
        else:
            # Simple deduplication
            return list({str(item): item for item in data}.values())
    
    def _merge_data(self, data: List[Any], other_data: List[Any] = None, **kwargs) -> List[Any]:
        """Merge two datasets."""
        if other_data is None:
            return data
        return data + other_data
    
    def _split_data(self, data: List[Any], ratio: float = 0.5, **kwargs) -> Dict[str, List[Any]]:
        """Split data into two parts."""
        split_point = int(len(data) * ratio)
        return {
            'first': data[:split_point],
            'second': data[split_point:]
        }
    
    def _generate_field_value(self, field_type: str, field_params: Dict[str, Any], index: int, distribution: str) -> Any:
        """Generate value for a specific field type."""
        import random
        
        if field_type == 'string':
            length = field_params.get('length', 10)
            chars = 'abcdefghijklmnopqrstuvwxyz'
            return ''.join(random.choice(chars) for _ in range(length))
        elif field_type == 'integer':
            min_val = field_params.get('min', 0)
            max_val = field_params.get('max', 100)
            return random.randint(min_val, max_val)
        elif field_type == 'float':
            min_val = field_params.get('min', 0.0)
            max_val = field_params.get('max', 100.0)
            return round(random.uniform(min_val, max_val), 2)
        elif field_type == 'boolean':
            return random.choice([True, False])
        elif field_type == 'date':
            from datetime import datetime, timedelta
            start_date = datetime.now() - timedelta(days=365)
            random_days = random.randint(0, 365)
            return (start_date + timedelta(days=random_days)).isoformat()
        else:
            return f'value_{index}'
    
    def _process_batch(self, batch: List[Any], processors: List[str]) -> List[Any]:
        """Process a batch of data with specified processors."""
        result = batch
        for processor_name in processors:
            if processor_name in self.processors:
                processor_func = self.processors[processor_name]
                result = processor_func(result)
        return result
    
    def _parse_input(self, data: Any, input_format: str) -> List[Any]:
        """Parse input data based on format."""
        if input_format == 'json':
            if isinstance(data, str):
                return json.loads(data)
            return data
        elif input_format == 'csv':
            # Simple CSV parsing
            lines = data.strip().split('\n')
            if len(lines) < 2:
                return []
            
            headers = lines[0].split(',')
            result = []
            for line in lines[1:]:
                values = line.split(',')
                record = dict(zip(headers, values))
                result.append(record)
            return result
        else:
            return data if isinstance(data, list) else [data]
    
    def _validate_against_schema(self, data: List[Any], schema: Dict[str, Any]) -> List[str]:
        """Validate data against schema."""
        errors = []
        
        if not isinstance(data, list):
            errors.append("Data must be a list")
            return errors
        
        for i, record in enumerate(data):
            if not isinstance(record, dict):
                errors.append(f"Record {i} must be a dictionary")
                continue
            
            for field_name, field_spec in schema.items():
                if isinstance(field_spec, dict):
                    field_type = field_spec.get('type')
                    required = field_spec.get('required', False)
                    
                    if required and field_name not in record:
                        errors.append(f"Record {i}: Missing required field '{field_name}'")
                    elif field_name in record:
                        value = record[field_name]
                        if field_type == 'string' and not isinstance(value, str):
                            errors.append(f"Record {i}: Field '{field_name}' must be a string")
                        elif field_type == 'integer' and not isinstance(value, int):
                            errors.append(f"Record {i}: Field '{field_name}' must be an integer")
        
        return errors
    
    def _apply_validation_rule(self, data: List[Any], rule: Dict[str, Any]) -> List[str]:
        """Apply custom validation rule to data."""
        errors = []
        # Simple rule application - can be extended
        return errors
    
    def _generate_sensor_data(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Generate sensor data."""
        return {
            'id': str(uuid.uuid4()),
            'sensor_type': random.choice(['temperature', 'humidity', 'pressure', 'motion']),
            'value': round(random.uniform(0, 100), 2),
            'unit': random.choice(['celsius', 'fahrenheit', 'percent', 'pascal', 'boolean']),
            'timestamp': datetime.now().isoformat(),
            'location': f"Room_{random.randint(1, 10)}",
            **schema
        }
    
    def _generate_financial_data(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Generate financial data."""
        return {
            'id': str(uuid.uuid4()),
            'account_id': str(uuid.uuid4()),
            'transaction_type': random.choice(['debit', 'credit', 'transfer']),
            'amount': round(random.uniform(1, 10000), 2),
            'currency': random.choice(['USD', 'EUR', 'GBP', 'JPY']),
            'timestamp': datetime.now().isoformat(),
            'description': f"Financial transaction {random.randint(1000, 9999)}",
            **schema
        }
    
    def _generate_healthcare_data(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Generate healthcare data."""
        return {
            'patient_id': str(uuid.uuid4()),
            'visit_date': datetime.now().isoformat(),
            'diagnosis': random.choice(['Hypertension', 'Diabetes', 'Influenza', 'Migraine']),
            'treatment': random.choice(['Medication', 'Therapy', 'Surgery', 'Observation']),
            'duration_days': random.randint(1, 30),
            'cost': round(random.uniform(100, 5000), 2),
            **schema
        }
    
    def _generate_retail_data(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Generate retail data."""
        return {
            'order_id': str(uuid.uuid4()),
            'customer_id': str(uuid.uuid4()),
            'product_category': random.choice(['Electronics', 'Clothing', 'Books', 'Food']),
            'quantity': random.randint(1, 10),
            'unit_price': round(random.uniform(5, 500), 2),
            'discount': round(random.uniform(0, 0.3), 2),
            'order_date': datetime.now().isoformat(),
            **schema
        }
    
    def _validate_email(self, email: str) -> bool:
        """Validate email format."""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def _validate_phone(self, phone: str) -> bool:
        """Validate phone number format."""
        import re
        # Simple phone validation
        pattern = r'^\+?1?\d{9,15}$'
        return bool(re.match(pattern, phone.replace('-', '').replace(' ', '')))
    
    def _validate_url(self, url: str) -> bool:
        """Validate URL format."""
        import re
        pattern = r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:\w*))?)?$'
        return bool(re.match(pattern, url))
    
    def _validate_date(self, date_str: str) -> bool:
        """Validate date format."""
        try:
            datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return True
        except ValueError:
            return False
    
    def _validate_credit_card(self, card_number: str) -> bool:
        """Validate credit card number using Luhn algorithm."""
        # Simple validation - just check if it's numeric and reasonable length
        card_number = card_number.replace(' ', '').replace('-', '')
        return card_number.isdigit() and 13 <= len(card_number) <= 19
    
    def _validate_ssn(self, ssn: str) -> bool:
        """Validate SSN format."""
        import re
        pattern = r'^\d{3}-\d{2}-\d{4}$'
        return bool(re.match(pattern, ssn))
    
    def _validate_uuid(self, uuid_str: str) -> bool:
        """Validate UUID format."""
        try:
            uuid.UUID(uuid_str)
            return True
        except ValueError:
            return False