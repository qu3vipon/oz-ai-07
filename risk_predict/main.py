from fastapi import FastAPI

from user.router import router as user_router
# from prediction.router import router as prediction_router


app = FastAPI(title="건강 예측 API")
app.include_router(user_router)
# app.include_router(prediction_router)
