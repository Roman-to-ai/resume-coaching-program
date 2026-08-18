import 'dotenv/config';

export const config = {
  port: Number(process.env.BFF_PORT || 3000),
  backendBaseUrl: process.env.BACKEND_BASE_URL || 'http://localhost:8080',
  aiServiceUrl: process.env.AI_SERVICE_URL || 'http://localhost:8001',
};
