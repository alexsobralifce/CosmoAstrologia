

// Função utilitária para remover informações de suporte e conteúdo técnico
export const removeSupportAndTechnicalContent = (text: string): string => {
  let cleaned = text;
  
  // Remover seção "Suporte" completa (todas as variações)
  cleaned = cleaned.replace(/##?\s*📞\s*Suporte[\s\S]*?(?=\n\n|$)/gi, '');
  cleaned = cleaned.replace(/##?\s*Suporte[\s\S]*?(?=\n\n|$)/gi, '');
  cleaned = cleaned.replace(/Suporte[\s\S]*?Consulta com astrólogo profissional[\s\S]*?(?=\n\n|$)/gi, '');
  cleaned = cleaned.replace(/Para dúvidas sobre interpretação astrológica[\s\S]*?Consulta com astrólogo profissional[\s\S]*?(?=\n\n|$)/gi, '');
  
  // Remover linhas específicas de suporte
  cleaned = cleaned.replace(/Livros de astrologia na pasta.*?/gi, '');
  cleaned = cleaned.replace(/Análise com IA.*?botão.*?/gi, '');
  cleaned = cleaned.replace(/Análise com IA.*?/gi, '');
  cleaned = cleaned.replace(/Consulta com astrólogo profissional.*?/gi, '');
  
  // Remover rodapé
  cleaned = cleaned.replace(/Desenvolvido com.*?autoconhecimento profundo[\s\S]*?(?=\n\n|$)/gi, '');
  cleaned = cleaned.replace(/Desenvolvido com.*?❤️.*?autoconhecimento[\s\S]*?(?=\n\n|$)/gi, '');
  
  // Remover separadores markdown
  cleaned = cleaned.replace(/^[-]{3,}$/gm, '');
  cleaned = cleaned.replace(/^[=]{3,}$/gm, '');
  
  return cleaned;
};
