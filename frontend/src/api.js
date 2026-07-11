export const fetchStatus = async () => {
  try {
    const res = await fetch("http://localhost:8000/api/status");
    return await res.json();
  } catch (e) {
    console.error("Failed to fetch status", e);
    return null;
  }
};

export const fetchSchedules = async () => {
  try {
    const res = await fetch("http://localhost:8000/api/schedule");
    return await res.json();
  } catch (e) {
    console.error("Failed to fetch schedules", e);
    return [];
  }
};

export const markMedicineTaken = async () => {
  try {
    const res = await fetch("http://localhost:8000/api/medicine-taken", {
      method: "POST"
    });
    return await res.json();
  } catch (e) {
    console.error("Failed to mark medicine taken", e);
    return null;
  }
};

export const updateSchedule = async (data) => {
  try {
    const res = await fetch("http://localhost:8000/api/schedule", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data)
    });
    return await res.json();
  } catch (e) {
    console.error("Failed to update schedule", e);
    return null;
  }
};
