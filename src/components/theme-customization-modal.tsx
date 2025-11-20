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

export interface TypographyConfig {
  fontSize: FontSizeConfig;
  fontFamily: string;
  fontWeight: 'normal' | 'medium' | 'semibold' | 'bold';
  fontStyle: 'normal' | 'italic';
  textColor: {
    primary: string;
    secondary: string;
    accent: string;
  };
  letterSpacing: 'tight' | 'normal' | 'wide';
  lineHeight: 'tight' | 'normal' | 'relaxed';
}

interface ThemeCustomizationModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSave: (theme: ThemeConfig) => void;
  onFontSizeChange?: (fontSize: FontSizeConfig) => void;
  onTypographyChange?: (typography: TypographyConfig) => void;
  initialValue?: ThemeConfig | null;
  initialFontSize?: FontSizeConfig | null;
  initialTypography?: TypographyConfig | null;
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

const DEFAULT_TYPOGRAPHY: TypographyConfig = {
  fontSize: { base: 16 },
  fontFamily: 'system-ui, -apple-system, sans-serif',
  fontWeight: 'normal',
  fontStyle: 'normal',
  textColor: {
    primary: '#0A0E2F',
    secondary: '#6B7280',
    accent: '#D4A024',
  },
  letterSpacing: 'normal',
  lineHeight: 'normal',
};

export const ThemeCustomizationModal = ({
  open,
  onOpenChange,
  onSave,
  onFontSizeChange,
  onTypographyChange,
  initialValue,
  initialFontSize,
  initialTypography,
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
  const [typography, setTypography] = useState<TypographyConfig>(
    initialTypography ?? DEFAULT_TYPOGRAPHY
  );
  const [activeTab, setActiveTab] = useState<'light' | 'dark' | 'typography'>('light');

  useEffect(() => {
    if (initialValue) {
      setLightTheme(initialValue.light);
      setDarkTheme(initialValue.dark);
    }
    if (initialFontSize) {
      setFontSize(initialFontSize);
      setTypography(prev => ({ ...prev, fontSize: initialFontSize }));
    }
    if (initialTypography) {
      setTypography(initialTypography);
    }
  }, [initialValue, initialFontSize, initialTypography, open]);

  const handleSave = () => {
    onSave({ light: lightTheme, dark: darkTheme });
    if (onFontSizeChange) {
      onFontSizeChange(fontSize);
    }
    if (onTypographyChange) {
      onTypographyChange({ ...typography, fontSize });
    }
    onOpenChange(false);
  };

  const handleFontSizeChange = (newSize: number) => {
    const newFontSize = { base: newSize };
    setFontSize(newFontSize);
    setTypography(prev => ({ ...prev, fontSize: newFontSize }));
    if (onFontSizeChange) {
      onFontSizeChange(newFontSize);
    }
  };

  const handleTypographyChange = (updates: Partial<TypographyConfig>) => {
    const newTypography = { ...typography, ...updates };
    setTypography(newTypography);
    if (updates.fontSize) {
      setFontSize(updates.fontSize);
      if (onFontSizeChange) {
        onFontSizeChange(updates.fontSize);
      }
    }
    if (onTypographyChange) {
      onTypographyChange(newTypography);
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
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Personalização do Sistema</DialogTitle>
        </DialogHeader>
        <div className="space-y-4">
          <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as 'light' | 'dark' | 'typography')}>
            <TabsList className="w-full flex gap-1 p-1 bg-card/50 backdrop-blur-sm">
              <TabsTrigger value="light" className="flex-1">Tema Claro</TabsTrigger>
              <TabsTrigger value="dark" className="flex-1">Tema Escuro</TabsTrigger>
              <TabsTrigger value="typography" className="flex-1">Tipografia</TabsTrigger>
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
              <div className="space-y-4 max-h-[calc(90vh-200px)] overflow-y-auto pr-2">
                <p className="text-sm text-secondary">
                  Personalize a tipografia do sistema: tamanho, família, peso, estilo e cores das fontes.
                </p>

                {/* Grid de 2 colunas para layout mais horizontal */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Coluna Esquerda */}
                  <div className="space-y-4">
                    {/* Tamanho da Fonte */}
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <label className="text-sm font-medium">
                          Tamanho Base da Fonte
                        </label>
                        <span className="text-sm text-accent font-mono">
                          {typography.fontSize.base}px
                        </span>
                      </div>
                      <input
                        type="range"
                        min="12"
                        max="24"
                        step="1"
                        value={typography.fontSize.base}
                        onChange={(e) => handleTypographyChange({ fontSize: { base: Number(e.target.value) } })}
                        className="w-full h-2 bg-border/40 rounded-lg appearance-none cursor-pointer accent-accent"
                        style={{
                          background: `linear-gradient(to right, var(--accent) 0%, var(--accent) ${((typography.fontSize.base - 12) / (24 - 12)) * 100}%, var(--border) ${((typography.fontSize.base - 12) / (24 - 12)) * 100}%, var(--border) 100%)`
                        }}
                      />
                      <div className="flex justify-between text-xs text-secondary/70 mt-1">
                        <span>12px</span>
                        <span>16px</span>
                        <span>20px</span>
                        <span>24px</span>
                      </div>
                    </div>

                    {/* Família da Fonte */}
                    <div>
                      <label className="text-sm font-medium mb-2 block">Família da Fonte</label>
                      <select
                        value={typography.fontFamily}
                        onChange={(e) => handleTypographyChange({ fontFamily: e.target.value })}
                        className="w-full px-3 py-2 rounded-lg border border-border/50 bg-card text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-accent/50"
                      >
                        <option value="system-ui, -apple-system, sans-serif">Sistema (Padrão)</option>
                        <option value="'Inter', sans-serif">Inter</option>
                        <option value="'Roboto', sans-serif">Roboto</option>
                        <option value="'Open Sans', sans-serif">Open Sans</option>
                        <option value="'Lato', sans-serif">Lato</option>
                        <option value="'Montserrat', sans-serif">Montserrat</option>
                        <option value="'Poppins', sans-serif">Poppins</option>
                        <option value="'Playfair Display', serif">Playfair Display (Serifada)</option>
                        <option value="'Merriweather', serif">Merriweather (Serifada)</option>
                        <option value="'Courier New', monospace">Courier New (Monospace)</option>
                      </select>
                    </div>

                    {/* Peso e Estilo da Fonte - lado a lado */}
                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <label className="text-sm font-medium mb-2 block">Peso da Fonte</label>
                        <div className="grid grid-cols-2 gap-1.5">
                          {(['normal', 'medium', 'semibold', 'bold'] as const).map((weight) => (
                            <button
                              key={weight}
                              onClick={() => handleTypographyChange({ fontWeight: weight })}
                              className={`px-2 py-1.5 rounded border text-xs transition-all ${
                                typography.fontWeight === weight
                                  ? 'bg-accent/20 border-accent text-accent'
                                  : 'border-border/50 hover:border-accent/50'
                              }`}
                              style={{ fontWeight: weight === 'normal' ? 400 : weight === 'medium' ? 500 : weight === 'semibold' ? 600 : 700 }}
                            >
                              {weight === 'normal' ? 'Normal' : weight === 'medium' ? 'Médio' : weight === 'semibold' ? 'Semi' : 'Negrito'}
                            </button>
                          ))}
                        </div>
                      </div>
                      <div>
                        <label className="text-sm font-medium mb-2 block">Estilo</label>
                        <div className="grid grid-cols-2 gap-1.5">
                          {(['normal', 'italic'] as const).map((style) => (
                            <button
                              key={style}
                              onClick={() => handleTypographyChange({ fontStyle: style })}
                              className={`px-2 py-1.5 rounded border text-xs transition-all ${
                                typography.fontStyle === style
                                  ? 'bg-accent/20 border-accent text-accent'
                                  : 'border-border/50 hover:border-accent/50'
                              }`}
                              style={{ fontStyle: style }}
                            >
                              {style === 'normal' ? 'Normal' : 'Itálico'}
                            </button>
                          ))}
                        </div>
                      </div>
                    </div>

                    {/* Espaçamento e Altura - lado a lado */}
                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <label className="text-sm font-medium mb-2 block">Espaçamento</label>
                        <div className="grid grid-cols-1 gap-1.5">
                          {(['tight', 'normal', 'wide'] as const).map((spacing) => (
                            <button
                              key={spacing}
                              onClick={() => handleTypographyChange({ letterSpacing: spacing })}
                              className={`px-2 py-1.5 rounded border text-xs transition-all ${
                                typography.letterSpacing === spacing
                                  ? 'bg-accent/20 border-accent text-accent'
                                  : 'border-border/50 hover:border-accent/50'
                              }`}
                              style={{ 
                                letterSpacing: spacing === 'tight' ? '-0.025em' : spacing === 'normal' ? '0' : '0.05em' 
                              }}
                            >
                              {spacing === 'tight' ? 'Apertado' : spacing === 'normal' ? 'Normal' : 'Amplo'}
                            </button>
                          ))}
                        </div>
                      </div>
                      <div>
                        <label className="text-sm font-medium mb-2 block">Altura da Linha</label>
                        <div className="grid grid-cols-1 gap-1.5">
                          {(['tight', 'normal', 'relaxed'] as const).map((lineHeight) => (
                            <button
                              key={lineHeight}
                              onClick={() => handleTypographyChange({ lineHeight })}
                              className={`px-2 py-1.5 rounded border text-xs transition-all ${
                                typography.lineHeight === lineHeight
                                  ? 'bg-accent/20 border-accent text-accent'
                                  : 'border-border/50 hover:border-accent/50'
                              }`}
                            >
                              {lineHeight === 'tight' ? 'Apertado' : lineHeight === 'normal' ? 'Normal' : 'Relaxado'}
                            </button>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Coluna Direita */}
                  <div className="space-y-4">
                    {/* Cores do Texto */}
                    <div>
                      <label className="text-sm font-medium mb-3 block">Cores do Texto</label>
                      <div className="space-y-3">
                        <div>
                          <label className="text-xs text-secondary/70 mb-1 block">Cor Primária</label>
                          <div className="flex gap-2 items-center">
                            <input
                              type="color"
                              value={typography.textColor.primary}
                              onChange={(e) => handleTypographyChange({ 
                                textColor: { ...typography.textColor, primary: e.target.value } 
                              })}
                              className="h-10 w-16 rounded border border-border/50 cursor-pointer flex-shrink-0"
                            />
                            <input
                              type="text"
                              value={typography.textColor.primary}
                              onChange={(e) => handleTypographyChange({ 
                                textColor: { ...typography.textColor, primary: e.target.value } 
                              })}
                              className="flex-1 px-2 py-1.5 rounded border border-border/50 bg-card text-foreground text-xs font-mono"
                              placeholder="#000000"
                            />
                          </div>
                        </div>
                        <div>
                          <label className="text-xs text-secondary/70 mb-1 block">Cor Secundária</label>
                          <div className="flex gap-2 items-center">
                            <input
                              type="color"
                              value={typography.textColor.secondary}
                              onChange={(e) => handleTypographyChange({ 
                                textColor: { ...typography.textColor, secondary: e.target.value } 
                              })}
                              className="h-10 w-16 rounded border border-border/50 cursor-pointer flex-shrink-0"
                            />
                            <input
                              type="text"
                              value={typography.textColor.secondary}
                              onChange={(e) => handleTypographyChange({ 
                                textColor: { ...typography.textColor, secondary: e.target.value } 
                              })}
                              className="flex-1 px-2 py-1.5 rounded border border-border/50 bg-card text-foreground text-xs font-mono"
                              placeholder="#6B7280"
                            />
                          </div>
                        </div>
                        <div>
                          <label className="text-xs text-secondary/70 mb-1 block">Cor de Acento</label>
                          <div className="flex gap-2 items-center">
                            <input
                              type="color"
                              value={typography.textColor.accent}
                              onChange={(e) => handleTypographyChange({ 
                                textColor: { ...typography.textColor, accent: e.target.value } 
                              })}
                              className="h-10 w-16 rounded border border-border/50 cursor-pointer flex-shrink-0"
                            />
                            <input
                              type="text"
                              value={typography.textColor.accent}
                              onChange={(e) => handleTypographyChange({ 
                                textColor: { ...typography.textColor, accent: e.target.value } 
                              })}
                              className="flex-1 px-2 py-1.5 rounded border border-border/50 bg-card text-foreground text-xs font-mono"
                              placeholder="#D4A024"
                            />
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Preview */}
                    <div className="p-3 rounded-lg border border-border/40 bg-card/30">
                      <p className="text-xs uppercase tracking-wide text-secondary mb-2">Preview</p>
                      <div 
                        className="space-y-2"
                        style={{
                          fontSize: `${typography.fontSize.base}px`,
                          fontFamily: typography.fontFamily,
                          fontWeight: typography.fontWeight === 'normal' ? 400 : typography.fontWeight === 'medium' ? 500 : typography.fontWeight === 'semibold' ? 600 : 700,
                          fontStyle: typography.fontStyle,
                          letterSpacing: typography.letterSpacing === 'tight' ? '-0.025em' : typography.letterSpacing === 'normal' ? '0' : '0.05em',
                          lineHeight: typography.lineHeight === 'tight' ? '1.25' : typography.lineHeight === 'normal' ? '1.5' : '1.75',
                        }}
                      >
                        <p style={{ color: typography.textColor.primary }}>
                          Texto primário
                        </p>
                        <p style={{ color: typography.textColor.secondary, fontSize: `${typography.fontSize.base * 0.875}px` }}>
                          Texto secundário
                        </p>
                        <p style={{ color: typography.textColor.accent }}>
                          Texto de destaque
                        </p>
                        <div className="flex gap-2 flex-wrap mt-2">
                          <button 
                            className="px-2 py-1 rounded bg-accent text-accent-foreground text-xs"
                            style={{ fontFamily: typography.fontFamily }}
                          >
                            Botão
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
            <AstroButton onClick={handleSave}>Salvar configurações</AstroButton>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

