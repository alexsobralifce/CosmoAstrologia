# Teste de Registro - Email e Senha

## Problema Identificado
Alguns usuários estão sendo criados sem senha no banco de dados.

## Correções Implementadas

1. **App.tsx** - Ajustada a lógica para usar `tempPassword` quando a senha vem do auth-portal
2. **onboarding.tsx** - Melhorada a lógica de passagem de senha
3. **Logs de debug** adicionados para rastrear o fluxo da senha

## Como Testar

1. Abra o console do navegador (F12)
2. Vá para a tela de "Criar Conta"
3. Preencha:
   - Email: teste@exemplo.com
   - Senha: 123456
   - Confirmar Senha: 123456
4. Clique em "Continuar"
5. Complete o onboarding
6. Verifique no console os logs `[DEBUG Onboarding]` e `[DEBUG App]`
7. Verifique se o usuário foi criado com senha no banco

## Verificar no Banco

```bash
cd backend
source venv/bin/activate
python -c "from app.models.database import User; from app.core.database import SessionLocal; db = SessionLocal(); users = db.query(User).all(); [print(f'{u.email} - Senha: {\"Sim\" if u.password_hash else \"Não\"}') for u in users]; db.close()"
```

## Logs Esperados

No console do navegador, você deve ver:
- `[DEBUG Onboarding] Dados preparados para envio:` - mostra se a senha está presente
- `[DEBUG App] Dados de registro preparados:` - mostra a fonte da senha (data.password ou tempPassword)

