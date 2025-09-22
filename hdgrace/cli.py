"""
Command line interface for HDGRACE.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

from .generators.text_generator import TextGenerator
from .generators.code_generator import CodeGenerator
from .generators.data_generator import DataGenerator
from .utils.config import Config
from .utils.logger import setup_logger


def create_parser() -> argparse.ArgumentParser:
    """Create command line argument parser."""
    parser = argparse.ArgumentParser(
        description="HDGRACE - High-Definition Generator and Runtime Application Code Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  hdgrace text --pattern lorem --length 100 --format paragraph
  hdgrace code --language python --type class --name MyClass
  hdgrace data --type user --count 10 --format json
  hdgrace data --operation process --processor filter --data-file input.json
        """
    )
    
    parser.add_argument(
        "--config", "-c",
        type=str,
        help="Path to configuration file"
    )
    
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Output file path (default: stdout)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Text generation subcommand
    text_parser = subparsers.add_parser("text", help="Generate text content")
    text_parser.add_argument("--pattern", default="lorem", help="Text pattern to use")
    text_parser.add_argument("--length", type=int, default=100, help="Number of words to generate")
    text_parser.add_argument("--format", default="paragraph", help="Output format")
    text_parser.add_argument("--transformation", help="Text transformation to apply")
    
    # Code generation subcommand
    code_parser = subparsers.add_parser("code", help="Generate code")
    code_parser.add_argument("--language", required=True, help="Programming language")
    code_parser.add_argument("--type", default="class", help="Code type (class, function, api, etc.)")
    code_parser.add_argument("--name", required=True, help="Name of the code element")
    code_parser.add_argument("--methods", nargs="*", help="Methods to include")
    code_parser.add_argument("--properties", nargs="*", help="Properties to include")
    code_parser.add_argument("--docstring", help="Documentation string")
    
    # Data generation subcommand
    data_parser = subparsers.add_parser("data", help="Generate or process data")
    data_parser.add_argument("--operation", default="generate", choices=["generate", "process", "convert", "validate"])
    data_parser.add_argument("--type", default="user", help="Data type to generate")
    data_parser.add_argument("--count", type=int, default=10, help="Number of records to generate")
    data_parser.add_argument("--format", default="json", help="Output format")
    data_parser.add_argument("--processor", help="Data processor to use")
    data_parser.add_argument("--data-file", help="Input data file")
    data_parser.add_argument("--schema-file", help="Schema file for validation")
    
    return parser


def run_text_generation(args, config: Config) -> str:
    """Run text generation command."""
    generator = TextGenerator(config)
    
    return generator.generate(
        pattern_type=args.pattern,
        length=args.length,
        format_type=args.format,
        transformation=args.transformation
    )


def run_code_generation(args, config: Config) -> str:
    """Run code generation command."""
    generator = CodeGenerator(config)
    
    return generator.generate(
        language=args.language,
        code_type=args.type,
        name=args.name,
        methods=args.methods or [],
        properties=args.properties or [],
        docstring=args.docstring
    )


def run_data_generation(args, config: Config) -> str:
    """Run data generation command."""
    generator = DataGenerator(config)
    
    kwargs = {
        "operation": args.operation,
        "output_format": args.format
    }
    
    if args.operation == "generate":
        kwargs.update({
            "data_type": args.type,
            "count": args.count
        })
    elif args.operation == "process":
        if not args.data_file:
            raise ValueError("--data-file required for process operation")
        
        # Load data from file
        data_path = Path(args.data_file)
        if not data_path.exists():
            raise FileNotFoundError(f"Data file not found: {args.data_file}")
        
        with open(data_path, 'r', encoding='utf-8') as f:
            if args.data_file.endswith('.json'):
                data = json.load(f)
            else:
                data = f.read()
        
        kwargs.update({
            "data": data,
            "processor": args.processor or "filter"
        })
    elif args.operation == "validate":
        if not args.data_file:
            raise ValueError("--data-file required for validate operation")
        
        # Load data and schema
        with open(args.data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        schema = {}
        if args.schema_file:
            with open(args.schema_file, 'r', encoding='utf-8') as f:
                schema = json.load(f)
        
        kwargs.update({
            "data": data,
            "schema": schema
        })
    
    result = generator.generate(**kwargs)
    
    # For validation, format the result nicely
    if args.operation == "validate" and isinstance(result, dict):
        return json.dumps(result, indent=2)
    
    return result


def main(argv: Optional[list] = None) -> int:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args(argv)
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Setup logging
    log_level = "DEBUG" if args.verbose else "INFO"
    logger = setup_logger("hdgrace", log_level)
    
    try:
        # Load configuration
        config = Config(args.config) if args.config else Config()
        logger.info(f"Loaded configuration with cache_size={config.get('cache_size')}")
        
        # Run the appropriate command
        if args.command == "text":
            result = run_text_generation(args, config)
        elif args.command == "code":
            result = run_code_generation(args, config)
        elif args.command == "data":
            result = run_data_generation(args, config)
        else:
            logger.error(f"Unknown command: {args.command}")
            return 1
        
        # Output result
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(result)
            logger.info(f"Output written to {output_path}")
        else:
            print(result)
        
        return 0
        
    except Exception as e:
        logger.error(f"Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())