#!/bin/bash

set -e

echo "Cleaning previous build..."
rm -rf build
mkdir build

echo "Compiling Java classes..."
javac -cp "arx_dependencies/libarx-3.9.1.jar" JavaArxAdapter.java

echo "Copying classes to build folder..."
cp *.class build/

echo "Extracting dependencies into build folder..."
cd build
for jar in ../arx_dependencies/*.jar; do
    jar xf "$jar"
done
cd ..

echo "Creating fat JAR..."
jar cfm arx_adapter_javaside.jar manifest.txt -C build .
mv arx_adapter_javaside.jar ../src/anonymization_manager/adapters/arx/
echo "Done! You can now run:"
echo "java -jar arx_adapter_javaside.jar anonymization_manager.JavaArxAdapter"
