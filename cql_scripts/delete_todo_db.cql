
// Delete Relationships
MATCH ()-[r]->() DELETE r

// Delete Nodes
MATCH (n) DETACH DELETE n
