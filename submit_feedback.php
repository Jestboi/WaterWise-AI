<?php
// Database connection
$db = new SQLite3('feedback.db');

// Create feedback table if it doesn't exist
$db->exec('CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rating INTEGER,
    name TEXT,
    email TEXT,
    comment TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)');

// Get POST data
$data = json_decode(file_get_contents('php://input'), true);

if ($data) {
    // Prepare and execute insert statement
    $stmt = $db->prepare('INSERT INTO feedback (rating, name, email, comment) VALUES (:rating, :name, :email, :comment)');
    $stmt->bindValue(':rating', $data['rating'], SQLITE3_INTEGER);
    $stmt->bindValue(':name', $data['name'], SQLITE3_TEXT);
    $stmt->bindValue(':email', $data['email'], SQLITE3_TEXT);
    $stmt->bindValue(':comment', $data['comment'], SQLITE3_TEXT);
    
    if ($stmt->execute()) {
        http_response_code(200);
        echo json_encode(['status' => 'success']);
    } else {
        http_response_code(500);
        echo json_encode(['status' => 'error', 'message' => 'Failed to save feedback']);
    }
} else {
    http_response_code(400);
    echo json_encode(['status' => 'error', 'message' => 'Invalid data']);
}
