import { useState, useEffect } from 'react';

/**
 * Hook para renderizar componentes apenas no cliente
 * Útil para componentes que dependem de APIs do browser
 */
export function useClientOnly(): boolean {
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);
  }, []);

  return isClient;
}
