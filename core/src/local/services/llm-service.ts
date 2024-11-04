import { Ollama } from 'ollama'
import { OpenAIApi } from 'openai'
import { modelConfig } from '../config/model-config'

export class LLMService {
  private ollama: Ollama;
  private openai: OpenAIApi;

  constructor() {
    this.ollama = new Ollama({
      host: modelConfig.endpoint
    });
  }

  async generateResponse(prompt: string, systemPrompt?: string) {
    try {
      if (modelConfig.type === 'local') {
        const response = await this.ollama.chat({
          model: modelConfig.modelName,
          messages: [
            ...(systemPrompt ? [{ role: 'system', content: systemPrompt }] : []),
            { role: 'user', content: prompt }
          ],
          stream: false
        })
        return response.message.content
      } else {
        // Your existing OpenAI code
      }
    } catch (error) {
      console.error('LLM Error:', error)
      throw error
    }
  }

  async streamResponse(prompt: string, onToken: (token: string) => void) {
    if (modelConfig.type === 'local') {
      const stream = await this.ollama.chat({
        model: modelConfig.modelName,
        messages: [{ role: 'user', content: prompt }],
        stream: true
      })

      for await (const part of stream) {
        onToken(part.message.content)
      }
    }
  }
}