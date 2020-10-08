# Running User Directory Elastic Search locally

Elastic Search will automatically start up on `docker-compose up`
Additional configuration options are available in the elasticsearch.yml file.

*Setup Steps*

1. Install the Materialized View in your database. (<https://gist.github.com/danlipert/8604040ca8f1163f29d7e841fd3a54fb>)
2. Add an ENV for the HAYSTACK_ELASTIC_SEARCH_URL variable to your app/app/.env file, `HAYSTACK_ELASTIC_SEARCH_URL=http://elasticsearch:9200`
3. Restart Gitcoin Web with updated env variables
4. Execute the management command rebuild_index and select Y when asked if you want to destroy your index. `docker-compose exec web app/manage.py rebuild_index`
