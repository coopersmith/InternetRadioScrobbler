# Setting Up Radio FIP Hip-Hop Scrobbler

Radio FIP Hip-Hop loads track data dynamically via JavaScript, so we need to find the actual API endpoint that the website uses.

## Finding the API Endpoint

1. **Open the Radio FIP Hip-Hop page:**
   - Go to https://www.radiofrance.fr/fip/radio-hip-hop

2. **Open Developer Tools:**
   - Press `F12` (or right-click → Inspect)
   - Go to the **Network** tab

3. **Filter API requests:**
   - Click the filter icon and select **XHR** or **Fetch**
   - Refresh the page (F5) to capture network requests

4. **Find the track data endpoint:**
   - Look for requests that return JSON data containing track information
   - The response should contain fields like:
     - `firstLine` / `secondLine` (artist / title)
     - `artist` / `title`
     - `now` / `current` / `live`
   - Copy the **Request URL**

5. **Update the fetcher:**
   - Open `src/stations/fiphiphop.py`
   - Add the discovered URL to the `API_URLS` list in the `FIPHipHopFetcher` class
   - Example:
     ```python
     API_URLS = [
         "https://api.radiofrance.fr/v2/stations/fip-hip-hop/now",
     ]
     ```

6. **Test it:**
   ```bash
   python main.py --config config/stations.yaml
   ```

## Alternative: Using a Headless Browser

If the API endpoint requires authentication or is difficult to find, we can use a headless browser (Playwright or Selenium) to render the JavaScript and extract track data. This is more complex but guaranteed to work.

Let me know if you'd like help setting up a headless browser solution!
