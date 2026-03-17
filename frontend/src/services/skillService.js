import api from './api'

const analyze = (payload) => {
  return api.post('/chatbot/skill-analysis/', payload)
}

export default { analyze }
