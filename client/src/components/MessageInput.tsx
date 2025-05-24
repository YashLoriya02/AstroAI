
import { useState } from 'react';
import { Rocket } from 'lucide-react';
import { toast } from 'sonner';

interface MessageInputProps {
  onSendMessage: (content: string) => void;
  isLoading: boolean
}

export const MessageInput = ({ onSendMessage, isLoading }: MessageInputProps) => {
  const [message, setMessage] = useState('');
  // const [isChatLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!message.trim() || isLoading) {
      toast.error("Please wait while bot is typing...")
      return
    };

    const content = message.trim();
    setMessage('');

    onSendMessage(content);
  };

  return (
    <div className='flex justify-start h-1/2 flex-col w-full gap-5 items-start'>
      {
        isLoading &&
        <div className="flex items-center space-x-2 h-6">
          <span className="w-3 h-3 bg-gray-500 rounded-full animate-bounce [animation-delay:0s]"></span>
          <span className="w-3 h-3 bg-gray-500 rounded-full animate-bounce [animation-delay:0.1s]"></span>
          <span className="w-3 h-3 bg-gray-500 rounded-full animate-bounce [animation-delay:0.2s]"></span>
        </div>
      }
      <form onSubmit={handleSubmit} className="w-full relative">
        <div className="relative">
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Ask me about space, stars, planets, galaxies, or any cosmic phenomena..."
            className="w-full p-4 pr-16 bg-white/10 rounded-2xl text-white placeholder-purple-300/60 resize-none focus:!outline-none focus:!border-none transition-all duration-300"
            rows={3}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSubmit(e);
              }
            }}
          />

          <button
            type="submit"
            disabled={!message.trim() || isLoading}
            className="absolute bottom-4 right-4 w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white disabled:opacity-50 disabled:cursor-not-allowed hover:scale-105 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-purple-500/50"
          >
            {isLoading ? (
              <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
            ) : (
              <Rocket className="w-5 h-5" />
            )}
          </button>
        </div>

        <div className="mt-3 flex items-center justify-between text-xs text-purple-300/60">
          <span>Press Enter to send, Shift+Enter for new line</span>
          <span>{message.length}/1000</span>
        </div>
      </form>
    </div>
  );
};
