import { useState, useEffect } from 'react';
import { ChevronUp } from 'lucide-react';

export const ScrollToTop = () => {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const toggleVisibility = () => {
      // Mostrar o botão quando o usuário rolar mais de 200px
      const scrollY = window.scrollY || window.pageYOffset || document.documentElement.scrollTop;
      setIsVisible(scrollY > 200);
    };

    // Verificar posição inicial
    toggleVisibility();

    // Adicionar listener de scroll
    window.addEventListener('scroll', toggleVisibility, { passive: true });

    return () => {
      window.removeEventListener('scroll', toggleVisibility);
    };
  }, []);

  const scrollToTop = () => {
    window.scrollTo({
      top: 0,
      behavior: 'smooth',
    });
  };

  if (!isVisible) {
    return null;
  }

  return (
    <button
      onClick={scrollToTop}
      className="fixed bottom-8 right-8 z-[9999] p-3 rounded-full bg-accent hover:bg-accent/80 shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-110 backdrop-blur-sm border border-accent/30"
      aria-label="Voltar ao topo"
      style={{ 
        position: 'fixed',
        bottom: '2rem',
        right: '2rem',
        zIndex: 9999,
        color: 'var(--background)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
      }}
    >
      <ChevronUp size={24} style={{ color: 'var(--background)' }} />
    </button>
  );
};
