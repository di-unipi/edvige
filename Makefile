deploy:
	rsync -avz --delete --exclude ".git*" --exclude "node_modules/" --exclude "www/" --exclude "Makefile" --exclude "logs/" --exclude "www/" ./ edvige:edvige/
