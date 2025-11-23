"""
Integration tests for CLI-library integration.

Tests the command-line interface integration with the core library,
including argument parsing, library calls, and output formatting.

Test Strategy (TDD):
1. Write these tests FIRST
2. Verify they FAIL (no CLI implementation yet)
3. Implement the CLI
4. Verify tests PASS
"""

import pytest
import json
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

from docscalpel.models import ElementType


class TestCLIArgumentParsing:
    """Test CLI argument parsing and library integration."""

    def test_cli_main_function_exists(self):
        """Verify CLI main function is importable."""
        from docscalpel.cli.main import main
        assert callable(main)

    def test_cli_with_minimal_args(self, sample_pdf_path, temp_output_dir, capsys):
        """
        Integration test: CLI with just PDF path (default settings).

        Given: PDF file path
        When: CLI is called with minimal arguments
        Then: Extraction runs with defaults, prints results
        """
        from docscalpel.cli.main import main

        test_args = ['pdf-extractor', sample_pdf_path]

        with patch('sys.argv', test_args):
            exit_code = main()

        # Verify: Success exit code
        assert exit_code == 0

        # Verify: Output was printed
        captured = capsys.readouterr()
        assert len(captured.out) > 0

    def test_cli_with_custom_output_directory(
        self, sample_pdf_path, temp_output_dir, capsys
    ):
        """
        Integration test: CLI with custom output directory.

        Given: PDF file and custom output directory
        When: CLI is called with --output flag
        Then: Files are created in specified directory
        """
        from docscalpel.cli.main import main

        custom_dir = temp_output_dir / "custom"
        test_args = [
            'pdf-extractor',
            sample_pdf_path,
            '--output', str(custom_dir)
        ]

        with patch('sys.argv', test_args):
            exit_code = main()

        assert exit_code == 0
        assert custom_dir.exists()

    def test_cli_with_types_filter(self, sample_pdf_path, temp_output_dir):
        """
        Integration test: CLI with --types filter.

        Given: PDF file
        When: CLI is called with --types figure
        Then: Only figures are extracted
        """
        from docscalpel.cli.main import main

        test_args = [
            'pdf-extractor',
            sample_pdf_path,
            '--types', 'figure',
            '--output', str(temp_output_dir)
        ]

        with patch('sys.argv', test_args):
            exit_code = main()

        assert exit_code == 0

    def test_cli_with_multiple_types(self, sample_pdf_path, temp_output_dir):
        """
        Integration test: CLI with multiple element types.

        Given: PDF file
        When: CLI is called with --types figure,table,equation
        Then: All types are extracted
        """
        from docscalpel.cli.main import main

        test_args = [
            'pdf-extractor',
            sample_pdf_path,
            '--types', 'figure,table,equation',
            '--output', str(temp_output_dir)
        ]

        with patch('sys.argv', test_args):
            exit_code = main()

        assert exit_code == 0

    def test_cli_with_json_output(self, sample_pdf_path, temp_output_dir, capsys):
        """
        Integration test: CLI with JSON output format.

        Given: PDF file
        When: CLI is called with --format json
        Then: Output is valid JSON
        """
        from docscalpel.cli.main import main

        test_args = [
            'pdf-extractor',
            sample_pdf_path,
            '--format', 'json',
            '--output', str(temp_output_dir)
        ]

        with patch('sys.argv', test_args):
            exit_code = main()

        assert exit_code == 0

        # Verify: Output is valid JSON
        captured = capsys.readouterr()
        result = json.loads(captured.out)
        assert 'success' in result
        assert 'statistics' in result

    def test_cli_with_confidence_threshold(self, sample_pdf_path, temp_output_dir):
        """
        Integration test: CLI with custom confidence threshold.

        Given: PDF file
        When: CLI is called with --confidence 0.8
        Then: Extraction uses specified threshold
        """
        from docscalpel.cli.main import main

        test_args = [
            'pdf-extractor',
            sample_pdf_path,
            '--confidence', '0.8',
            '--output', str(temp_output_dir)
        ]

        with patch('sys.argv', test_args):
            exit_code = main()

        assert exit_code == 0

    def test_cli_with_naming_pattern(self, sample_pdf_path, temp_output_dir):
        """
        Integration test: CLI with custom naming pattern.

        Given: PDF file
        When: CLI is called with --naming-pattern
        Then: Files follow custom naming pattern
        """
        from docscalpel.cli.main import main

        test_args = [
            'pdf-extractor',
            sample_pdf_path,
            '--naming-pattern', 'extracted_{type}_{counter:03d}.pdf',
            '--output', str(temp_output_dir)
        ]

        with patch('sys.argv', test_args):
            exit_code = main()

        assert exit_code == 0

    def test_cli_with_padding(self, sample_pdf_path, temp_output_dir):
        """
        Integration test: CLI with boundary padding.

        Given: PDF file
        When: CLI is called with --padding 10
        Then: Extraction uses specified padding
        """
        from docscalpel.cli.main import main

        test_args = [
            'pdf-extractor',
            sample_pdf_path,
            '--padding', '10',
            '--output', str(temp_output_dir)
        ]

        with patch('sys.argv', test_args):
            exit_code = main()

        assert exit_code == 0

    def test_cli_with_max_pages(self, sample_pdf_path, temp_output_dir):
        """
        Integration test: CLI with max pages limit.

        Given: PDF file
        When: CLI is called with --max-pages 5
        Then: Only first 5 pages are processed
        """
        from docscalpel.cli.main import main

        test_args = [
            'pdf-extractor',
            sample_pdf_path,
            '--max-pages', '5',
            '--output', str(temp_output_dir)
        ]

        with patch('sys.argv', test_args):
            exit_code = main()

        assert exit_code == 0

    def test_cli_with_overwrite_flag(self, sample_pdf_path, temp_output_dir):
        """
        Integration test: CLI with overwrite flag.

        Given: PDF file and existing output
        When: CLI is called with --overwrite
        Then: Existing files are overwritten
        """
        from docscalpel.cli.main import main

        test_args = [
            'pdf-extractor',
            sample_pdf_path,
            '--overwrite',
            '--output', str(temp_output_dir)
        ]

        with patch('sys.argv', test_args):
            exit_code = main()

        assert exit_code == 0


class TestCLIErrorHandling:
    """Test CLI error handling."""

    def test_cli_with_missing_pdf(self, temp_output_dir):
        """
        Integration test: CLI with non-existent PDF file.

        Given: Non-existent PDF path
        When: CLI is called
        Then: Returns error exit code and prints error message
        """
        from docscalpel.cli.main import main

        test_args = [
            'pdf-extractor',
            '/nonexistent/file.pdf',
            '--output', str(temp_output_dir)
        ]

        with patch('sys.argv', test_args):
            exit_code = main()

        # Verify: Non-zero exit code
        assert exit_code != 0

    def test_cli_with_invalid_type(self, sample_pdf_path, temp_output_dir):
        """
        Integration test: CLI with invalid element type.

        Given: PDF file
        When: CLI is called with invalid --types value
        Then: Returns error exit code
        """
        from docscalpel.cli.main import main

        test_args = [
            'pdf-extractor',
            sample_pdf_path,
            '--types', 'invalid_type',
            '--output', str(temp_output_dir)
        ]

        with patch('sys.argv', test_args):
            exit_code = main()

        assert exit_code != 0

    def test_cli_with_invalid_confidence(self, sample_pdf_path, temp_output_dir):
        """
        Integration test: CLI with invalid confidence threshold.

        Given: PDF file
        When: CLI is called with confidence > 1.0
        Then: Returns error exit code
        """
        from docscalpel.cli.main import main

        test_args = [
            'pdf-extractor',
            sample_pdf_path,
            '--confidence', '1.5',
            '--output', str(temp_output_dir)
        ]

        with patch('sys.argv', test_args):
            exit_code = main()

        assert exit_code != 0


class TestCLIOutputFormats:
    """Test CLI output formatting."""

    def test_cli_text_output_format(self, sample_pdf_path, temp_output_dir, capsys):
        """
        Integration test: CLI text output format structure.

        Given: PDF file
        When: CLI is called with --format text
        Then: Output follows human-readable format
        """
        from docscalpel.cli.main import main

        test_args = [
            'pdf-extractor',
            sample_pdf_path,
            '--format', 'text',
            '--output', str(temp_output_dir)
        ]

        with patch('sys.argv', test_args):
            exit_code = main()

        assert exit_code == 0

        # Verify: Text output contains key information
        captured = capsys.readouterr()
        assert 'Extracted' in captured.out or 'Success' in captured.out

    def test_cli_help_command(self, capsys):
        """
        Integration test: CLI --help command.

        Given: CLI
        When: Called with --help
        Then: Prints help message and exits successfully
        """
        from docscalpel.cli.main import main

        test_args = ['pdf-extractor', '--help']

        with patch('sys.argv', test_args):
            with pytest.raises(SystemExit) as exc_info:
                main()

        # --help should exit with code 0
        assert exc_info.value.code == 0

        # Verify: Help text was printed
        captured = capsys.readouterr()
        assert 'usage' in captured.out.lower() or 'help' in captured.out.lower()

    def test_cli_version_command(self, capsys):
        """
        Integration test: CLI --version command.

        Given: CLI
        When: Called with --version
        Then: Prints version and exits successfully
        """
        from docscalpel.cli.main import main

        test_args = ['pdf-extractor', '--version']

        with patch('sys.argv', test_args):
            with pytest.raises(SystemExit) as exc_info:
                main()

        # --version should exit with code 0
        assert exc_info.value.code == 0

        # Verify: Version was printed
        captured = capsys.readouterr()
        assert len(captured.out) > 0


class TestCLIVerboseMode:
    """Test CLI verbose/logging modes."""

    def test_cli_with_verbose_flag(self, sample_pdf_path, temp_output_dir, capsys):
        """
        Integration test: CLI with verbose logging.

        Given: PDF file
        When: CLI is called with --verbose
        Then: Detailed logging output is printed
        """
        from docscalpel.cli.main import main

        test_args = [
            'pdf-extractor',
            sample_pdf_path,
            '--verbose',
            '--output', str(temp_output_dir)
        ]

        with patch('sys.argv', test_args):
            exit_code = main()

        assert exit_code == 0

        # Verify: More detailed output in verbose mode
        captured = capsys.readouterr()
        # In verbose mode, should see logging output
        assert len(captured.out) > 0 or len(captured.err) > 0
