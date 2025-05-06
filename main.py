import traceback
from fastapi import FastAPI
from database import engine,Base
from Router import auth_router,vehicle_routes

Base.metadata.create_all(bind=engine)

def create_app()->FastAPI:
    """Factory function to create and configure the FastAPI app."""
    try:
        app=FastAPI(
            title="User Authentication & Management",
             version="1.0.0",
        )
        app.include_router(auth_router.user_route)
        app.include_router(vehicle_routes.vehicle_route)
        

        return app
        
    except:
        print(traceback.print_exc)

app=create_app()


if __name__=="__main__":
    import uvicorn
    uvicorn.run("main:app", port=8080, host="127.0.0.1", reload=True)
    
    
