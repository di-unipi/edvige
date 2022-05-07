#! bash

# Iterate over the markdown files
for file in archive/*.md; do
  # Get the filename without the extension
  filename=$(basename "$file" .md)
  python src/mjml_generator.py "$file" >> "build/$filename.mjml"
  mjml "build/$filename.mjml" > "build/$filename.html"
  rm "build/$filename.mjml"
done

# Build index.html
python src/index_generator.py > "build/index.html"
