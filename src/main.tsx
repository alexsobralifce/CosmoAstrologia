import { createRoot } from "react-dom/client";
import App from "./App.tsx";
import "./index.css";

// Filtrar erros de extensões do navegador no console
if (typeof window !== 'undefined') {
  const originalError = console.error;
  console.error = (...args: any[]) => {
    // Filtrar erros de content_script.js (extensões do navegador)
    const errorString = args.join(' ');
    if (errorString.includes('content_script.js') || 
        errorString.includes('deref') ||
        errorString.includes('MutationObserver')) {
      // Ignorar esses erros silenciosamente
      return;
    }
    originalError.apply(console, args);
  };

  // Handler global de erros não capturados
  window.addEventListener('error', (event) => {
    // Filtrar erros de extensões
    if (event.filename && event.filename.includes('content_script')) {
      event.preventDefault();
      return false;
    }
  });

  // Handler para promessas rejeitadas
  window.addEventListener('unhandledrejection', (event) => {
    // Log apenas erros relevantes da aplicação
    if (!event.reason?.message?.includes('content_script')) {
      console.error('Unhandled promise rejection:', event.reason);
    }
  });
}

const rootElement = document.getElementById("root");
if (!rootElement) {
  throw new Error("Root element not found");
}

createRoot(rootElement).render(<App />);
  