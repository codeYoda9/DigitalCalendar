import { useState, useEffect, useCallback } from 'react';

/**
 * Custom hook for polling backend data with offline fallback
 * Polls generated/local data or backend data with quiet cached fallback.
 */
export function usePolledData(fetchFunction, pollInterval = 60000) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isOnline, setIsOnline] = useState(true);

  const fetchData = useCallback(async () => {
    try {
      const response = await fetchFunction();
      setData(response.data);
      setError(null);
      setIsOnline(true);
      // Save to localStorage for offline fallback
      localStorage.setItem(`cached_${fetchFunction.name}`, JSON.stringify(response.data));
    } catch (err) {
      // Try to restore from cache
      const cached = localStorage.getItem(`cached_${fetchFunction.name}`);
      if (cached) {
        setData(JSON.parse(cached));
        setError(null);
        setIsOnline(false);
      } else {
        setError(err.message);
        setIsOnline(false);
      }
    } finally {
      setLoading(false);
    }
  }, [fetchFunction]);

  // Initial fetch
  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Setup polling
  useEffect(() => {
    const interval = setInterval(fetchData, pollInterval);
    return () => clearInterval(interval);
  }, [fetchData, pollInterval]);

  return { data, loading, error, isOnline, refetch: fetchData };
}

export default usePolledData;
