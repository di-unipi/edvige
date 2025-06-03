# deploy on edvige
rsync -avz --delete \
	--exclude ".*" \
       	--exclude ".git*" \
	--exclude "node_modules/" \
	--exclude "www/" \
	--exclude "deploy.sh" \
	--exclude "logs/" \
	--exclude "www/" \
	./ edvige:edvige/
