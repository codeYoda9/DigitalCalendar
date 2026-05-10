import React, { useState, useEffect } from 'react';
import { format } from 'date-fns';
import { calendarApi } from '../api';
import usePolledData from '../hooks/usePolledData';

function CalendarPanel() {
  const today = new Date();
  const { data: eventsData, isOnline, error } = usePolledData(
    () => calendarApi.getEvents(format(today, 'yyyy-MM-dd')),
    10000 // Poll every 10 seconds
  );

  const [events, setEvents] = useState([]);

  useEffect(() => {
    if (eventsData?.events) {
      setEvents(eventsData.events);
    }
  }, [eventsData]);

  const formatTime = (dateString) => {
    try {
      const date = new Date(dateString);
      return format(date, 'HH:mm');
    } catch {
      return 'N/A';
    }
  };

  return (
    <div className="panel calendar-panel">
      <h2 className="panel-header">📅 Today</h2>

      {!isOnline && (
        <div className="offline-banner">
          ⚠️ Offline: Showing cached data
        </div>
      )}

      {error && (
        <div className="error-message">
          Error loading calendar: {error}
        </div>
      )}

      <div className="panel-content">
        <div className="calendar-date">
          {format(today, 'd')}
        </div>
        <div className="calendar-day">
          {format(today, 'EEEE')}
        </div>

        {events.length === 0 ? (
          <div className="empty-message">
            No events today
          </div>
        ) : (
          <ul className="events-list">
            {events.map((event) => (
              <li key={event.id} className="event-item">
                <div className="event-time">
                  {formatTime(event.start)}
                </div>
                <div className="event-title">
                  {event.title}
                </div>
                {event.description && (
                  <div className="event-description">
                    {event.description}
                  </div>
                )}
                {event.location && (
                  <div className="event-description">
                    📍 {event.location}
                  </div>
                )}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

export default CalendarPanel;
