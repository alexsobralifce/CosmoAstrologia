import { useEffect, useRef, useCallback } from 'react';

interface UseInactivityTimeoutOptions {
  /**
   * Tempo de inatividade em milissegundos antes de executar o callback
   * Padrão: 30 minutos (1800000ms)
   */
  timeout?: number;
  
  /**
   * Callback executado quando o timeout é atingido
   */
  onTimeout: () => void;
  
  /**
   * Callback opcional executado antes do timeout (aviso)
   * @param remainingTime Tempo restante em segundos
   */
  onWarning?: (remainingTime: number) => void;
  
  /**
   * Tempo de aviso antes do timeout (em milissegundos)
   * Padrão: 2 minutos (120000ms)
   */
  warningTime?: number;
  
  /**
   * Se deve ativar o timeout
   * Padrão: true
   */
  enabled?: boolean;
}

/**
 * Hook que detecta inatividade do usuário e executa callback após timeout
 * 
 * @example
 * ```tsx
 * useInactivityTimeout({
 *   timeout: 30 * 60 * 1000, // 30 minutos
 *   onTimeout: () => {
 *     console.log('Sessão expirada por inatividade');
 *     handleLogout();
 *   },
 *   onWarning: (remainingTime) => {
 *     console.log(`Sua sessão expira em ${remainingTime} segundos`);
 *   },
 *   warningTime: 2 * 60 * 1000 // Aviso 2 minutos antes
 * });
 * ```
 */
export const useInactivityTimeout = ({
  timeout = 30 * 60 * 1000, // 30 minutos por padrão
  onTimeout,
  onWarning,
  warningTime = 2 * 60 * 1000, // 2 minutos de aviso
  enabled = true
}: UseInactivityTimeoutOptions) => {
  const timeoutIdRef = useRef<NodeJS.Timeout | null>(null);
  const warningIdRef = useRef<NodeJS.Timeout | null>(null);
  const warningShownRef = useRef(false);

  // Limpar timers
  const clearTimers = useCallback(() => {
    if (timeoutIdRef.current) {
      clearTimeout(timeoutIdRef.current);
      timeoutIdRef.current = null;
    }
    if (warningIdRef.current) {
      clearTimeout(warningIdRef.current);
      warningIdRef.current = null;
    }
    warningShownRef.current = false;
  }, []);

  // Resetar timer de inatividade
  const resetTimer = useCallback(() => {
    if (!enabled) return;

    clearTimers();

    // Timer de aviso
    if (onWarning && warningTime > 0 && warningTime < timeout) {
      const warningDelay = timeout - warningTime;
      warningIdRef.current = setTimeout(() => {
        if (!warningShownRef.current) {
          warningShownRef.current = true;
          const remainingSeconds = Math.floor(warningTime / 1000);
          onWarning(remainingSeconds);
        }
      }, warningDelay);
    }

    // Timer principal de timeout
    timeoutIdRef.current = setTimeout(() => {
      console.log('[InactivityTimeout] Sessão expirada por inatividade');
      onTimeout();
    }, timeout);
  }, [enabled, timeout, warningTime, onTimeout, onWarning, clearTimers]);

  // Eventos que indicam atividade do usuário
  useEffect(() => {
    if (!enabled) {
      clearTimers();
      return;
    }

    // Lista de eventos que resetam o timer
    const events = [
      'mousedown',
      'mousemove',
      'keypress',
      'scroll',
      'touchstart',
      'click',
    ];

    // Throttle para evitar muitas chamadas em eventos como mousemove
    let throttleTimer: NodeJS.Timeout | null = null;
    const throttledResetTimer = () => {
      if (!throttleTimer) {
        throttleTimer = setTimeout(() => {
          resetTimer();
          throttleTimer = null;
        }, 1000); // Throttle de 1 segundo
      }
    };

    // Adicionar listeners
    events.forEach(event => {
      window.addEventListener(event, throttledResetTimer);
    });

    // Iniciar timer
    resetTimer();

    // Cleanup
    return () => {
      events.forEach(event => {
        window.removeEventListener(event, throttledResetTimer);
      });
      clearTimers();
      if (throttleTimer) {
        clearTimeout(throttleTimer);
      }
    };
  }, [enabled, resetTimer, clearTimers]);

  return {
    /**
     * Reseta manualmente o timer de inatividade
     */
    resetTimer,
    /**
     * Limpa todos os timers (útil para desabilitar temporariamente)
     */
    clearTimers
  };
};

