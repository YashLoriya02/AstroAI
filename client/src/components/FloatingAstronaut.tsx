
import { useEffect, useState } from 'react';

export const FloatingAstronaut = () => {
  const [position, setPosition] = useState({ x: 0, y: 0 });

  useEffect(() => {
    const updatePosition = () => {
      const time = Date.now() * 0.001;
      setPosition({
        x: Math.sin(time * 0.5) * 20,
        y: Math.cos(time * 0.3) * 15
      });
    };

    const interval = setInterval(updatePosition, 50);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="fixed top-20 right-10 z-30 hidden lg:block pointer-events-none">
      <div 
        className="relative transition-transform duration-100 ease-out"
        style={{
          transform: `translate(${position.x}px, ${position.y}px)`
        }}
      >
        {/* Astronaut emoji with glow effect */}
        <div className="text-6xl filter drop-shadow-lg">
          🧑‍🚀
        </div>
        
        {/* Floating particles around astronaut */}
        <div className="absolute inset-0 -m-8">
          {[...Array(6)].map((_, i) => (
            <div
              key={i}
              className="absolute w-1 h-1 bg-blue-400 rounded-full animate-ping"
              style={{
                top: `${20 + Math.sin(i * 60) * 30}%`,
                left: `${20 + Math.cos(i * 60) * 30}%`,
                animationDelay: `${i * 0.5}s`,
                animationDuration: '2s'
              }}
            />
          ))}
        </div>
      </div>
    </div>
  );
};
