import dotenv from 'dotenv'
dotenv.config()

export const env = {
  modelType: process.env.MODEL_TYPE as 'local' | 'openai',
  modelName: process.env.MODEL_NAME || 'mistral',
  modelEndpoint: process.env.MODEL_ENDPOINT,
  openaiKey: process.env.OPENAI_API_KEY
}