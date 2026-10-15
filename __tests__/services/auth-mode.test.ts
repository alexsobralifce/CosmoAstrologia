/** Modos de autenticação do cliente HTTP: 'token' (localStorage) e 'cookie' (httpOnly). */

const respostaLogin = () =>
  Promise.resolve({
    ok: true,
    status: 200,
    statusText: 'OK',
    json: () => Promise.resolve({ access_token: 'jwt-123', token_type: 'bearer' }),
    clone() { return this; },
    text: () => Promise.resolve(''),
  } as unknown as Response);

async function carregar(modo?: string) {
  jest.resetModules();
  if (modo) process.env.NEXT_PUBLIC_AUTH_MODE = modo; else delete process.env.NEXT_PUBLIC_AUTH_MODE;
  return (await import('@/services/api')).apiService;
}

describe('modo de autenticação', () => {
  beforeEach(() => {
    localStorage.clear();
    global.fetch = jest.fn(respostaLogin) as unknown as typeof fetch;
  });
  afterAll(() => { delete process.env.NEXT_PUBLIC_AUTH_MODE; });

  it("modo 'token' guarda o token e o envia no cabeçalho", async () => {
    const api = await carregar();
    await api.loginUser('a@b.com', 'senha123');

    expect(localStorage.getItem('auth_token')).toBe('jwt-123');
    await api.getCurrentUser();
    const [, init] = (global.fetch as jest.Mock).mock.calls.at(-1);
    expect(init.headers.Authorization).toBe('Bearer jwt-123');
  });

  it("modo 'cookie' não guarda o token no localStorage e envia credenciais", async () => {
    const api = await carregar('cookie');
    await api.loginUser('a@b.com', 'senha123');

    expect(localStorage.getItem('auth_token')).toBeNull();
    const [, init] = (global.fetch as jest.Mock).mock.calls.at(-1);
    expect(init.credentials).toBe('include');
    expect(init.headers.Authorization).toBeUndefined();
  });
});
