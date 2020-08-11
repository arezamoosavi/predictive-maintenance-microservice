from kafka import KafkaProducer

kafka_server = "kafka:9092"


if __name__ == "__main__":
    try:

        producer = KafkaProducer(bootstrap_servers=[kafka_server])
        producer.bootstrap_connected()

        exit(1)
    except Exception as e:

        print("Error! {}".format(e))
        exit(0)

