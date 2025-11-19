import { useEffect, useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from './ui/dialog';
import { AstroButton } from './astro-button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';

export interface ThemeColors {
  primary: string;
  secondary: string;
  accent: string;
  neutral: string;
}

export interface ThemeConfig {
  light: ThemeColors;
  dark: ThemeColors;
}

export interface FontSizeConfig {
  base: number; // Tamanho base em px (padrão: 16)
}

interface ThemeCustomizationModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSave: (theme: ThemeConfig) => void;
  onFontSizeChange?: (fontSize: FontSizeConfig) => void;
  initialValue?: ThemeConfig | null;
  initialFontSize?: FontSizeConfig | null;
}

const DEFAULT_LIGHT: ThemeColors = {
  primary: '#FDFBF7',
  secondary: '#6B7280',
  accent: '#D4A024',
  neutral: '#F0E6D2',
};

const DEFAULT_DARK: ThemeColors = {
  primary: '#0A0E2F',
  secondary: '#A0AEC0',
  accent: '#E8B95A',
  neutral: '#1A1F4A',
};

export const ThemeCustomizationModal = ({
  open,
  onOpenChange,
  onSave,
  onFontSizeChange,
  initialValue,
  initialFontSize,
}: ThemeCustomizationModalProps) => {
  const [lightTheme, setLightTheme] = useState<ThemeColors>(
    initialValue?.light ?? DEFAULT_LIGHT
  );
  const [darkTheme, setDarkTheme] = useState<ThemeColors>(
    initialValue?.dark ?? DEFAULT_DARK
  );
  const [fontSize, setFontSize] = useState<FontSizeConfig>(
    initialFontSize ?? { base: 16 }
  );
  const [activeTab, setActiveTab] = useState<'light' | 'dark' | 'typography'>('light');

  useEffect(() => {
    if (initialValue) {
      setLightTheme(initialValue.light);
      setDarkTheme(initialValue.dark);
    }
    if (initialFontSize) {
      setFontSize(initialFontSize);
    }
  }, [initialValue, initialFontSize, open]);

  const handleSave = () => {
    onSave({ light: lightTheme, dark: darkTheme });
    if (onFontSizeChange) {
      onFontSizeChange(fontSize);
    }
    onOpenChange(false);
  };

  const handleFontSizeChange = (newSize: number) => {
    const newFontSize = { base: newSize };
    setFontSize(newFontSize);
    if (onFontSizeChange) {
      onFontSizeChange(newFontSize);
    }
  };

  const ColorInput = ({
    label,
    description,
    value,
    onChange,
  }: {
    label: string;
    description: string;
    value: string;
    onChange: (value: string) => void;
  }) => (
    <label className="flex flex-col text-sm gap-1">
      <div>
        <span className="font-medium">{label}</span>
        <span className="text-xs text-secondary/70 ml-2">({description})</span>
      </div>
      <input
        type="color"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="h-10 rounded border border-border/50 cursor-pointer"
      />
      <span className="text-xs font-mono text-secondary">{value.toUpperCase()}</span>
    </label>
  );

  const ThemeSection = ({
    theme,
    setTheme,
    themeName,
  }: {
    theme: ThemeColors;
    setTheme: (theme: ThemeColors) => void;
    themeName: 'light' | 'dark';
  }) => (
    <div className="space-y-4">
      <p className="text-sm text-secondary">
        Defina 4 cores para o tema <strong>{themeName === 'light' ? 'claro' : 'escuro'}</strong>. Use valores hexadecimais.
      </p>
      <div className="grid grid-cols-1 gap-3">
        <ColorInput
          label="Primária"
          description="fundos principais"
          value={theme.primary}
          onChange={(value) => setTheme({ ...theme, primary: value })}
        />
        <ColorInput
          label="Secundária"
          description="textos/elementos de apoio"
          value={theme.secondary}
          onChange={(value) => setTheme({ ...theme, secondary: value })}
        />
        <ColorInput
          label="Acento"
          description="destaques, botões"
          value={theme.accent}
          onChange={(value) => setTheme({ ...theme, accent: value })}
        />
        <ColorInput
          label="Neutro"
          description="gradientes de fundo"
          value={theme.neutral}
          onChange={(value) => setTheme({ ...theme, neutral: value })}
        />
      </div>
      <div className="p-3 rounded-lg border border-border/40 bg-card/30">
        <p className="text-xs uppercase tracking-wide text-secondary mb-2">Preview</p>
        <div className="flex gap-2">
          <div
            className="w-8 h-8 rounded border border-border/50"
            style={{ backgroundColor: theme.primary }}
            title="Primária"
          />
          <div
            className="w-8 h-8 rounded border border-border/50"
            style={{ backgroundColor: theme.secondary }}
            title="Secundária"
          />
          <div
            className="w-8 h-8 rounded border border-border/50"
            style={{ backgroundColor: theme.accent }}
            title="Acento"
          />
          <div
            className="w-8 h-8 rounded border border-border/50"
            style={{ backgroundColor: theme.neutral }}
            title="Neutro"
          />
        </div>
      </div>
    </div>
  );

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Personalização do Sistema</DialogTitle>
        </DialogHeader>
        <div className="space-y-4">
          <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as 'light' | 'dark' | 'typography')}>
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="light">Tema Claro</TabsTrigger>
              <TabsTrigger value="dark">Tema Escuro</TabsTrigger>
              <TabsTrigger value="typography">Tipografia</TabsTrigger>
            </TabsList>
            <TabsContent value="light" className="mt-4">
              <ThemeSection
                theme={lightTheme}
                setTheme={setLightTheme}
                themeName="light"
              />
            </TabsContent>
            <TabsContent value="dark" className="mt-4">
              <ThemeSection
                theme={darkTheme}
                setTheme={setDarkTheme}
                themeName="dark"
              />
            </TabsContent>
            <TabsContent value="typography" className="mt-4">
              <div className="space-y-6">
                <div>
                  <p className="text-sm text-secondary mb-4">
                    Ajuste o tamanho base das fontes do sistema. Isso afetará todos os textos da aplicação.
                  </p>
                  <div className="space-y-4">
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <label className="text-sm font-medium">
                          Tamanho Base da Fonte
                        </label>
                        <span className="text-sm text-accent font-mono">
                          {fontSize.base}px
                        </span>
                      </div>
                      <input
                        type="range"
                        min="12"
                        max="24"
                        step="1"
                        value={fontSize.base}
                        onChange={(e) => handleFontSizeChange(Number(e.target.value))}
                        className="w-full h-2 bg-border/40 rounded-lg appearance-none cursor-pointer accent-accent"
                        style={{
                          background: `linear-gradient(to right, var(--accent) 0%, var(--accent) ${((fontSize.base - 12) / (24 - 12)) * 100}%, var(--border) ${((fontSize.base - 12) / (24 - 12)) * 100}%, var(--border) 100%)`
                        }}
                      />
                      <div className="flex justify-between text-xs text-secondary/70 mt-1">
                        <span>Pequeno (12px)</span>
                        <span>Médio (16px)</span>
                        <span>Grande (20px)</span>
                        <span>Extra Grande (24px)</span>
                      </div>
                    </div>
                    <div className="p-4 rounded-lg border border-border/40 bg-card/30 space-y-3">
                      <p className="text-xs uppercase tracking-wide text-secondary mb-2">Preview</p>
                      <div className="space-y-2" style={{ fontSize: `${fontSize.base}px` }}>
                        <p className="text-foreground font-medium">
                          Texto de exemplo com tamanho {fontSize.base}px
                        </p>
                        <p className="text-secondary text-sm">
                          Este é um texto secundário para você ver como ficará o tamanho das fontes em diferentes contextos.
                        </p>
                        <div className="flex gap-2">
                          <button className="px-3 py-1.5 rounded bg-accent text-accent-foreground text-sm">
                            Botão de exemplo
                          </button>
                          <button className="px-3 py-1.5 rounded border border-border text-foreground text-sm">
                            Botão secundário
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </TabsContent>
          </Tabs>
          <div className="flex justify-end gap-2 pt-4 border-t border-border/40">
            <AstroButton variant="ghost" onClick={() => onOpenChange(false)}>
              Cancelar
            </AstroButton>
            <AstroButton onClick={handleSave}>Salvar cores</AstroButton>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

