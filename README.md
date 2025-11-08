# ToDoApp_Streamlit_Neo4j
A modern, interactive ToDo application built with Streamlit and Neo4j Graph Database that visualizes your tasks and their relationships in a graph format.

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

### 🌟 Features
- Graph Visualization: View your tasks as interconnected nodes in a Neo4j graph database
- Interactive Interface: Built with Streamlit for a seamless user experience
- Real-time Updates: See changes reflected immediately in the graph visualization

### Task Management
- Create Tasks: Add new tasks with descriptions and status
- Update Tasks: Modify task status and details through an intuitive sidebar form
- Delete Tasks: Remove completed tasks (only when status is "Done")
- Status Tracking: Monitor task progress with different status states

### Database Management
- Database Loading: Initialize and connect to Neo4j ToDo Graph DB
- Database Reset: Reset the entire graph database using CQL scripts
- Snapshot System: Save and load database snapshots for backup and restoration
- Script-based Operations: Manage database structure through CQL script files

🚀 Quick Start

### Prerequisites
Python 3.7 or higher
Neo4j Database (local or AuraDB instance)
Streamlit
Installation

### Clone the repository
git clone https://github.com/nanditab35/ToDoApp_Streamlit_Neo4j.git
cd ToDoApp_Streamlit_Neo4j

### Install dependencies
- pip install -r requirements.txt
- Set up Neo4j connection
- Update the Neo4j connection details in the app
- Ensure your Neo4j instance is running

### Run the application
streamlit run app.py

### 📁 Project Structure
ToDoApp_Streamlit_Neo4j/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── cql_scripts/
│   ├── create_todo_db.cql # Database initialization script
│   └── todo_snapshot.cql  # Database snapshot template
└── README.md             # This file

### 🔧 Usage
- **Initial Setup**
  - Launch the app using streamlit run app.py
  - Configure your Neo4j database connection in the sidebar
  - Load the initial database structure using the "Load Neo4j ToDo Graph DB" option
- **Managing Tasks**
  - Create New Task: Use the task creation form in the sidebar
  - Update Tasks: Click on any node in the graph and update its properties in the sidebar form
  - Delete Tasks: Remove tasks marked as "Done" through the delete functionality
  - View Relationships: See how tasks are connected in the graph visualization
- **Database Operations**
  - Reset Database: Use the reset functionality to clear and recreate the database structure
  - Take Snapshots: Save the current state of your database for backup
  - Load Snapshots: Restore your database from previously saved snapshots
- 🗃️ **CQL Scripts**
  - The application uses Cypher Query Language (CQL) scripts for database operations:
  - cql_scripts/create_todo_db.cql: Initializes the database structure
  - cql_scripts/todo_snapshot.cql: Template for database snapshots
- 🔒 **Security Notes**
  - Ensure your Neo4j credentials are properly secured
  - The application only allows deletion of tasks with "Done" status
  - Database reset operations require confirmation
    
### 📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

👥 Author
GitHub: @nanditab35

🙏 Acknowledgments
- Built with Streamlit
- Database powered by Neo4j
- Graph visualization using Neo4j's native capabilities
