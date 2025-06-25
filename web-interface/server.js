const express = require('express');
const path = require('path');
const cors = require('cors');

const app = express();
const PORT = 8080;

// Enable CORS for all routes
app.use(cors());

// Serve static files
app.use(express.static(__dirname));

// Default route
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'index.html'));
});

// Start server
app.listen(PORT, () => {
  console.log(`Web interface running at http://localhost:${PORT}`);
  console.log(`Connecting to Rasa server at http://localhost:5005`);
});
