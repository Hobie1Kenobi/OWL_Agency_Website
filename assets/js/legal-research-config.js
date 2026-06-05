/**
 * OWL Legal Research Demo — API configuration
 * After deploying to Render, set LEGAL_RESEARCH_API to your service URL.
 */
window.OWL_LEGAL_CONFIG = {
  API_BASE: window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:8000'
    : 'https://owl-agency-website.onrender.com',
  DEMO_CASE_ID: 'carpenter_v_us',
};
