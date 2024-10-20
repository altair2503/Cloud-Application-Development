// Define the logEvents function
exports.logEvents = (req, res) => {
  // Check if content type is JSON
  if (req.get('content-type') !== 'application/json') {
      return res.status(415).json({ error: 'Unsupported Media Type' });
  }

  const requestBody = req.body;
  const method = requestBody.method;

  // Validate the presence of 'name' and 'phone' in the request
  if (!requestBody || !requestBody.name || !requestBody.phone) {
      console.log('Error 400: No name or phone provided!');
      return res.status(400).json({ error: 'No name or phone provided' });
  }

  let message;

  // Determine the action based on the HTTP method
  if (method === 'POST') {
      console.log(`New phone added: ${JSON.stringify(requestBody)}`);
      message = `New phone ${JSON.stringify(requestBody)} created.`;
  } else if (method === 'PUT') {
      console.log(`Phone updated: ${JSON.stringify(requestBody)}`);
      message = `Phone ${JSON.stringify(requestBody)} updated.`;
  } else if (method === 'DELETE') {
      console.log(`Phone deleted! ${JSON.stringify(requestBody)}`);
      message = `Phone ${JSON.stringify(requestBody)} deleted.`;
  } else {
      console.log(`Unsupported HTTP method: ${method}`);
      return res.status(405).json({ error: 'Method Not Allowed' });
  }

  return res.status(200).json({ message: message });
};
