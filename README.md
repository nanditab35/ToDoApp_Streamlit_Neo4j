# ToDoApp_Streamlit_Neo4j

### Main Features:
- Load Neo4j ToDo Graph DB.
- Reset the Neo4j ToDo Graph DB, using some basic script like cql_scripts/crerate_todo_db.cql. This script will delete the current Graph first then create it from the script.
- Update Nodes form the ToDo Graph App, by clicking on any Node and updating the task status in the Update form inside the Sidebar.
- Delete Nodes form the ToDo Graph App (Only when task status is "Done").
- Create new Task Nodes form the ToDo Graph App.
- Take ToDo Graph DB Snapshots (todo_snapshot.cql), and Load fom the last saved Snapshot. This script (todo_snapshot.cql) will delete the current Graph first then create it from the script.

### How to run
- pip install -r requirements.txt
- steamlit run app.py
