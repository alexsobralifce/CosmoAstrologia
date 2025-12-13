import { renderHook, act } from '@testing-library/react';
import { useLocalStorage } from '@/hooks/useLocalStorage';

// Mock do localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {};

  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => {
      store[key] = String(value);
    },
    removeItem: (key: string) => {
      delete store[key];
    },
    clear: () => {
      store = {};
    },
    get length() {
      return Object.keys(store).length;
    },
    key: (index: number) => {
      const keys = Object.keys(store);
      return keys[index] || null;
    },
  };
})();

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
});

describe('useLocalStorage', () => {
  beforeEach(() => {
    // Limpar localStorage antes de cada teste
    localStorage.clear();
    jest.clearAllMocks();
  });

  it('should return initial value when localStorage is empty', () => {
    const { result } = renderHook(() => useLocalStorage('test-key', 'initial'));

    expect(result.current[0]).toBe('initial');
  });

  it('should read value from localStorage on mount', () => {
    localStorage.setItem('test-key', JSON.stringify('stored-value'));

    const { result } = renderHook(() => useLocalStorage('test-key', 'initial'));

    // Aguardar o useEffect executar
    act(() => {
      // O hook deve ler do localStorage após montagem
    });

    // Aguardar um tick para o useEffect executar
    return new Promise<void>((resolve) => {
      setTimeout(() => {
        expect(result.current[0]).toBe('stored-value');
        resolve();
      }, 100);
    });
  });

  it('should write value to localStorage when setValue is called', () => {
    const { result } = renderHook(() => useLocalStorage('test-key', 'initial'));

    act(() => {
      result.current[1]('new-value');
    });

    // Aguardar o useEffect executar
    return new Promise<void>((resolve) => {
      setTimeout(() => {
        expect(localStorage.getItem('test-key')).toBe(JSON.stringify('new-value'));
        expect(result.current[0]).toBe('new-value');
        resolve();
      }, 100);
    });
  });

  it('should update value when setValue is called multiple times', () => {
    const { result } = renderHook(() => useLocalStorage('test-key', 'initial'));

    act(() => {
      result.current[1]('value-1');
    });

    return new Promise<void>((resolve) => {
      setTimeout(() => {
        act(() => {
          result.current[1]('value-2');
        });

        setTimeout(() => {
          expect(localStorage.getItem('test-key')).toBe(JSON.stringify('value-2'));
          expect(result.current[0]).toBe('value-2');
          resolve();
        }, 100);
      }, 100);
    });
  });

  it('should handle function updater in setValue', () => {
    const { result } = renderHook(() => useLocalStorage('test-key', 0));

    act(() => {
      result.current[1]((prev) => prev + 1);
    });

    return new Promise<void>((resolve) => {
      setTimeout(() => {
        expect(result.current[0]).toBe(1);
        act(() => {
          result.current[1]((prev) => prev + 1);
        });

        setTimeout(() => {
          expect(result.current[0]).toBe(2);
          resolve();
        }, 100);
      }, 100);
    });
  });

  it('should handle complex objects', () => {
    const initialValue = { name: 'Test', age: 25 };
    const { result } = renderHook(() => useLocalStorage('test-key', initialValue));

    act(() => {
      result.current[1]({ name: 'Updated', age: 30 });
    });

    return new Promise<void>((resolve) => {
      setTimeout(() => {
        expect(localStorage.getItem('test-key')).toBe(JSON.stringify({ name: 'Updated', age: 30 }));
        expect(result.current[0]).toEqual({ name: 'Updated', age: 30 });
        resolve();
      }, 100);
    });
  });

  it('should handle arrays', () => {
    const initialValue: string[] = [];
    const { result } = renderHook(() => useLocalStorage('test-key', initialValue));

    act(() => {
      result.current[1](['item1', 'item2']);
    });

    return new Promise<void>((resolve) => {
      setTimeout(() => {
        expect(localStorage.getItem('test-key')).toBe(JSON.stringify(['item1', 'item2']));
        expect(result.current[0]).toEqual(['item1', 'item2']);
        resolve();
      }, 100);
    });
  });

  it('should handle SSR safety - not access localStorage on server', () => {
    // Simular ambiente de servidor (sem window.localStorage)
    const originalLocalStorage = window.localStorage;
    // @ts-ignore
    delete window.localStorage;

    const { result } = renderHook(() => useLocalStorage('test-key', 'initial'));

    // Deve retornar o valor inicial sem acessar localStorage
    expect(result.current[0]).toBe('initial');

    // Restaurar localStorage
    window.localStorage = originalLocalStorage;
  });

  it('should handle localStorage errors gracefully', () => {
    // Mock localStorage.setItem para lançar erro
    const originalSetItem = localStorage.setItem;
    localStorage.setItem = jest.fn(() => {
      throw new Error('Storage quota exceeded');
    });

    const { result } = renderHook(() => useLocalStorage('test-key', 'initial'));

    // Não deve lançar erro, apenas atualizar o estado
    act(() => {
      result.current[1]('new-value');
    });

    // O estado deve ser atualizado mesmo se localStorage falhar
    expect(result.current[0]).toBe('new-value');

    // Restaurar
    localStorage.setItem = originalSetItem;
  });

  it('should handle invalid JSON in localStorage', () => {
    // Colocar valor inválido no localStorage
    localStorage.setItem('test-key', 'invalid-json{');

    const { result } = renderHook(() => useLocalStorage('test-key', 'initial'));

    // Deve retornar o valor inicial quando JSON é inválido
    return new Promise<void>((resolve) => {
      setTimeout(() => {
        // O hook deve usar o valor inicial quando há erro de parsing
        expect(result.current[0]).toBe('initial');
        resolve();
      }, 100);
    });
  });

  it('should synchronize between multiple components using same key', () => {
    const { result: result1 } = renderHook(() => useLocalStorage('shared-key', 'initial'));
    const { result: result2 } = renderHook(() => useLocalStorage('shared-key', 'initial'));

    act(() => {
      result1.current[1]('updated');
    });

    return new Promise<void>((resolve) => {
      setTimeout(() => {
        // Ambos devem refletir a mudança após re-render
        expect(result1.current[0]).toBe('updated');
        // O segundo hook deve ler do localStorage na próxima renderização
        const { result: result2New } = renderHook(() => useLocalStorage('shared-key', 'initial'));
        setTimeout(() => {
          expect(result2New.current[0]).toBe('updated');
          resolve();
        }, 100);
      }, 100);
    });
  });
});
