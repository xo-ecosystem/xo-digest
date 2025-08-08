export type MinecraftEffect = Record<string, unknown>;
export type SimsEffect = Record<string, unknown>;
export type UnityWebGLEffect = { glow?: string } & Record<string, unknown>;
export type VRChatEffect = { glow_on?: boolean } & Record<string, unknown>;

export type GameEffects = {
  minecraft?: MinecraftEffect;
  sims?: SimsEffect;
  unity_webgl?: UnityWebGLEffect;
  vrchat?: VRChatEffect;
};

export type Trait = {
  id: string;
  name: string;
  description: string;
  rarity?: string;
  tags?: string[];
  media?: { image?: string; animation?: string };
  attributes?: Array<Record<string, unknown>>;
  game_effects?: GameEffects;
};


