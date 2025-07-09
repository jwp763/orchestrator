import { describe, it, expect } from 'vitest';
import { formatDate, daysBetween, isPastDate } from './date';

describe('formatDate', () => {
  it('should format ISO date string correctly', () => {
    // Use UTC to avoid timezone issues
    const date1 = formatDate('2024-03-15T12:00:00Z');
    const date2 = formatDate('2024-01-01T12:00:00Z');
    const date3 = formatDate('2024-12-31T12:00:00Z');
    
    expect(date1).toMatch(/Mar 1[45], 2024/); // Allow for timezone differences
    expect(date2).toMatch(/Jan 1, 2024/);
    expect(date3).toMatch(/Dec 31, 2024/);
  });
});

describe('daysBetween', () => {
  it('should calculate days between dates correctly', () => {
    expect(daysBetween('2024-01-01', '2024-01-01')).toBe(0);
    expect(daysBetween('2024-01-01', '2024-01-02')).toBe(1);
    expect(daysBetween('2024-01-01', '2024-01-08')).toBe(7);
    expect(daysBetween('2024-01-08', '2024-01-01')).toBe(-7);
  });
});

describe('isPastDate', () => {
  it('should return true for past dates', () => {
    const yesterday = new Date();
    yesterday.setDate(yesterday.getDate() - 1);
    expect(isPastDate(yesterday.toISOString().split('T')[0])).toBe(true);
  });

  it('should return false for future dates', () => {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    expect(isPastDate(tomorrow.toISOString().split('T')[0])).toBe(false);
  });

  it('should return false for today', () => {
    const today = new Date();
    const todayString = today.toISOString().split('T')[0];
    expect(isPastDate(todayString)).toBe(false);
  });
});