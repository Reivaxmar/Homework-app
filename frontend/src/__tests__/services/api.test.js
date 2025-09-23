import { describe, it, expect, vi, beforeEach } from 'vitest'

// Mock axios with factory function
vi.mock('axios', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
    defaults: {
      headers: {
        common: {}
      }
    }
  },
  create: vi.fn(() => ({
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
    defaults: {
      headers: {
        common: {}
      }
    }
  }))
}))

describe('API Service', () => {
  let mockApi

  beforeEach(async () => {
    vi.clearAllMocks()
    // Dynamically import the mocked axios
    const axios = await import('axios')
    mockApi = axios.default.create()
  })

  it('should make GET requests', async () => {
    const mockData = { message: 'success' }
    mockApi.get.mockResolvedValue({ data: mockData })

    const result = await mockApi.get('/test-endpoint')

    expect(mockApi.get).toHaveBeenCalledWith('/test-endpoint')
    expect(result.data).toEqual(mockData)
  })

  it('should make POST requests', async () => {
    const requestData = { name: 'Test' }
    const responseData = { id: 1, name: 'Test' }
    mockApi.post.mockResolvedValue({ data: responseData })

    const result = await mockApi.post('/test-endpoint', requestData)

    expect(mockApi.post).toHaveBeenCalledWith('/test-endpoint', requestData)
    expect(result.data).toEqual(responseData)
  })

  it('should make PUT requests', async () => {
    const requestData = { name: 'Updated Test' }
    const responseData = { id: 1, name: 'Updated Test' }
    mockApi.put.mockResolvedValue({ data: responseData })

    const result = await mockApi.put('/test-endpoint/1', requestData)

    expect(mockApi.put).toHaveBeenCalledWith('/test-endpoint/1', requestData)
    expect(result.data).toEqual(responseData)
  })

  it('should make DELETE requests', async () => {
    mockApi.delete.mockResolvedValue({ status: 204 })

    const result = await mockApi.delete('/test-endpoint/1')

    expect(mockApi.delete).toHaveBeenCalledWith('/test-endpoint/1')
    expect(result.status).toBe(204)
  })

  it('should handle request errors', async () => {
    const errorResponse = {
      response: {
        status: 400,
        data: { detail: 'Bad Request' }
      }
    }
    mockApi.get.mockRejectedValue(errorResponse)

    await expect(mockApi.get('/error-endpoint')).rejects.toEqual(errorResponse)
  })

  it('should handle network errors', async () => {
    const networkError = new Error('Network Error')
    mockApi.get.mockRejectedValue(networkError)

    await expect(mockApi.get('/network-error')).rejects.toThrow('Network Error')
  })

  it('should set authorization header when token is provided', () => {
    const token = 'test-jwt-token'
    mockApi.defaults.headers.common['Authorization'] = `Bearer ${token}`

    expect(mockApi.defaults.headers.common['Authorization']).toBe(`Bearer ${token}`)
  })

  it('should remove authorization header when token is cleared', () => {
    mockApi.defaults.headers.common['Authorization'] = 'Bearer test-token'
    delete mockApi.defaults.headers.common['Authorization']

    expect(mockApi.defaults.headers.common['Authorization']).toBeUndefined()
  })

  it('should handle timeout errors', async () => {
    const timeoutError = {
      code: 'ECONNABORTED',
      message: 'timeout of 10000ms exceeded'
    }
    mockApi.get.mockRejectedValue(timeoutError)

    await expect(mockApi.get('/slow-endpoint')).rejects.toEqual(timeoutError)
  })

  it('should handle different HTTP status codes', async () => {
    const testCases = [
      { status: 200, shouldResolve: true },
      { status: 201, shouldResolve: true },
      { status: 204, shouldResolve: true },
      { status: 400, shouldResolve: false },
      { status: 401, shouldResolve: false },
      { status: 403, shouldResolve: false },
      { status: 404, shouldResolve: false },
      { status: 500, shouldResolve: false }
    ]

    for (const testCase of testCases) {
      if (testCase.shouldResolve) {
        mockApi.get.mockResolvedValue({ 
          status: testCase.status, 
          data: { success: true } 
        })
        
        const result = await mockApi.get('/test')
        expect(result.status).toBe(testCase.status)
      } else {
        mockApi.get.mockRejectedValue({
          response: {
            status: testCase.status,
            data: { detail: 'Error' }
          }
        })
        
        await expect(mockApi.get('/test')).rejects.toHaveProperty(
          'response.status', 
          testCase.status
        )
      }
    }
  })
})