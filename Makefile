build/index.html:
	mkdir -p build
	python src/html_generator.py archive/may_2022.md > build/index.mjml
	mjml build/index.mjml > build/index.html
	rm build/index.mjml
