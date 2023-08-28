import ast
import pkg_resources

# Specify the path to your Flask app module
flask_app_path = '/Users/alejandro/Desktop/Life/Card-Fraud-Detection/cfd/api.py'

# Read the Flask app module file
with open(flask_app_path, 'r') as file:
    code = file.read()

# Parse the code into an AST
tree = ast.parse(code)

# Collect the imported modules and their versions
imported_modules = {}

for node in ast.walk(tree):
    if isinstance(node, ast.Import):
        for alias in node.names:
            module_name = alias.name
            try:
                module_version = pkg_resources.get_distribution(module_name).version
                imported_modules[module_name] = module_version
            except pkg_resources.DistributionNotFound:
                imported_modules[module_name] = 'Unknown'
    elif isinstance(node, ast.ImportFrom):
        module_name = node.module
        for alias in node.names:
            imported_name = node.module + '.' + alias.name
            try:
                module_version = pkg_resources.get_distribution(imported_name).version
                imported_modules[imported_name] = module_version
            except pkg_resources.DistributionNotFound:
                imported_modules[imported_name] = 'Unknown'

# Print the captured imports and their versions
for module, version in imported_modules.items():
    print(f"{module} ({version})")
