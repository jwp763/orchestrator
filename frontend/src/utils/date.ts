/**
 * Formats a date string to a human-readable format
 * @param dateString - ISO date string
 * @returns Formatted date string
 */
export const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  });
};

/**
 * Calculates the number of days between two dates
 * @param startDate - Start date string
 * @param endDate - End date string
 * @returns Number of days between dates
 */
export const daysBetween = (startDate: string, endDate: string): number => {
  const start = new Date(startDate);
  const end = new Date(endDate);
  const timeDiff = end.getTime() - start.getTime();
  return Math.ceil(timeDiff / (1000 * 3600 * 24));
};

/**
 * Checks if a date is in the past
 * @param dateString - Date string to check
 * @returns True if date is in the past
 */
export const isPastDate = (dateString: string): boolean => {
  const date = new Date(dateString + 'T00:00:00'); // Force local time interpretation
  const today = new Date();
  
  // Set both dates to start of day for accurate comparison
  date.setHours(0, 0, 0, 0);
  today.setHours(0, 0, 0, 0);
  
  return date.getTime() < today.getTime();
};