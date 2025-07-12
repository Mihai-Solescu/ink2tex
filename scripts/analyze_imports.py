#!/usr/bin/env python3
"""
Analyze all imports used in the project to ensure PyInstaller includes them
"""

import ast
import sys
from pathlib import Path
from typing import Set, List
import importlib.util

def find_project_root():
    """Find the project root directory"""
    current = Path(__file__).resolve().parent
    while current != current.parent:
        if (current / "pyproject.toml").exists():
            return current
        current = current.parent
    raise FileNotFoundError("Could not find project root")

def extract_imports_from_file(filepath: Path) -> Set[str]:
    """Extract all imports from a Python file"""
    imports = set()
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module.split('.')[0])
                    
    except Exception as e:
        print(f"Error parsing {filepath}: {e}")
    
    return imports

def find_all_python_files(src_dir: Path) -> List[Path]:
    """Find all Python files in source directory"""
    python_files = []
    for py_file in src_dir.rglob("*.py"):
        if "__pycache__" not in str(py_file):
            python_files.append(py_file)
    return python_files

def check_import_availability(import_name: str, python_exe: str = None) -> bool:
    """Check if an import is available in current environment or specified Python executable"""
    if python_exe:
        # Check in specified Python environment
        try:
            import subprocess
            result = subprocess.run([python_exe, "-c", f"import {import_name}"], 
                                  capture_output=True, check=True, timeout=10)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            return False
    else:
        # Check in current environment
        try:
            spec = importlib.util.find_spec(import_name)
            return spec is not None
        except (ImportError, ModuleNotFoundError, ValueError):
            return False

def get_build_venv_python(project_root: Path) -> str:
    """Get the Python executable from the build virtual environment"""
    # Check for .venv first
    venv_dir = project_root / ".venv"
    if venv_dir.exists():
        if sys.platform == "win32":
            python_exe = venv_dir / "Scripts" / "python.exe"
        else:
            python_exe = venv_dir / "bin" / "python"
        
        if python_exe.exists():
            return str(python_exe)
    
    # Fall back to build_venv
    build_venv_dir = project_root / "build_venv"
    if build_venv_dir.exists():
        if sys.platform == "win32":
            python_exe = build_venv_dir / "Scripts" / "python.exe"
        else:
            python_exe = build_venv_dir / "bin" / "python"
        
        if python_exe.exists():
            return str(python_exe)
    
    # Fall back to current Python
    return sys.executable

def main():
    try:
        project_root = find_project_root()
        src_dir = project_root / "src"
        
        # Get build environment Python executable
        build_python = get_build_venv_python(project_root)
        
        print("🔍 Analyzing imports in Ink2TeX project...")
        print(f"📁 Source directory: {src_dir}")
        print(f"🐍 Build environment: {build_python}")
        print()
        
        # Find all Python files
        python_files = find_all_python_files(src_dir)
        print(f"📄 Found {len(python_files)} Python files")
        
        # Extract all imports
        all_imports = set()
        for py_file in python_files:
            file_imports = extract_imports_from_file(py_file)
            all_imports.update(file_imports)
        
        # Filter out standard library and local imports
        stdlib_modules = {
            'sys', 'os', 'pathlib', 'typing', 'subprocess', 'shutil', 
            'json', 'configparser', 'threading', 'time', 'datetime',
            'logging', 'queue', 'multiprocessing', 'abc', 'contextlib',
            'functools', 'itertools', 'collections', 'tempfile', 'io',
            'warnings', 'traceback', 'inspect', 'copy', 'weakref'
        }
        
        # Separate third-party imports
        third_party_imports = set()
        local_imports = set()
        missing_imports = set()
        
        for imp in all_imports:
            if imp.startswith('ink2tex') or imp.startswith('src'):
                local_imports.add(imp)
            elif imp in stdlib_modules:
                continue  # Skip standard library
            else:
                third_party_imports.add(imp)
        
        print("\n📦 Third-party dependencies found:")
        for imp in sorted(third_party_imports):
            print(f"  Checking {imp}...", end="", flush=True)
            try:
                is_available = check_import_availability(imp, build_python)
                status = "✅ Available" if is_available else "❌ MISSING"
                print(f"\r  {imp:<25} {status}")
                if not is_available:
                    missing_imports.add(imp)
            except Exception as e:
                print(f"\r  {imp:<25} ⚠️  Error checking: {e}")
                missing_imports.add(imp)
        
        print(f"\n🏠 Local modules found:")
        for imp in sorted(local_imports):
            print(f"  {imp}")
        
        if missing_imports:
            print(f"\n⚠️  MISSING DEPENDENCIES in build environment:")
            for imp in sorted(missing_imports):
                print(f"  ❌ {imp}")
            print(f"\nTo install missing dependencies in build environment:")
            print(f'"{build_python}" -m pip install {" ".join(sorted(missing_imports))}')
        else:
            print(f"\n✅ All third-party dependencies are available in build environment!")
        
        # Show installed packages in build environment
        print(f"\n📋 Installed packages in build environment:")
        try:
            import subprocess
            result = subprocess.run([build_python, "-m", "pip", "list", "--format=columns"], 
                                  capture_output=True, text=True, check=True)
            # Show only relevant packages
            lines = result.stdout.strip().split('\n')
            if len(lines) > 2:  # Skip header lines
                relevant_packages = []
                for line in lines[2:]:  # Skip header
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 2:
                            package_name = parts[0].lower()
                            # Only show packages we care about
                            if any(dep.lower() in package_name or package_name in dep.lower() 
                                  for dep in third_party_imports):
                                relevant_packages.append(line)
                
                if relevant_packages:
                    print("  Package                    Version")
                    print("  " + "-" * 40)
                    for pkg in relevant_packages:
                        print(f"  {pkg}")
                else:
                    print("  (No relevant packages found in detailed list)")
        except Exception as e:
            print(f"  ⚠️ Could not retrieve package list: {e}")
        
        # Check current PyInstaller hidden imports
        spec_file = project_root / "installer" / "ink2tex.spec"
        if spec_file.exists():
            print(f"\n📋 Comparing with PyInstaller spec file...")
            
            with open(spec_file, 'r') as f:
                spec_content = f.read()
            
            # Extract hidden_imports from spec
            spec_imports = set()
            in_hidden_imports = False
            for line in spec_content.split('\n'):
                line = line.strip()
                if 'hidden_imports = [' in line:
                    in_hidden_imports = True
                elif in_hidden_imports and line == ']':
                    break
                elif in_hidden_imports and ("'" in line or '"' in line):
                    # Extract import name from quoted strings
                    import_line = line.strip()
                    if import_line.startswith("'") and ("'," in import_line or import_line.endswith("'")):
                        import_name = import_line.split("'")[1]
                        if not import_name.startswith('#') and import_name:
                            spec_imports.add(import_name.split('.')[0])
                    elif import_line.startswith('"') and ('",') in import_line:
                        import_name = import_line.split('"')[1]
                        if not import_name.startswith('#') and import_name:
                            spec_imports.add(import_name.split('.')[0])
            
            missing_from_spec = third_party_imports - spec_imports
            extra_in_spec = spec_imports - third_party_imports - local_imports
            
            if missing_from_spec:
                print(f"\n⚠️  Missing from PyInstaller spec:")
                for imp in sorted(missing_from_spec):
                    print(f"  📝 Add: '{imp}'")
            
            if extra_in_spec:
                print(f"\n💡 Extra in PyInstaller spec (might be okay):")
                for imp in sorted(extra_in_spec):
                    print(f"  📋 {imp}")
            
            if not missing_from_spec:
                print(f"\n✅ All dependencies are in PyInstaller spec!")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
