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
android.api = 31
android.minapi = 21
android.ndk = 23b
android.arch = arm64-v8a

[buildozer]
log_level = 2

[requirements]
python_version = 3.9
kivy_version = 2.1.0
requirements = python3,kivy,numpy,scipy,matplotlib,pandas,openpyxl,Pillow
