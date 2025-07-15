#!/usr/bin/env python3
"""
DEL-007: Development Setup Script
New developer setup automation for the Orchestrator project.

This script automates:
- Python and Node.js dependency installation
- Environment file creation from templates
- Database setup and initialization
- API key configuration (interactive)
- Initial test runs to verify setup

Usage:
    python setup_development.py [--interactive] [--skip-tests] [--environment ENV]

Examples:
    python setup_development.py                    # Interactive setup
    python setup_development.py --no-interactive   # Automated setup
    python setup_development.py --skip-tests       # Skip test verification
"""

import os
import sys
import json
import argparse
import subprocess
import shutil
import getpass
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict

# Import validation from sibling module
try:
    from validate_environment import EnvironmentValidator, ValidationResult
except ImportError:
    print("❌ Cannot import validate_environment module")
    print("   Make sure validate_environment.py is in the same directory")
    sys.exit(1)


@dataclass
class SetupStep:
    """Represents a single setup step."""
    name: str
    description: str
    function: Callable[[], bool]
    required: bool = True
    environment_specific: bool = False
    
    def execute(self) -> bool:
        """Execute this setup step."""
        try:
            return self.function()
        except Exception as e:
            print(f"❌ Step failed: {e}")
            return False


@dataclass
class SetupResult:
    """Results of the complete setup process."""
    success: bool = False
    steps_completed: List[str] = None
    steps_failed: List[Dict[str, str]] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration: float = 0.0
    environment: str = "development"
    recommendations: List[str] = None
    
    def __post_init__(self):
        if self.steps_completed is None:
            self.steps_completed = []
        if self.steps_failed is None:
            self.steps_failed = []
        if self.recommendations is None:
            self.recommendations = []
        if self.start_time is None:
            self.start_time = datetime.now(timezone.utc)
    
    def add_completed_step(self, step_name: str):
        """Add a completed step."""
        self.steps_completed.append(step_name)
    
    def add_failed_step(self, step_name: str, error: str):
        """Add a failed step."""
        self.steps_failed.append({
            'step': step_name,
            'error': error
        })
    
    def is_success(self) -> bool:
        """Check if setup was successful (no critical failures)."""
        return len(self.steps_failed) == 0
    
    def finalize(self):
        """Finalize the setup result."""
        self.end_time = datetime.now(timezone.utc)
        if self.start_time:
            self.duration = (self.end_time - self.start_time).total_seconds()
        self.success = self.is_success()


class DevelopmentSetup:
    """Main development setup class."""
    
    def __init__(self, interactive: bool = True, environment: str = "development"):
        """Initialize setup with configuration."""
        self.interactive = interactive
        self.environment = environment
        self.result = SetupResult(environment=environment)
        
        # Define setup steps
        self.steps = [
            SetupStep(
                name="check_python_version",
                description="Verify Python version requirements",
                function=self._check_python_version,
                required=True
            ),
            SetupStep(
                name="check_node_version", 
                description="Verify Node.js version requirements",
                function=self._check_node_version,
                required=True
            ),
            SetupStep(
                name="install_python_dependencies",
                description="Install Python dependencies",
                function=self._install_python_dependencies,
                required=True
            ),
            SetupStep(
                name="install_node_dependencies",
                description="Install Node.js dependencies", 
                function=self._install_node_dependencies,
                required=True
            ),
            SetupStep(
                name="create_environment_files",
                description="Create environment configuration files",
                function=self._create_environment_files,
                required=True
            ),
            SetupStep(
                name="setup_database",
                description="Initialize database",
                function=self._setup_database,
                required=False
            ),
            SetupStep(
                name="configure_api_keys",
                description="Configure AI provider API keys",
                function=self._configure_api_keys,
                required=False
            )
        ]
    
    def run(self) -> SetupResult:
        """Run the complete setup process."""
        print("🚀 DEL-007 Development Environment Setup")
        print("=" * 45)
        print(f"Environment: {self.environment}")
        print(f"Interactive mode: {'Yes' if self.interactive else 'No'}")
        print()
        
        self.result.start_time = datetime.now(timezone.utc)
        
        # Execute each setup step
        for step in self.steps:
            self._execute_step(step)
        
        # Run final validation
        self._run_final_validation()
        
        # Finalize results
        self.result.finalize()
        
        # Print summary
        self._print_summary()
        
        return self.result
    
    def _execute_step(self, step: SetupStep) -> bool:
        """Execute a single setup step."""
        print(f"📋 {step.description}...")
        
        try:
            success = step.execute()
            
            if success:
                print(f"✅ {step.name} completed")
                self.result.add_completed_step(step.name)
                return True
            else:
                if step.required:
                    print(f"❌ {step.name} failed (required)")
                    self.result.add_failed_step(step.name, "Step failed")
                else:
                    print(f"⚠️  {step.name} failed (optional)")
                    self.result.add_failed_step(step.name, "Step failed (optional)")
                return False
                
        except Exception as e:
            error_msg = str(e)
            if step.required:
                print(f"❌ {step.name} failed: {error_msg}")
                self.result.add_failed_step(step.name, error_msg)
            else:
                print(f"⚠️  {step.name} failed: {error_msg} (optional)")
                self.result.add_failed_step(step.name, f"{error_msg} (optional)")
            return False
    
    def _check_python_version(self) -> bool:
        """Check Python version requirements."""
        version = sys.version_info
        
        if version < (3, 8):
            print(f"   Python {version.major}.{version.minor} found, but 3.8+ required")
            return False
        
        print(f"   Python {version.major}.{version.minor}.{version.micro} ✓")
        
        # Check pip
        try:
            subprocess.run([sys.executable, '-m', 'pip', '--version'], 
                         check=True, capture_output=True)
            print("   pip available ✓")
        except subprocess.CalledProcessError:
            print("   pip not available - installing...")
            try:
                subprocess.run([sys.executable, '-m', 'ensurepip', '--default-pip'],
                             check=True)
            except subprocess.CalledProcessError:
                print("   Failed to install pip")
                return False
        
        return True
    
    def _check_node_version(self) -> bool:
        """Check Node.js version requirements."""
        try:
            result = subprocess.run(['node', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                print("   Node.js not found")
                return False
            
            version_str = result.stdout.strip()
            print(f"   Node.js {version_str} found")
            
            # Parse version
            if version_str.startswith('v'):
                major_version = int(version_str[1:].split('.')[0])
                if major_version < 16:
                    print(f"   Node.js {version_str} is too old (16+ required)")
                    return False
            
            print("   Node.js version ✓")
            return True
            
        except FileNotFoundError:
            print("   Node.js not installed")
            if self.interactive:
                print("   Please install Node.js 16+ from https://nodejs.org")
            return False
        except Exception as e:
            print(f"   Node.js check failed: {e}")
            return False
    
    def _install_python_dependencies(self) -> bool:
        """Install Python dependencies."""
        try:
            # Install backend dependencies
            print("   Installing backend dependencies...")
            backend_dir = Path("backend")
            if backend_dir.exists() and (backend_dir / "requirements.txt").exists():
                subprocess.run([
                    sys.executable, '-m', 'pip', 'install', '-r', 
                    str(backend_dir / "requirements.txt")
                ], check=True, cwd=backend_dir)
                print("   Backend dependencies installed ✓")
            else:
                print("   No backend/requirements.txt found, skipping")
            
            # Install root dependencies if they exist
            if Path("requirements.txt").exists():
                subprocess.run([
                    sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
                ], check=True)
                print("   Root dependencies installed ✓")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"   Failed to install Python dependencies: {e}")
            return False
    
    def _install_node_dependencies(self) -> bool:
        """Install Node.js dependencies."""
        try:
            # Install root dependencies
            if Path("package.json").exists():
                print("   Installing root Node.js dependencies...")
                subprocess.run(['npm', 'install'], check=True, cwd='.')
                print("   Root dependencies installed ✓")
            
            # Install frontend dependencies
            frontend_dir = Path("frontend")
            if frontend_dir.exists() and (frontend_dir / "package.json").exists():
                print("   Installing frontend dependencies...")
                subprocess.run(['npm', 'install'], check=True, cwd=frontend_dir)
                print("   Frontend dependencies installed ✓")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"   Failed to install Node.js dependencies: {e}")
            return False
    
    def _create_environment_files(self) -> bool:
        """Create environment configuration files."""
        try:
            env_files = {
                '.env.defaults': self._get_default_env_content(),
                f'.env.{self.environment}': self._get_environment_specific_content(),
                '.env.example': self._get_example_env_content()
            }
            
            created_files = []
            for filename, content in env_files.items():
                if not Path(filename).exists():
                    with open(filename, 'w') as f:
                        f.write(content)
                    created_files.append(filename)
                    print(f"   Created {filename}")
                else:
                    print(f"   {filename} already exists (skipped)")
            
            # Create .env.local template if it doesn't exist
            if not Path('.env.local').exists():
                local_content = self._get_local_env_template()
                with open('.env.local', 'w') as f:
                    f.write(local_content)
                print("   Created .env.local (for secrets)")
                created_files.append('.env.local')
            
            if created_files:
                print(f"   Created {len(created_files)} environment files ✓")
            else:
                print("   All environment files already exist ✓")
            
            return True
            
        except Exception as e:
            print(f"   Failed to create environment files: {e}")
            return False
    
    def _setup_database(self) -> bool:
        """Initialize database."""
        try:
            # For development, use SQLite by default
            db_url = f"sqlite:///orchestrator_{self.environment}.db"
            
            # Update environment file with database URL
            env_file = f".env.{self.environment}"
            if Path(env_file).exists():
                # Check if DATABASE_URL already set
                with open(env_file, 'r') as f:
                    content = f.read()
                
                if 'DATABASE_URL=' not in content:
                    with open(env_file, 'a') as f:
                        f.write(f"\nDATABASE_URL={db_url}\n")
                    print(f"   Added DATABASE_URL to {env_file}")
            
            print(f"   Database configured: {db_url} ✓")
            return True
            
        except Exception as e:
            print(f"   Database setup failed: {e}")
            return False
    
    def _configure_api_keys(self) -> bool:
        """Configure API keys interactively."""
        if not self.interactive:
            print("   Skipping API key configuration (non-interactive mode)")
            return True
        
        try:
            print("   \n🔑 API Key Configuration")
            print("   " + "-" * 25)
            print("   Configure AI provider API keys for the orchestrator.")
            print("   These will be stored in .env.local (not committed to git).")
            print()
            
            api_providers = {
                'ANTHROPIC_API_KEY': {
                    'name': 'Anthropic (Claude)',
                    'description': 'For Claude AI integration',
                    'url': 'https://console.anthropic.com'
                },
                'OPENAI_API_KEY': {
                    'name': 'OpenAI',
                    'description': 'For GPT integration', 
                    'url': 'https://platform.openai.com'
                },
                'GEMINI_API_KEY': {
                    'name': 'Google Gemini',
                    'description': 'For Gemini AI integration',
                    'url': 'https://makersuite.google.com'
                },
                'XAI_API_KEY': {
                    'name': 'xAI',
                    'description': 'For Grok AI integration',
                    'url': 'https://x.ai'
                }
            }
            
            configured_keys = []
            
            for key_name, info in api_providers.items():
                # Check if already configured
                current_value = os.environ.get(key_name) or self._get_from_env_file('.env.local', key_name)
                
                if current_value:
                    print(f"   {info['name']}: Already configured ✓")
                    continue
                
                # Ask user if they want to configure this key
                response = input(f"   Configure {info['name']} API key? (y/N): ").strip().lower()
                
                if response in ['y', 'yes']:
                    print(f"   Get your API key from: {info['url']}")
                    api_key = getpass.getpass(f"   Enter {info['name']} API key: ").strip()
                    
                    if api_key:
                        self._add_to_env_local(key_name, api_key)
                        configured_keys.append(info['name'])
                        print(f"   ✅ {info['name']} API key configured")
                    else:
                        print(f"   ⏭️  Skipped {info['name']} API key")
                else:
                    print(f"   ⏭️  Skipped {info['name']} API key")
            
            if configured_keys:
                print(f"   \n✅ Configured API keys for: {', '.join(configured_keys)}")
            else:
                print("   ⚠️  No API keys configured - some features may not work")
            
            return True
            
        except Exception as e:
            print(f"   API key configuration failed: {e}")
            return False
    
    def _run_final_validation(self):
        """Run final environment validation."""
        print("\n🔍 Final Environment Validation")
        print("-" * 35)
        
        try:
            validator = EnvironmentValidator(environment=self.environment)
            result = validator.validate()
            
            if result.is_valid:
                print("✅ Environment validation passed!")
            else:
                print("⚠️  Environment validation found issues:")
                for error in result.errors[:3]:  # Show first 3 errors
                    print(f"   ❌ {error.message}")
                if len(result.errors) > 3:
                    print(f"   ... and {len(result.errors) - 3} more errors")
                
                for warning in result.warnings[:2]:  # Show first 2 warnings
                    print(f"   ⚠️  {warning.message}")
                if len(result.warnings) > 2:
                    print(f"   ... and {len(result.warnings) - 2} more warnings")
            
        except Exception as e:
            print(f"❌ Validation failed: {e}")
    
    def _print_summary(self):
        """Print setup summary."""
        print("\n📊 Setup Summary")
        print("=" * 20)
        print(f"Duration: {self.result.duration:.1f} seconds")
        print(f"Steps completed: {len(self.result.steps_completed)}")
        print(f"Steps failed: {len(self.result.steps_failed)}")
        
        if self.result.is_success():
            print("\n🎉 Setup completed successfully!")
            print("\nNext steps:")
            print("1. Run: npm run start:dev")
            print("2. Open: http://localhost:5174 (frontend)")
            print("3. API: http://localhost:8000 (backend)")
        else:
            print("\n⚠️  Setup completed with issues:")
            for failure in self.result.steps_failed:
                print(f"   - {failure['step']}: {failure['error']}")
            print("\nResolve issues and re-run setup if needed.")
    
    def _get_default_env_content(self) -> str:
        """Get default environment file content."""
        return """# Default environment configuration
# These values are used across all environments unless overridden

# Application
APP_NAME=orchestrator
VERSION=1.0.0

# Logging
LOG_LEVEL=INFO

# Database (default to SQLite)
DATABASE_URL=sqlite:///orchestrator.db

# API Settings
API_HOST=0.0.0.0
API_PORT=8000

# Frontend
FRONTEND_PORT=5174
"""
    
    def _get_environment_specific_content(self) -> str:
        """Get environment-specific configuration."""
        if self.environment == "development":
            return """# Development environment configuration
ENVIRONMENT=development
DEBUG=true

# Development database
DATABASE_URL=sqlite:///orchestrator_dev.db

# API settings
API_PORT=8000
API_HOST=localhost

# Frontend
FRONTEND_PORT=5174
"""
        elif self.environment == "staging":
            return """# Staging environment configuration
ENVIRONMENT=staging
DEBUG=false

# Staging database
DATABASE_URL=sqlite:///orchestrator_staging.db

# API settings
API_PORT=8001
API_HOST=localhost

# Frontend
FRONTEND_PORT=5175
"""
        elif self.environment == "production":
            return """# Production environment configuration
ENVIRONMENT=production
DEBUG=false

# Production database (PostgreSQL recommended)
# DATABASE_URL=postgresql://user:password@localhost/orchestrator_prod

# API settings
API_PORT=8002
API_HOST=0.0.0.0

# Frontend
FRONTEND_PORT=5176
"""
        else:
            return f"# {self.environment} environment configuration\nENVIRONMENT={self.environment}\n"
    
    def _get_example_env_content(self) -> str:
        """Get example environment file content."""
        return """# Example environment configuration
# Copy this file to .env.local and configure your secrets

# AI Provider API Keys (get from respective providers)
ANTHROPIC_API_KEY=sk-ant-your-key-here
OPENAI_API_KEY=sk-your-openai-key-here
GEMINI_API_KEY=your-gemini-key-here
XAI_API_KEY=xai-your-key-here

# Database URL (for production)
# DATABASE_URL=postgresql://username:password@host:port/database

# Optional: Override any default settings
# DEBUG=true
# LOG_LEVEL=DEBUG
"""
    
    def _get_local_env_template(self) -> str:
        """Get local environment template content."""
        return """# Local environment secrets
# This file is git-ignored and should contain your personal API keys

# Configure at least one AI provider API key:

# Anthropic Claude (recommended)
# ANTHROPIC_API_KEY=sk-ant-your-key-here

# OpenAI GPT
# OPENAI_API_KEY=sk-your-openai-key-here

# Google Gemini
# GEMINI_API_KEY=your-gemini-key-here

# xAI Grok
# XAI_API_KEY=xai-your-key-here

# Uncomment and configure the keys you want to use
"""
    
    def _get_from_env_file(self, file_path: str, key: str) -> Optional[str]:
        """Get value from environment file."""
        try:
            if not Path(file_path).exists():
                return None
            
            with open(file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith(f"{key}="):
                        return line.split('=', 1)[1].strip('"\'')
        except Exception:
            pass
        return None
    
    def _add_to_env_local(self, key: str, value: str):
        """Add key-value pair to .env.local file."""
        env_local = Path('.env.local')
        
        # Read existing content
        existing_content = ""
        if env_local.exists():
            with open(env_local, 'r') as f:
                existing_content = f.read()
        
        # Check if key already exists
        lines = existing_content.split('\n')
        key_exists = False
        
        for i, line in enumerate(lines):
            if line.strip().startswith(f"{key}="):
                lines[i] = f"{key}={value}"
                key_exists = True
                break
        
        if not key_exists:
            if existing_content and not existing_content.endswith('\n'):
                existing_content += '\n'
            existing_content += f"{key}={value}\n"
        else:
            existing_content = '\n'.join(lines)
        
        # Write back to file
        with open(env_local, 'w') as f:
            f.write(existing_content)


# Convenience functions for direct use
def install_python_dependencies(create_venv: bool = False) -> bool:
    """Install Python dependencies."""
    setup = DevelopmentSetup(interactive=False)
    return setup._install_python_dependencies()


def install_node_dependencies() -> bool:
    """Install Node.js dependencies."""
    setup = DevelopmentSetup(interactive=False)
    return setup._install_node_dependencies()


def create_environment_files(interactive: bool = False, overwrite: bool = False) -> bool:
    """Create environment files from templates."""
    setup = DevelopmentSetup(interactive=interactive)
    return setup._create_environment_files()


def setup_database(environment: str = "development", run_migrations: bool = False, seed_data: bool = False) -> bool:
    """Setup database for specified environment."""
    setup = DevelopmentSetup(interactive=False, environment=environment)
    return setup._setup_database()


def validate_api_keys_interactive() -> bool:
    """Interactive API key validation and setup."""
    setup = DevelopmentSetup(interactive=True)
    return setup._configure_api_keys()


def run_initial_tests(components: List[str] = None) -> bool:
    """Run initial tests to verify setup."""
    if components is None:
        components = ["backend", "frontend"]
    
    try:
        success = True
        
        if "backend" in components:
            print("Running backend tests...")
            result = subprocess.run(
                [sys.executable, '-m', 'pytest', 'backend/tests/', '-v'],
                capture_output=True
            )
            if result.returncode != 0:
                print("❌ Backend tests failed")
                success = False
            else:
                print("✅ Backend tests passed")
        
        if "frontend" in components:
            print("Running frontend tests...")
            result = subprocess.run(['npm', 'test'], cwd='frontend', capture_output=True)
            if result.returncode != 0:
                print("❌ Frontend tests failed")
                success = False
            else:
                print("✅ Frontend tests passed")
        
        return success
        
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        return False


def complete_setup_flow(interactive: bool = True, skip_tests: bool = False) -> SetupResult:
    """Run complete setup flow."""
    setup = DevelopmentSetup(interactive=interactive)
    result = setup.run()
    
    if not skip_tests and result.is_success():
        print("\n🧪 Running initial tests...")
        test_success = run_initial_tests()
        if not test_success:
            result.add_failed_step("initial_tests", "Some tests failed")
    
    return result


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Setup development environment for DEL-007",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Interactive setup
  %(prog)s --no-interactive         # Automated setup
  %(prog)s --skip-tests            # Skip test verification
  %(prog)s --environment staging   # Setup for staging
        """
    )
    
    parser.add_argument(
        '--interactive', 
        action='store_true',
        default=True,
        help='Interactive mode (default)'
    )
    
    parser.add_argument(
        '--no-interactive',
        action='store_false', 
        dest='interactive',
        help='Non-interactive mode'
    )
    
    parser.add_argument(
        '--skip-tests',
        action='store_true',
        help='Skip initial test runs'
    )
    
    parser.add_argument(
        '--environment', '-e',
        default='development',
        choices=['development', 'staging', 'production'],
        help='Environment to setup (default: development)'
    )
    
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results as JSON'
    )
    
    args = parser.parse_args()
    
    try:
        result = complete_setup_flow(
            interactive=args.interactive,
            skip_tests=args.skip_tests
        )
        
        if args.json:
            output = asdict(result)
            # Convert datetime objects to strings for JSON serialization
            if output.get('start_time'):
                output['start_time'] = output['start_time'].isoformat()
            if output.get('end_time'):
                output['end_time'] = output['end_time'].isoformat()
            print(json.dumps(output, indent=2))
        
        sys.exit(0 if result.is_success() else 1)
        
    except KeyboardInterrupt:
        print("\n⚠️  Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Setup failed with error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()