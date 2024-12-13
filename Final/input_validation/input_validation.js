// Define the input validation function
exports.inputValidation = (req, res) => {
  // Check if content type is JSON
  if (req.get('content-type') !== 'application/json') {
    return res.status(415).json({ error: 'Unsupported Media Type' });
  }

  const requestBody = req.body;

  // Validate the presence of 'name' and 'phone' in the request body
  if (!requestBody.tittle) {
    return res.status(400).json({ error: 'Tittle not provided!' });
  }

  if (!requestBody.text) {
    return res.status(400).json({ error: 'Text not provided!' });
  }

  if (!requestBody.category) {
    return res.status(400).json({ error: 'Category not provided!' });
  }

  // Input data are validated
  return res.status(200).json({ message: 'Input data are validated.' });
};
