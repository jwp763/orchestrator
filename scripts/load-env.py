#!/usr/bin/env python3
"""
Environment loader utility for startup scripts.
Replaces shell variable substitution with proper layered configuration.
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.env_loader import load_environment_config, validate_api_keys


def load_and_export_environment(environment: str = 'development') -> bool:
    """
    Load environment configuration and export to shell environment.
    
    Args:
        environment: Environment name (development, staging, production)
        
    Returns:
        True if successful, False if critical configuration is missing
    """
    try:
        # Load configuration
        config = load_environment_config(environment)
        
        if not config:
            print(f"❌ Failed to load configuration for environment: {environment}")
            return False
        
        # Export to environment
        for key, value in config.items():
            os.environ[key] = str(value)
        
        # Validate critical configuration
        is_valid, missing_keys = validate_api_keys(config)
        
        print(f"🔧 Loaded {len(config)} environment variables for: {environment}")
        
        if not is_valid:
            print(f"⚠️  Missing API keys: {', '.join(missing_keys)}")
            print(f"💡 Copy .env.example to .env.local and add your API keys")
            
            # Don't fail for missing API keys - allow development without all keys
            return True
        else:
            print(f"✅ All required API keys configured")
            return True
            
    except Exception as e:
        print(f"❌ Error loading environment: {e}")
        return False


def print_environment_summary(environment: str = 'development'):
    """Print a summary of the loaded environment configuration."""
    from scripts.env_loader import get_environment_info
    
    info = get_environment_info(environment)
    
    print(f"\n📋 Environment Summary")
    print(f"   Environment: {info['environment']}")
    print(f"   Files loaded: {sum(info['files_found'].values())}/4")
    print(f"   Variables: {info['config_count']}")
    print(f"   Shell substitution: {'❌ Detected' if info['shell_substitution_detected'] else '✅ None'}")
    
    # Show which files were loaded
    for file_type, exists in info['files_found'].items():
        status = '✅' if exists else '❌'
        print(f"   .env.{file_type}: {status}")


if __name__ == '__main__':
    """Command-line interface for loading environment."""
    
    # Get environment from command line argument
    environment = sys.argv[1] if len(sys.argv) > 1 else 'development'
    
    print(f"🚀 Loading environment configuration: {environment}")
    print("=" * 55)
    
    # Load and export environment
    success = load_and_export_environment(environment)
    
    # Print summary
    print_environment_summary(environment)
    
    if success:
        print(f"\n✅ Environment '{environment}' loaded successfully!")
        
        # Print environment variables for shell to export
        config = load_environment_config(environment)
        print(f"\n# Export the following variables:")
        for key, value in sorted(config.items()):
            # Escape shell special characters
            escaped_value = value.replace('"', '\\"').replace('$', '\\$')
            print(f'export {key}="{escaped_value}"')
        
        sys.exit(0)
    else:
        print(f"\n❌ Failed to load environment '{environment}'")
        sys.exit(1)