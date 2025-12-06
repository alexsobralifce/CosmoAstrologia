import React from 'react';
import { 
  Settings, LogOut, User, X, Menu, Eye, EyeOff, Search, Bell, 
  ChevronDown, ChevronLeft, ChevronRight, Calendar, MapPin, Clock, 
  Star, Heart, Bookmark, Share2, Info, Sun, Moon, AlertCircle, 
  CheckCircle, Loader2, ArrowLeft, ArrowRight, ArrowUp, ArrowDown, BookOpen, Home, 
  Activity, Sparkles, Zap, Globe, Briefcase, Users, Compass, ChevronUp, UserCircle,
  TrendingUp, RefreshCw, Hash, FileText, Download, Mail, Brain,
  // Ícones para Aspectos
  Circle, Triangle, Square, Octagon, Link2, Target, Lightbulb, Shield, Flame, Scale
} from 'lucide-react';

// ===== ÍCONES SVG PARA ASPECTOS ASTROLÓGICOS =====

interface AspectIconProps {
  size?: number;
  className?: string;
  color?: string;
}

// Conjunção ☌ - Dois círculos sobrepostos (símbolo clássico)
const ConjunctionIcon = ({ size = 24, className = '', color }: AspectIconProps) => (
  <svg width={size} height={size} viewBox="0 0 24 24" className={className} style={{ color }}>
    <circle cx="9" cy="12" r="4.5" stroke={color || "currentColor"} strokeWidth="2.5" fill="none" />
    <circle cx="15" cy="12" r="4.5" stroke={color || "currentColor"} strokeWidth="2.5" fill="none" />
  </svg>
);

// Trígono △ - Triângulo equilátero
const TrineIcon = ({ size = 24, className = '', color }: AspectIconProps) => (
  <svg width={size} height={size} viewBox="0 0 24 24" className={className} style={{ color }}>
    <path 
      d="M12 4L21 19H3L12 4Z" 
      stroke={color || "currentColor"} 
      strokeWidth="2.5" 
      strokeLinejoin="round"
      fill="none"
    />
  </svg>
);

// Sextil ⚹ - Estrela de 6 pontas / Asterisco
const SextileIcon = ({ size = 24, className = '', color }: AspectIconProps) => (
  <svg width={size} height={size} viewBox="0 0 24 24" className={className} style={{ color }}>
    {/* Asterisco de 6 pontas */}
    <line x1="12" y1="2" x2="12" y2="22" stroke={color || "currentColor"} strokeWidth="2.5" strokeLinecap="round" />
    <line x1="3" y1="7" x2="21" y2="17" stroke={color || "currentColor"} strokeWidth="2.5" strokeLinecap="round" />
    <line x1="3" y1="17" x2="21" y2="7" stroke={color || "currentColor"} strokeWidth="2.5" strokeLinecap="round" />
  </svg>
);

// Quadratura □ - Quadrado
const SquareAspectIcon = ({ size = 24, className = '', color }: AspectIconProps) => (
  <svg width={size} height={size} viewBox="0 0 24 24" className={className} style={{ color }}>
    <rect 
      x="4" y="4" 
      width="16" height="16" 
      stroke={color || "currentColor"} 
      strokeWidth="2.5" 
      fill="none"
    />
  </svg>
);

// Oposição ☍ - Dois círculos conectados por linha
const OppositionIcon = ({ size = 24, className = '', color }: AspectIconProps) => (
  <svg width={size} height={size} viewBox="0 0 24 24" className={className} style={{ color }}>
    <circle cx="5" cy="12" r="3.5" stroke={color || "currentColor"} strokeWidth="2.5" fill="none" />
    <circle cx="19" cy="12" r="3.5" stroke={color || "currentColor"} strokeWidth="2.5" fill="none" />
    <line x1="8.5" y1="12" x2="15.5" y2="12" stroke={color || "currentColor"} strokeWidth="2.5" strokeLinecap="round" />
  </svg>
);

export const UIIcons = {
  Settings,
  LogOut,
  User,
  UserCircle,
  X,
  Menu,
  Eye,
  EyeOff,
  Search,
  Bell,
  ChevronDown,
  ChevronUp,
  ChevronLeft,
  ChevronRight,
  Calendar,
  MapPin,
  Clock,
  Star,
  Heart,
  Bookmark,
  Share2,
  Info,
  Sun,
  Moon,
  AlertCircle,
  CheckCircle,
  Loader: Loader2,
  Mail,
  ArrowLeft,
  ArrowRight,
  ArrowUp,
  ArrowDown,
  BookOpen,
  Home,
  Activity,
  Sparkles,
  Zap,
  Globe,
  Briefcase,
  Users,
  Compass,
  TrendingUp,
  RefreshCw,
  Hash,
  FileText,
  Download,
  Brain,
  // Ícones para Aspectos Astrológicos
  Circle,      
  Triangle,    
  Square,      
  Octagon,     
  Link2,       
  Target,      
  Lightbulb,   
  Shield,      
  Flame,       
  Scale,       
  // Ícones SVG customizados para Aspectos
  ConjunctionIcon,  // ☌ Conjunção
  TrineIcon,        // △ Trígono
  SextileIcon,      // ⚹ Sextil
  SquareAspectIcon, // □ Quadratura
  OppositionIcon,   // ☍ Oposição
};

export type IconName = keyof typeof UIIcons;
