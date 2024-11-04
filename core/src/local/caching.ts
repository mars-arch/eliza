import NodeCache from 'node-cache'

export class CachedLLMService extends LLMService {
  private cache: NodeCache;

  constructor() {
    super();
    this.cache = new NodeCache({ stdTTL: 3600 }); // 1 hour cache
  }

  async generateResponse(prompt: string, systemPrompt?: string) {
    const cacheKey = `${prompt}-${systemPrompt || ''}`
    const cached = this.cache.get(cacheKey)
    
    if (cached) return cached as string

    const response = await super.generateResponse(prompt, systemPrompt)
    this.cache.set(cacheKey, response)
    return response
  }
}