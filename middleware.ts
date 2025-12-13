import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Rotas que precisam de autenticação
  const protectedRoutes = ['/dashboard', '/onboarding', '/interpretation'];
  const isProtectedRoute = protectedRoutes.some(route => pathname.startsWith(route));

  if (isProtectedRoute) {
    // Verificar token no cookie (se estiver usando cookies) ou redirecionar
    // Por enquanto, vamos deixar a verificação no cliente
    // Em produção, considere usar cookies HTTP-only
    const token = request.cookies.get('auth_token')?.value;

    // Se não tiver token, permitir que o cliente faça a verificação
    // O componente da página fará o redirect se necessário
    // Isso evita problemas com SSR e localStorage
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    '/dashboard/:path*',
    '/onboarding/:path*',
    '/interpretation/:path*',
  ],
};
