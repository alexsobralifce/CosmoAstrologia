# 🔧 Funções que Precisam de Ajuste - RAG Service

## Funções que ainda usam `rag_service.groq_client` diretamente

Essas funções precisam ser ajustadas para usar o cliente HTTP (`rag_client`) ao invés de acessar o Groq diretamente.

### 1. `get_planet_interpretation` (linha ~778)
**Endpoint:** `POST /api/interpretation/planet`
**Problema:** Usa `rag_service.groq_client.chat.completions.create()` diretamente
**Solução:** Usar `await rag_client.get_interpretation()` com `use_groq=True`

**Código atual:**
```python
if rag_service.groq_client:
    chat_completion = rag_service.groq_client.chat.completions.create(...)
```

**Deve ser:**
```python
rag_client = get_rag_client()
if rag_client:
    interpretation = await rag_client.get_interpretation(
        planet=planet,
        sign=sign,
        house=house,
        use_groq=True
    )
```

---

### 2. `get_chart_ruler_interpretation` (linha ~996)
**Endpoint:** `POST /api/interpretation/chart-ruler`
**Problema:** Usa `rag_service.groq_client.chat.completions.create()` diretamente
**Solução:** Usar `await rag_client.get_interpretation()` com query customizada

---

### 3. `get_planet_house_interpretation` (linha ~1260)
**Endpoint:** `POST /api/interpretation/planet-house`
**Problema:** Usa `rag_service.groq_client` e `rag_service._generate_with_groq()`
**Solução:** Usar `await rag_client.get_interpretation()` com house especificada

---

### 4. `get_aspect_interpretation` (linha ~1339)
**Endpoint:** `POST /api/interpretation/aspect`
**Problema:** Usa `rag_service.groq_client.chat.completions.create()` diretamente
**Solução:** Usar `await rag_client.get_interpretation()` com aspect especificado

---

### 5. `generate_birth_chart_section` (linha ~2686)
**Endpoint:** `POST /api/full-birth-chart/section`
**Problema:** Usa `rag_service.groq_client.chat.completions.create()` e verifica `rag_service.index`
**Solução:** Usar `await rag_client.get_interpretation()` ou `await rag_client.search()`

---

### 6. `generate_full_birth_chart` (linha ~2977)
**Endpoint:** `POST /api/full-birth-chart/all`
**Problema:** Usa `rag_service.groq_client.chat.completions.create()` diretamente
**Solução:** Usar `await rag_client.get_interpretation()` com query customizada

---

## Funções com verificações de status que precisam ajuste

### 7. `get_birth_chart_diagnostics` (linha ~297)
**Problema:** Verifica `rag_service.index`, `rag_service.documents`, `rag_service.load_index()`
**Solução:** Usar `await rag_client.get_status()`

**Código atual:**
```python
has_index = rag_service.index is not None
has_index = len(rag_service.documents) > 0
if not rag_service.load_index():
```

**Deve ser:**
```python
rag_client = get_rag_client()
if rag_client:
    status = await rag_client.get_status()
    has_index = status.get("has_index", False)
```

---

## Resumo

**Total de funções a ajustar:** 7

1. ✅ `get_interpretation` - JÁ AJUSTADA
2. ✅ `search_documents` - JÁ AJUSTADA  
3. ✅ `get_rag_status` - JÁ AJUSTADA
4. ❌ `get_planet_interpretation` - PENDENTE
5. ❌ `get_chart_ruler_interpretation` - PENDENTE
6. ❌ `get_planet_house_interpretation` - PENDENTE
7. ❌ `get_aspect_interpretation` - PENDENTE
8. ❌ `generate_birth_chart_section` - PENDENTE
9. ❌ `generate_full_birth_chart` - PENDENTE
10. ❌ `get_birth_chart_diagnostics` - PENDENTE

## Padrão de substituição

**ANTES:**
```python
rag_service = get_rag_service()
if rag_service.groq_client:
    chat_completion = rag_service.groq_client.chat.completions.create(
        model="llama-3.1-70b-versatile",
        messages=[...],
        temperature=0.7,
        max_tokens=2000
    )
    interpretation_text = chat_completion.choices[0].message.content
```

**DEPOIS:**
```python
rag_client = get_rag_client()
if rag_client:
    interpretation = await rag_client.get_interpretation(
        planet=planet,
        sign=sign,
        house=house,
        aspect=aspect,
        custom_query=custom_query,
        use_groq=True,
        top_k=8
    )
    interpretation_text = interpretation.get('interpretation', '')
```

