
import { Rocket, Star } from 'lucide-react';
import ReactMarkdown from "react-markdown"
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css'; // ✅ Required for styling LaTeX

interface Message {
  id: number;
  type: string;
  content: string;
  timestamp: Date;
}

interface MessageBubbleProps {
  message: Message;
}

export const MessageBubble = ({ message }: MessageBubbleProps) => {
  const isBot = message.type === 'bot';

  return (
    <div className={`flex items-start space-x-4 ${!isBot ? 'flex-row-reverse space-x-reverse' : ''}`}>
      <div className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${isBot
        ? 'bg-gradient-to-br from-blue-500 to-purple-600'
        : 'bg-gradient-to-br from-purple-500 to-pink-600'
        }`}>
        {isBot ? (
          <Rocket className="w-5 h-5 text-white" />
        ) : (
          <Star className="w-5 h-5 text-white" />
        )}
      </div>

      {/* <div className={`flex-1 max-w-[80%] ${!isBot ? 'flex flex-col justify-end' : ''}`}> */}
      <div className={`${!isBot ? 'flex flex-col justify-end' : ''} max-w-[80%] w-fit`}>
        <div className={`relative p-4 rounded-2xl ${isBot
          ? 'bxsd-class'
          : 'bg-gradient-to-br from-purple-900/40 to-pink-900/40 border border-purple-500/20'
          } backdrop-blur-sm`}>
          <p className="text-white/90 leading-relaxed whitespace-pre-wrap">
            <ReactMarkdown
              children={message.content}
              remarkPlugins={[remarkMath]}
              rehypePlugins={[rehypeKatex]}
              components={{
                p: ({ children }) => <p className="mb-2">{children}</p>,
              }}
            />
          </p>

          {/* <div className={`absolute w-3 h-3 ${
            isBot ? 'left-[-6px]' : 'right-[-6px]'
          } top-4 transform rotate-45 ${
            isBot 
              ? 'bg-gradient-to-br from-blue-900/40 to-purple-900/40 border-l border-b border-blue-500/20' 
              : 'bg-gradient-to-br from-purple-900/40 to-pink-900/40 border-r border-t border-purple-500/20'
          }`}></div> */}
        </div>

        <div className={`mt-2 text-xs text-purple-300/60 ${!isBot ? 'text-right mr-1' : 'ml-2'}`}>
          {message.timestamp.toLocaleTimeString()}
        </div>
      </div>
    </div>
  );
};
