from server import create_app
from core.config import settings
import uvicorn

app = create_app()

if __name__ == "__main__":

    uvicorn.run(app='main:app', host=settings.SERVER_HOST, port=settings.SERVER_PORT, reload=True, debug=True)