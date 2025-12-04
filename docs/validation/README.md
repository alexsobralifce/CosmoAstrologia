# Arquivos de Validação por Seção

Este diretório contém arquivos de validação separados para cada seção do mapa astral. Isso facilita a manutenção e atualização das instruções de validação sem precisar modificar o código Python.

## Estrutura

Cada seção tem seu próprio arquivo de validação:
- `power_pt.txt` - Validação para a seção "A Engenharia da Sua Energia (Temperamento)"
- `triad_pt.txt` - Validação para a seção "O Núcleo da Personalidade (A Tríade Primordial)"
- `personal_pt.txt` - Validação para a seção "Estratégia de Tomada de Decisão & Carreira"
- `houses_pt.txt` - Validação para a seção "A Dinâmica dos Relacionamentos (Casa 7)"
- `karma_pt.txt` - Validação para a seção "O Caminho Kármico e Desafios de Crescimento"
- `synthesis_pt.txt` - Validação para a seção "Síntese e Orientação Estratégica"

## Como Funciona

Os arquivos de validação são carregados pela função `_load_validation_file()` no arquivo `backend/app/api/interpretation.py`. 

### Placeholders

Os arquivos podem conter placeholders que serão substituídos pelos dados do request:
- `{name}` - Nome da pessoa
- `{sunSign}` - Signo do Sol
- `{moonSign}` - Signo da Lua
- `{ascendant}` - Signo do Ascendente
- `{mercurySign}`, `{marsSign}`, `{venusSign}` - Signos dos planetas pessoais
- `{sunHouse}`, `{moonHouse}`, etc. - Casas dos planetas

### Exemplo de Uso

```python
# No código Python
validation_content = _load_validation_file('power', 'pt')
if validation_content:
    validation_content = validation_content.format(
        name=request.name or 'o nativo',
        sunSign=request.sunSign,
        # ... outros campos
    )
    prompt = f"""{full_context}

**1. A ENGENHARIA DA SUA ENERGIA (TEMPERAMENTO)**

{validation_content}"""
```

## Vantagens

1. **Manutenção Fácil**: Cada seção tem seu próprio arquivo, facilitando atualizações
2. **Separação de Responsabilidades**: Instruções de validação separadas do código
3. **Reutilização**: Os mesmos arquivos podem ser usados em diferentes contextos
4. **Versionamento**: Mudanças nos arquivos de validação são rastreadas pelo Git
5. **Colaboração**: Não- programadores podem editar os arquivos de validação sem mexer no código

## Próximos Passos

Para implementar completamente o uso desses arquivos:

1. Modificar a função `_generate_section_prompt()` em `backend/app/api/interpretation.py` para usar `_load_validation_file()` em cada seção
2. Substituir os prompts hardcoded pelos arquivos de validação
3. Testar cada seção para garantir que os placeholders estão sendo substituídos corretamente

## Notas Importantes

- Todos os arquivos devem começar com o aviso: `⚠️⚠️⚠️ **INSTRUÇÕES INTERNAS - NÃO REPITA NA RESPOSTA** ⚠️⚠️⚠️`
- As instruções são apenas para orientar o modelo, não devem aparecer na resposta final
- Use placeholders `{campo}` para dados dinâmicos que vêm do request

