"""
System Specs Checker - Detects hardware for optimization recommendations
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
    print("⚠ py-cpuinfo not installed. Install with: pip install py-cpuinfo")

class SpecsChecker:
    def __init__(self):
        self.specs = {}
        self.output_file = Path('data/system_specs.json')
    
    def detect_all(self):
        """Run all detection methods"""
        print("🔍 Detecting system specifications...")
        
        self.specs['system'] = self.get_system_info()
        self.specs['cpu'] = self.get_cpu_info()
        self.specs['memory'] = self.get_memory_info()
        self.specs['gpu'] = self.get_gpu_info()
        self.specs['storage'] = self.get_storage_info()
        self.specs['performance_tier'] = self.calculate_performance_tier()
        
        return self.specs
    
    def get_system_info(self):
        """Basic system information"""
        return {
            'os': platform.system(),
            'os_version': platform.version(),
            'os_release': platform.release(),
            'architecture': platform.machine(),
            'python_version': platform.python_version()
        }
    
    def get_cpu_info(self):
        """CPU details"""
        cpu_data = {
            'physical_cores': psutil.cpu_count(logical=False),
            'logical_cores': psutil.cpu_count(logical=True),
            'max_frequency': None,
            'current_frequency': None,
            'usage_percent': psutil.cpu_percent(interval=1)
        }
        
        # Get frequency info
        try:
            freq = psutil.cpu_freq()
            if freq:
                cpu_data['max_frequency'] = f"{freq.max:.0f} MHz"
                cpu_data['current_frequency'] = f"{freq.current:.0f} MHz"
        except:
            pass
        
        # Get detailed CPU info if available
        if HAS_CPUINFO:
            try:
                info = cpuinfo.get_cpu_info()
                cpu_data['brand'] = info.get('brand_raw', 'Unknown')
                cpu_data['arch'] = info.get('arch', 'Unknown')
            except:
                cpu_data['brand'] = 'Unknown'
        
        return cpu_data
    
    def get_memory_info(self):
        """RAM information"""
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        return {
            'total_gb': round(mem.total / (1024**3), 2),
            'available_gb': round(mem.available / (1024**3), 2),
            'used_gb': round(mem.used / (1024**3), 2),
            'percent_used': mem.percent,
            'swap_total_gb': round(swap.total / (1024**3), 2),
            'swap_used_gb': round(swap.used / (1024**3), 2)
        }
    
    def get_gpu_info(self):
        """GPU detection (basic - no driver required)"""
        gpu_info = {
            'detected': False,
            'name': 'None detected',
            'note': 'Basic detection - may not show all GPUs'
        }
        
        # Try different detection methods
        try:
            # Method 1: Check Windows via wmic (Windows only)
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
        
        # Method 2: Check for common GPU indicators
        if not gpu_info['detected']:
            # This is a fallback - just check if system has common GPU terms
            gpu_info['note'] = 'Unable to detect GPU. May be integrated graphics or detection failed.'
        
        return gpu_info
    
    def get_storage_info(self):
        """Disk space information"""
        partitions = psutil.disk_partitions()
        storage = []
        
        for partition in partitions:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                storage.append({
                    'device': partition.device,
                    'mountpoint': partition.mountpoint,
                    'fstype': partition.fstype,
                    'total_gb': round(usage.total / (1024**3), 2),
                    'used_gb': round(usage.used / (1024**3), 2),
                    'free_gb': round(usage.free / (1024**3), 2),
                    'percent_used': usage.percent
                })
            except PermissionError:
                continue
        
        return storage
    
    def calculate_performance_tier(self):
        """Estimate performance tier for recommendations"""
        mem_gb = self.specs['memory']['total_gb']
        cpu_cores = self.specs['cpu']['physical_cores']
        has_gpu = self.specs['gpu']['detected']
        
        score = 0
        
        # Memory scoring
        if mem_gb >= 32:
            score += 40
        elif mem_gb >= 16:
            score += 30
        elif mem_gb >= 8:
            score += 20
        else:
            score += 10
        
        # CPU scoring
        if cpu_cores >= 8:
            score += 30
        elif cpu_cores >= 6:
            score += 25
        elif cpu_cores >= 4:
            score += 20
        else:
            score += 10
        
        # GPU scoring
        if has_gpu:
            score += 30
        else:
            score += 0
        
        # Determine tier
        if score >= 80:
            tier = 'high'
            desc = 'High-end system - Can handle complex games and advanced features'
        elif score >= 60:
            tier = 'medium-high'
            desc = 'Good system - Suitable for most game development tasks'
        elif score >= 40:
            tier = 'medium'
            desc = 'Moderate system - Can handle lightweight to medium projects'
        else:
            tier = 'low'
            desc = 'Basic system - Best for 2D games and simple 3D projects'
        
        return {
            'tier': tier,
            'score': score,
            'description': desc,
            'recommendations': self.get_recommendations(tier)
        }
    
    def get_recommendations(self, tier):
        """Get performance recommendations based on tier"""
        recommendations = {
            'high': [
                "✓ Can use high-poly 3D assets",
                "✓ Real-time lighting and post-processing OK",
                "✓ Large open-world environments supported",
                "✓ Advanced particle systems fine",
                "✓ Can run Unity editor with multiple scenes open"
            ],
            'medium-high': [
                "✓ Good for most 3D games",
                "✓ Use baked lighting for better performance",
                "✓ Medium-poly assets recommended",
                "✓ Moderate particle effects OK",
                "⚠ May struggle with very large scenes"
            ],
            'medium': [
                "⚠ Focus on optimized 3D or 2D games",
                "⚠ Use baked lighting exclusively",
                "⚠ Low-to-medium poly assets",
                "⚠ Limit particle effects",
                "✓ 2D games will run smoothly"
            ],
            'low': [
                "⚠ Stick to 2D games for best results",
                "⚠ Simple 3D games only (low-poly)",
                "⚠ Minimal particle effects",
                "⚠ Avoid real-time lighting",
                "⚠ Keep scene complexity low"
            ]
        }
        
        return recommendations.get(tier, [])
    
    def save_report(self):
        """Save specs to JSON file"""
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.output_file, 'w') as f:
            json.dump(self.specs, f, indent=2)
        
        print(f"✓ Specs saved to {self.output_file}")
    
    def print_report(self):
        """Print human-readable report"""
        print("\n" + "="*60)
        print("📊 SYSTEM SPECIFICATIONS REPORT")
        print("="*60)
        
        # System
        sys = self.specs['system']
        print(f"\n🖥️  SYSTEM")
        print(f"   OS: {sys['os']} {sys['os_release']}")
        print(f"   Architecture: {sys['architecture']}")
        
        # CPU
        cpu = self.specs['cpu']
        print(f"\n⚙️  CPU")
        if 'brand' in cpu:
            print(f"   Model: {cpu['brand']}")
        print(f"   Cores: {cpu['physical_cores']} physical, {cpu['logical_cores']} logical")
        if cpu['max_frequency']:
            print(f"   Max Frequency: {cpu['max_frequency']}")
        print(f"   Current Usage: {cpu['usage_percent']}%")
        
        # Memory
        mem = self.specs['memory']
        print(f"\n💾 MEMORY")
        print(f"   Total RAM: {mem['total_gb']} GB")
        print(f"   Available: {mem['available_gb']} GB")
        print(f"   Used: {mem['used_gb']} GB ({mem['percent_used']}%)")
        
        # GPU
        gpu = self.specs['gpu']
        print(f"\n🎮 GPU")
        print(f"   Status: {'✓ Detected' if gpu['detected'] else '✗ Not detected'}")
        print(f"   Name: {gpu['name']}")
        
        # Storage
        print(f"\n💿 STORAGE")
        for disk in self.specs['storage']:
            print(f"   {disk['device']} ({disk['fstype']})")
            print(f"      Total: {disk['total_gb']} GB")
            print(f"      Free: {disk['free_gb']} GB ({100-disk['percent_used']:.1f}% available)")
        
        # Performance Tier
        perf = self.specs['performance_tier']
        print(f"\n🎯 PERFORMANCE ASSESSMENT")
        print(f"   Tier: {perf['tier'].upper()} (Score: {perf['score']}/100)")
        print(f"   {perf['description']}")
        print(f"\n   Recommendations:")
        for rec in perf['recommendations']:
            print(f"   {rec}")
        
        print("\n" + "="*60 + "\n")

def main():
    """Standalone execution"""
    checker = SpecsChecker()
    checker.detect_all()
    checker.print_report()
    checker.save_report()

if __name__ == "__main__":
    main()