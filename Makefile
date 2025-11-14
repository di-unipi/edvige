setup:
	bundle install
	pip install -r scripts/requirements.txt

serve:
	bundle exec jekyll serve --livereload

build:
	python3 scripts/render.py
	export JEKYLL_ENV="production" && bundle exec jekyll build

clean: 
	rm -rf scripts/basic.ics
	rm -rf _data/events.yml

render: build clean