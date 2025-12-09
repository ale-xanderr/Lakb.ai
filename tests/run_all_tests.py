#!/usr/bin/env python3
"""
All-in-One Test Runner for LAKb.ai

This script runs all unit and integration tests with coverage reporting.
It provides a simple interface for running different test suites.

Usage:
    python tests/run_all_tests.py                    # Run all tests
    python tests/run_all_tests.py --unit            # Run only unit tests
    python tests/run_all_tests.py --integration     # Run only integration tests
    python tests/run_all_tests.py --file tests/test_api_service.py  # Run specific file
    python tests/run_all_tests.py --html            # Generate HTML coverage report
    python tests/run_all_tests.py --no-coverage     # Skip coverage reporting
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path


def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")


def print_summary(text, status="INFO"):
    """Print a formatted summary message."""
    symbols = {
        "SUCCESS": "✓",
        "ERROR": "✗",
        "INFO": "ℹ",
        "WARNING": "⚠"
    }
    symbol = symbols.get(status, "•")
    print(f"\n{symbol} {text}\n")


def check_dependencies():
    """Check if required test dependencies are installed."""
    print_header("Checking Dependencies")
    
    required = [
        "pytest",
        "pytest-cov",
        "pytest-mock",
        "pytest-asyncio"
    ]
    
    missing = []
    for package in required:
        try:
            __import__(package.replace("-", "_"))
            print(f"✓ {package} is installed")
        except ImportError:
            print(f"✗ {package} is NOT installed")
            missing.append(package)
    
    if missing:
        print_summary(
            f"Missing dependencies: {', '.join(missing)}\n"
            f"Install with: pip install {' '.join(missing)}",
            "ERROR"
        )
        return False
    
    print_summary("All dependencies are installed", "SUCCESS")
    return True


def run_tests(args):
    """Run tests based on command line arguments."""
    # Build pytest command
    cmd = ["pytest"]
    
    # Add test discovery path
    if args.file:
        cmd.append(args.file)
    else:
        cmd.append("tests/")
    
    # Add markers for filtering
    if args.unit:
        cmd.extend(["-m", "unit"])
        print_header("Running Unit Tests")
    elif args.integration:
        cmd.extend(["-m", "integration"])
        print_header("Running Integration Tests")
    else:
        print_header("Running All Tests")
    
    # Add coverage if requested
    if not args.no_coverage:
        cmd.extend([
            "--cov=src",
            "--cov-report=term-missing",
        ])
        
        if args.html:
            cmd.append("--cov-report=html")
    
    # Add verbose output
    if args.verbose:
        cmd.append("-vv")
    else:
        cmd.append("-v")
    
    # Add color output
    cmd.append("--color=yes")
    
    # Show test summary
    cmd.append("-ra")
    
    # Run the tests
    print(f"Command: {' '.join(cmd)}\n")
    
    try:
        result = subprocess.run(cmd, cwd=Path(__file__).parent.parent)
        return result.returncode
    except KeyboardInterrupt:
        print_summary("Tests interrupted by user", "WARNING")
        return 130
    except Exception as e:
        print_summary(f"Error running tests: {e}", "ERROR")
        return 1


def main():
    """Main entry point for test runner."""
    parser = argparse.ArgumentParser(
        description="Run LAKb.ai test suite with coverage reporting",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          Run all tests with coverage
  %(prog)s --unit                   Run only unit tests
  %(prog)s --integration            Run only integration tests
  %(prog)s --file tests/test_api_service.py    Run specific test file
  %(prog)s --html                   Generate HTML coverage report
  %(prog)s --no-coverage            Skip coverage reporting
  %(prog)s -v                       Verbose output
        """
    )
    
    parser.add_argument(
        "--unit",
        action="store_true",
        help="Run only unit tests"
    )
    
    parser.add_argument(
        "--integration",
        action="store_true",
        help="Run only integration tests"
    )
    
    parser.add_argument(
        "--file",
        type=str,
        help="Run specific test file"
    )
    
    parser.add_argument(
        "--html",
        action="store_true",
        help="Generate HTML coverage report in htmlcov/"
    )
    
    parser.add_argument(
        "--no-coverage",
        action="store_true",
        help="Skip coverage reporting"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    # Check dependencies first
    if not check_dependencies():
        print_summary(
            "Please install missing dependencies before running tests",
            "ERROR"
        )
        return 1
    
    # Run tests
    exit_code = run_tests(args)
    
    # Print final summary
    if exit_code == 0:
        print_summary("All tests passed!", "SUCCESS")
        
        if args.html and not args.no_coverage:
            print_summary(
                "HTML coverage report generated in htmlcov/index.html",
                "INFO"
            )
    else:
        print_summary("Some tests failed. See output above for details.", "ERROR")
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
