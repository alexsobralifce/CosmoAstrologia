import { useState } from 'react';
import { AstroCard } from './astro-card';
import { AstroButton } from './astro-button';
import { UIIcons } from './ui-icons';
import { ThemeToggle } from './theme-toggle';
import { UserProfileModal } from './user-profile-modal';
import { Avatar, AvatarImage, AvatarFallback } from './ui/avatar';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuTrigger } from './ui/dropdown-menu';
import { UserWithBirthData } from '../hooks/useAuth';

interface PreChartDashboardProps {
  user: UserWithBirthData;
  onGenerateChart: () => void;
  onUpdateUser: (name: string) => Promise<void>;
  onLogout: () => Promise<void> | void;
}

export const PreChartDashboard = ({
  user,
  onGenerateChart,
  onUpdateUser,
  onLogout
}: PreChartDashboardProps) => {
  const [showUserProfile, setShowUserProfile] = useState(false);

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map(n => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  const handleLogout = async () => {
    await onLogout();
    window.location.href = '/';
  };

  const birthData = user.birthData!;

  return (
    <div className="min-h-screen bg-gradient-to-b from-background via-background to-[#1a1f4a] dark:to-[#1a1f4a] light:to-[#F0E6D2]">
      {/* Header */}
      <header className="border-b border-border/30 backdrop-blur-sm sticky top-0 z-10 bg-background/80">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <h2 className="text-accent">Minha Conta Astrológica</h2>
          <div className="flex items-center gap-2">
            <ThemeToggle />
            <button className="p-2 rounded-lg hover:bg-accent/10 transition-colors">
              <UIIcons.Bell size={20} className="text-secondary" />
            </button>
            <button className="p-2 rounded-lg hover:bg-accent/10 transition-colors">
              <UIIcons.Settings size={20} className="text-secondary" />
            </button>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <button className="p-1 rounded-full hover:ring-2 hover:ring-accent/50 transition-all focus:outline-none focus:ring-2 focus:ring-accent/50">
                  <Avatar className="w-8 h-8 cursor-pointer">
                    {user.picture ? (
                      <AvatarImage src={user.picture} alt={user.name} />
                    ) : null}
                    <AvatarFallback className="bg-accent/20 text-accent text-sm">
                      {getInitials(user.name)}
                    </AvatarFallback>
                  </Avatar>
                </button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-56">
                <DropdownMenuLabel className="font-normal">
                  <div className="flex flex-col space-y-1">
                    <p className="text-sm font-medium leading-none">{user.name}</p>
                    <p className="text-xs leading-none text-muted-foreground">{user.email}</p>
                  </div>
                </DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={() => setShowUserProfile(true)} className="cursor-pointer">
                  <UIIcons.User className="mr-2 h-4 w-4" />
                  <span>Perfil</span>
                </DropdownMenuItem>
                <DropdownMenuItem className="cursor-pointer">
                  <UIIcons.Settings className="mr-2 h-4 w-4" />
                  <span>Configurações</span>
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={handleLogout} className="cursor-pointer text-red-500 focus:text-red-500">
                  <UIIcons.LogOut className="mr-2 h-4 w-4" />
                  <span>Sair</span>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto px-4 py-12">
        <div className="text-center space-y-8">
          {/* Welcome Section */}
          <div className="space-y-4">
            <div className="flex justify-center">
              <div className="w-20 h-20 rounded-full bg-accent/20 flex items-center justify-center">
                <UIIcons.Star size={40} className="text-accent" />
              </div>
            </div>
            <h1 className="text-accent">Bem-vindo(a), {user.name}!</h1>
            <p className="text-secondary max-w-2xl mx-auto">
              Seus dados astrológicos estão salvos e seguros. Agora você pode gerar seu mapa astral personalizado.
            </p>
          </div>

          {/* Birth Data Summary */}
          <AstroCard className="max-w-2xl mx-auto">
            <div className="space-y-4">
              <h3 className="text-accent text-center">Seus Dados Astrológicos</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-center">
                <div className="space-y-2">
                  <UIIcons.Calendar className="w-6 h-6 text-accent mx-auto" />
                  <div>
                    <p className="text-sm text-secondary">Data de Nascimento</p>
                    <p className="text-foreground font-medium">
                      {new Date(birthData.birth_date).toLocaleDateString('pt-BR')}
                    </p>
                  </div>
                </div>
                <div className="space-y-2">
                  <UIIcons.Clock className="w-6 h-6 text-accent mx-auto" />
                  <div>
                    <p className="text-sm text-secondary">Hora de Nascimento</p>
                    <p className="text-foreground font-medium">{birthData.birth_time}</p>
                  </div>
                </div>
                <div className="space-y-2">
                  <UIIcons.MapPin className="w-6 h-6 text-accent mx-auto" />
                  <div>
                    <p className="text-sm text-secondary">Local de Nascimento</p>
                    <p className="text-foreground font-medium">{birthData.birth_place}</p>
                  </div>
                </div>
              </div>
            </div>
          </AstroCard>

          {/* Generate Chart CTA */}
          <div className="space-y-6">
            <AstroButton
              variant="primary"
              size="lg"
              onClick={onGenerateChart}
              className="mx-auto"
            >
              <UIIcons.Star size={24} />
              Gerar Meu Mapa Astral
            </AstroButton>
            
            <p className="text-sm text-secondary">
              Clique no botão acima para calcular e visualizar seu mapa astral completo
            </p>
          </div>

          {/* Features Preview */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-8">
            <div className="space-y-3">
              <UIIcons.Star size={32} className="text-accent mx-auto" />
              <h3 className="text-foreground">Posições Planetárias</h3>
              <p className="text-sm text-secondary">
                Veja onde cada planeta estava no momento do seu nascimento
              </p>
            </div>
            <div className="space-y-3">
              <UIIcons.Eye size={32} className="text-accent mx-auto" />
              <h3 className="text-foreground">Interpretações Detalhadas</h3>
              <p className="text-sm text-secondary">
                Análises profundas de cada aspecto do seu mapa natal
              </p>
            </div>
            <div className="space-y-3">
              <UIIcons.Heart size={32} className="text-accent mx-auto" />
              <h3 className="text-foreground">Insights Personalizados</h3>
              <p className="text-sm text-secondary">
                Descubra características únicas da sua personalidade
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* User Profile Modal */}
      <UserProfileModal
        open={showUserProfile}
        onOpenChange={setShowUserProfile}
        user={user}
        onUpdateUser={onUpdateUser}
        onLogout={handleLogout}
      />
    </div>
  );
};
