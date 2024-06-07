deploy:
	rsync -avz --delete --exclude ".git*" --exclude "node_modules/" --exclude "www/" ./ edvige:edvige/
