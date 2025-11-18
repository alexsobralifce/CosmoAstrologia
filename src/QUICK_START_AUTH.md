# 🚀 Guia Rápido - Testando o Sistema de Autenticação

## Como Testar os 3 Fluxos

### 🎯 Passo 1: Acesse a Landing Page
1. Abra a aplicação
2. Você verá a landing page com estrelas animadas
3. Clique em **"Calcular Meu Mapa Astral"**

---

## 📋 Fluxo 1: Cadastro de Novo Usuário (E-mail)

### Passos:
1. Na tela de Auth, mantenha a aba **"Criar Conta"** selecionada
2. Digite um e-mail que NÃO está nos exemplos (ex: `teste@novo.com`)
3. Digite uma senha (mínimo 6 caracteres)
4. Digite a mesma senha novamente
   - ✅ Aparecerá um ícone verde se coincidir
5. Clique em **"Continuar"**
6. Você será levado para o Onboarding (coleta de dados)
7. Preencha os dados de nascimento
8. Clique em **"Gerar Mapa Astral"**
9. Verá o loader místico girando
10. Chegará ao Dashboard! 🎉

### O que observar:
- Validação em tempo real (borda vermelha se senha < 6 caracteres)
- Ícone verde quando senhas coincidem
- Se tentar usar `joao@exemplo.com` (já existe), verá um toast de erro

---

## 🔐 Fluxo 2: Login de Usuário Existente

### Cenário A: Usuário COM mapa completo

1. Clique na aba **"Entrar"**
2. Digite:
   - **E-mail:** `joao@exemplo.com`
   - **Senha:** `123456`
3. Clique em **"Acessar meu Mapa"**
4. Verá toast: "Bem-vindo de volta!"
5. Loader místico
6. **Dashboard aparece diretamente** (pula o onboarding)

### Cenário B: Usuário SEM mapa completo

1. Clique na aba **"Entrar"**
2. Digite:
   - **E-mail:** `maria@exemplo.com`
   - **Senha:** `123456`
3. Clique em **"Acessar meu Mapa"**
4. Será levado para o **Onboarding** (para completar os dados)
5. Preencha e gere o mapa

### O que observar:
- Toast de erro se senha estiver errada
- Link "Esqueceu a senha?" funcional
- Diferença de comportamento entre usuários com/sem mapa

---

## 🌐 Fluxo 3: Login com Google (Simulado)

### Como funciona:
O sistema **simula** autenticação Google com 50% de chance de ser usuário novo ou existente.

### Passos:
1. Na tela de Auth (qualquer aba)
2. Role até o botão **"Google"** (com ícone colorido)
3. Clique no botão
4. Verá loader místico
5. **Dois cenários possíveis:**

#### Cenário A: Novo Usuário (50% chance)
- Toast: "Conta Google conectada!"
- Vai para Onboarding
- **Nome e e-mail já preenchidos** (importados do Google)
- Preencha data, hora e local
- Gere o mapa

#### Cenário B: Usuário Existente (50% chance)
- Toast: "Login realizado com sucesso!"
- Loader místico
- **Dashboard aparece diretamente**

### O que observar:
- Aleatório - clique várias vezes para ver ambos cenários
- Onboarding com nome pré-preenchido quando for novo usuário
- Card mostrando "Conta conectada: usuario@gmail.com"

---

## 🎨 Features para Testar

### 1. Mostrar/Ocultar Senha
- Clique no ícone de olho 👁️ ao lado dos campos de senha
- Senha fica visível/oculta

### 2. Validação em Tempo Real
- Digite senha com menos de 6 caracteres → borda vermelha
- Digite senhas diferentes → mensagem de erro
- Digite senhas iguais → ícone verde ✅

### 3. Toggle Login/Cadastro
- Clique em "Criar Conta" ou "Entrar" no topo
- Transição suave entre modos
- Formulário se adapta

### 4. Esqueceu a Senha
1. Vá para aba "Entrar"
2. Digite um e-mail válido
3. Clique em "Esqueceu a senha?"
4. Toast de confirmação aparece

### 5. Toasts Coloridos
- ✅ **Verde:** Sucesso (login bem-sucedido)
- ❌ **Vermelho:** Erro (credenciais inválidas)
- ℹ️ **Azul:** Info (Google conectado)

### 6. Fundo Cósmico
- Estrelas piscando aleatoriamente
- Gradientes pulsantes
- Efeito parallax sutil

### 7. Loader Místico
- Mandala girando em 3 camadas
- 6 partículas orbitando
- Texto "Alinhando os Astros..."
- Pontinhos animados

---

## 🧪 Casos de Teste Recomendados

### Teste 1: E-mail Duplicado
1. Tente criar conta com `joao@exemplo.com`
2. Verá toast: "Este e-mail já possui um mapa astral"
3. Clique no botão "Ir para Login" no toast
4. Será levado para aba de Login

### Teste 2: Senha Curta
1. Digite uma senha com 5 caracteres
2. Veja a mensagem de erro aparecer
3. Digite mais 1 caractere
4. Erro desaparece

### Teste 3: Senhas Diferentes
1. Digite senhas diferentes em "Senha" e "Confirmar Senha"
2. Campo ficará vermelho
3. Botão "Continuar" fica desabilitado
4. Digite a mesma senha
5. Ícone verde ✅ aparece

### Teste 4: Credenciais Inválidas
1. Tente login com e-mail inexistente
2. Toast de erro aparece
3. Tente com senha errada
4. Toast de erro aparece novamente

### Teste 5: Google Aleatório
1. Clique no botão Google 5 vezes
2. Observe os diferentes resultados
3. Aprox. 2-3 vezes irá para Onboarding
4. Aprox. 2-3 vezes irá direto pro Dashboard

---

## 📱 Teste de Responsividade

### Mobile (< 640px)
- Abra DevTools (F12)
- Mude para view mobile
- Observe: cards se ajustam, botões ficam full-width

### Tablet (640px - 1024px)
- Layout se mantém elegante
- Espaçamentos ajustados

### Desktop (> 1024px)
- Card centralizado com max-width 448px
- Espaçamento ideal

---

## 🌓 Teste de Temas

### Tema Noturno → Diurno
1. Clique no toggle de tema (canto superior direito)
2. Observe as mudanças:
   - Fundo: Escuro → Claro
   - Cards: Translúcidos → Mais opacos
   - Estrelas: Dourado → Âmbar
   - Texto: Branco → Escuro

### Tema Diurno → Noturno
1. Clique novamente
2. Volta ao tema cósmico original

---

## 🐛 Troubleshooting

### Toast não aparece?
- Verifique console do navegador
- Certifique-se que Toaster está no App.tsx

### Loader não gira?
- Verifique se globals.css foi carregado
- Inspecione elemento e veja se classes `animate-spin` estão aplicadas

### Estrelas não piscam?
- Verifique animação `animate-twinkle` no CSS
- Pode precisar de hard refresh (Ctrl+Shift+R)

### Formulário não valida?
- Abra console para ver possíveis erros
- Certifique-se de preencher todos os campos

---

## 📊 Dados de Teste

### Usuários Mockados

| E-mail | Senha | Status | Vai para |
|--------|-------|--------|----------|
| joao@exemplo.com | 123456 | Com mapa completo | Dashboard |
| maria@exemplo.com | 123456 | Sem mapa | Onboarding |
| qualquer@novo.com | qualquer | Novo usuário | Onboarding |

### E-mails para Testar Erro
- `joao@exemplo.com` (já existe - teste cadastro)
- `erro@exemplo.com` (não existe - teste login)

---

## ✨ Easter Eggs

1. **Mensagens Místicas:** O loader mostra mensagens aleatórias
2. **Estrelas Únicas:** Cada estrela pisca com timing diferente
3. **Gradientes:** Dois gradientes pulsam em ritmos diferentes
4. **Partículas:** 6 partículas orbitam a mandala no loader

---

## 🎯 Checklist de Teste Completo

- [ ] Cadastro com e-mail novo
- [ ] Cadastro com e-mail existente (erro)
- [ ] Login com credenciais corretas (usuário com mapa)
- [ ] Login com credenciais corretas (usuário sem mapa)
- [ ] Login com credenciais incorretas (erro)
- [ ] Login com Google (cenário novo usuário)
- [ ] Login com Google (cenário usuário existente)
- [ ] Esqueceu senha
- [ ] Mostrar/ocultar senha
- [ ] Validação de e-mail
- [ ] Validação de senha (min 6 chars)
- [ ] Validação de senhas coincidentes
- [ ] Toggle entre Login e Cadastro
- [ ] Toast notifications funcionando
- [ ] Loader místico aparece
- [ ] Tema dia/noite funciona
- [ ] Responsividade mobile
- [ ] Estrelas animadas
- [ ] Onboarding com dados pré-preenchidos

---

## 🎓 Próximos Passos

Depois de testar a autenticação:
1. Explore o **Dashboard** completo
2. Veja a aba **"Seu Guia Pessoal"** com os novos componentes
3. Teste o **Theme Toggle** em todas as páginas
4. Navegue entre as diferentes abas do Dashboard

---

**Divirta-se testando! ✨🌙⭐**
