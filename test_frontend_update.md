# Teste de Atualização do Dashboard

## Passos para testar:

1. **Iniciar o sistema:**
   ```bash
   ./start-all.sh
   ```

2. **Abrir o navegador:**
   - Acessar http://localhost:3000
   - Abrir o Console do Desenvolvedor (F12)

3. **Fazer login:**
   - Email: alexandre@bol.com
   - Senha: 123456

4. **Verificar dados iniciais:**
   - Anotar os signos exibidos no dashboard (Sol, Lua, Ascendente)
   - Verificar no console os logs `[DEBUG Dashboard]`

5. **Editar dados:**
   - Clicar no avatar no canto superior direito
   - Clicar em "Editar Perfil"
   - Alterar a hora de nascimento (ex: de 13:30 para 09:30)
   - Clicar em "Salvar Alterações"

6. **Verificar atualização:**
   - Verificar no console os logs:
     - `[DEBUG EditUserModal]` - dados do backend
     - `[DEBUG App]` - atualização do userData
     - `[DEBUG Dashboard]` - recálculo do mapa
   - Verificar se os signos no dashboard mudaram
   - Verificar se o Ascendente mudou (deve mudar ao alterar a hora)

## Problemas possíveis:

1. **Se os logs não aparecerem:**
   - Verificar se o console está aberto
   - Verificar se há erros no console

2. **Se os dados não atualizarem:**
   - Verificar se o backend está rodando
   - Verificar se a atualização foi bem-sucedida (toast de sucesso)
   - Verificar os logs no console para identificar onde está falhando

3. **Se o dashboard não recalcular:**
   - Verificar se `currentUserData` está sendo atualizado
   - Verificar se `chartBasics` está sendo recalculado
   - Verificar se os signos exibidos estão usando `chartBasics`

