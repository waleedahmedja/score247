[app]

# Application metadata
title = Score247
package.name = score247
package.domain = org.score247

# Source code
source.dir = .
source.include_exts = py,png,jpg,kv,atlas

# Version
version = 1.0.0

# Requirements
requirements = python3,kivy==2.3.0

# Permissions (MINIMAL - offline only)
android.permissions = 

# Orientation (portrait only for consistent UX)
orientation = portrait

# Icon (512x512 recommended)
# Place icon.png in same directory as buildozer.spec
#icon.filename = %(source.dir)s/icon.png

# Presplash (optional)
#presplash.filename = %(source.dir)s/presplash.png

# Android specific
android.api = 31
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True
android.archs = armeabi-v7a, arm64-v8a

# Optimize
# android.add_compile_options = ndkArgs "APP_SHORT_COMMANDS=true"

# No Google services
android.gradle_dependencies = 

# Build settings
log_level = 2
warn_on_root = 1

[buildozer]
log_level = 2
warn_on_root = 1
