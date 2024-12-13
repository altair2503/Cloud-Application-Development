// Define the logEvents function
exports.eventNotification = (req, res) => {
  // Check if content type is JSON
  if (req.get('content-type') !== 'application/json') {
      return res.status(415).json({ error: 'Unsupported Media Type' });
  }

  const requestBody = req.body;
  const method = requestBody.method;

  let message;

  // Determine the action based on the HTTP method
  if (method === 'POST') {
      console.log(`New post published: ${JSON.stringify(requestBody)}`);
      message = `New post ${JSON.stringify(requestBody)} created.`;
  } else if (method === 'PUT') {
      console.log(`Post updated: ${JSON.stringify(requestBody)}`);
      message = `Post ${JSON.stringify(requestBody)} updated.`;
  } else if (method === 'DELETE') {
      console.log(`Post deleted! ${JSON.stringify(requestBody)}`);
      message = `Post ${JSON.stringify(requestBody)} deleted.`;
  } else {
      console.log(`Unsupported HTTP method: ${method}`);
      return res.status(405).json({ error: 'Method Not Allowed' });
  }

  return res.status(200).json({ message: message });
};
