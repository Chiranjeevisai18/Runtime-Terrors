"""
Download free 3D GLB models for the Gruha Alankara 3D studio.
Uses free models from market.pmnd.rs and other CC0 sources.
Creates static/models/ directory and downloads one GLB per furniture type.
"""

import os
import urllib.request
import ssl

# Output directory
MODELS_DIR = os.path.join(os.path.dirname(__file__), 'static', 'models')
os.makedirs(MODELS_DIR, exist_ok=True)

# Free GLB model URLs — sourced from market.pmnd.rs, KhronosGroup samples,
# and other free/CC0 sources. These are lightweight, web-optimized GLBs.
MODEL_SOURCES = {
    'sofa': 'https://market-assets.fra1.cdn.digitaloceanspaces.com/market-assets/models/couch/model.gltf',
    'table': 'https://market-assets.fra1.cdn.digitaloceanspaces.com/market-assets/models/table/model.gltf',
    'chair': 'https://market-assets.fra1.cdn.digitaloceanspaces.com/market-assets/models/chair/model.gltf',
    'bed': 'https://market-assets.fra1.cdn.digitaloceanspaces.com/market-assets/models/bed/model.gltf',
    'wardrobe': 'https://market-assets.fra1.cdn.digitaloceanspaces.com/market-assets/models/wardrobe/model.gltf',
    'bookshelf': 'https://market-assets.fra1.cdn.digitaloceanspaces.com/market-assets/models/bookcase/model.gltf',
    'lamp': 'https://market-assets.fra1.cdn.digitaloceanspaces.com/market-assets/models/lamp/model.gltf',
    'desk': 'https://market-assets.fra1.cdn.digitaloceanspaces.com/market-assets/models/desk/model.gltf',
    'rug': None,  # Rug stays procedural (flat plane — no 3D model needed)
    'tv_stand': 'https://market-assets.fra1.cdn.digitaloceanspaces.com/market-assets/models/tv/model.gltf',
    'dining_table': 'https://market-assets.fra1.cdn.digitaloceanspaces.com/market-assets/models/dining-table/model.gltf',
    'side_table': 'https://market-assets.fra1.cdn.digitaloceanspaces.com/market-assets/models/side-table/model.gltf',
    'plant': 'https://market-assets.fra1.cdn.digitaloceanspaces.com/market-assets/models/flower-pot/model.gltf',
    'mirror': None,  # Mirror stays procedural (reflective effect better with three.js material)
}

# SSL context for HTTPS downloads  
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


def download_model(name, url):
    """Download a single GLB/GLTF model."""
    ext = '.gltf' if url.endswith('.gltf') else '.glb'
    output_path = os.path.join(MODELS_DIR, f'{name}{ext}')
    
    if os.path.exists(output_path):
        size = os.path.getsize(output_path)
        print(f"  ✅ {name}{ext} already exists ({size / 1024:.0f} KB)")
        return True
    
    try:
        print(f"  ⬇️  Downloading {name}{ext}...")
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=ctx, timeout=30) as response:
            data = response.read()
        
        with open(output_path, 'wb') as f:
            f.write(data)
        
        size = len(data) / 1024
        print(f"  ✅ {name}{ext} downloaded ({size:.0f} KB)")
        return True
        
    except Exception as e:
        print(f"  ❌ {name}: Failed — {e}")
        return False


def main():
    print("=" * 55)
    print("  Gruha Alankara – 3D Model Downloader")
    print("=" * 55)
    print(f"\nOutput directory: {MODELS_DIR}\n")
    
    success = 0
    skipped = 0
    failed = 0
    
    for name, url in MODEL_SOURCES.items():
        if url is None:
            print(f"  ⏭️  {name} — stays procedural (skipped)")
            skipped += 1
            continue
        
        if download_model(name, url):
            success += 1
        else:
            failed += 1
    
    print(f"\n{'=' * 55}")
    print(f"  Done! ✅ {success} downloaded, ⏭️ {skipped} skipped, ❌ {failed} failed")
    print(f"{'=' * 55}")


if __name__ == '__main__':
    main()
