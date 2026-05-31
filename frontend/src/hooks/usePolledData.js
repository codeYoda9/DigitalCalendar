import { useState, useEffect, useCallback } from 'react';

/**
 * Custom hook for polling backend data with offline fallback
 * Polls generated/local data or backend data with quiet cached fallback.
 */
export function usePolledData(fetchFunction, pollInterval = 60000, cacheKey = null) {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const storageKey = `cached_${cacheKey || fetchFunction.name || 'polledData'}`;

  const fetchData = useCallback(async () => {
    try {
      const response = await fetchFunction();
      setData(response.data);
      setError(null);
      localStorage.setItem(storageKey, JSON.stringify(response.data));
    } catch (err) {
      const cached = localStorage.getItem(storageKey);
      if (cached) {
        setData(JSON.parse(cached));
        setError(null);
      } else {
        setError(err.message);
      }
    }
  }, [fetchFunction, storageKey]);

  // Initial fetch
  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Setup polling
  useEffect(() => {
    const interval = setInterval(fetchData, pollInterval);
    return () => clearInterval(interval);
  }, [fetchData, pollInterval]);

  return { data, error, refetch: fetchData };
}

export default usePolledData;
