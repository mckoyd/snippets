import logging, argparse, psycopg2

logging.basicConfig(filename="snippets.log", level=logging.DEBUG)

logging.debug("Connecting to PostgreSQL")
connection = psycopg2.connect(database="snippets")
logging.debug("Database connection established")

def put(name, snippet, hide, show):
    """
    Store a snippet with an associated name.
    Returns the name and the snippet.
    """
    if not hide or not show:
        hidden = False
    elif hide:
        hidden = hide
    elif show:
        hidden = show
    
    logging.info("Storing snippet {!r}: {!r}, hidden: {!r}".format(name, snippet, hidden))
    try:
        with connection, connection.cursor() as cursor:
            cursor.execute("INSERT INTO snippets VALUES({!r}, {!r}, {!r})".format(name, snippet, hidden))
    except:
        with connection, connection.cursor() as cursor:
            cursor.execute("UPDATE snippets SET message={!r}, hidden={!r} WHERE keyword={!r}".format(snippet, hidden, name))
    logging.debug("Snippet stored successfully.")
    return name, snippet, hidden
    
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

def catalog():
    """
    Retrieves all keywords.
    """
    logging.debug("Retrieving all keywords")
    with connection, connection.cursor() as cursor:
        cursor.execute("SELECT keyword FROM snippets ORDER BY keyword")
        keywords = cursor.fetchall()
    logging.debug("Retrieved all keywords successfully")
    return keywords

def search(query):
    """
    Retrieves names and snippets based on search query.
    """
    logging.debug("Retrieving all keywords and snippets matching the following search query: {!r}".format(query))
    with connection, connection.cursor() as cursor:
        cursor.execute("SELECT * FROM snippets WHERE message LIKE '%{}%'".format(query))
        entries = cursor.fetchall()
    logging.debug("Retrieved all entries matching query.")
    return entries

def delete(name):
    """
    Deletes a snippet based on name.
    """
    logging.debug("Retrieving snippet with name: {!r}".format(name))
    with connection, connection.cursor() as cursor:
        cursor.execute("DELETE FROM snippets WHERE keyword={!r}".format(name))
    logging.debug("Deleted entry with name: {}".format(name))
    return name

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
    put_parser.add_argument("--hide", help="Declare that snippet is hidden", action="store_true")
    put_parser.add_argument("--show", help="Declare snippet to not be hidden", action="store_false")
    
    # Subparser for the get command
    logging.debug("Constructing get subparser")
    get_parser = subparsers.add_parser("get", help="Get a snippet by name")
    get_parser.add_argument("name", help="Name of snippet")

    # Subparser for the catalog command
    logging.debug("Constructing catalog subparser")
    get_parser = subparsers.add_parser("catalog", help="Get all names and snippets")

    # Subparser for the search command
    logging.debug("Constructing search subparser")
    get_parser = subparsers.add_parser("search", help="Search for snippets based on query")
    get_parser.add_argument("query", help="Query string to search for in all snippets")

    # Subparser for the delete command
    logging.debug("Constructing delete subparser")
    get_parser = subparsers.add_parser("delete", help="Deletes a snippet by name")
    get_parser.add_argument("name", help="Name of snippet to delete")

    arguments = parser.parse_args()
    arguments = vars(arguments)
    command = arguments.pop("command")

    if command == "put":
        name, snippet, hidden = put(**arguments)
        print("Stored {!r} as {!r}, hidden: {!r}".format(snippet, name, hidden))
    elif command == "get":
        snippet = get(**arguments)
        print("Retreived snippet: {!r}".format(snippet))
    elif command == "catalog":
        keywords = catalog()
        results = []
        for i in range(len(keywords)):
            results.append(keywords[i][0])
        print("Retrieved all keywords: {!r}".format(results))
    elif command == "search":
        entries = search(**arguments)
        print("Retrieved all entries matching given query: {!r}".format(entries))
    elif command == "delete":
        name = delete(**arguments)
        print("Deleted snippet with name: {}".format(name))

if __name__ == "__main__":
    main()
    