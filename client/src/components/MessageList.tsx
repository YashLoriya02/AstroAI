
import { MessageBubble } from './MessageBubble';

interface Message {
  id: number;
  type: string;
  content: string;
  timestamp: Date;
}

interface MessageListProps {
  messages: Message[];
}

export const MessageList = ({ messages }: MessageListProps) => {
  return (
    <div className="space-y-6">
      {messages.map((message) => (
        <MessageBubble key={message.id} message={message} />
      ))}
    </div>
  );
};
