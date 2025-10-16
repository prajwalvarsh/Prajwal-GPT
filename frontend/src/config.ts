import defaults from "@shared/constants.json";

type SharedDefaults = {
  OLLAMA_HOST: string;
  OLLAMA_MODEL: string;
  EMBEDDING_MODEL: string;
  VECTOR_STORE_PATH: string;
  API_BASE_URL: string;
  API_PORT: number;
  FRONTEND_BASE_URL: string;
};

const sharedDefaults = defaults as SharedDefaults;

export type AppConfig = {
  apiBaseUrl: string;
  frontendBaseUrl: string;
  defaultModel: string;
};

export const APP_CONFIG: AppConfig = {
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL || sharedDefaults.API_BASE_URL,
  frontendBaseUrl: sharedDefaults.FRONTEND_BASE_URL,
  defaultModel: sharedDefaults.OLLAMA_MODEL,
};
