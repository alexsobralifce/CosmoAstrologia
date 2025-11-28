# 📚 Incremento do RAG com Documentos Locais

## ✅ Documentos Adicionados

### 1. **BASE_CONHECIMENTO_HIERARQUICA.md**
Documento completo com estrutura hierárquica de conhecimento astrológico:
- **Os "Atores"**: Planetas e Pontos Sensíveis (Luminares, Planetas Pessoais, Sociais, Transpessoais, Pontos Calculados)
- **O Cenário**: Zodíaco e Casas (Elementos, Modalidades, Polaridades, Regências, Sistemas de Casas)
- **A Dinâmica**: Aspectos e Geometria (Aspectos Maiores, Menores, Orbes, Configurações)
- **Técnicas de Previsão**: Trânsitos, Progressões, Revolução Solar, Direções, Profecção
- **Astrologia Relacional**: Sinastria, Mapa Composto
- **Contexto Teórico**: Moderna, Tradicional, Védica, Mundana, Horária
- **Chunks Sintéticos**: Combinações comuns com interpretações práticas

### 2. **ASPECTOS_E_CONEXOES.md**
Documento detalhado sobre aspectos planetários:
- Tipos de aspectos (Harmônicos, Tensos, Neutros)
- Significados específicos de cada aspecto
- Configurações especiais (Stellium, T-Square, Grand Trine, Yod)
- Como o sistema interpreta os aspectos
- Orientações práticas para autoconhecimento

### 3. **CICLOS_CRITICOS.md**
Documento sobre ciclos astrológicos importantes:
- Retorno de Saturno (1º e 2º)
- Ciclo de Júpiter
- Oposição de Urano (Crise de Meia-Idade)
- Linha do tempo integrada
- Orientações práticas

## 🔧 Melhorias na Base de Conhecimento Local

### Aspectos Expandidos
Adicionados novos aspectos menores:
- **Quincúncio**: Ajuste e adaptação
- **Semissextil**: Conexão leve e sutil
- **Quintil**: Talento criativo
- **Sesqui-Quadratura**: Tensão residual

### Casas com Categorias
Cada casa agora inclui:
- **Categoria**: Angular, Sucedente ou Cadente
- **Descrição**: Explicação detalhada do significado
- **Informações sobre pontos sensíveis**: AC, MC, DC, IC

### Informações de Aspectos Melhoradas
- Classificação por tipo (harmônico, tenso, neutro, criativo, ajuste)
- Explicações mais detalhadas
- Contexto sobre como trabalhar com cada tipo

## 📊 Estrutura de Metadados

### Exemplo de Chunk Estruturado

```
Tópico: Marte em Touro
Categoria: Posicionamento Natal (Signo)
Tags: #Ação, #Lento, #Resistência, #Terra, #Fixo, #Detrimento
Conteúdo Teórico: [Explicação astrológica]
Conteúdo Prático: [Aplicação na vida real]
```

## 🚀 Próximos Passos

1. ✅ Documentos copiados para `backend/docs/`
2. ✅ Base de conhecimento local incrementada
3. ⏳ Recompilar o índice RAG para incluir os novos documentos
4. ⏳ Testar buscas e verificar melhorias

## 📝 Como Recompilar

```bash
cd backend
python3 scripts/build_rag_index.py
```

O script processará automaticamente:
- `BASE_CONHECIMENTO_HIERARQUICA.md`
- `ASPECTOS_E_CONEXOES.md`
- `CICLOS_CRITICOS.md`

## 🎯 Resultados Esperados

- ✅ **Mais contexto**: Documentos hierárquicos fornecem estrutura completa
- ✅ **Melhor precisão**: Informações organizadas reduzem "alucinações"
- ✅ **Cobertura ampla**: Aspectos, ciclos, pontos sensíveis, técnicas
- ✅ **Interpretações mais ricas**: Groq recebe contexto estruturado e completo

