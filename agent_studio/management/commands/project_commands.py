"""
Project Management Commands

Commands for managing Agent Studio projects, including initialization,
configuration, and project status operations.
"""

import os
import json
from pathlib import Path
from ..command_registry import register


@register('init', category='project', description='Initialize a new Agent Studio project')
def init_project(args=None, **kwargs):
    """
    Initialize a new Agent Studio project.
    
    Args:
        args: Command line arguments [project_name, path]
        **kwargs: Additional options
    """
    if isinstance(args, list) and len(args) >= 1:
        project_name = args[0]
        path = args[1] if len(args) > 1 else '.'
    else:
        project_name = kwargs.get('project_name', 'my_agent_project')
        path = kwargs.get('path', '.')
    
    project_path = Path(path) / project_name
    
    try:
        # Create project structure
        project_path.mkdir(parents=True, exist_ok=False)
        (project_path / "agents").mkdir()
        (project_path / "workflows").mkdir()
        (project_path / "config").mkdir()
        (project_path / "tests").mkdir()
        
        # Create configuration file
        config = {
            "project_name": project_name,
            "version": "1.0.0",
            "agent_studio_version": "1.0.0",
            "created_at": "2025-06-27T16:00:00Z",
        }
        
        with open(project_path / "config" / "project.json", 'w') as f:
            json.dump(config, f, indent=2)
        
        # Create basic files
        (project_path / "__init__.py").touch()
        (project_path / "agents" / "__init__.py").touch()
        (project_path / "workflows" / "__init__.py").touch()
        (project_path / "tests" / "__init__.py").touch()
        
        print(f"✅ Project '{project_name}' created successfully at {project_path}")
        return {
            'status': 'success',
            'project_name': project_name,
            'path': str(project_path),
        }
        
    except FileExistsError:
        print(f"❌ Error: Project '{project_name}' already exists at {project_path}")
        return {'status': 'error', 'message': 'Project already exists'}
    except Exception as e:
        print(f"❌ Error creating project: {e}")
        return {'status': 'error', 'message': str(e)}


@register('status', category='project', description='Show project status and information')
def project_status(args=None, **kwargs):
    """
    Show current project status and configuration.
    
    Args:
        args: Command line arguments
        **kwargs: Additional options
    """
    current_path = Path.cwd()
    
    # Look for project configuration
    config_file = current_path / "config" / "project.json"
    
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            print("📊 Agent Studio Project Status")
            print("=" * 30)
            print(f"Project Name: {config.get('project_name', 'Unknown')}")
            print(f"Version: {config.get('version', 'Unknown')}")
            print(f"Agent Studio Version: {config.get('agent_studio_version', 'Unknown')}")
            print(f"Created: {config.get('created_at', 'Unknown')}")
            print(f"Path: {current_path}")
            
            # Check project structure
            dirs_to_check = ['agents', 'workflows', 'config', 'tests']
            missing_dirs = [d for d in dirs_to_check if not (current_path / d).exists()]
            
            if missing_dirs:
                print(f"⚠️  Missing directories: {', '.join(missing_dirs)}")
            else:
                print("✅ Project structure is complete")
            
            return {
                'status': 'success',
                'config': config,
                'missing_dirs': missing_dirs,
            }
            
        except Exception as e:
            print(f"❌ Error reading project config: {e}")
            return {'status': 'error', 'message': str(e)}
    else:
        print("❌ No Agent Studio project found in current directory")
        print("Use 'agent-studio manage init <project_name>' to create a new project")
        return {'status': 'error', 'message': 'No project found'}


@register('validate', category='project', description='Validate project structure and configuration')
def validate_project(args=None, **kwargs):
    """
    Validate the current project structure and configuration.
    
    Args:
        args: Command line arguments
        **kwargs: Additional options
    """
    current_path = Path.cwd()
    issues = []
    
    # Check for required directories
    required_dirs = ['agents', 'workflows', 'config', 'tests']
    for dir_name in required_dirs:
        if not (current_path / dir_name).exists():
            issues.append(f"Missing directory: {dir_name}")
    
    # Check for configuration file
    config_file = current_path / "config" / "project.json"
    if not config_file.exists():
        issues.append("Missing project configuration file: config/project.json")
    else:
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            required_fields = ['project_name', 'version', 'agent_studio_version']
            for field in required_fields:
                if field not in config:
                    issues.append(f"Missing configuration field: {field}")
                    
        except Exception as e:
            issues.append(f"Invalid configuration file: {e}")
    
    # Check for __init__.py files
    init_files = [
        '__init__.py',
        'agents/__init__.py',
        'workflows/__init__.py',
        'tests/__init__.py',
    ]
    
    for init_file in init_files:
        if not (current_path / init_file).exists():
            issues.append(f"Missing {init_file}")
    
    if issues:
        print("❌ Project validation failed:")
        for issue in issues:
            print(f"  - {issue}")
        return {'status': 'failed', 'issues': issues}
    else:
        print("✅ Project validation passed")
        return {'status': 'success', 'issues': []}


@register('clean', category='project', description='Clean project temporary files and caches')
def clean_project(args=None, **kwargs):
    """
    Clean project temporary files and caches.
    
    Args:
        args: Command line arguments
        **kwargs: Additional options
    """
    current_path = Path.cwd()
    patterns_to_clean = [
        '**/__pycache__',
        '**/*.pyc',
        '**/*.pyo',
        '**/.pytest_cache',
        '**/node_modules',
        '**/.coverage',
    ]
    
    cleaned_items = []
    
    for pattern in patterns_to_clean:
        for item in current_path.glob(pattern):
            try:
                if item.is_file():
                    item.unlink()
                    cleaned_items.append(str(item))
                elif item.is_dir():
                    import shutil
                    shutil.rmtree(item)
                    cleaned_items.append(str(item))
            except Exception as e:
                print(f"Warning: Could not clean {item}: {e}")
    
    if cleaned_items:
        print(f"🧹 Cleaned {len(cleaned_items)} items:")
        for item in cleaned_items[:10]:  # Show first 10 items
            print(f"  - {item}")
        if len(cleaned_items) > 10:
            print(f"  ... and {len(cleaned_items) - 10} more items")
    else:
        print("✅ No items to clean")
    
    return {
        'status': 'success',
        'cleaned_count': len(cleaned_items),
        'cleaned_items': cleaned_items,
    }
