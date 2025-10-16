#!/bin/bash
set -e

MAIN_CLASS="JavaArxAdapter.java"  # <-- change this
OUT_JAR="ArxAdapter.jar"

# Compile Java sources
mkdir -p bin
javac -cp "lib/*" -d bin $(find src -name "*.java")

# Create base JAR
jar cfe "$OUT_JAR" "$MAIN_CLASS" -C bin .

# Merge dependencies into the JAR
for f in lib/*.jar; do
  echo "Including $f..."
  mkdir -p tmp_unpack
  cd tmp_unpack
  jar xf "../$f"
  cd ..
  jar uf "$OUT_JAR" -C tmp_unpack .
  rm -rf tmp_unpack
done

echo "✅ Built $OUT_JAR"

