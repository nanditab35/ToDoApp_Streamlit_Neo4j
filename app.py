import os
from dotenv import load_dotenv
import streamlit as st
from neo4j import GraphDatabase
from streamlit_agraph import agraph, Node, Edge, Config
import textwrap

NODE_COLOR_MAP = {
    "Start_Node": "#FFEF00", # Light Yellow for Start Node
    "Task_Category": "#C6A4FF",  # A reddish color Task_Category
    "Task": "#88E788", # A purple color for Task
    "SubTask": "#90D5FF",   # A teal color for SubTask
    # Add other labels from your graph here
}
DEFAULT_NODE_COLOR = "#B2B2B2" # A neutral default color for other node types
# START_NODE_NAME = "GenAI ToDo"

##================== Neo4j Connection ======================

def wrap_text(text, width=9):
    """Wraps text to a specified width with newlines."""
    # Use textwrap to handle wrapping gracefully
    return '\n'.join(textwrap.wrap(str(text), width=width, break_on_hyphens=True))

# Use Streamlit's caching to store the driver instance
@st.cache_resource
def get_driver():
    """Creates a Neo4j driver instance."""
    load_dotenv()
    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USERNAME")
    password = os.getenv("NEO4J_PASSWORD")
    return GraphDatabase.driver(uri, auth=(user, password), max_connection_lifetime=3600)

##TODO: Debug & test this function with actual .cql file
def run_cypher_script(driver, file_path):
    """Reads a .cql file and executes the Cypher queries against the database."""
    with driver.session() as session:
        try:
            with open(file_path, 'r') as f:
                cql_script = f.read()
                # Split script into individual statements, removing empty ones
                queries = [q.strip() for q in cql_script.split(';') if q.strip()]
                
                for query in queries:
                    if query: # Ensure not to run empty queries
                        session.run(query)
            return True, "Script executed successfully."
        except FileNotFoundError:
            return False, f"Error: The file {file_path} was not found."
        except Exception as e:
            return False, f"An error occurred: {e}"
        
# Use Streamlit's data caching for the query results
@st.cache_data(ttl=3600) # Cache data for 1 hour
def fetch_graph_data(_driver):
    """Fetches all nodes and relationships from the graph."""
    with _driver.session() as session:
        # This query fetches nodes and the relationships between them
        # We limit to 100 to avoid overwhelming the browser with a very large graph
        result = session.run("MATCH (n)-[r]->(m) RETURN n, r, m LIMIT 100")
        # Process data into a simple list of dicts before returning
        processed_data = []
        for record in result:
            source_node = record['n']
            target_node = record['m']
            relationship = record['r']
            
            processed_data.append({
                "source": {"id": source_node.element_id, "labels": list(source_node.labels), "properties": dict(source_node)},
                "target": {"id": target_node.element_id, "labels": list(target_node.labels), "properties": dict(target_node)},
                "relationship": {"type": relationship.type}
            })
        return processed_data

##================== Database Interaction Functions ======================

def format_cypher_properties(props):
    """Formats a dictionary of properties into a Cypher map string, escaping values."""
    items = []
    for key, value in props.items():
        # Use backticks for keys to handle special characters or keywords
        formatted_key = f"`{key}`"
        if isinstance(value, str):
            # Escape backslashes and single quotes in the string value
            escaped_value = value.replace('\\', '\\\\').replace("'", "\\'")
            formatted_value = f"'{escaped_value}'"
        elif isinstance(value, (int, float, bool)):
            formatted_value = str(value)
        else:
            # For other types (like lists or null), convert to string and quote
            escaped_value = str(value).replace('\\', '\\\\').replace("'", "\\'")
            formatted_value = f"'{escaped_value}'"
        items.append(f"{formatted_key}: {formatted_value}")
    return "{" + ", ".join(items) + "}"

def create_database_snapshot(_driver, file_path):
    """Queries the current database state and writes it to a .cql snapshot file."""
    cypher_statements = []
    try:
        with _driver.session() as session:
            # 1. Start with a command to clear the database
            cypher_statements.append("MATCH (n) DETACH DELETE n;")
            cypher_statements.append("\n// --- Creating Nodes ---")

            # 2. Fetch all nodes and generate CREATE statements
            nodes_result = session.run("MATCH (n) RETURN n")
            nodes_data = [record['n'] for record in nodes_result]

            if not nodes_data:
                with open(file_path, 'w') as f:
                    f.write("// Database is empty. No snapshot created.")
                return True, "Snapshot created (database was empty)."

            for node in nodes_data:
                labels = ":".join(node.labels)
                props = format_cypher_properties(dict(node))
                cypher_statements.append(f"CREATE (:{labels} {props});")

            cypher_statements.append("\n// --- Creating Relationships ---")

            # 3. Fetch all relationships and generate CREATE statements
            rels_result = session.run("MATCH (n)-[r]->(m) RETURN n, r, m")
            for record in rels_result:
                source_node, rel, target_node = record['n'], record['r'], record['m']
                source_match = f"(a:{':'.join(source_node.labels)} {format_cypher_properties(dict(source_node))})"
                target_match = f"(b:{':'.join(target_node.labels)} {format_cypher_properties(dict(target_node))})"
                rel_create = f"[:`{rel.type}` {format_cypher_properties(dict(rel))}]" if dict(rel) else f"[:`{rel.type}`]"
                cypher_statements.append(f"MATCH {source_match}, {target_match} CREATE (a)-{rel_create}->(b);")

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(cypher_statements))
        return True, f"Snapshot created at `{os.path.basename(file_path)}`"
    except Exception as e:
        return False, f"An error occurred during snapshot creation: {e}"

@st.cache_data(ttl=5) # ttl=5, Use a short cache to get fresh data for editing
def fetch_node_properties(_driver, node_id):
    """Fetches properties for a specific node by its element ID."""
    with _driver.session() as session:
        result = session.run("MATCH (n) WHERE elementId(n) = $node_id RETURN properties(n) AS props", node_id=node_id)
        record = result.single()
        return record['props'] if record else {}

def update_node_properties(_driver, node_id, new_properties):
    """Updates properties for a specific node using its element ID."""
    with _driver.session() as session:
        # Using SET n += $props is a convenient way to update properties from a dictionary
        session.run("MATCH (n) WHERE elementId(n) = $node_id SET n += $props", 
                    node_id=node_id, props=new_properties)

def delete_node(_driver, node_id):
    """Deletes a node and its relationships using its element ID."""
    with _driver.session() as session:
        # DETACH DELETE removes the node and all its relationships
        result = session.run("MATCH (n) WHERE elementId(n) = $node_id DETACH DELETE n", 
                             node_id=node_id)
        if result.consume().counters.nodes_deleted == 0:
            raise Exception("Node could not be deleted. It might have been removed already.")

def create_node_and_relationship(_driver, node_name, parent_node_name, relationship_type):
    """Creates a new node and a relationship to a parent node."""
    # Define allowed relationships and their corresponding new node labels
    rel_to_label_map = {
        "HAS_TASK": "Task",
        "HAS_SUBTASK": "SubTask",
        "HAS_TASK_TYPE": "Task_Category"
    }

    if relationship_type not in rel_to_label_map:
        raise ValueError(f"Invalid relationship type: {relationship_type}. Must be one of {list(rel_to_label_map.keys())}")

    node_label = rel_to_label_map[relationship_type]

    with _driver.session() as session:
        # This query finds the parent, creates the new node, and then the relationship.
        # The node label and relationship type are validated above, so f-string is safe here.
        query = (f"MATCH (p {{name: $parent_node_name}}) "
                 f"CREATE (n:{node_label} {{name: $node_name, status: 'Planning'}}) "
                 f"CREATE (p)-[:`{relationship_type}`]->(n)")
        result = session.run(query, node_name=node_name, parent_node_name=parent_node_name)
        if result.consume().counters.nodes_created == 0:
            raise Exception(f"Could not create node. Parent node '{parent_node_name}' might not exist.")

##================== Sidebar and Form Rendering ======================
def render_sidebar(driver):
    """
    This function acts as an "alias" for the sidebar UI.
    It renders all sidebar components, including the always-visible edit form.
    """
    st.sidebar.header("Database Controls")

    if st.sidebar.button("Backup Snapshot"):
        with st.spinner("Creating database snapshot..."):
            snapshot_dir = os.path.join(os.path.dirname(__file__), 'cql_scripts')
            os.makedirs(snapshot_dir, exist_ok=True) # Ensure directory exists
            snapshot_path = os.path.join(snapshot_dir, 'todo_snapshot.cql')
            success, message = create_database_snapshot(driver, snapshot_path)
            if success:
                st.sidebar.success(message)
            else:
                st.sidebar.error(message)
    
    if st.sidebar.button("Load Snapshot"):
        with st.spinner("Setting up database from `todo_snapshot.cql`..."):
            script_path = os.path.join(os.path.dirname(__file__), 'cql_scripts', 'todo_snapshot.cql')
            success, message = run_cypher_script(driver, script_path)
            if success:
                st.sidebar.success(message)
                st.cache_data.clear()
                st.session_state.graph_visible = True
                st.rerun()
            else:
                st.sidebar.error(message)

    if st.sidebar.button("Setup / Reset Database"):
        with st.spinner("Setting up database from `create_todo_db.cql`..."):
            script_path = os.path.join(os.path.dirname(__file__), 'cql_scripts', 'create_todo_db.cql')
            success, message = run_cypher_script(driver, script_path)
            if success:
                st.sidebar.success(message)
                st.cache_data.clear()
                st.session_state.graph_visible = True
                st.rerun()
            else:
                st.sidebar.error(message)

    st.sidebar.header("Edit Node")

    node_id = st.session_state.get('selected_node')
    node_props = {}
    is_node_selected = node_id is not None

    if is_node_selected:
        try:
            node_props = fetch_node_properties(driver, node_id)
            if not node_props:
                st.sidebar.warning("Could not find properties for the selected node.")
                st.session_state.selected_node = None
                st.rerun()
        except Exception as e:
            st.sidebar.error(f"Error fetching node: {e}")
            st.session_state.selected_node = None
            st.rerun()

    # Display a dynamic subheader
    st.sidebar.subheader(f"Editing: {node_props.get('name', 'N/A')}" if is_node_selected else "Select a node to edit")

    with st.sidebar.form(key="edit_node_form"):
        new_props = {}
        # Dynamically create inputs. They will be disabled if no node is selected.
        for key, value in node_props.items():
            if key == 'status':
                status_options = ["Planning", "InProgress", "Done"]
                # Ensure current value is in options, otherwise default to first
                current_index = status_options.index(value) if value in status_options else 0
                new_props[key] = st.selectbox(
                    "Status", 
                    options=status_options, 
                    index=current_index, 
                    key="edit_status", 
                    disabled=not is_node_selected
                )
            else:
                new_props[key] = st.text_input(f"{key.capitalize()}", value=str(value), key=f"edit_{key}", disabled=not is_node_selected)

        submitted = st.form_submit_button("Update Node", disabled=not is_node_selected)
        if submitted:
            # If status is 'Done', we delete the node. Otherwise, we update it.
            if new_props.get('status') == 'Done':
                try:
                    with st.spinner("Completing and removing task..."):
                        delete_node(driver, node_id)
                    st.cache_data.clear()
                    st.session_state.selected_node = None
                    st.sidebar.success("Task marked as 'Done' and removed!")
                    st.rerun()
                except Exception as e:
                    st.sidebar.error(f"Error deleting node: {e}")
            else:
                with st.spinner("Updating node..."):
                    update_node_properties(driver, node_id, new_props)
                    st.cache_data.clear()
                    st.session_state.selected_node = None
                st.sidebar.success("Node updated successfully!")
                st.rerun()

    # A separate button outside the form to clear the selection
    if st.sidebar.button("Clear Selection", disabled=not is_node_selected):
        st.session_state.selected_node = None
        st.rerun()

    st.sidebar.header("Create New Node")
    with st.sidebar.form(key="create_node_form", clear_on_submit=True):
        node_name = st.text_input("NodeName", key="new_node_name")
        parent_name = st.text_input("ParentNodeName", key="parent_node_name")
        relation_type = st.selectbox(
            "RelationWithParent",
            options=["HAS_TASK", "HAS_SUBTASK", "HAS_TASK_TYPE"],
            index=0,
            help="This determines the new node's type (e.g., HAS_TASK creates a Task node)."
        )

        create_submitted = st.form_submit_button("Create Node")

        if create_submitted:
            if not node_name or not parent_name:
                st.sidebar.warning("Please fill in all fields.")
            else:
                try:
                    with st.spinner("Creating node..."):
                        create_node_and_relationship(driver, node_name, parent_name, relation_type)
                    st.cache_data.clear()
                    st.sidebar.success("Node created successfully! Refreshing graph...")
                    st.rerun()
                except Exception as e:
                    st.sidebar.error(f"Error: {e}")
##========================================================================

def draw_graph(processed_records):
    """Draws the graph using streamlit-agraph."""
    nodes = []
    edges = []
    node_ids = set()

    for record in processed_records:
        source_data = record['source']
        target_data = record['target']
        relationship_data = record['relationship']

        source_id = str(source_data['id'])
        if source_id not in node_ids:
            # Use a property for the label, like 'name' or 'title'. Fallback to the first property value.
            # label = source_node.get('name') or source_node.get('title') or next(iter(source_node.values()), source_id)
            source_props = source_data['properties']
            source_labels = source_data.get('labels', [])
            source_name = source_props['name']
            source_main_label = source_labels[0] if source_labels else None
            # print(source_main_label)
            node_color = NODE_COLOR_MAP.get(source_main_label, DEFAULT_NODE_COLOR)
            # if source_name == START_NODE_NAME:
            #     node_color = NODE_COLOR_MAP.get("START_NODE", DEFAULT_NODE_COLOR)
            label = source_props.get('name') or source_props.get('title') or next(iter(source_props.values()), source_id)
            wrap_label = wrap_text(label)
            # nodes.append(Node(id=source_id, label=str(label), size=25, shape='circle', font={'size': 10, 'align': 'middle'}))
            nodes.append(Node(id=source_id, label=str(wrap_label), size=25, shape='circle', color=node_color, font={'size': 9, 'align': 'middle'}))
            node_ids.add(source_id)

        target_id = str(target_data['id'])
        if target_id not in node_ids:
            # label = target_node.get('name') or target_node.get('title') or next(iter(target_node.values()), target_id)
            target_props = target_data['properties']
            target_labels = target_data.get('labels', [])
            target_main_label = target_labels[0] if target_labels else None
            # print(target_main_label)
            # print(target_props['name'])
            node_color = NODE_COLOR_MAP.get(target_main_label, DEFAULT_NODE_COLOR)
            
            label = target_props.get('name') or target_props.get('title') or next(iter(target_props.values()), target_id)
            wrap_label = wrap_text(label)
            # nodes.append(Node(id=target_id, label=str(label), size=25, shape='circle', font={'size': 10}))
            nodes.append(Node(id=target_id, label=str(wrap_label), size=25, shape='circle', color=node_color, font={'size': 9}))
            node_ids.add(target_id)

        # Use the relationship type as the edge label
        # edges.append(Edge(source=source_id, target=target_id, label=relationship.type))
        edges.append(Edge(source=source_id, target=target_id, \
                          label=relationship_data['type'], \
                          weight=5,
                          length=150,
                          font={'size': 9, 'align': 'middle'}))

    # Configure the graph's appearance
    config = Config(width=800,
                    height=800,
                    directed=True,
                    physics=True,
                    hierarchical=False,
                    interaction={"navigationButtons": True, "zoomView": True, "dragView": True},
                    zoomView=True,
                    dragView=True,
                    )
                    # **{"interaction": }

    clicked_node_id = agraph(nodes=nodes, edges=edges, config=config)
    return clicked_node_id

def main():
    ##================== App Configuration ======================
    st.set_page_config(
        page_title="ToDo Graph App",
        page_icon="✅",
        layout="wide"
    )

    st.title("ToDo Graph App")
    st.write("Welcome to this interactive ToDo App built with Streamlit!")

    # --- Session State Initialization ---
    # Used to track UI state across reruns
    if 'graph_visible' not in st.session_state:
        st.session_state.graph_visible = False
    if 'selected_node' not in st.session_state:
        st.session_state.selected_node = None

    driver = get_driver()

    # --- Sidebar Rendering (The "Alias") ---
    # This function now handles all sidebar logic, including the edit form.
    render_sidebar(driver)

    # --- Main Content Area ---
    # st.header("ToDo Graph")
    button_text = "Hide ToDo Graph" if st.session_state.graph_visible else "Load ToDo Graph"
    if st.button(button_text):
        if not st.session_state.graph_visible:
            st.cache_data.clear()
        st.session_state.graph_visible = not st.session_state.graph_visible
        if not st.session_state.graph_visible:
            st.session_state.selected_node = None
        st.rerun()

    # --- Graph Display and Node Selection Logic ---
    if st.session_state.graph_visible:
        records = fetch_graph_data(driver)
        if not records:
            st.warning("No data found in the database. Please set up the database to see the graph.")
        else:
            clicked_node = draw_graph(records)
            # If a new node is clicked, update the session state and rerun
            # to trigger the sidebar form to populate.
            if clicked_node and clicked_node != st.session_state.get('selected_node'):
                st.session_state.selected_node = clicked_node
                st.rerun()

if __name__ == "__main__":
    main()