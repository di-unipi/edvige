#! bash

# Iterate over the markdown files
for file in archive/*.md; do
  # Get the filename without the extension
  filename=$(basename "$file" .md)
  python src/mjml_generator.py "$file" >> "docs/$filename.mjml"
  mjml "docs/$filename.mjml" > "docs/$filename.html"
  rm "docs/$filename.mjml"
done

# Build index.html
python src/index_generator.py > "docs/index.html"
