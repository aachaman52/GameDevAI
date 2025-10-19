"""
System Specs Checker - Hardware detection
Phase 3 implementation
"""

import platform
import psutil
import json
from pathlib import Path

try:
    import cpuinfo
    HAS_CPUINFO = True
except ImportError:
    HAS_CPUINFO = False

class SpecsChecker:
    def __init__(self):
        self.specs = {}
        self.output_file = Path('data/system_specs.json')
    
    def detect_all(self):
        print("🔍 Detecting system specifications...")
        
        self.specs['system'] = self.get_system_info()
        self.specs['cpu'] = self.get_cpu_info()
        self.specs['memory'] = self.get_memory_info()
        self.specs['gpu'] = self.get_gpu_info()
        self.specs['performance_tier'] = self.calculate_performance_tier()
        
        return self.specs
    
    def get_system_info(self):
        return {
            'os': platform.system(),
            'os_version': platform.version(),
            'os_release': platform.release(),
            'architecture': platform.machine()
        }
    
    def get_cpu_info(self):
        cpu_data = {
            'physical_cores': psutil.cpu_count(logical=False),
            'logical_cores': psutil.cpu_count(logical=True),
            'usage_percent': psutil.cpu_percent(interval=1)
        }
        
        try:
            freq = psutil.cpu_freq()
            if freq:
                cpu_data['max_frequency'] = f"{freq.max:.0f} MHz"
        except:
            pass
        
        if HAS_CPUINFO:
            try:
                info = cpuinfo.get_cpu_info()
                cpu_data['brand'] = info.get('brand_raw', 'Unknown')
            except:
                cpu_data['brand'] = 'Unknown'
        
        return cpu_data
    
    def get_memory_info(self):
        mem = psutil.virtual_memory()
        
        return {
            'total_gb': round(mem.total / (1024**3), 2),
            'available_gb': round(mem.available / (1024**3), 2),
            'used_gb': round(mem.used / (1024**3), 2),
            'percent_used': mem.percent
        }
    
    def get_gpu_info(self):
        gpu_info = {
            'detected': False,
            'name': 'None detected'
        }
        
        try:
            if platform.system() == 'Windows':
                import subprocess
                result = subprocess.run(
                    ['wmic', 'path', 'win32_VideoController', 'get', 'name'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    if len(lines) > 1:
                        gpu_name = lines[1].strip()
                        if gpu_name and 'Microsoft' not in gpu_name:
                            gpu_info['detected'] = True
                            gpu_info['name'] = gpu_name
        except:
            pass
        
        return gpu_info
    
    def calculate_performance_tier(self):
        mem_gb = self.specs['memory']['total_gb']
        cpu_cores = self.specs['cpu']['physical_cores']
        has_gpu = self.specs['gpu']['detected']
        
        score = 0
        
        if mem_gb >= 32:
            score += 40
        elif mem_gb >= 16:
            score += 30
        elif mem_gb >= 8:
            score += 20
        else:
            score += 10
        
        if cpu_cores >= 8:
            score += 30
        elif cpu_cores >= 6:
            score += 25
        elif cpu_cores >= 4:
            score += 20
        else:
            score += 10
        
        if has_gpu:
            score += 30
        
        if score >= 80:
            tier = 'high'
            desc = 'High-end system - Can handle complex games'
        elif score >= 60:
            tier = 'medium-high'
            desc = 'Good system - Suitable for most tasks'
        elif score >= 40:
            tier = 'medium'
            desc = 'Moderate system - Lightweight to medium projects'
        else:
            tier = 'low'
            desc = 'Basic system - Best for 2D and simple 3D'
        
        return {
            'tier': tier,
            'score': score,
            'description': desc
        }
    
    def save_report(self):
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.output_file, 'w') as f:
            json.dump(self.specs, f, indent=2)
        
        print(f"✓ Specs saved to {self.output_file}")
    
    def print_report(self):
        print("\n" + "="*60)
        print("📊 SYSTEM SPECIFICATIONS")
        print("="*60)
        
        sys = self.specs['system']
        print(f"\n🖥️  SYSTEM")
        print(f"   OS: {sys['os']} {sys['os_release']}")
        
        cpu = self.specs['cpu']
        print(f"\n⚙️  CPU")
        if 'brand' in cpu:
            print(f"   Model: {cpu['brand']}")
        print(f"   Cores: {cpu['physical_cores']} physical, {cpu['logical_cores']} logical")
        
        mem = self.specs['memory']
        print(f"\n💾 MEMORY")
        print(f"   Total: {mem['total_gb']} GB")
        print(f"   Available: {mem['available_gb']} GB")
        
        gpu = self.specs['gpu']
        print(f"\n🎮 GPU")
        print(f"   Status: {'✓ Detected' if gpu['detected'] else '✗ Not detected'}")
        print(f"   Name: {gpu['name']}")
        
        perf = self.specs['performance_tier']
        print(f"\n🎯 PERFORMANCE")
        print(f"   Tier: {perf['tier'].upper()} (Score: {perf['score']}/100)")
        print(f"   {perf['description']}")
        
        print("\n" + "="*60 + "\n")

def main():
    checker = SpecsChecker()
    checker.detect_all()
    checker.print_report()
    checker.save_report()

if __name__ == "__main__":
    main()