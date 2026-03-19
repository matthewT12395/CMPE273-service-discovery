"""
Client - Demonstrates service discovery and calling random instances

This client:
1. Discovers available service instances
2. Randomly selects one instance
3. Makes a request to that instance
"""

import requests
import random
import time
import sys

class DiscoveryClient:
    def __init__(self, registry_url="http://localhost:5001"):
        self.registry_url = registry_url
    
    def discover_service(self, service_name):
        """Discover instances of a service"""
        try:
            response = requests.get(f"{self.registry_url}/discover/{service_name}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"\n🔍 Discovered {service_name}:")
                print(f"   Found {data['count']} instance(s)")
                for instance in data['instances']:
                    print(f"   - {instance['address']} (uptime: {instance['uptime_seconds']:.1f}s)")
                return data['instances']
            else:
                print(f"✗ Discovery failed: {response.json()}")
                return []
        except Exception as e:
            print(f"✗ Discovery error: {e}")
            return []
    
    def call_random_instance(self, service_name, endpoint="/", method="GET", **kwargs):
        """Discover service and call a random instance"""
        instances = self.discover_service(service_name)
        
        if not instances:
            print(f"✗ No instances of {service_name} available")
            return None
        
        # Select random instance
        selected = random.choice(instances)
        address = selected['address']
        
        print(f"\n🎲 Selected random instance: {address}")
        print(f"   Making {method} request to {address}{endpoint}")
        
        try:
            if method.upper() == "GET":
                response = requests.get(f"{address}{endpoint}", timeout=5, **kwargs)
            elif method.upper() == "POST":
                response = requests.post(f"{address}{endpoint}", timeout=5, **kwargs)
            elif method.upper() == "PUT":
                response = requests.put(f"{address}{endpoint}", timeout=5, **kwargs)
            elif method.upper() == "DELETE":
                response = requests.delete(f"{address}{endpoint}", timeout=5, **kwargs)
            else:
                print(f"✗ Unsupported HTTP method: {method}")
                return None
            
            print(f"✓ Response status: {response.status_code}")
            if response.text:
                print(f"   Response: {response.text[:200]}")
            return response
        except requests.exceptions.ConnectionError:
            print(f"✗ Cannot connect to {address}")
            print(f"   Make sure the service is actually running on that address")
            return None
        except Exception as e:
            print(f"✗ Error calling service: {e}")
            return None


def demo_client():
    """Demonstrate client discovering and calling random instances"""
    print("\n" + "="*60)
    print("CLIENT DISCOVERY AND RANDOM INSTANCE CALLING DEMO")
    print("="*60)
    
    client = DiscoveryClient()
    
    # Check registry health
    try:
        response = requests.get(f"{client.registry_url}/health")
        if response.status_code != 200:
            print("✗ Registry health check failed")
            return
    except Exception as e:
        print(f"✗ Cannot connect to registry: {e}")
        print("Make sure the registry is running: python service_registry_improved.py")
        return
    
    print("✓ Registry is healthy\n")
    
    # Get service name from user or use default
    if len(sys.argv) > 1:
        service_name = sys.argv[1]
    else:
        service_name = "user-service"
        print(f"Using default service: {service_name}")
        print("Usage: python client.py <service_name> [num_calls]")
        print("Example: python client.py user-service 5\n")
    
    # Number of calls to make
    num_calls = 1
    if len(sys.argv) > 2:
        try:
            num_calls = int(sys.argv[2])
        except ValueError:
            print("Invalid number of calls, using 1")
    
    print(f"Making {num_calls} call(s) to {service_name}...\n")
    
    # Make multiple calls to demonstrate random selection
    for i in range(num_calls):
        print(f"\n--- Call #{i+1} ---")
        client.call_random_instance(service_name, endpoint="/")
        if i < num_calls - 1:
            time.sleep(1)  # Small delay between calls
    
    print("\n" + "="*60)
    print("Demo complete!")
    print("="*60)


if __name__ == "__main__":
    demo_client()

# Made with Bob
