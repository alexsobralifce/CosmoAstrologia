import { computeElementDistribution } from '@/components/dashboard-sections/overview/element-distribution';
import { getRulerSignAndHouse, RULER_BY_SIGN, RULER_DETAILS } from '@/components/dashboard-sections/overview/chart-ruler-data';

const base: any = { name: 'T', birthDate: new Date(), birthTime: '12:00', birthPlace: 'X' };

describe('computeElementDistribution', () => {
  it('conta os elementos dos planetas e do ascendente e acha dominante e ausente', () => {
    const r = computeElementDistribution({ ...base, sunSign: 'Áries', moonSign: 'Leão', ascendant: 'Sagitário', venusSign: 'Touro' }, 'pt');
    expect(r.dominantElement.name).toBe('Fogo');
    expect(r.dominantElement.percentage).toBe(75);
    expect(r.missingElement?.name).toBe('Ar');
  });

  it('traduz o nome do elemento e não divide por zero sem planetas', () => {
    const r = computeElementDistribution(base, 'en');
    expect(r.elementData.map((e) => e.name)).toEqual(['Fire', 'Earth', 'Air', 'Water']);
    expect(r.elementData.every((e) => e.percentage === 0)).toBe(true);
  });
});

describe('regente do mapa', () => {
  it('todo signo tem um regente com detalhes cadastrados', () => {
    for (const regente of Object.values(RULER_BY_SIGN)) {
      expect(RULER_DETAILS[regente]).toBeDefined();
    }
  });

  it('devolve signo e casa do regente, com fallback para o signo solar e casa 1', () => {
    expect(getRulerSignAndHouse({ ...base, venusSign: 'Aquário', venusHouse: 4 }, 'Vênus', 'Áries')).toEqual({ sign: 'Aquário', house: 4 });
    expect(getRulerSignAndHouse(base, 'Vênus', 'Áries')).toEqual({ sign: 'Áries', house: 1 });
    expect(getRulerSignAndHouse(base, 'Desconhecido', 'Libra')).toEqual({ sign: 'Libra', house: 1 });
  });
});
