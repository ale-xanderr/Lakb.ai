#!/usr/bin/env python3
"""
Build script for creating Android APK from Flet app.

This script:
1. Sets necessary environment variables for the build
2. Validates required configuration
3. Executes the Flet build command
4. Provides helpful feedback and instructions

Usage:
    python build_apk.py

Before running:
1. Ensure you have 'flet' installed: pip install flet
2. Set up your environment variables (see .env.example)
3. Optionally, add your app icon to assets/icons/app_icon.png
"""

import os
import sys
import subprocess
from pathlib import Path


def load_env_file(env_file=".env"):
    """Load environment variables from .env file."""
    if not os.path.exists(env_file):
        print(f"⚠️  Warning: {env_file} not found")
        return False
    
    print(f"📁 Loading environment variables from {env_file}")
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                # Remove quotes if present
                value = value.strip().strip('"').strip("'")
                os.environ[key] = value
                print(f"   ✓ Set {key}")
    return True


def validate_configuration():
    """Validate that essential configuration is present."""
    print("\n🔍 Validating configuration...")
    
    required_vars = [
        "GOOGLE_PLACES_API_KEY",
        "SUPABASE_URL",
        "SUPABASE_KEY"
    ]
    
    missing = []
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
    
    if missing:
        print(f"❌ Missing required environment variables: {', '.join(missing)}")
        print("\nOptions:")
        print("1. Add them to your .env file")
        print("2. Set them as system environment variables")
        print("3. Hardcode them in src/core/config.py (not recommended for production)")
        return False
    
    print("✅ All required configuration present")
    return True


def check_icon():
    """Check if app icon exists."""
    icon_path = Path("assets/icons/app_icon.png")
    if icon_path.exists():
        print(f"✅ App icon found: {icon_path}")
        return True
    else:
        print(f"⚠️  App icon not found at {icon_path}")
        print("   Consider adding a 512x512 PNG icon for better app appearance")
        return False





def check_oauth_config():
    """Check OAuth configuration for Android."""
    print("\n🔐 OAuth Configuration Check:")
    
    android_redirect = os.getenv("ANDROID_REDIRECT_URL", "lakbai://oauth_callback")
    print(f"   Android Redirect URL: {android_redirect}")
    
    print("\n📝 IMPORTANT: Supabase Dashboard Configuration Required")
    print("   Before testing OAuth on Android, configure Supabase correctly:")
    print("")
    print("   1. SITE URL (Authentication → URL Configuration):")
    print("      - Must be an HTTP(S) URL, NOT a custom scheme!")
    print("      - Example: http://localhost:8550 or https://yourdomain.com")
    print("      - ❌ WRONG: lakbai://oauth_callback")
    print("")
    print("   2. REDIRECT URLs (Authentication → URL Configuration):")
    print(f"      - Add: {android_redirect}")
    print("      - Also keep: http://localhost:8550/oauth_callback (for desktop testing)")
    print("")
    print("   ⚠️  If Site URL is set to a custom scheme, OAuth will redirect")
    print("      to localhost:3000 (Supabase default) instead of your app!")
    
    return True


def build_apk():
    """Execute the Flet build command."""
    print("\n🔨 Building Android APK...")
    print("This may take several minutes on the first build...\n")
    
    try:
        # Run flet build with Android target
        # Deep linking is configured in pyproject.toml [tool.flet.android.deep_linking]
        # Command-line flags below provide additional/override configuration
        result = subprocess.run(
            [
                "flet", "build", "apk",
                "--deep-linking-scheme", "lakbai",
                "--deep-linking-host", "oauth_callback",
                "--verbose"
            ],
            check=True,
            capture_output=False
        )
        
        print("\n✅ Build completed successfully!")
        print("\n📦 Your APK should be in the 'build/apk' directory")
        print("\nNext steps:")
        print("1. Find your APK at: build/apk/Lakb.ai.apk")
        print("2. Transfer it to your Android device")
        print("3. Install and test (you may need to enable 'Install from Unknown Sources')")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Build failed with error code {e.returncode}")
        print("\nCommon issues:")
        print("- Make sure 'flet' is installed: pip install flet")
        print("- Check that Java JDK is installed (required for Android builds)")
        print("- Ensure Android SDK is configured")
        print("\nFor more help, see: https://flet.dev/docs/guides/python/packaging-app-for-distribution")
        return False
    
    except FileNotFoundError:
        print("\n❌ 'flet' command not found")
        print("Install Flet: pip install flet")
        return False


def main():
    """Main build process."""
    print("=" * 60)
    print("🚀 Lakb.ai Android APK Build Script")
    print("=" * 60)
    
    # Load environment variables
    env_loaded = load_env_file()
    
    # Validate configuration
    if not validate_configuration():
        print("\n⚠️  Configuration incomplete. Build may fail or app may not work correctly.")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            print("Build cancelled.")
            sys.exit(1)
    
    # Check icon
    check_icon()
    
    # Check OAuth configuration
    check_oauth_config()
    
    # Build APK
    success = build_apk()
    
    if success:
        print("\n" + "=" * 60)
        print("🎉 Build process completed!")
        print("=" * 60)
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("❌ Build process failed")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()
