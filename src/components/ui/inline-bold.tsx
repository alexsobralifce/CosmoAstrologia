import type { ReactNode } from 'react';

/**
 * Renderiza `**negrito**` como <strong> sem usar HTML cru: o texto vem da LLM e
 * não pode ser injetado com dangerouslySetInnerHTML (XSS).
 */
export function InlineBold({ text }: { text: string }): ReactNode {
  const partes = text.split(/\*\*(.+?)\*\*/g);
  return (
    <>
      {partes.map((parte, i) => (i % 2 === 1 ? <strong key={i}>{parte}</strong> : parte))}
    </>
  );
}
