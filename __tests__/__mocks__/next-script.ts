// Mock para next/script
import React from 'react';

const Script = ({ src, strategy, onLoad, onError, ...props }: any) => {
  // Simular carregamento do script
  React.useEffect(() => {
    if (onLoad && strategy === 'afterInteractive') {
      // Simular carregamento assíncrono
      setTimeout(() => {
        onLoad();
      }, 0);
    }
  }, [onLoad, strategy]);

  return null;
};

export default Script;
