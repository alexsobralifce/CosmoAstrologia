export const AuthLoader = () => {
  return (
    <div className="min-h-screen flex items-center justify-center p-4 relative overflow-hidden">
      {/* Fundo escuro com overlay */}
      <div className="absolute inset-0 bg-background/95 backdrop-blur-sm">
        {/* Gradientes místicos animados */}
        <div className="absolute top-1/3 left-1/3 w-96 h-96 bg-accent/10 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-1/3 right-1/3 w-96 h-96 bg-secondary/10 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }}></div>
      </div>

      {/* Conteúdo do Loader */}
      <div className="relative z-10 flex flex-col items-center gap-8">
        {/* Mandala Girando */}
        <div className="relative">
          {/* Círculo externo */}
          <div className="w-32 h-32 border-4 border-accent/20 rounded-full animate-spin-slow">
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="w-24 h-24 border-4 border-accent/40 border-t-accent rounded-full animate-spin"></div>
            </div>
          </div>
          
          {/* Estrela central */}
          <div className="absolute inset-0 flex items-center justify-center">
            <svg
              width="48"
              height="48"
              viewBox="0 0 24 24"
              className="text-accent animate-pulse"
              fill="currentColor"
            >
              <path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z" />
            </svg>
          </div>

          {/* Partículas orbitando */}
          {[0, 60, 120, 180, 240, 300].map((deg, i) => (
            <div
              key={i}
              className="absolute top-1/2 left-1/2 w-2 h-2"
              style={{
                transform: `rotate(${deg}deg) translateY(-60px)`,
                transformOrigin: '0 0'
              }}
            >
              <div
                className="w-2 h-2 bg-accent rounded-full animate-pulse"
                style={{ animationDelay: `${i * 0.2}s` }}
              ></div>
            </div>
          ))}
        </div>

        {/* Texto de Loading */}
        <div className="text-center space-y-2">
          <h3 className="text-accent animate-pulse" style={{ fontFamily: 'var(--font-serif)' }}>
            Alinhando os Astros...
          </h3>
          <div className="flex items-center gap-1 justify-center">
            <div className="w-2 h-2 bg-accent rounded-full animate-bounce" style={{ animationDelay: '0s' }}></div>
            <div className="w-2 h-2 bg-accent rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
            <div className="w-2 h-2 bg-accent rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
          </div>
        </div>

        {/* Mensagens místicas aleatórias */}
        <p className="text-secondary text-sm max-w-xs text-center animate-fadeIn">
          Consultando as estrelas e preparando sua jornada cósmica...
        </p>
      </div>
    </div>
  );
};
