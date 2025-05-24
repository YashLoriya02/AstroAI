import { ChatInterface } from '@/components/ChatInterface';
import { CosmicHeader } from '@/components/CosmicHeader';
import { StarField } from '@/components/StarField';
import { useState } from 'react';

const SERVER_URL = 'http://localhost:5000/generate'

const Index = () => {
  const [isLoading, setIsLoading] = useState(false)

  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'bot',
      content: "🚀 Welcome to AstroAI! I'm your advanced space science assistant, specialized in astronomy, astrophysics, and space exploration. Ask me anything about the cosmos!",
      timestamp: new Date()
    }
  ]);

  const handleSendMessage = async (content: string) => {
    setIsLoading(true)

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);

    const botMessageId = Date.now() + 1;

    try {
      const response = await fetch(SERVER_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ text: content })
      });

      if (response.status === 404) {
        const data = await response.json()

        if (data.response_type === "rejection") {
          const rejectionMessage = {
            id: botMessageId,
            type: 'bot',
            content: data.message,
            timestamp: new Date()
          };

          setMessages(prev => [...prev, rejectionMessage]);
          // toast.error(data.message || "Something went wrong")
          return
        }
      }

      if (!response.ok) {
        throw new Error('Failed to connect to the server.');
      }

      const initialBotMessage = {
        id: botMessageId,
        type: 'bot',
        content: '',
        timestamp: new Date()
      };

      setMessages(prev => [...prev, initialBotMessage]);

      const reader = response.body?.getReader();
      const decoder = new TextDecoder('utf-8');
      let botContent = '';

      while (reader) {
        const { value, done } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        botContent += chunk;

        // Update the last bot message incrementally
        setMessages(prev =>
          prev.map(msg =>
            msg.id === botMessageId ? { ...msg, content: botContent } : msg
          )
        );
      }

    } catch (error) {
      console.error(error);
      setMessages(prev =>
        prev.map(msg =>
          msg.id === botMessageId
            ? { ...msg, content: '⚠️ Error fetching response from server.' }
            : msg
        )
      );
    }
    finally {
      setIsLoading(false)
    }
  };

  return (
    <div className="bg-gradient-to-b h-screen from-slate-900 to-slate-900 relative overflow-hidden">
      <StarField />
      {/* <FloatingAstronaut /> */}

      <div className="relative z-10 flex flex-col">
        <CosmicHeader />

        <main className="mx-auto p-3 w-full">
          <ChatInterface
            messages={messages}
            onSendMessage={handleSendMessage}
            isLoading={isLoading}
          />
        </main>

        {/* <footer className="text-center py-4 text-purple-300/60 text-sm">
          <p>AstroAI - Your Gateway to the Cosmos</p>
        </footer> */}
      </div>
    </div>
  );
};

export default Index;
