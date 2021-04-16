# Remobe dist directory before building
rm -dr ../dist/

# Run Pyinstaller
pyinstaller \
    --distpath ../dist/ \
    --onefile \
    --specpath ../dist/ \
    --workpath ../dist/work/ \
    --noconsole \
    --name "SwordDrill" \
    --clean \
    --debug=all \
    ../src/main.py

# Cleanup uneeded files
rm -dr ../dist/work
rm ../dist/SwordDrill.spec