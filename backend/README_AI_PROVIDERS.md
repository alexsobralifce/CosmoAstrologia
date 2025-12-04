# Configuração de Provedores de IA

O sistema agora suporta múltiplos provedores de IA. Você pode escolher entre:

- **Groq** (padrão) - Modelos Llama via Groq
- **OpenAI** - GPT-4, GPT-4o, GPT-4o-mini
- **Anthropic** - Claude 3.5 Sonnet, Claude 3 Opus
- **Google Gemini** - Gemini Pro

## Como Configurar

### 1. Escolher o Provedor

No arquivo `backend/.env`, adicione:

```env
# Escolha o provedor: groq, openai, anthropic, gemini
AI_PROVIDER=groq
```

### 2. Configurar as Chaves de API

#### Groq (Padrão)
```env
GROQ_API_KEY=gsk_sua_chave_aqui
```

#### OpenAI
```env
OPENAI_API_KEY=sk-sua_chave_aqui
```

#### Anthropic (Claude)
```env
ANTHROPIC_API_KEY=sk-ant-sua_chave_aqui
```

#### Google Gemini
```env
GEMINI_API_KEY=sua_chave_aqui
```

## Modelos Disponíveis por Provedor

### Groq
- `llama-3.3-70b-versatile` (padrão)
- `llama-3.1-8b-instant`
- `llama-3.2-90b-text-preview`

### OpenAI
- `gpt-4o-mini` (padrão, mais barato)
- `gpt-4o`
- `gpt-4-turbo`
- `gpt-3.5-turbo`

### Anthropic
- `claude-3-5-sonnet-20241022` (padrão)
- `claude-3-opus-20240229`
- `claude-3-haiku-20240307`

### Google Gemini
- `gemini-pro` (padrão)
- `gemini-pro-vision`

## Como Funciona

O sistema tenta usar o provedor especificado em `AI_PROVIDER`. Se esse provedor não estiver disponível (chave não configurada), ele automaticamente tenta os outros provedores na seguinte ordem:

1. Groq
2. OpenAI
3. Anthropic
4. Gemini

## Verificar Provedores Disponíveis

Você pode verificar quais provedores estão disponíveis através do endpoint de diagnóstico:

```bash
GET /api/interpretation/birth-chart/diagnostics
```

## Vantagens de Cada Provedor

### Groq
- ✅ Mais rápido
- ✅ Mais barato
- ✅ Boa qualidade com Llama 3.3 70B
- ⚠️ Pode ter limitações com prompts muito longos

### OpenAI
- ✅ Excelente qualidade (GPT-4o)
- ✅ Muito confiável
- ✅ Boa compreensão de contexto
- ⚠️ Mais caro que Groq

### Anthropic (Claude)
- ✅ Excelente para textos longos
- ✅ Muito bom em seguir instruções
- ✅ Melhor compreensão de contexto
- ⚠️ Mais caro

### Google Gemini
- ✅ Boa qualidade
- ✅ Preço competitivo
- ⚠️ Pode ter limitações em alguns casos

## Recomendações

- **Para desenvolvimento/testes**: Use Groq (mais barato e rápido)
- **Para produção com alta qualidade**: Use OpenAI GPT-4o ou Anthropic Claude
- **Para custo-benefício**: Use Groq ou Gemini

## Instalação de Dependências

Dependendo do provedor escolhido, você pode precisar instalar:

```bash
# Groq (já instalado)
pip install groq

# OpenAI
pip install openai

# Anthropic
pip install anthropic

# Google Gemini
pip install google-generativeai
```

## Exemplo de Uso

O código automaticamente detecta qual provedor usar baseado na configuração. Não é necessário mudar o código, apenas as variáveis de ambiente.

```python
# O sistema automaticamente usa o provedor configurado
from app.services.ai_provider_service import get_ai_provider

provider = get_ai_provider()  # Retorna o provedor configurado
if provider:
    text = provider.generate_text(
        system_prompt="Você é um astrólogo...",
        user_prompt="Interprete Sol em Libra...",
        temperature=0.6,
        max_tokens=4000
    )
```

