import React, { useState } from 'react';
import axios from 'axios';

const Chat: React.FC = () => {
  const [prompt, setPrompt] = useState('');
  const [response, setResponse] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(''); // Clear previous error
    try {
      const result = await axios.post('/api/chat', { prompt });
      setResponse(result.data.response);
    } catch (error) {
      console.error('Error fetching response:', error);
      setError('Error fetching response');
    }
  };

  return (
    <div>
      <h1>Chat with your Agent</h1>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Enter your prompt"
        />
        <button type="submit">Send</button>
      </form>
      {response && <div><strong>Response:</strong> {response}</div>}
      {error && <div><strong>Error:</strong> {error}</div>}
    </div>
  );
};

export default Chat;