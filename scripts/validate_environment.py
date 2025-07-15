#!/usr/bin/env python3
"""
DEL-007: Environment Validation Script
Comprehensive validation script to help developers set up environments correctly.

This script validates:
- Python and Node.js versions
- Database connectivity
- API key configuration
- Required directories and files
- Environment-specific requirements

Usage:
    python validate_environment.py [--environment ENV] [--quiet] [--json]

Examples:
    python validate_environment.py                    # Validate current environment
    python validate_environment.py --environment production  # Validate production
    python validate_environment.py --json            # JSON output
"""

import os
import sys
import json
import argparse
import subprocess
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict


@dataclass
class ValidationError:
    """Represents a validation error or warning."""
    code: str
    message: str
    suggestion: str
    severity: str = "error"  # error, warning, info
    
    def __str__(self):
        return f"[{self.severity.upper()}] {self.code}: {self.message}"


@dataclass
class ValidationResult:
    """Results of environment validation."""
    is_valid: bool
    environment: str
    errors: List[ValidationError]
    warnings: List[ValidationError]
    timestamp: str = None
    duration_seconds: float = 0.0
    recommendations: List[str] = None
    
    def __post_init__(self):
        if self.recommendations is None:
            self.recommendations = []
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc).isoformat()
    
    def get_summary(self) -> str:
        """Get a human-readable summary of validation results."""
        error_count = len(self.errors)
        warning_count = len(self.warnings)
        
        if self.is_valid:
            status = "✅ VALID"
        else:
            status = "❌ INVALID"
        
        summary = f"{status} - Environment: {self.environment}\n"
        summary += f"Errors: {error_count}, Warnings: {warning_count}\n"
        summary += f"Validated at: {self.timestamp}\n"
        summary += f"Duration: {self.duration_seconds:.2f}s"
        
        return summary
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'is_valid': self.is_valid,
            'environment': self.environment,
            'errors': [asdict(error) for error in self.errors],
            'warnings': [asdict(warning) for warning in self.warnings],
            'timestamp': self.timestamp,
            'duration_seconds': self.duration_seconds,
            'recommendations': self.recommendations,
            'summary': self.get_summary()
        }


class EnvironmentValidator:
    """Main environment validation class."""
    
    def __init__(self, environment: Optional[str] = None):
        """Initialize validator for specific environment."""
        self.environment = environment or self._detect_environment()
        self.errors: List[ValidationError] = []
        self.warnings: List[ValidationError] = []
        self.recommendations: List[str] = []
        
    def _detect_environment(self) -> str:
        """Detect current environment from environment variables."""
        env = os.environ.get('ENVIRONMENT', '').lower()
        if env in ['development', 'staging', 'production']:
            return env
        
        # Try to detect from other common variables
        if os.environ.get('DEBUG', '').lower() == 'true':
            return 'development'
        
        return 'development'  # Default
    
    def validate(self) -> ValidationResult:
        """Run complete environment validation."""
        start_time = time.time()
        
        # Reset state
        self.errors = []
        self.warnings = []
        self.recommendations = []
        
        # Run all validation checks
        self._check_python_version()
        self._check_node_version()
        self._check_database_accessibility()
        self._check_api_keys()
        self._check_required_directories()
        self._check_environment_files()
        
        # Determine overall validity
        is_valid = len(self.errors) == 0
        
        # Generate recommendations
        self._generate_recommendations()
        
        end_time = time.time()
        duration = end_time - start_time
        
        return ValidationResult(
            is_valid=is_valid,
            environment=self.environment,
            errors=self.errors,
            warnings=self.warnings,
            timestamp=datetime.now(timezone.utc).isoformat(),
            duration_seconds=duration,
            recommendations=self.recommendations
        )
    
    def check_all(self) -> ValidationResult:
        """Alias for validate() method."""
        return self.validate()
    
    def _check_python_version(self) -> None:
        """Check Python version requirements."""
        try:
            version = sys.version_info
            
            if version < (3, 8):
                self.errors.append(ValidationError(
                    code="PYTHON_VERSION_TOO_OLD",
                    message=f"Python {version.major}.{version.minor} is too old. Python 3.8+ required.",
                    suggestion="Install Python 3.8 or newer"
                ))
            else:
                # Check for pip
                try:
                    import pip
                except ImportError:
                    self.warnings.append(ValidationError(
                        code="PIP_NOT_AVAILABLE",
                        message="pip is not available",
                        suggestion="Install pip for package management",
                        severity="warning"
                    ))
                    
        except Exception as e:
            self.errors.append(ValidationError(
                code="PYTHON_CHECK_FAILED",
                message=f"Failed to check Python version: {e}",
                suggestion="Ensure Python is properly installed"
            ))
    
    def _check_node_version(self) -> None:
        """Check Node.js version requirements."""
        try:
            result = subprocess.run(
                ['node', '--version'], 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            
            if result.returncode != 0:
                self.errors.append(ValidationError(
                    code="NODE_NOT_FOUND",
                    message="Node.js is not installed or not in PATH",
                    suggestion="Install Node.js 16+ from https://nodejs.org"
                ))
                return
            
            version_str = result.stdout.strip()
            # Parse version like "v18.0.0"
            if version_str.startswith('v'):
                version_parts = version_str[1:].split('.')
                major_version = int(version_parts[0])
                
                if major_version < 16:
                    self.errors.append(ValidationError(
                        code="NODE_VERSION_TOO_OLD",
                        message=f"Node.js {version_str} is too old. Node.js 16+ required.",
                        suggestion="Install Node.js 16 or newer"
                    ))
            
        except FileNotFoundError:
            self.errors.append(ValidationError(
                code="NODE_NOT_FOUND",
                message="Node.js is not installed or not in PATH",
                suggestion="Install Node.js 16+ from https://nodejs.org"
            ))
        except subprocess.TimeoutExpired:
            self.warnings.append(ValidationError(
                code="NODE_CHECK_TIMEOUT",
                message="Node.js version check timed out",
                suggestion="Check Node.js installation",
                severity="warning"
            ))
        except Exception as e:
            self.warnings.append(ValidationError(
                code="NODE_CHECK_FAILED",
                message=f"Failed to check Node.js version: {e}",
                suggestion="Check Node.js installation",
                severity="warning"
            ))
    
    def _check_database_accessibility(self) -> None:
        """Check database connectivity."""
        database_url = os.environ.get('DATABASE_URL')
        
        if not database_url:
            # Check environment-specific files
            env_file = f".env.{self.environment}"
            if os.path.exists(env_file):
                database_url = self._get_from_env_file(env_file, 'DATABASE_URL')
            
            if not database_url:
                if self.environment == 'production':
                    self.errors.append(ValidationError(
                        code="DATABASE_URL_MISSING",
                        message="DATABASE_URL not configured",
                        suggestion="Set DATABASE_URL in environment or .env file"
                    ))
                else:
                    self.warnings.append(ValidationError(
                        code="DATABASE_URL_MISSING",
                        message="DATABASE_URL not configured",
                        suggestion="Set DATABASE_URL in .env file for database features",
                        severity="warning"
                    ))
                return
        
        # Validate database URL format and connectivity
        if database_url.startswith('sqlite:///'):
            self._check_sqlite_database(database_url)
        elif database_url.startswith('postgresql://'):
            self._check_postgresql_database(database_url)
        else:
            self.errors.append(ValidationError(
                code="INVALID_DATABASE_URL",
                message=f"Unsupported database URL format: {database_url[:20]}...",
                suggestion="Use sqlite:/// or postgresql:// URL format"
            ))
    
    def _check_sqlite_database(self, database_url: str) -> None:
        """Check SQLite database accessibility."""
        try:
            # Extract file path from sqlite:///path
            db_path = database_url[10:]  # Remove 'sqlite:///'
            
            # Check if directory exists
            db_dir = os.path.dirname(db_path)
            if db_dir and not os.path.exists(db_dir):
                self.errors.append(ValidationError(
                    code="DATABASE_DIRECTORY_MISSING",
                    message=f"Database directory does not exist: {db_dir}",
                    suggestion="Create the database directory or update DATABASE_URL"
                ))
                return
            
            # Try to connect to database
            conn = sqlite3.connect(db_path, timeout=5.0)
            conn.execute("SELECT 1")
            conn.close()
            
        except sqlite3.Error as e:
            self.errors.append(ValidationError(
                code="SQLITE_CONNECTION_FAILED",
                message=f"Cannot connect to SQLite database: {e}",
                suggestion="Check database file permissions and path"
            ))
        except Exception as e:
            self.errors.append(ValidationError(
                code="DATABASE_CHECK_FAILED",
                message=f"Database connectivity check failed: {e}",
                suggestion="Verify database configuration"
            ))
    
    def _check_postgresql_database(self, database_url: str) -> None:
        """Check PostgreSQL database accessibility."""
        try:
            # For now, just validate URL format
            # Full connectivity testing would require psycopg2
            import urllib.parse
            parsed = urllib.parse.urlparse(database_url)
            
            if not parsed.hostname:
                self.errors.append(ValidationError(
                    code="INVALID_POSTGRESQL_URL",
                    message="PostgreSQL URL missing hostname",
                    suggestion="Use format: postgresql://user:pass@host:port/dbname"
                ))
            
            if not parsed.username:
                self.warnings.append(ValidationError(
                    code="POSTGRESQL_NO_USERNAME",
                    message="PostgreSQL URL missing username",
                    suggestion="Include username in DATABASE_URL",
                    severity="warning"
                ))
                
        except Exception as e:
            self.warnings.append(ValidationError(
                code="POSTGRESQL_CHECK_FAILED",
                message=f"PostgreSQL URL validation failed: {e}",
                suggestion="Verify PostgreSQL DATABASE_URL format",
                severity="warning"
            ))
    
    def _check_api_keys(self) -> None:
        """Check API key configuration."""
        api_keys = {
            'ANTHROPIC_API_KEY': 'sk-ant-',
            'OPENAI_API_KEY': 'sk-',
            'GEMINI_API_KEY': '',  # Varies
            'XAI_API_KEY': 'xai-'
        }
        
        missing_keys = []
        invalid_keys = []
        
        for key_name, expected_prefix in api_keys.items():
            key_value = os.environ.get(key_name)
            
            if not key_value:
                # Check environment file
                env_file = f".env.{self.environment}"
                if os.path.exists(env_file):
                    key_value = self._get_from_env_file(env_file, key_name)
                
                # Also check .env.local for secrets
                if not key_value and os.path.exists('.env.local'):
                    key_value = self._get_from_env_file('.env.local', key_name)
            
            if not key_value:
                missing_keys.append(key_name)
            elif expected_prefix and not key_value.startswith(expected_prefix):
                invalid_keys.append(key_name)
        
        # Handle missing keys based on environment
        if missing_keys:
            if self.environment == 'production':
                if len(missing_keys) >= len(api_keys):
                    self.errors.append(ValidationError(
                        code="NO_API_KEYS_CONFIGURED",
                        message="No AI provider API keys configured",
                        suggestion="Configure at least one API key (Anthropic, OpenAI, Gemini, or XAI)"
                    ))
                else:
                    for key in missing_keys:
                        self.warnings.append(ValidationError(
                            code="API_KEY_MISSING",
                            message=f"{key} not configured",
                            suggestion=f"Set {key} in .env.local or environment variables",
                            severity="warning"
                        ))
            else:
                # Development/staging - more lenient
                if len(missing_keys) >= len(api_keys):
                    self.warnings.append(ValidationError(
                        code="NO_API_KEYS_CONFIGURED",
                        message="No AI provider API keys configured",
                        suggestion="Configure at least one API key for AI features",
                        severity="warning"
                    ))
        
        # Handle invalid key formats
        for key in invalid_keys:
            self.warnings.append(ValidationError(
                code="API_KEY_INVALID_FORMAT",
                message=f"{key} has unexpected format",
                suggestion=f"Verify {key} format is correct",
                severity="warning"
            ))
    
    def _check_required_directories(self) -> None:
        """Check required project directories exist."""
        required_dirs = [
            'backend',
            'frontend', 
            'scripts',
            'docs'
        ]
        
        for dir_name in required_dirs:
            if not os.path.exists(dir_name):
                self.errors.append(ValidationError(
                    code="MISSING_DIRECTORY",
                    message=f"Required directory '{dir_name}' not found",
                    suggestion=f"Create {dir_name}/ directory or run from project root"
                ))
            elif not os.path.isdir(dir_name):
                self.errors.append(ValidationError(
                    code="INVALID_DIRECTORY",
                    message=f"'{dir_name}' exists but is not a directory",
                    suggestion=f"Remove file and create {dir_name}/ directory"
                ))
    
    def _check_environment_files(self) -> None:
        """Check environment configuration files."""
        env_file = f".env.{self.environment}"
        
        if not os.path.exists(env_file):
            if self.environment == 'production':
                self.errors.append(ValidationError(
                    code="MISSING_ENV_FILE",
                    message=f"Environment file {env_file} not found",
                    suggestion=f"Create {env_file} with production configuration"
                ))
            else:
                self.warnings.append(ValidationError(
                    code="MISSING_ENV_FILE",
                    message=f"Environment file {env_file} not found",
                    suggestion=f"Create {env_file} from .env.example template",
                    severity="warning"
                ))
        
        # Check for .env.example
        if not os.path.exists('.env.example'):
            self.warnings.append(ValidationError(
                code="MISSING_ENV_EXAMPLE",
                message=".env.example template not found",
                suggestion="Create .env.example as template for new developers",
                severity="warning"
            ))
    
    def _get_from_env_file(self, file_path: str, key: str) -> Optional[str]:
        """Get value from environment file."""
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith(f"{key}="):
                        return line.split('=', 1)[1].strip('"\'')
        except Exception:
            pass
        return None
    
    def _generate_recommendations(self) -> None:
        """Generate actionable recommendations based on validation results."""
        if self.errors or self.warnings:
            self.recommendations.append("Review and fix validation errors and warnings above")
        
        if any(error.code.startswith("API_KEY") for error in self.errors + self.warnings):
            self.recommendations.append("Configure API keys in .env.local file (not committed to git)")
        
        if any(error.code.startswith("DATABASE") for error in self.errors + self.warnings):
            self.recommendations.append("Verify database configuration and connectivity")
        
        if any(error.code.startswith("NODE") for error in self.errors + self.warnings):
            self.recommendations.append("Install or update Node.js from https://nodejs.org")
        
        if any(error.code.startswith("PYTHON") for error in self.errors + self.warnings):
            self.recommendations.append("Install or update Python from https://python.org")
        
        if not self.errors and not self.warnings:
            self.recommendations.append("Environment validation passed! Ready for development.")


# Convenience functions for direct use
def check_python_version() -> ValidationResult:
    """Check Python version requirements."""
    validator = EnvironmentValidator()
    validator._check_python_version()
    
    return ValidationResult(
        is_valid=len(validator.errors) == 0,
        environment="check",
        errors=validator.errors,
        warnings=validator.warnings,
        timestamp=datetime.now(timezone.utc).isoformat()
    )


def check_node_version() -> ValidationResult:
    """Check Node.js version requirements."""
    validator = EnvironmentValidator()
    validator._check_node_version()
    
    return ValidationResult(
        is_valid=len(validator.errors) == 0,
        environment="check",
        errors=validator.errors,
        warnings=validator.warnings,
        timestamp=datetime.now(timezone.utc).isoformat()
    )


def check_database_accessibility(database_url: str) -> ValidationResult:
    """Check database accessibility."""
    validator = EnvironmentValidator()
    os.environ['DATABASE_URL'] = database_url
    validator._check_database_accessibility()
    
    return ValidationResult(
        is_valid=len(validator.errors) == 0,
        environment="check",
        errors=validator.errors,
        warnings=validator.warnings,
        timestamp=datetime.now(timezone.utc).isoformat()
    )


def check_api_keys(environment: str = "development") -> ValidationResult:
    """Check API keys configuration."""
    validator = EnvironmentValidator(environment=environment)
    validator._check_api_keys()
    
    return ValidationResult(
        is_valid=len(validator.errors) == 0,
        environment=environment,
        errors=validator.errors,
        warnings=validator.warnings,
        timestamp=datetime.now(timezone.utc).isoformat()
    )


def check_required_directories() -> ValidationResult:
    """Check required directories exist."""
    validator = EnvironmentValidator()
    validator._check_required_directories()
    
    return ValidationResult(
        is_valid=len(validator.errors) == 0,
        environment="check",
        errors=validator.errors,
        warnings=validator.warnings,
        timestamp=datetime.now(timezone.utc).isoformat()
    )


def check_environment_files(environment: str = "development") -> ValidationResult:
    """Check environment files exist."""
    validator = EnvironmentValidator(environment=environment)
    validator._check_environment_files()
    
    return ValidationResult(
        is_valid=len(validator.errors) == 0,
        environment=environment,
        errors=validator.errors,
        warnings=validator.warnings,
        timestamp=datetime.now(timezone.utc).isoformat()
    )


def validate_all_environments() -> Dict[str, ValidationResult]:
    """Validate all environments (development, staging, production)."""
    environments = ["development", "staging", "production"]
    results = {}
    
    for env in environments:
        validator = EnvironmentValidator(environment=env)
        results[env] = validator.validate()
    
    return results


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Validate environment configuration for DEL-007",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                              # Validate current environment
  %(prog)s --environment production     # Validate production environment
  %(prog)s --json                       # Output JSON format
  %(prog)s --quiet                      # Minimal output
        """
    )
    
    parser.add_argument(
        '--environment', '-e',
        choices=['development', 'staging', 'production'],
        help='Environment to validate (default: auto-detect)'
    )
    
    parser.add_argument(
        '--json', '-j',
        action='store_true',
        help='Output results as JSON'
    )
    
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Minimal output (errors only)'
    )
    
    parser.add_argument(
        '--all',
        action='store_true',
        help='Validate all environments'
    )
    
    args = parser.parse_args()
    
    try:
        if args.all:
            results = validate_all_environments()
            
            if args.json:
                output = {env: result.to_dict() for env, result in results.items()}
                print(json.dumps(output, indent=2))
            else:
                for env, result in results.items():
                    print(f"\n{'='*50}")
                    print(f"Environment: {env.upper()}")
                    print('='*50)
                    print(result.get_summary())
                    
                    if not args.quiet:
                        for error in result.errors:
                            print(f"❌ {error}")
                        for warning in result.warnings:
                            print(f"⚠️  {warning}")
            
            # Exit with error if any environment is invalid
            any_invalid = any(not result.is_valid for result in results.values())
            sys.exit(1 if any_invalid else 0)
        
        else:
            validator = EnvironmentValidator(environment=args.environment)
            result = validator.validate()
            
            if args.json:
                print(json.dumps(result.to_dict(), indent=2))
            else:
                print(result.get_summary())
                print()
                
                if not args.quiet:
                    if result.errors:
                        print("ERRORS:")
                        for error in result.errors:
                            print(f"❌ {error}")
                        print()
                    
                    if result.warnings:
                        print("WARNINGS:")
                        for warning in result.warnings:
                            print(f"⚠️  {warning}")
                        print()
                    
                    if result.recommendations:
                        print("RECOMMENDATIONS:")
                        for rec in result.recommendations:
                            print(f"💡 {rec}")
                        print()
            
            sys.exit(0 if result.is_valid else 1)
    
    except KeyboardInterrupt:
        print("\n⚠️  Validation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Validation failed with error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()