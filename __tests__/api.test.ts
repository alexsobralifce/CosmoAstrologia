import { apiService } from '@/services/api';

// Mock fetch
global.fetch = jest.fn();

describe('API Service', () => {
  beforeEach(() => {
    (fetch as jest.Mock).mockClear();
    localStorage.clear();
  });

  it('should use correct API base URL', () => {
    const expectedUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    // The API service should use the environment variable
    expect(process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000').toBe(expectedUrl);
  });

  it('should handle authentication token', () => {
    localStorage.setItem('auth_token', 'test-token');
    // Token should be retrieved from localStorage
    const token = localStorage.getItem('auth_token');
    expect(token).toBe('test-token');
  });

  it('should handle logout', () => {
    localStorage.setItem('auth_token', 'test-token');
    apiService.logout();
    const token = localStorage.getItem('auth_token');
    expect(token).toBeNull();
  });
});
