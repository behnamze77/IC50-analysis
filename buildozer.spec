[app]
title = IC50 Calculator
package.name = ic50calculator
package.domain = org.example
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
orientation = portrait
osx.python_version = 3
osx.kivy_version = 2.1.0
fullscreen = 0
android.permissions = WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE
android.api = 30
android.minapi = 21
android.ndk = 23b
android.archs = arm64-v8a

[buildozer]
log_level = 2

[requirements]
python_version = 3.9
kivy_version = 2.1.0
requirements = python3,kivy==2.1.0,numpy==1.24.3,scipy==1.10.1,matplotlib==3.7.1,pandas==1.5.3,openpyxl==3.1.2,Pillow==9.5.0,cython==0.29.36
