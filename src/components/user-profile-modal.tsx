import { useState } from 'react';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogFooter } from './ui/dialog';
import { Avatar, AvatarImage, AvatarFallback } from './ui/avatar';
import { AstroButton } from './astro-button';
import { AstroInput } from './astro-input';
import { Label } from './ui/label';
import { UIIcons } from './ui-icons';
import { User } from '../hooks/useAuth';

interface UserProfileModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  user: User;
  onUpdateUser: (name: string) => Promise<void>;
  onLogout: () => void;
}

export const UserProfileModal = ({ 
  open, 
  onOpenChange, 
  user,
  onUpdateUser,
  onLogout 
}: UserProfileModalProps) => {
  const [name, setName] = useState(user.name);
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSave = async () => {
    if (!name.trim()) {
      setError('Nome não pode estar vazio');
      return;
    }

    setIsSaving(true);
    setError(null);

    try {
      await onUpdateUser(name.trim());
      setIsEditing(false);
    } catch (err) {
      setError('Erro ao atualizar perfil. Tente novamente.');
      console.error('Error updating user:', err);
    } finally {
      setIsSaving(false);
    }
  };

  const handleCancel = () => {
    setName(user.name);
    setIsEditing(false);
    setError(null);
  };

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map(n => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="text-accent">Perfil do Usuário</DialogTitle>
          <DialogDescription>
            Gerencie suas informações de perfil
          </DialogDescription>
        </DialogHeader>

        <div className="flex flex-col items-center gap-4 py-4">
          {/* Avatar */}
          <Avatar className="w-24 h-24">
            {user.picture ? (
              <AvatarImage src={user.picture} alt={user.name} />
            ) : null}
            <AvatarFallback className="bg-accent/20 text-accent text-2xl">
              {getInitials(user.name)}
            </AvatarFallback>
          </Avatar>

          {/* User Info */}
          <div className="w-full space-y-4">
            {/* Email (read-only) */}
            <div className="space-y-2">
              <Label htmlFor="email" className="text-secondary">Email</Label>
              <div className="flex items-center gap-2 p-3 rounded-lg bg-card/30 border border-border/20">
                <UIIcons.Mail size={16} className="text-secondary" />
                <span className="text-sm text-foreground/80">{user.email}</span>
              </div>
            </div>

            {/* Name (editable) */}
            <div className="space-y-2">
              <Label htmlFor="name" className="text-secondary">Nome</Label>
              {isEditing ? (
                <AstroInput
                  id="name"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Seu nome"
                  disabled={isSaving}
                />
              ) : (
                <div className="flex items-center justify-between p-3 rounded-lg bg-card/30 border border-border/20">
                  <span className="text-sm text-foreground">{user.name}</span>
                  <button
                    onClick={() => setIsEditing(true)}
                    className="p-1 rounded hover:bg-accent/10 transition-colors"
                  >
                    <UIIcons.Edit size={16} className="text-accent" />
                  </button>
                </div>
              )}
              {error && (
                <p className="text-xs text-red-500 flex items-center gap-1">
                  <UIIcons.AlertCircle size={12} />
                  {error}
                </p>
              )}
            </div>

            {/* Member Since */}
            <div className="space-y-2">
              <Label className="text-secondary">Membro desde</Label>
              <div className="flex items-center gap-2 p-3 rounded-lg bg-card/30 border border-border/20">
                <UIIcons.Calendar size={16} className="text-secondary" />
                <span className="text-sm text-foreground/80">
                  {new Date(user.created_at || Date.now()).toLocaleDateString('pt-BR')}
                </span>
              </div>
            </div>
          </div>
        </div>

        <DialogFooter className="flex-col sm:flex-row gap-2">
          {isEditing ? (
            <>
              <AstroButton
                variant="outline"
                onClick={handleCancel}
                disabled={isSaving}
                className="w-full sm:w-auto"
              >
                Cancelar
              </AstroButton>
              <AstroButton
                onClick={handleSave}
                disabled={isSaving}
                className="w-full sm:w-auto"
              >
                {isSaving ? 'Salvando...' : 'Salvar Alterações'}
              </AstroButton>
            </>
          ) : (
            <>
              <AstroButton
                variant="outline"
                onClick={onLogout}
                className="w-full sm:w-auto text-red-500 border-red-500/20 hover:bg-red-500/10"
              >
                <UIIcons.LogOut size={16} />
                Sair
              </AstroButton>
              <AstroButton
                onClick={() => onOpenChange(false)}
                className="w-full sm:w-auto"
              >
                Fechar
              </AstroButton>
            </>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

