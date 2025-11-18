import { DailyAdviceSection } from './daily-advice-section';

/**
 * Componente de demonstração mostrando diferentes estados da DailyAdviceSection
 * Use este como referência para entender os diferentes casos de uso
 */

export const DailyAdviceDemo = () => {
  return (
    <div className="space-y-12 p-8">
      {/* Cenário 1: Dia Normal - Apenas Lua */}
      <div>
        <h2 className="text-accent mb-4">Cenário 1: Dia Normal</h2>
        <p className="text-secondary mb-6">Apenas o trânsito da Lua é exibido.</p>
        <DailyAdviceSection
          moonSign="Leão"
          moonHouse={5}
          isMercuryRetrograde={false}
          isMoonVoidOfCourse={false}
        />
      </div>

      {/* Cenário 2: Mercúrio Retrógrado Ativo */}
      <div>
        <h2 className="text-accent mb-4">Cenário 2: Mercúrio Retrógrado</h2>
        <p className="text-secondary mb-6">Mercúrio está retrógrado - mostra alerta vermelho com conselhos.</p>
        <DailyAdviceSection
          moonSign="Câncer"
          moonHouse={11}
          isMercuryRetrograde={true}
          isMoonVoidOfCourse={false}
        />
      </div>

      {/* Cenário 3: Lua Fora de Curso */}
      <div>
        <h2 className="text-accent mb-4">Cenário 3: Lua Fora de Curso</h2>
        <p className="text-secondary mb-6">Lua void of course - pausa cósmica para tarefas rotineiras.</p>
        <DailyAdviceSection
          moonSign="Gêmeos"
          moonHouse={3}
          isMercuryRetrograde={false}
          isMoonVoidOfCourse={true}
          voidEndsAt="18:45"
        />
      </div>

      {/* Cenário 4: Tudo Ativo - Dia Desafiador */}
      <div>
        <h2 className="text-accent mb-4">Cenário 4: Dia Intenso</h2>
        <p className="text-secondary mb-6">
          Mercúrio retrógrado E Lua void of course - máxima cautela necessária.
        </p>
        <DailyAdviceSection
          moonSign="Peixes"
          moonHouse={12}
          isMercuryRetrograde={true}
          isMoonVoidOfCourse={true}
          voidEndsAt="14:20"
        />
      </div>
    </div>
  );
};
