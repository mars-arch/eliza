import pino from 'pino'

const logger = pino({
  level: 'info',
  transport: {
    target: 'pino-pretty'
  }
})

export class MonitoredLLMService extends CachedLLMService {
  async generateResponse(prompt: string, systemPrompt?: string) {
    const startTime = Date.now()
    try {
      const response = await super.generateResponse(prompt, systemPrompt)
      logger.info({
        type: 'llm_request',
        duration: Date.now() - startTime,
        modelType: modelConfig.type,
        modelName: modelConfig.modelName,
        promptLength: prompt.length,
        responseLength: response.length
      })
      return response
    } catch (error) {
      logger.error({
        type: 'llm_error',
        error,
        prompt,
        systemPrompt
      })
      throw error
    }
  }
}