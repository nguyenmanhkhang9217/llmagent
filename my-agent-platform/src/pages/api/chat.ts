import type { NextApiRequest, NextApiResponse } from 'next';
import axios from 'axios';
import { headers } from 'next/headers';

type Data = {
  response: string;
};

const handler = async (req: NextApiRequest, res: NextApiResponse<Data>) => {
  if (req.method === 'POST') {
    const { prompt } = req.body;
    try {
        const conf = {
            headers: { 'Content-Type': 'application/json'}
        }
      const response = await axios.post('http://127.0.0.1:9000/api/chat', { prompt });
      console.log(response.data.response)
      res.status(200).json({ response: response.data.response });
    } catch (error) {
        console.log(error)
      res.status(500).json({ response: 'Error fetching response' });
    }
  } else {
    res.status(405).json({ response: 'Method not allowed' });
  }
};

export default handler;