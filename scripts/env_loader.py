"""
Environment Configuration Loader for DEL-004
Implements layered environment configuration without shell variable substitution.

Precedence order (highest to lowest):
1. .env.local (local secrets, gitignored)
2. .env.{environment} (environment-specific, e.g., .env.development)
3. .env.defaults (base configuration, committed)
"""

import os
from pathlib import Path
from typing import Dict, Tuple, List, Optional
import re


def load_environment_config(environment: str = 'development') -> Dict[str, str]:
    """
    Load environment configuration with layered precedence.
    
    Args:
        environment: Environment name (development, staging, production)
        
    Returns:
        Dictionary of environment variables with proper precedence applied
    """
    config = {}
    
    # Load in precedence order (lowest to highest)
    env_files = [
        '.env.defaults',
        f'.env.{environment}',
        '.env.local'
    ]
    
    for env_file in env_files:
        if os.path.exists(env_file):
            file_config = _load_env_file(env_file)
            config.update(file_config)
    
    return config


def _load_env_file(file_path: str) -> Dict[str, str]:
    """
    Load a single environment file without shell substitution.
    
    Args:
        file_path: Path to the environment file
        
    Returns:
        Dictionary of key-value pairs from the file
    """
    config = {}
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Parse KEY=VALUE format
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Remove quotes if present
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    
                    # Store as literal value (no shell substitution)
                    config[key] = value
                    
    except Exception as e:
        # Graceful handling of missing or malformed files
        print(f"Warning: Could not load {file_path}: {e}")
    
    return config


def validate_api_keys(config: Optional[Dict[str, str]] = None) -> Tuple[bool, List[str]]:
    """
    Validate that required API keys are present and properly formatted.
    
    Args:
        config: Environment configuration dict (loads current if None)
        
    Returns:
        Tuple of (is_valid, list_of_missing_keys)
    """
    if config is None:
        config = load_environment_config()
    
    # Define required API keys
    required_keys = [
        'ANTHROPIC_API_KEY',
        'OPENAI_API_KEY'
    ]
    
    # Define optional API keys (for integrations)
    optional_keys = [
        'XAI_API_KEY',
        'GEMINI_API_KEY',
        'MOTION_API_KEY',
        'LINEAR_API_KEY',
        'GITLAB_TOKEN',
        'NOTION_TOKEN'
    ]
    
    missing_keys = []
    
    # Check required keys
    for key in required_keys:
        value = config.get(key, '').strip()
        if not value or value.startswith('${'):  # Empty or still has shell substitution
            missing_keys.append(key)
    
    is_valid = len(missing_keys) == 0
    return is_valid, missing_keys


def get_environment_info(environment: str = 'development') -> Dict[str, any]:
    """
    Get comprehensive environment information for debugging.
    
    Args:
        environment: Environment name
        
    Returns:
        Dictionary with environment configuration and metadata
    """
    config = load_environment_config(environment)
    
    # Collect file existence info
    env_files = {
        'defaults': os.path.exists('.env.defaults'),
        f'{environment}': os.path.exists(f'.env.{environment}'),
        'local': os.path.exists('.env.local'),
        'example': os.path.exists('.env.example')
    }
    
    # Check for shell substitution patterns
    shell_substitution_found = any(
        value and '${' in str(value) 
        for value in config.values()
    )
    
    return {
        'environment': environment,
        'config': config,
        'files_found': env_files,
        'shell_substitution_detected': shell_substitution_found,
        'config_count': len(config)
    }


def migrate_from_shell_substitution(environment: str = 'development') -> bool:
    """
    Helper function to migrate from old shell substitution format.
    
    Args:
        environment: Environment to migrate
        
    Returns:
        True if migration was successful
    """
    old_file = f'.env.{environment}'
    new_file = f'.env.{environment}.new'
    
    if not os.path.exists(old_file):
        return False
    
    try:
        with open(old_file, 'r') as f:
            content = f.read()
        
        # Replace shell substitution with placeholders
        substitution_pattern = r'\$\{([^}]+)\}'
        
        def replace_substitution(match):
            var_name = match.group(1)
            return f"# TODO: Set {var_name} in .env.local"
        
        new_content = re.sub(substitution_pattern, replace_substitution, content)
        
        with open(new_file, 'w') as f:
            f.write(new_content)
        
        print(f"Migration file created: {new_file}")
        print("Review the migration file and manually update your configuration.")
        return True
        
    except Exception as e:
        print(f"Migration failed: {e}")
        return False


if __name__ == '__main__':
    """Command-line interface for testing the environment loader."""
    import sys
    
    if len(sys.argv) > 1:
        env = sys.argv[1]
    else:
        env = 'development'
    
    print(f"🔧 Loading environment configuration for: {env}")
    print("=" * 50)
    
    config = load_environment_config(env)
    info = get_environment_info(env)
    
    print(f"Environment: {info['environment']}")
    print(f"Files found: {info['files_found']}")
    print(f"Configuration variables: {info['config_count']}")
    print(f"Shell substitution detected: {info['shell_substitution_detected']}")
    
    if config:
        print("\nLoaded configuration:")
        for key, value in sorted(config.items()):
            # Mask sensitive values
            if 'key' in key.lower() or 'token' in key.lower() or 'secret' in key.lower():
                display_value = f"{value[:8]}..." if len(value) > 8 else "***"
            else:
                display_value = value
            print(f"  {key}={display_value}")
    else:
        print("\nNo configuration loaded!")
    
    # Validate API keys
    is_valid, missing = validate_api_keys(config)
    print(f"\nAPI key validation: {'✅ Valid' if is_valid else '❌ Invalid'}")
    if missing:
        print(f"Missing keys: {', '.join(missing)}")