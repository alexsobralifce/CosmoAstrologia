import { AstroCard } from './astro-card';
import { zodiacSigns } from './zodiac-icons';
import { planets } from './planet-icons';
import { UIIcons } from './ui-icons';
import { AlertCircle, CheckCircle, Clock } from 'lucide-react';
import { Badge } from './ui/badge';

interface DailyAdviceSectionProps {
  moonSign: string;
  moonHouse: number;
  isMercuryRetrograde?: boolean;
  isMoonVoidOfCourse?: boolean;
  voidEndsAt?: string;
}

export const DailyAdviceSection = ({ 
  moonSign, 
  moonHouse, 
  isMercuryRetrograde = false,
  isMoonVoidOfCourse = false,
  voidEndsAt = "16:30"
}: DailyAdviceSectionProps) => {
  const MoonIcon = zodiacSigns.find(z => z.name === moonSign)?.icon;
  const MercuryIcon = planets.find(p => p.name === 'Mercúrio')?.icon;

  const getMoonAdvice = () => {
    const houseAdvice: Record<number, string> = {
      1: "Hoje, sua segurança emocional vem de focar em si mesmo. É um bom dia para novos começos e cuidar da sua aparência.",
      2: "Hoje, sua segurança emocional vem de estabilidade financeira. Foque em administrar recursos e valorizar o que já possui.",
      3: "Hoje, sua segurança emocional vem de comunicação e aprendizado. É um bom dia para conversas, estudos e conectar-se com irmãos.",
      4: "Hoje, sua segurança emocional vem do lar e família. Fique perto de quem ama e cuide do seu espaço pessoal.",
      5: "Hoje, sua segurança emocional vem de criatividade e diversão. É um bom dia para hobbies, romance e expressão pessoal.",
      6: "Hoje, sua segurança emocional vem de rotina e produtividade. Organize suas tarefas, cuide da saúde e seja útil.",
      7: "Hoje, sua segurança emocional vem de parcerias. É um bom dia para colaborações, negociações e tempo com parceiros.",
      8: "Hoje, sua segurança emocional vem de transformação e intimidade. Explore questões profundas e compartilhe recursos.",
      9: "Hoje, sua segurança emocional vem de exploração e filosofia. É um bom dia para viagens, estudos superiores e expandir horizontes.",
      10: "Hoje, sua segurança emocional vem de carreira e reconhecimento público. Foque em metas profissionais e sua reputação.",
      11: "Hoje, sua segurança emocional vem de estar com amigos e grupos. É um bom dia para networking e atividades humanitárias.",
      12: "Hoje, sua segurança emocional vem de solitude e reflexão. É um bom dia para meditação, descanso e processos internos."
    };
    
    return houseAdvice[moonHouse] || "Sintonize-se com suas emoções hoje.";
  };

  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-accent mb-1" style={{ fontFamily: 'var(--font-serif)' }}>
          Conselhos para Hoje
        </h2>
        <p className="text-sm text-muted-foreground">
          Guia prático baseado nos trânsitos atuais
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4">
        {/* Trânsito da Lua - Sempre Visível */}
        <AstroCard className="border-l-4 border-l-accent shadow-lg shadow-accent/10 hover:shadow-xl hover:shadow-accent/20 transition-all duration-300 animate-fadeIn">
          <div className="flex items-start gap-4">
            {MoonIcon && <MoonIcon size={40} className="text-accent flex-shrink-0 drop-shadow-lg" />}
            <div className="flex-1 space-y-3">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <h3 className="text-foreground">Humor do Dia: Lua em {moonSign}</h3>
                  <Badge variant="outline" className="bg-accent/10 text-accent border-accent/30">
                    Ativo Hoje
                  </Badge>
                </div>
                <p className="text-sm text-muted-foreground">Casa {moonHouse}</p>
              </div>
              <p className="text-secondary">
                {getMoonAdvice()}
              </p>
            </div>
          </div>
        </AstroCard>

        {/* Mercúrio Retrógrado - Condicional */}
        {isMercuryRetrograde && (
          <AstroCard className="border-l-4 border-l-destructive bg-destructive/15 dark:bg-destructive/20 shadow-lg shadow-destructive/10 hover:shadow-xl hover:shadow-destructive/20 transition-all duration-300 animate-fadeIn">
            <div className="flex items-start gap-4">
              <div className="relative flex-shrink-0">
                {MercuryIcon && <MercuryIcon size={40} className="text-destructive drop-shadow-lg" />}
                <div className="absolute -top-1 -right-1 bg-destructive text-destructive-foreground rounded-full w-5 h-5 flex items-center justify-center text-xs font-bold shadow-md">
                  R
                </div>
              </div>
              <div className="flex-1 space-y-3">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <AlertCircle size={18} className="text-destructive" />
                    <h3 className="text-foreground font-semibold">Alerta: Mercúrio Retrógrado Ativo</h3>
                  </div>
                  <p className="text-sm text-foreground/80 dark:text-foreground/70">Em efeito por ~3 semanas</p>
                </div>
                
                <div className="space-y-3 text-base">
                  <div className="flex items-start gap-3 p-3 rounded-lg bg-destructive/10 dark:bg-destructive/15 border border-destructive/20">
                    <AlertCircle size={20} className="text-destructive mt-0.5 flex-shrink-0" />
                    <div className="flex-1">
                      <span className="text-destructive font-semibold block mb-1">Não Fazer:</span>
                      <span className="text-foreground/90 dark:text-foreground leading-relaxed">
                        Evite assinar contratos, tomar decisões finais ou fazer grandes compras 
                        (especialmente eletrônicos ou veículos). A comunicação pode estar confusa.
                      </span>
                    </div>
                  </div>
                  <div className="flex items-start gap-3 p-3 rounded-lg bg-accent/10 dark:bg-accent/15 border border-accent/30">
                    <CheckCircle size={20} className="text-accent mt-0.5 flex-shrink-0" />
                    <div className="flex-1">
                      <span className="text-accent font-semibold block mb-1">Fazer:</span>
                      <span className="text-foreground/90 dark:text-foreground leading-relaxed">
                        Ótimo momento para Revisar, Reavaliar e Replanejar. Reconecte-se com pessoas 
                        do passado ou revise projetos antigos.
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </AstroCard>
        )}

        {/* Lua Fora de Curso - Condicional */}
        {isMoonVoidOfCourse && (
          <AstroCard className="border-l-4 border-l-muted-foreground bg-muted/30 shadow-lg shadow-muted/10 hover:shadow-xl hover:shadow-muted/20 transition-all duration-300 animate-fadeIn">
            <div className="flex items-start gap-4">
              <Clock size={40} className="text-muted-foreground flex-shrink-0 drop-shadow-lg" />
              <div className="flex-1 space-y-3">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="text-foreground">Pausa Cósmica: Lua Fora de Curso</h3>
                  </div>
                  <p className="text-sm text-muted-foreground">Termina às {voidEndsAt} hoje</p>
                </div>
                
                <div className="space-y-2 text-sm">
                  <div className="flex items-start gap-2">
                    <AlertCircle size={16} className="text-muted-foreground mt-0.5 flex-shrink-0" />
                    <div>
                      <span className="text-muted-foreground font-medium">Não Fazer:</span>
                      <span className="text-secondary ml-1">
                        Evite iniciar qualquer empreendimento significativo (reuniões importantes, 
                        primeiros encontros, lançar um projeto). O que for começado agora tende a não 
                        trazer resultados.
                      </span>
                    </div>
                  </div>
                  <div className="flex items-start gap-2">
                    <CheckCircle size={16} className="text-accent mt-0.5 flex-shrink-0" />
                    <div>
                      <span className="text-accent font-medium">Fazer:</span>
                      <span className="text-secondary ml-1">
                        Perfeito para tarefas rotineiras, organizar sua mesa, meditar ou finalizar 
                        assuntos pendentes.
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </AstroCard>
        )}
      </div>
    </div>
  );
};
