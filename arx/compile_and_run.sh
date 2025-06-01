# Compiles all the examples.
javac -cp libs/libarx-3.9.1.jar $(find . -name "*.java")

# Runs the examples.
for cls in examples/*.class; do java -cp "examples:libs/libarx-3.9.1.jar" "$(basename "$cls" .class)"; done