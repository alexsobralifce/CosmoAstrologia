export interface BirthData {
  name: string;
  birth_date: string; // ISO format
  birth_time: string; // "HH:MM"
  birth_place: string;
  latitude: number;
  longitude: number;
}

export interface UserRegisterData {
  email: string;
  password?: string;
  name: string;
  birth_data: BirthData;
}

export interface AuthToken {
  access_token: string;
  token_type: string;
}

export interface BirthChartResponse {
  id: number;
  user_id: number;
  name: string;
  birth_date: string;
  birth_time: string;
  birth_place: string;
  latitude: number;
  longitude: number;
  sun_sign: string;
  moon_sign: string;
  ascendant_sign: string;
  sun_degree?: number;
  moon_degree?: number;
  ascendant_degree?: number;
  // Planetas principais
  mercury_sign?: string;
  mercury_degree?: number;
  venus_sign?: string;
  venus_degree?: number;
  mars_sign?: string;
  mars_degree?: number;
  jupiter_sign?: string;
  jupiter_degree?: number;
  saturn_sign?: string;
  saturn_degree?: number;
  uranus_sign?: string;
  uranus_degree?: number;
  neptune_sign?: string;
  neptune_degree?: number;
  pluto_sign?: string;
  pluto_degree?: number;
  midheaven_sign?: string;
  midheaven_degree?: number;
  planets_conjunct_midheaven?: string[];
  uranus_on_midheaven?: boolean;
  // Nodos Lunares
  north_node_sign?: string;
  north_node_degree?: number;
  south_node_sign?: string;
  south_node_degree?: number;
  // Quíron (a ferida do curador)
  chiron_sign?: string;
  chiron_degree?: number;
  is_primary: boolean;
  created_at: string;
  updated_at?: string;
}
