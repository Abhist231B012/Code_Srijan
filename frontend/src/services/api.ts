const BASE_URL = '/api/v1';

export const apiService = {
  // ── Authenticated predict (requires JWT + DB) ──────────────────────────────
  async predict(data: any) {
    const response = await fetch(`${BASE_URL}/predict`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      const errData = await response.json().catch(() => ({}));
      throw new Error(errData.detail || 'Failed to score applicant');
    }
    return response.json();
  },

  // ── Guest predict (no auth, no DB — ML model only) ─────────────────────────
  async predictGuest(data: any) {
    const response = await fetch(`${BASE_URL}/predict/guest`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      const errData = await response.json().catch(() => ({}));
      const detail = errData.detail;
      if (Array.isArray(detail)) {
        throw new Error(detail.map((e: any) => e.msg).join(', '));
      }
      throw new Error(typeof detail === 'string' ? detail : 'Failed to score applicant');
    }
    return response.json();
  },

  async explain(data: any) {
    const response = await fetch(`${BASE_URL}/explain`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      const errData = await response.json().catch(() => ({}));
      throw new Error(errData.detail || 'Failed to fetch explanation');
    }
    return response.json();
  },

  async health() {
    const response = await fetch(`${BASE_URL}/health`);
    return response.json();
  },
};
