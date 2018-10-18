import logging, argparse, psycopg2

logging.basicConfig(filename="snippets.log", level=logging.DEBUG)

logging.debug("Connecting to PostgreSQL")
connection = psycopg2.connect(database="snippets")
logging.debug("Database connection established")

def put(name, snippet):
    """
    Store a snippet with an associated name.
    Returns the name and the snippet.
    """
    logging.info("Storing snippet {!r}: {!r}".format(name, snippet))
    try:
        with connection, connection.cursor() as cursor:
            cursor.execute("INSERT INTO snippets VALUES({!r}, {!r})".format(name, snippet))
    except:
        with connection, connection.cursor() as cursor:
            cursor.execute("UPDATE snippets SET message={!r} WHERE keyword={!r}".format(snippet, name))
    logging.debug("Snippet stored successfully.")
    return name, snippet
    
def get(name):
    """
    Retrieve the snippet with a given name.
    If there is no such snippet, return '404: Snippet Not Found'.
    Returns the snippet.
    """
    logging.info("Retrieving snippets with name: {!r}.".format(name))
    with connection, connection.cursor() as cursor:
        cursor.execute("SELECT message FROM snippets WHERE keyword={!r}".format(name))
        snippet = cursor.fetchone()

    if not snippet:
        # No snippet was found with that name.
        logging.error("Snippet not found in db")
        return "404: Snippet Not Found"
    logging.debug("Retrieved snippet successfully")
    return snippet[0]

def main():
    """Main function"""
    logging.info("Constructing parser")
    parser = argparse.ArgumentParser(description="Store and retrieve snippets of text")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Subparser for the put command
    logging.debug("Constructing put subparser")
    put_parser = subparsers.add_parser("put", help="Store a snippet")
    put_parser.add_argument("name", help="Name of the snippet")
    put_parser.add_argument("snippet", help="Snippet")
    
    # Subparser for the get command
    logging.debug("Constructing get subparser")
    get_parser = subparsers.add_parser("get", help="Get a snippet")
    get_parser.add_argument("name", help="Name of snippet")
    
    arguments = parser.parse_args()
    arguments = vars(arguments)
    command = arguments.pop("command")
    
    if command == "put":
        name, snippet = put(**arguments)
        print("Stored {!r} as {!r}".format(snippet, name))
    elif command == "get":
        snippet = get(**arguments)
        print("Retreived snippet: {!r}".format(snippet))
        
    

if __name__ == "__main__":
    main()
    