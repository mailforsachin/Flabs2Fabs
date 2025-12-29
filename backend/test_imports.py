import sys
sys.path.append('.')

print("Testing imports...")
modules_to_test = [
    'app.knowledge_level',
    'app.recommendation', 
    'app.override_tracking',
    'app.progress_projections'
]

for module in modules_to_test:
    try:
        __import__(module)
        print(f"✅ {module} - OK")
    except Exception as e:
        print(f"❌ {module} - FAILED: {str(e)[:100]}")
