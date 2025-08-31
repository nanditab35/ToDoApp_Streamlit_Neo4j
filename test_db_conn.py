import os
from dotenv import load_dotenv
import streamlit as st
from neo4j import GraphDatabase, exceptions

# Load environment variables from .env file
# load_dotenv()
def check_neo4j_connection():
    """
    Tests the connection to the Neo4j database using credentials from .env
    """
    print("Attempting to connect to Neo4j...")
    load_dotenv()
    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USERNAME")
    password = os.getenv("NEO4J_PASSWORD")

    if not all([uri, user, password]):
        print("Error: NEO4J_URI, NEO4J_USERNAME, or NEO4J_PASSWORD not found in .env file.")
        return

    # You can now use these variables to connect to your database
    # Set the title of the web application
    st.title("My First Streamlit Website")
    driver = None
    try:
        # Establish the driver connection
        driver = GraphDatabase.driver(uri, auth=(user, password))
        # Verify connectivity by fetching server info
        driver.verify_connectivity()
        print("Connection Successful!")

        # Add a simple text message
        st.write("Welcome to this interactive website built with Streamlit!")
        # Optional: Run a simple query to ensure the database is responsive
        with driver.session() as session:
            result = session.run("MATCH (n) RETURN count(n) AS node_count")
            record = result.single()
            print(f"Found {record['node_count']} nodes in the database.")

        # Create a text input widget
        user_name = st.text_input("What's your name?")
    except exceptions.AuthError:
        print("Authentication Failed: Please double-check your NEO4J_USERNAME and NEO4J_PASSWORD in the .env file.")
    except exceptions.ServiceUnavailable as e:
        print(f"Connection Failed: The database seems to be unreachable from this script. Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if driver:
            driver.close()
            print("Connection closed.")


if __name__ == "__main__":
    check_neo4j_connection()