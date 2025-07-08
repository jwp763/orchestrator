import { renderHook, act } from '@testing-library/react'
import { useLocalStorage, useSessionStorage } from './useLocalStorage'

// Mock localStorage and sessionStorage
const mockLocalStorage = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
}

const mockSessionStorage = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
}

Object.defineProperty(window, 'localStorage', {
  value: mockLocalStorage,
  writable: true,
})

Object.defineProperty(window, 'sessionStorage', {
  value: mockSessionStorage,
  writable: true,
})

describe('useLocalStorage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('initial value', () => {
    test('should return initial value when localStorage is empty', () => {
      mockLocalStorage.getItem.mockReturnValue(null)

      const { result } = renderHook(() => useLocalStorage('testKey', 'initialValue'))

      expect(result.current[0]).toBe('initialValue')
      expect(mockLocalStorage.getItem).toHaveBeenCalledWith('testKey')
    })

    test('should return stored value when localStorage has data', () => {
      mockLocalStorage.getItem.mockReturnValue(JSON.stringify('storedValue'))

      const { result } = renderHook(() => useLocalStorage('testKey', 'initialValue'))

      expect(result.current[0]).toBe('storedValue')
      expect(mockLocalStorage.getItem).toHaveBeenCalledWith('testKey')
    })

    test('should handle complex objects', () => {
      const complexObject = { name: 'John', age: 30, active: true }
      mockLocalStorage.getItem.mockReturnValue(JSON.stringify(complexObject))

      const { result } = renderHook(() => useLocalStorage('testKey', {}))

      expect(result.current[0]).toEqual(complexObject)
    })

    test('should handle arrays', () => {
      const arrayValue = [1, 2, 3, 'test']
      mockLocalStorage.getItem.mockReturnValue(JSON.stringify(arrayValue))

      const { result } = renderHook(() => useLocalStorage('testKey', []))

      expect(result.current[0]).toEqual(arrayValue)
    })

    test('should handle null values', () => {
      mockLocalStorage.getItem.mockReturnValue(JSON.stringify(null))

      const { result } = renderHook(() => useLocalStorage('testKey', 'default'))

      expect(result.current[0]).toBe(null)
    })

    test('should handle boolean values', () => {
      mockLocalStorage.getItem.mockReturnValue(JSON.stringify(false))

      const { result } = renderHook(() => useLocalStorage('testKey', true))

      expect(result.current[0]).toBe(false)
    })

    test('should handle number values', () => {
      mockLocalStorage.getItem.mockReturnValue(JSON.stringify(42))

      const { result } = renderHook(() => useLocalStorage('testKey', 0))

      expect(result.current[0]).toBe(42)
    })
  })

  describe('error handling', () => {
    test('should handle JSON parsing errors gracefully', () => {
      mockLocalStorage.getItem.mockReturnValue('invalid json')
      const consoleSpy = vi.spyOn(console, 'warn').mockImplementation(() => {})

      const { result } = renderHook(() => useLocalStorage('testKey', 'defaultValue'))

      expect(result.current[0]).toBe('defaultValue')
      expect(consoleSpy).toHaveBeenCalledWith(
        'Error reading localStorage key "testKey":',
        expect.any(SyntaxError)
      )

      consoleSpy.mockRestore()
    })

    test('should handle localStorage access errors', () => {
      mockLocalStorage.getItem.mockImplementation(() => {
        throw new Error('localStorage access denied')
      })
      const consoleSpy = vi.spyOn(console, 'warn').mockImplementation(() => {})

      const { result } = renderHook(() => useLocalStorage('testKey', 'defaultValue'))

      expect(result.current[0]).toBe('defaultValue')
      expect(consoleSpy).toHaveBeenCalledWith(
        'Error reading localStorage key "testKey":',
        expect.any(Error)
      )

      consoleSpy.mockRestore()
    })
  })

  describe('setValue', () => {
    test('should update value and localStorage', () => {
      mockLocalStorage.getItem.mockReturnValue(null)

      const { result } = renderHook(() => useLocalStorage('testKey', 'initialValue'))

      act(() => {
        result.current[1]('newValue')
      })

      expect(result.current[0]).toBe('newValue')
      expect(mockLocalStorage.setItem).toHaveBeenCalledWith('testKey', JSON.stringify('newValue'))
    })

    test('should handle function updates', () => {
      mockLocalStorage.getItem.mockReturnValue(JSON.stringify('initialValue'))

      const { result } = renderHook(() => useLocalStorage('testKey', 'defaultValue'))

      act(() => {
        result.current[1]((prev) => prev + ' updated')
      })

      expect(result.current[0]).toBe('initialValue updated')
      expect(mockLocalStorage.setItem).toHaveBeenCalledWith(
        'testKey',
        JSON.stringify('initialValue updated')
      )
    })

    test('should handle complex object updates', () => {
      const initialObject = { name: 'John', age: 30 }
      mockLocalStorage.getItem.mockReturnValue(JSON.stringify(initialObject))

      const { result } = renderHook(() => useLocalStorage('testKey', {}))

      act(() => {
        result.current[1]((prev: any) => ({ ...prev, age: 31 }))
      })

      expect(result.current[0]).toEqual({ name: 'John', age: 31 })
      expect(mockLocalStorage.setItem).toHaveBeenCalledWith(
        'testKey',
        JSON.stringify({ name: 'John', age: 31 })
      )
    })

    test('should handle array updates', () => {
      const initialArray = [1, 2, 3]
      mockLocalStorage.getItem.mockReturnValue(JSON.stringify(initialArray))

      const { result } = renderHook(() => useLocalStorage('testKey', []))

      act(() => {
        result.current[1]((prev: number[]) => [...prev, 4])
      })

      expect(result.current[0]).toEqual([1, 2, 3, 4])
      expect(mockLocalStorage.setItem).toHaveBeenCalledWith(
        'testKey',
        JSON.stringify([1, 2, 3, 4])
      )
    })

    test('should handle localStorage setItem errors', () => {
      mockLocalStorage.getItem.mockReturnValue(null)
      mockLocalStorage.setItem.mockImplementation(() => {
        throw new Error('localStorage quota exceeded')
      })
      const consoleSpy = vi.spyOn(console, 'warn').mockImplementation(() => {})

      const { result } = renderHook(() => useLocalStorage('testKey', 'initialValue'))

      act(() => {
        result.current[1]('newValue')
      })

      // Value should still be updated in state
      expect(result.current[0]).toBe('newValue')
      expect(consoleSpy).toHaveBeenCalledWith(
        'Error setting localStorage key "testKey":',
        expect.any(Error)
      )

      consoleSpy.mockRestore()
    })
  })

  describe('multiple instances', () => {
    test('should handle multiple instances of the same key', () => {
      mockLocalStorage.getItem.mockReturnValue(JSON.stringify('initialValue'))

      const { result: result1 } = renderHook(() => useLocalStorage('sharedKey', 'default'))
      const { result: result2 } = renderHook(() => useLocalStorage('sharedKey', 'default'))

      expect(result1.current[0]).toBe('initialValue')
      expect(result2.current[0]).toBe('initialValue')

      act(() => {
        result1.current[1]('updatedValue')
      })

      expect(result1.current[0]).toBe('updatedValue')
      // Note: result2 will still show old value as hooks don't sync across instances
      expect(result2.current[0]).toBe('initialValue')
    })
  })

  describe('TypeScript types', () => {
    test('should preserve types correctly', () => {
      interface TestObject {
        name: string
        count: number
      }

      const initialValue: TestObject = { name: 'test', count: 0 }
      mockLocalStorage.getItem.mockReturnValue(JSON.stringify(initialValue))

      const { result } = renderHook(() => useLocalStorage<TestObject>('testKey', initialValue))

      expect(result.current[0].name).toBe('test')
      expect(result.current[0].count).toBe(0)

      act(() => {
        result.current[1]({ name: 'updated', count: 5 })
      })

      expect(result.current[0].name).toBe('updated')
      expect(result.current[0].count).toBe(5)
    })
  })
})

describe('useSessionStorage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('initial value', () => {
    test('should return initial value when sessionStorage is empty', () => {
      mockSessionStorage.getItem.mockReturnValue(null)

      const { result } = renderHook(() => useSessionStorage('testKey', 'initialValue'))

      expect(result.current[0]).toBe('initialValue')
      expect(mockSessionStorage.getItem).toHaveBeenCalledWith('testKey')
    })

    test('should return stored value when sessionStorage has data', () => {
      mockSessionStorage.getItem.mockReturnValue(JSON.stringify('storedValue'))

      const { result } = renderHook(() => useSessionStorage('testKey', 'initialValue'))

      expect(result.current[0]).toBe('storedValue')
      expect(mockSessionStorage.getItem).toHaveBeenCalledWith('testKey')
    })
  })

  describe('setValue', () => {
    test('should update value and sessionStorage', () => {
      mockSessionStorage.getItem.mockReturnValue(null)

      const { result } = renderHook(() => useSessionStorage('testKey', 'initialValue'))

      act(() => {
        result.current[1]('newValue')
      })

      expect(result.current[0]).toBe('newValue')
      expect(mockSessionStorage.setItem).toHaveBeenCalledWith('testKey', JSON.stringify('newValue'))
    })

    test('should handle function updates', () => {
      mockSessionStorage.getItem.mockReturnValue(JSON.stringify('initialValue'))

      const { result } = renderHook(() => useSessionStorage('testKey', 'defaultValue'))

      act(() => {
        result.current[1]((prev) => prev + ' updated')
      })

      expect(result.current[0]).toBe('initialValue updated')
      expect(mockSessionStorage.setItem).toHaveBeenCalledWith(
        'testKey',
        JSON.stringify('initialValue updated')
      )
    })
  })

  describe('error handling', () => {
    test('should handle JSON parsing errors gracefully', () => {
      mockSessionStorage.getItem.mockReturnValue('invalid json')
      const consoleSpy = vi.spyOn(console, 'warn').mockImplementation(() => {})

      const { result } = renderHook(() => useSessionStorage('testKey', 'defaultValue'))

      expect(result.current[0]).toBe('defaultValue')
      expect(consoleSpy).toHaveBeenCalledWith(
        'Error reading sessionStorage key "testKey":',
        expect.any(SyntaxError)
      )

      consoleSpy.mockRestore()
    })

    test('should handle sessionStorage setItem errors', () => {
      mockSessionStorage.getItem.mockReturnValue(null)
      mockSessionStorage.setItem.mockImplementation(() => {
        throw new Error('sessionStorage quota exceeded')
      })
      const consoleSpy = vi.spyOn(console, 'warn').mockImplementation(() => {})

      const { result } = renderHook(() => useSessionStorage('testKey', 'initialValue'))

      act(() => {
        result.current[1]('newValue')
      })

      expect(result.current[0]).toBe('newValue')
      expect(consoleSpy).toHaveBeenCalledWith(
        'Error setting sessionStorage key "testKey":',
        expect.any(Error)
      )

      consoleSpy.mockRestore()
    })
  })
})