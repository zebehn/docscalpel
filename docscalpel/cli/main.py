"""
Command-line interface for DocScalpel.

DocScalpel: Surgical precision for PDF element extraction.

Provides a user-friendly CLI for extracting figures, tables, and equations
from PDF files using the core library.
"""

import argparse
import sys
import logging
from pathlib import Path
from typing import List

from docscalpel import (
    extract_elements,
    ExtractionConfig,
    ElementType,
    InvalidPDFError,
    ConfigurationError,
    ExtractionFailedError,
    __version__,
)
from .formatter import format_json, format_text
from .logger import setup_logging

logger = logging.getLogger(__name__)


def parse_element_types(types_str: str) -> List[ElementType]:
    """
    Parse comma-separated element types string.

    Args:
        types_str: Comma-separated types (e.g., "figure,table,equation")

    Returns:
        List of ElementType enums

    Raises:
        ValueError: If any type is invalid

    Example:
        >>> parse_element_types("figure,table")
        [ElementType.FIGURE, ElementType.TABLE]
    """
    type_mapping = {
        'figure': ElementType.FIGURE,
        'table': ElementType.TABLE,
        'equation': ElementType.EQUATION,
    }

    types_list = [t.strip().lower() for t in types_str.split(',')]
    result = []

    for type_str in types_list:
        if type_str not in type_mapping:
            raise ValueError(
                f"Invalid element type '{type_str}'. "
                f"Valid types: figure, table, equation"
            )
        result.append(type_mapping[type_str])

    return result


def validate_confidence(confidence: float) -> bool:
    """
    Validate confidence threshold value.

    Args:
        confidence: Confidence threshold (0.0-1.0)

    Returns:
        True if valid, False otherwise

    Example:
        >>> validate_confidence(0.5)
        True
        >>> validate_confidence(1.5)
        False
    """
    return 0.0 <= confidence <= 1.0


def create_argument_parser() -> argparse.ArgumentParser:
    """
    Create and configure argument parser for CLI.

    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        prog='pdf-extractor',
        description='Extract figures, tables, and equations from PDF files',
        epilog='Example: pdf-extractor paper.pdf --types figure,table --output ./extracted'
    )

    # Required arguments
    parser.add_argument(
        'pdf_file',
        type=str,
        help='Path to the PDF file to process'
    )

    # Optional arguments
    parser.add_argument(
        '--types',
        type=str,
        default='figure,table,equation',
        help='Comma-separated element types to extract (default: figure,table,equation)'
    )

    parser.add_argument(
        '--output',
        type=str,
        default='.',
        help='Output directory for extracted elements (default: current directory)'
    )

    parser.add_argument(
        '--naming-pattern',
        type=str,
        default='{type}_{counter:02d}.pdf',
        help='Naming pattern for output files (default: {type}_{counter:02d}.pdf)'
    )

    parser.add_argument(
        '--padding',
        type=int,
        default=0,
        help='Boundary padding in pixels (default: 0)'
    )

    parser.add_argument(
        '--confidence',
        type=float,
        default=0.5,
        help='Minimum confidence threshold 0.0-1.0 (default: 0.5)'
    )

    parser.add_argument(
        '--format',
        choices=['json', 'text'],
        default='text',
        help='Output format (default: text)'
    )

    parser.add_argument(
        '--overwrite',
        action='store_true',
        help='Overwrite existing output files'
    )

    parser.add_argument(
        '--max-pages',
        type=int,
        default=None,
        help='Maximum number of pages to process (default: all)'
    )

    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Enable verbose logging'
    )

    parser.add_argument(
        '--version',
        action='version',
        version=f'%(prog)s {__version__}'
    )

    return parser


def main() -> int:
    """
    Main CLI entry point.

    Returns:
        Exit code (0 for success, non-zero for failure)

    Example:
        >>> sys.argv = ['pdf-extractor', 'paper.pdf', '--types', 'figure']
        >>> exit_code = main()
        >>> print(f"Exit code: {exit_code}")
    """
    # Parse arguments
    parser = create_argument_parser()
    args = parser.parse_args()

    # Setup logging
    setup_logging(verbose=args.verbose)

    logger.info(f"DocScalpel v{__version__}")
    logger.info(f"Processing: {args.pdf_file}")

    try:
        # Validate arguments
        if not Path(args.pdf_file).exists():
            logger.error(f"PDF file not found: {args.pdf_file}")
            print(f"Error: PDF file not found: {args.pdf_file}", file=sys.stderr)
            return 1

        # Parse element types
        try:
            element_types = parse_element_types(args.types)
        except ValueError as e:
            logger.error(f"Invalid --types argument: {e}")
            print(f"Error: {e}", file=sys.stderr)
            return 1

        # Validate confidence threshold
        if not validate_confidence(args.confidence):
            logger.error(f"Invalid confidence threshold: {args.confidence}")
            print(
                f"Error: Confidence threshold must be between 0.0 and 1.0, got {args.confidence}",
                file=sys.stderr
            )
            return 1

        # Validate max_pages
        if args.max_pages is not None and args.max_pages <= 0:
            logger.error(f"Invalid max_pages: {args.max_pages}")
            print(
                f"Error: --max-pages must be a positive integer, got {args.max_pages}",
                file=sys.stderr
            )
            return 1

        # Create extraction configuration
        config = ExtractionConfig(
            element_types=element_types,
            output_directory=args.output,
            naming_pattern=args.naming_pattern,
            boundary_padding=args.padding,
            confidence_threshold=args.confidence,
            overwrite_existing=args.overwrite,
            max_pages=args.max_pages
        )

        logger.debug(f"Configuration: {config}")

        # Run extraction
        logger.info("Starting extraction...")
        result = extract_elements(args.pdf_file, config)

        # Format and print output
        if args.format == 'json':
            output = format_json(result)
        else:
            output = format_text(result)

        print(output)

        # Log completion
        if result.success:
            logger.info(
                f"Extraction completed successfully: {result.total_elements} elements "
                f"in {result.extraction_time_seconds:.2f}s"
            )
            return 0
        else:
            logger.warning(
                f"Extraction completed with errors: {len(result.errors)} errors, "
                f"{len(result.warnings)} warnings"
            )
            return 1

    except InvalidPDFError as e:
        logger.error(f"Invalid PDF: {e}")
        print(f"Error: {e}", file=sys.stderr)
        return 1

    except ConfigurationError as e:
        logger.error(f"Configuration error: {e}")
        print(f"Error: {e}", file=sys.stderr)
        return 1

    except ExtractionFailedError as e:
        logger.error(f"Extraction failed: {e}")
        print(f"Error: {e}", file=sys.stderr)
        return 1

    except KeyboardInterrupt:
        logger.info("Extraction cancelled by user")
        print("\nCancelled by user", file=sys.stderr)
        return 130  # Standard exit code for SIGINT

    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
