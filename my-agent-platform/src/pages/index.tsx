import Head from 'next/head';
import Chat from '../components/Chat';

const Home: React.FC = () => {
  return (
    <div>
      <Head>
        <title>Agent Platform</title>
        <meta name="description" content="Create and chat with your own agents" />
      </Head>
      <main>
        <Chat />
      </main>
    </div>
  );
};

export default Home;