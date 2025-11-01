# Pokémon Battle Predictor Frontend

A web interface for predicting Pokémon battle outcomes using machine learning.

## Setup

1. **Start the API server first** (see `algorithm/README.md`):
   ```bash
   cd algorithm
   python3 api.py
   ```
   The API should be running at `http://localhost:5000`

2. **Serve the frontend**:
   
   **Option A: Using Python HTTP Server (Recommended)**
   ```bash
   cd frontend
   python3 -m http.server 8000
   ```
   Then open `http://localhost:8000` in your browser.

   **Option B: Direct File**
   Simply open `index.html` in your browser. However, if you're using a different API URL, you'll need to configure it using the API URL input field in the header.

## API URL Configuration

If your API is running on a different URL or port:

1. **Using the UI**: Enter your API URL in the input field at the top of the page and click "Update"
2. **Using URL parameter**: Add `?api_url=YOUR_API_URL` to the page URL
   - Example: `http://localhost:8000/?api_url=http://localhost:5000/api`

The API URL is saved in localStorage and will persist between page reloads.

## Troubleshooting

**Issue: "Failed to load Pokemon list"**

1. Make sure the API server is running at `http://localhost:5000`
2. Check the browser console (F12) for detailed error messages
3. Verify the API URL in the header matches where your API is running
4. Test the API directly by visiting `http://localhost:5000/api/pokemon` in your browser

**Issue: CORS errors in console**

- Make sure `flask-cors` is installed: `pip3 install flask-cors`
- Check that the API server has CORS enabled (it should be by default)

