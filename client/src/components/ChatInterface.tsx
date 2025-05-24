
import { useState, useRef, useEffect } from 'react';
import { MessageList } from './MessageList';
import { MessageInput } from './MessageInput';

interface Message {
  id: number;
  type: string;
  content: string;
  timestamp: Date;
}

interface ChatInterfaceProps {
  messages: Message[];
  onSendMessage: (content: string) => void;
  isLoading: boolean
}

export const ChatInterface = ({ messages, onSendMessage, isLoading }: ChatInterfaceProps) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  return (
    <div className="flex flex-col h-[calc(100vh-100px)] max-w-[90%] mx-auto">
      <div className="flex-1 rounded-t-2xl pt-6 overflow-hidden">
        <div className="h-full flex flex-col">
          <div className="flex-1 overflow-y-auto no-scrollbar p-6 space-y-6">
            <MessageList messages={messages} />
            <div ref={messagesEndRef} />
          </div>
          
          <div className="mt-4 border-purple-500/20 p-6 pt-4">
            <MessageInput onSendMessage={onSendMessage} isLoading={isLoading} />
          </div>
        </div>
      </div>
    </div>
  );
};
