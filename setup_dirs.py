import os

dirs = ['core', 'services', 'storage', 'analytics', 'config']

for d in dirs:
    if not os.path.exists(d):
        os.makedirs(d)
    init_file = os.path.join(d, '__init__.py')
    if not os.path.exists(init_file):
        with open(init_file, 'w') as f:
            pass
print("Directories and __init__.py files created successfully.")
