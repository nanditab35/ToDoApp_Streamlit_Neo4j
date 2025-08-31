// Clear existing database to ensure a clean slate
MATCH (n) DETACH DELETE n;

// Start Creating Nodes (Start_Node, Task_Category) and Relationships
MERGE (:Start_Node {name: 'GenAI ToDo', status: 'Planning'});
MERGE (:Task_Category {name: 'Documenting', status: 'Planning'});
MERGE (:Task_Category {name: 'Apply Jobs', status: 'Planning'});
MERGE (:Task_Category {name: 'POC', status: 'Planning'});
MERGE (:Task_Category {name: 'Explore', status: 'Planning'});
MERGE (:Task_Category {name: 'Blogging', status: 'Planning'});
MERGE (:Task_Category {name: 'DSA', status: 'Planning'});
MERGE (:Task_Category {name: 'System Design', status: 'Planning'});

MATCH (p:Start_Node {name: 'GenAI ToDo'}), (t:Task_Category {name: 'Documenting'}) CREATE (p)-[:HAS_TASK_TYPE]->(t);
MATCH (p:Start_Node {name: 'GenAI ToDo'}), (t:Task_Category {name: 'Apply Jobs'}) CREATE (p)-[:HAS_TASK_TYPE]->(t);
MATCH (p:Start_Node {name: 'GenAI ToDo'}), (t:Task_Category {name: 'POC'}) CREATE (p)-[:HAS_TASK_TYPE]->(t);
MATCH (p:Start_Node {name: 'GenAI ToDo'}), (t:Task_Category {name: 'Explore'}) CREATE (p)-[:HAS_TASK_TYPE]->(t);
MATCH (p:Start_Node {name: 'GenAI ToDo'}), (t:Task_Category {name: 'Blogging'}) CREATE (p)-[:HAS_TASK_TYPE]->(t);
MATCH (p:Start_Node {name: 'GenAI ToDo'}), (t:Task_Category {name: 'DSA'}) CREATE (p)-[:HAS_TASK_TYPE]->(t);
MATCH (p:Start_Node {name: 'GenAI ToDo'}), (t:Task_Category {name: 'System Design'}) CREATE (p)-[:HAS_TASK_TYPE]->(t);

// Create Task Nodes and Relationships for 'Documenting' Task_Category
MERGE (:Task {name: 'Explation Slides', status: 'InProgress'});
MERGE (:Task {name: 'POC Tracker', status: 'InProgress'});
MERGE (:Task {name: 'Resume Updating', status: 'InProgress'});

MATCH (p:Task_Category {name: 'Documenting'}), (t:Task {name: 'Explation Slides'}) CREATE (p)-[:HAS_TASK]->(t);
MATCH (p:Task_Category {name: 'Documenting'}), (t:Task {name: 'POC Tracker'}) CREATE (p)-[:HAS_TASK]->(t);
MATCH (p:Task_Category {name: 'Documenting'}), (t:Task {name: 'Resume Updating'}) CREATE (p)-[:HAS_TASK]->(t);

// Create Task Nodes and Relationships for Blogging Task_Category
MERGE (:Task {name: 'Kaggle', status: 'Planning'});
MERGE (:Task {name: 'Github', status: 'Planning'});

MATCH (p:Task_Category {name: 'Blogging'}), (t:Task {name: 'Kaggle'}) CREATE (p)-[:HAS_TASK]->(t);
MATCH (p:Task_Category {name: 'Blogging'}), (t:Task {name: 'Github'}) CREATE (p)-[:HAS_TASK]->(t);

// Create Task Nodes and Relationships for Explore Task_Category
MERGE (:Task {name: 'Graph RAG Course', status: 'Planning'});
MERGE (:Task {name: 'Model Serving', status: 'Planning'});

MATCH (p:Task_Category {name: 'Explore'}), (t:Task {name: 'Graph RAG Course'}) CREATE (p)-[:HAS_TASK]->(t);
MATCH (p:Task_Category {name: 'Explore'}), (t:Task {name: 'Model Serving'}) CREATE (p)-[:HAS_TASK]->(t);

// Create Task_Category Nodes and Relationships for POC Task_Category (like sub-category)
MERGE (:Task_Category {name: 'App Building', status: 'Planning'});
MERGE (:Task_Category {name: 'RAG', status: 'InProgress'});
MERGE (:Task_Category {name: 'AI-Agent Building', status: 'Planning'});

MATCH (p:Task_Category {name: 'POC'}), (t:Task_Category {name: 'App Building'}) CREATE (p)-[:HAS_TASK]->(t);
MATCH (p:Task_Category {name: 'POC'}), (t:Task_Category {name: 'RAG'}) CREATE (p)-[:HAS_TASK]->(t);
MATCH (p:Task_Category {name: 'POC'}), (t:Task_Category {name: 'AI-Agent Building'}) CREATE (p)-[:HAS_TASK]->(t);

// Create Task Nodes and Relationships for App Building Task_Category
MERGE (:Task {name: 'ToDo App', status: 'Planning'});

MATCH (p:Task_Category {name: 'App Building'}), (t:Task {name: 'ToDo App'}) CREATE (p)-[:HAS_TASK]->(t);

// Create SubTask Nodes and Relationships for 'ToDo App' Task
MERGE (:SubTask {name: 'Task Update Feature', status: 'Planning'});
MERGE (:SubTask {name: 'Task Create Feature', status: 'Planning'});
MERGE (:SubTask {name: 'ToDo Reset Feature', status: 'Planning'});
MERGE (:SubTask {name: 'ToDo Snapshot Feature', status: 'Planning'});

MATCH (p:Task {name: 'ToDo App'}), (t:SubTask {name: 'Task Update Feature'}) CREATE (p)-[:HAS_SUBTASK]->(t);
MATCH (p:Task {name: 'ToDo App'}), (t:SubTask {name: 'Task Create Feature'}) CREATE (p)-[:HAS_SUBTASK]->(t);
MATCH (p:Task {name: 'ToDo App'}), (t:SubTask {name: 'ToDo Reset Feature'}) CREATE (p)-[:HAS_SUBTASK]->(t);
MATCH (p:Task {name: 'ToDo App'}), (t:SubTask {name: 'ToDo Snapshot Feature'}) CREATE (p)-[:HAS_SUBTASK]->(t);
