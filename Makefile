deploy:
	rsync -avz --delete --exclude ".*" --exclude ".git*" --exclude "node_modules/" --exclude "www/" --exclude "Makefile" --exclude "logs/" --exclude "www/" ./ edvige:edvige/
