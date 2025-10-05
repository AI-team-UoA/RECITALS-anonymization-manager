#!/bin/bash

set -e

echo "Cleaning previous build..."
rm -rf build
mkdir build

echo "Compiling Java classes..."
javac -cp "arx_dependencies/libarx-3.9.1.jar:arx_dependencies/py4j0.10.9.9.jar" ARXAdapterServer.java

echo "Copying classes to build folder..."
cp *.class build/

echo "Extracting dependencies into build folder..."
cd build
for jar in ../arx_dependencies/*.jar; do
    jar xf "$jar"
done
cd ..

echo "Creating fat JAR..."
jar cfm arx.jar manifest.txt -C build .
mv arx.jar ..
echo "Done! You can now run:"
echo "java -jar arx.jar anonymization_manager.ARXAdapterServer"
