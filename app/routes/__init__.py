from . import agents, conversations, files, users

def include_routers(app):
    app.include_router(agents.router)
    app.include_router(conversations.router)
    app.include_router(files.router)
    app.include_router(users.router)
    return app