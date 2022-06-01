#! bash

# Iterate over the markdown files
for file in archive/*.md; do
  # Get the filename without the extension
  filename=$(basename "$file" .md)
  python3 src/mjml_generator.py "$file" >> "www/newsletter/$filename.mjml"
  mjml "www/newsletter/$filename.mjml" > "www/newsletter/$filename.html"
  rm "www/newsletter/$filename.mjml"
done

# Build index.html
python3 src/index_generator.py > "www/newsletter/index.html"
