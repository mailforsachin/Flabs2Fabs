import sys
sys.path.append('.')

# Check each router's prefix
routers = ['auth', 'admin', 'system', 'exercise', 'workout', 'recommendation', 'intelligence', 'progress']

for router_name in routers:
    try:
        module = __import__(f'app.routes.{router_name}', fromlist=['router'])
        router = module.router
        print(f"{router_name}:")
        print(f"  Prefix: {router.prefix if hasattr(router, 'prefix') else 'None'}")
        print(f"  Routes: {len(router.routes)}")
        for route in router.routes[:2]:  # Show first 2 routes
            if hasattr(route, 'path'):
                print(f"    - {route.path}")
        print()
    except Exception as e:
        print(f"{router_name}: ERROR - {e}")
