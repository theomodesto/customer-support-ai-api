const API_BASE_URL = 'http://localhost:8000'

export const checkApiStatus = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/health`)
    if (response.ok) {
      return { online: true, text: 'API Online' }
    } else {
      throw new Error('API not responding')
    }
  } catch (error) {
    console.error('API Status Check Failed:', error)
    return { online: false, text: 'API Offline' }
  }
}

export const createSupportRequest = async (requestData) => {
  const response = await fetch(`${API_BASE_URL}/requests`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(requestData)
  })

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`)
  }

  return response.json()
}

export const getSupportRequests = async (page = 1, size = 20, filters = {}) => {
  const params = new URLSearchParams({
    page: page.toString(),
    size: size.toString()
  })

  if (filters.category) {
    params.append('category', filters.category)
  }
  if (filters.priority) {
    params.append('priority', filters.priority)
  }

  const response = await fetch(`${API_BASE_URL}/requests?${params}`)

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`)
  }

  return response.json()
}

export const getStatistics = async (days = 7) => {
  const response = await fetch(`${API_BASE_URL}/stats?days=${days}`)

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`)
  }

  return response.json()
} 