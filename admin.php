<?php
session_start();

// Basic authentication (you should replace this with more secure authentication)
$admin_username = "admin";
$admin_password = "admin123"; // Changed to a temporary password - please change this to something more secure

// Check if user is logged in
if (!isset($_SESSION['admin_logged_in'])) {
    if (isset($_POST['username']) && isset($_POST['password'])) {
        if ($_POST['username'] === $admin_username && $_POST['password'] === $admin_password) {
            $_SESSION['admin_logged_in'] = true;
        } else {
            $error = "Invalid credentials";
        }
    }
    
    // Show login form if not logged in
    if (!isset($_SESSION['admin_logged_in'])) {
        ?>
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Admin Login</title>
            <script src="https://cdn.tailwindcss.com"></script>
        </head>
        <body class="bg-gray-100 min-h-screen flex items-center justify-center">
            <div class="bg-white p-8 rounded-lg shadow-md w-96">
                <h1 class="text-2xl font-bold mb-6 text-center">Admin Login</h1>
                <?php if (isset($error)): ?>
                    <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
                        <?php echo htmlspecialchars($error); ?>
                    </div>
                <?php endif; ?>
                <form method="POST" class="space-y-4">
                    <div>
                        <label class="block text-gray-700 text-sm font-bold mb-2">Username</label>
                        <input type="text" name="username" required 
                               class="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:border-blue-500">
                    </div>
                    <div>
                        <label class="block text-gray-700 text-sm font-bold mb-2">Password</label>
                        <input type="password" name="password" required 
                               class="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:border-blue-500">
                    </div>
                    <button type="submit" 
                            class="w-full bg-blue-500 text-white font-bold py-2 px-4 rounded hover:bg-blue-600 transition-colors">
                        Login
                    </button>
                </form>
            </div>
        </body>
        </html>
        <?php
        exit;
    }
}

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

// Handle deletion
if (isset($_POST['delete']) && isset($_POST['id'])) {
    $stmt = $db->prepare('DELETE FROM feedback WHERE id = :id');
    $stmt->bindValue(':id', $_POST['id'], SQLITE3_INTEGER);
    $stmt->execute();
}

// Get all feedback entries
$results = $db->query('SELECT * FROM feedback ORDER BY timestamp DESC');
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Feedback Admin Panel</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
</head>
<body class="bg-gray-100 min-h-screen">
    <div class="container mx-auto px-4 py-8">
        <div class="flex justify-between items-center mb-6">
            <h1 class="text-3xl font-bold text-gray-800">Feedback Management</h1>
            <form method="POST" action="admin.php" class="inline">
                <input type="hidden" name="logout" value="1">
                <button type="submit" class="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600 transition-colors">
                    Logout
                </button>
            </form>
        </div>

        <div class="bg-white rounded-lg shadow-md">
            <div class="overflow-x-auto">
                <table class="min-w-full table-auto divide-y divide-gray-200">
                    <thead class="bg-gray-50">
                        <tr class="text-center">
                            <th scope="col" class="p-3 text-xs font-semibold tracking-wider text-gray-500 uppercase">Date</th>
                            <th scope="col" class="p-3 text-xs font-semibold tracking-wider text-gray-500 uppercase">Rating</th>
                            <th scope="col" class="p-3 text-xs font-semibold tracking-wider text-gray-500 uppercase">Name</th>
                            <th scope="col" class="p-3 text-xs font-semibold tracking-wider text-gray-500 uppercase">Email</th>
                            <th scope="col" class="p-3 text-xs font-semibold tracking-wider text-gray-500 uppercase">Comment</th>
                            <th scope="col" class="p-3 text-xs font-semibold tracking-wider text-gray-500 uppercase">Action</th>
                        </tr>
                    </thead>
                    <tbody class="bg-white divide-y divide-gray-200">
                        <?php while ($row = $results->fetchArray(SQLITE3_ASSOC)): ?>
                        <tr>
                            <td class="p-3 text-sm text-gray-500 text-center">
                                <?php echo htmlspecialchars(date('Y-m-d H:i', strtotime($row['timestamp']))); ?>
                            </td>
                            <td class="p-3 text-center">
                                <div class="flex justify-center gap-1">
                                    <?php for ($i = 1; $i <= 5; $i++): ?>
                                        <i class="fas fa-star <?php echo $i <= $row['rating'] ? 'text-yellow-400' : 'text-gray-300'; ?>"></i>
                                    <?php endfor; ?>
                                </div>
                            </td>
                            <td class="p-3 text-sm text-gray-900 text-center">
                                <?php echo htmlspecialchars($row['name']); ?>
                            </td>
                            <td class="p-3 text-sm text-gray-900 text-center">
                                <?php echo htmlspecialchars($row['email']); ?>
                            </td>
                            <td class="p-3 text-sm text-gray-900">
                                <?php echo nl2br(htmlspecialchars($row['comment'])); ?>
                            </td>
                            <td class="p-3 text-center">
                                <form method="POST" class="inline-block">
                                    <input type="hidden" name="id" value="<?php echo $row['id']; ?>">
                                    <button type="submit" name="delete" value="1" 
                                            class="text-red-600 hover:text-red-900 font-medium"
                                            onclick="return confirm('Are you sure you want to delete this feedback?')">
                                        Delete
                                    </button>
                                </form>
                            </td>
                        </tr>
                        <?php endwhile; ?>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</body>
</html>
