
import { Rocket, Star, Telescope } from 'lucide-react';

export const CosmicHeader = () => {
  return (
    <header className="relative z-20 border-b border-purple-500/20 bg-black/20 backdrop-blur-md">
      <div className="container mx-auto p-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="relative">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-400 to-purple-600 rounded-full flex items-center justify-center">
                <Rocket className="w-6 h-6 text-white" />
              </div>
              {/* <div className="absolute -top-1 -right-1 w-4 h-4 bg-yellow-400 rounded-full animate-ping"></div> */}
            </div>
            <div>
              <h1 className="text-xl font-bold bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
                AstroAI
              </h1>
              <p className="text-purple-300/80 text-sm">Advanced Space Science Assistant</p>
            </div>
          </div>
          
          <div className="hidden md:flex items-center space-x-6">
            <div className="flex items-center space-x-2 text-purple-300/60">
              <Star className="w-4 h-4" />
              <span className="text-xs">Astronomy</span>
            </div>
            <div className="flex items-center space-x-2 text-purple-300/60">
              <Telescope className="w-4 h-4" />
              <span className="text-xs">Astrophysics</span>
            </div>
            <div className="flex items-center space-x-2 text-purple-300/60">
              <Rocket className="w-4 h-4" />
              <span className="text-xs">Space Exploration</span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};
