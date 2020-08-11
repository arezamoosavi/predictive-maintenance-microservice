import happybase


if __name__ == "__main__":
    try:

        connection = happybase.Connection(host="hbase", port=9090, autoconnect=True)
        print("\n all tables before: ", connection.tables())

        try:
            connection.create_table("nasa-data", {"s": dict()})
            print("\n all tables after: ", connection.tables(), "\n done!")
        except Exception as e:
            print("\n existed: ", connection.tables(), "\n done!")
            pass

        exit(1)
    except Exception as e:

        print("Error! {}".format(e))
        exit(0)

