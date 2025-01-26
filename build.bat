rmdir /S /Q .\dist\main
pyinstaller -w main.py
xcopy .\data .\dist\main\data /E /I