build/index.html: src/ archive/
	mkdir -p build
	python src/html_generator.py > build/index.mjml
	mjml build/index.mjml > build/index.html
	rm build/index.mjml

clean:
	rm -rf build
