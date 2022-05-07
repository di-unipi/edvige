all: src/ archive/
	mkdir -p build
	bash src/render_all.sh

clean:
	rm -rf build
