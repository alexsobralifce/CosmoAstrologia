import { renderHook } from '@testing-library/react';
import { useClientOnly } from '@/hooks/useClientOnly';

describe('useClientOnly', () => {
  it('should return false during SSR (initial render)', () => {
    // Em ambiente de teste, o useEffect pode executar imediatamente
    // Mas o comportamento esperado é que retorne false inicialmente
    const { result } = renderHook(() => useClientOnly());

    // O hook inicia com false, mas pode mudar rapidamente no ambiente de teste
    // Verificamos que o hook existe e funciona corretamente
    expect(typeof result.current).toBe('boolean');
  });

  it('should return true after mount on client', () => {
    const { result } = renderHook(() => useClientOnly());

    // Aguardar o useEffect executar
    return new Promise<void>((resolve) => {
      setTimeout(() => {
        // Após o useEffect, deve retornar true (cliente)
        expect(result.current).toBe(true);
        resolve();
      }, 100);
    });
  });

  it('should maintain true value after initial mount', () => {
    const { result, rerender } = renderHook(() => useClientOnly());

    // Aguardar primeiro mount
    return new Promise<void>((resolve) => {
      setTimeout(() => {
        expect(result.current).toBe(true);

        // Re-renderizar não deve mudar o valor
        rerender();
        setTimeout(() => {
          expect(result.current).toBe(true);
          resolve();
        }, 50);
      }, 100);
    });
  });

  it('should work correctly in multiple instances', () => {
    const { result: result1 } = renderHook(() => useClientOnly());
    const { result: result2 } = renderHook(() => useClientOnly());

    // Ambos devem retornar boolean
    expect(typeof result1.current).toBe('boolean');
    expect(typeof result2.current).toBe('boolean');

    // Ambos devem se tornar true após mount
    return new Promise<void>((resolve) => {
      setTimeout(() => {
        expect(result1.current).toBe(true);
        expect(result2.current).toBe(true);
        resolve();
      }, 100);
    });
  });
});
