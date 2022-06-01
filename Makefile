all: src/ archive/
	mkdir -p www/newsletter
	bash src/render_all.sh
