# Transport Accuracy

This is an API and frontend to show the average delays and percentage of on time trains and metros. The search function uses Mobility Database data to search feeds, which may not be 100% accurate. It then extracts GTFS realtime delay data and compiles it into readable stats. This is sent to an AI (qwen3/32b at the moment) which writes a short analysis. To prevent AI overuse, responses are cached for 30 seconds.

![Preview](/static/preview.png)

## How to use
The repository is divided into two directories, `backend/` and `frontend/`. They both have their own modules and setup.

### Backend
A Python app with FastAPI. 

1. First, make sure you have Python installed. Then install the requirements; `cd backend && pip install -r requirements.txt`
2. After this, create an .env file (`touch .env`) and put the following contents in it:
    ```.env
    REFRESH_TOKEN=YOURTOKEN
    AI_API_KEY=YOURKEY
    SEARCH_API_KEY=YOURKEY
    ```
  Replace this with your keys. The `REFRESH_TOKEN` you obtain from [Mobility Database's API](https://mobilitydatabase.org/). The AI API key you can use with your provider of choice, follow their documentation. I went with Hack Club AI which is available for all teens under eighteen. The Search API key is optional, but this is an API key for Brave Search. I went with Hack Club Search for this one. Be sure to comment out the search context part in `main.py` if you don't want to give the AI extra context.
3. Now run `fastapi dev` for development or `fastapi run` for prod! 

If you are intending on hosting this somewhere (which is fine by me), be sure to change the CORS in `main.py`

### Frontend
A Svelte and TypeScript app.

1. First, make sure you have Node.js and npm installed. Then install the requirements; `cd frontend && npm i`. Be sure to do this in a different terminal window than backend and please ensure backend is running!
2. After this, create an .env file (`touch .env`) and put the following contents in it:
  ```.env
  VITE_API_URL=http://localhost:8000
  ```
  Change this URL if you are putting your API on a server other than localhost.
3. Now run `npm run dev` for development. For production, refer to your hosting provider's instructions or Svelte's documentation.
