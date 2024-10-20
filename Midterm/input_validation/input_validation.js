// Define the input validation function
exports.inputValidation = (req, res) => {
  // Check if content type is JSON
  if (req.get('content-type') !== 'application/json') {
    return res.status(415).json({ error: 'Unsupported Media Type' });
  }

  const requestBody = req.body;

  // Validate the presence of 'name' and 'phone' in the request body
  if (!requestBody.name && !requestBody.phone) {
    return res.status(400).json({ error: 'Name and phone not provided!' });
  }

  if (!requestBody.name) {
    return res.status(400).json({ error: 'Name not provided!' });
  }

  if (!requestBody.phone) {
    return res.status(400).json({ error: 'Phone not provided!' });
  }

  // Input data are validated
  return res.status(200).json({ message: 'Input data are validated.' });
};
