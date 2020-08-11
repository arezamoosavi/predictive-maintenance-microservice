create-topic:
	docker-compose exec kafka kafka-topics --create \
	--topic nasa-sensor-data --if-not-exists \
	kafka:9092 --replication-factor 1 --partitions 1 \
	--zookeeper zookeeper:2181 sleep infinity

init-elk:
	sudo sysctl -w vm.max_map_count=262144
	sudo rm -rf esdata/
	mkdir esdata
	sudo chmod 777 -R esdata/

build-start:
	docker-compose up --build -d

clean:
	docker-compose down -v

get-indexes:
	curl http://localhost:9200/_cat/indices