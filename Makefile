all: src/ archive/
	mkdir -p docs
	bash src/render_all.sh

clean:
	rm -rf docs
