import asyncio
import uvicorn
from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from sql_app import curd, models, schemas
from sql_app.database import async_session_local, engine, row2dict


app = FastAPI()
RESPONSE_STATUS_OK = 0
VALIDATE_STATUS_ERROR = 422


async def get_db():
    """
    manage DB session with every request, includes open and close.
    """
    async with async_session_local() as db:
        yield db


@app.get("/api/app/list")
async def get_app_list(page: int = 1, per_page: int = 10, app_name: str = '', desc: str = '', db: Session = Depends(get_db)):
    app_list, count = await curd.get_app_list(db=db, page=page, per_page=per_page, app_name=app_name, desc=desc)

    ans = []
    for app in app_list:
        row_dict = row2dict(app)
        row_filtered_dict = schemas.AppListOutput(**row_dict).model_dump()
        ans.append(row_filtered_dict)
    return {
        "status": RESPONSE_STATUS_OK,
        "msg": "ok",
        "data": {
            "count": count,
            "rows": ans,
        }
    }


@app.post("/api/app/create")
async def create_app(create_app_form: schemas.AppCreate, db: Session = Depends(get_db)):
    is_exist_app_name = await curd.check_app_name_duplicates(db=db, app_name=create_app_form.app_name)
    if is_exist_app_name:
        return {
            "status": VALIDATE_STATUS_ERROR,
            "msg": "",
            "errors": {"app_name": f"{create_app_form.app_name}已存在"},
            "data": None
        }

    await curd.create_app(create_app_form=create_app_form, db=db)
    return {
        "status": RESPONSE_STATUS_OK,
        "msg": "ok"
    }


@app.get("/api/app/{app_id}")
async def get_app_details(app_id: int, db: Session = Depends(get_db)):
    app_model = await curd.query_app_details(db=db, app_id=app_id)
    app_dict = row2dict(app_model)
    app_detail_filtered = schemas.AppDetails(**app_dict)
    return {
        "status": RESPONSE_STATUS_OK,
        "msg": "ok",
        "data": app_detail_filtered
    }


@app.post("/api/app/{app_id}/edit")
async def modify_app_detail(app_id: int, edit_app_form: schemas.AppCreate, db: Session = Depends(get_db)):
    await curd.update_app_details(db=db, app_id=app_id, edit_app_form=edit_app_form)
    return {
        "status": RESPONSE_STATUS_OK,
        "msg": "ok"
    }


@app.get("/api/env/list")
async def get_env_list(app_id: int, db: Session = Depends(get_db)):
    env_detail = await curd.get_app_env_list(db=db, app_id=app_id)
    data = []
    for line in env_detail:
        data.append({
            "id": line.id,
            "desc": line.desc,
            "url": f"{line.domain}{line.context}",
            "running": "1/1",
        })
    return {
        "status": RESPONSE_STATUS_OK,
        "msg": "ok",
        "data": data,
    }


@app.get("/api/agent/cmd")
async def start_docker():
    await websocket_manager.put_task("test_agent", {
        "operate": "compose",
        "image": "redis",
        "app_name": "redis",
    })


class ConnectionManager:
    def __init__(self):
        self.active_connections_queues: dict[str, asyncio.Queue] = {}

    def create_task_queue(self, agent_tag: str):
        self.active_connections_queues[agent_tag] = asyncio.Queue()

    async def get_task(self, agent_tag: str) -> dict:
        return await self.active_connections_queues[agent_tag].get()

    async def put_task(self, agent_tag: str, config: dict):
        await self.active_connections_queues[agent_tag].put(config)

    def disconnect(self, agent_tag: str):
        del self.active_connections_queues[agent_tag]


websocket_manager = ConnectionManager()


@app.websocket("/ws/docker")
async def docker_container_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        agent_tag = await websocket.receive_text()
        print(f"new connect from tag: {agent_tag}")
        websocket_manager.create_task_queue(agent_tag)

        while True:
            task = await websocket_manager.get_task(agent_tag)

            await websocket.send_json(task)
            result = await websocket.receive_json()
            print(f"task result: {result}")
    except WebSocketDisconnect:
        websocket_manager.disconnect(agent_tag)


@app.get("/api/build/list")
async def get_build_template_list(db: Session = Depends(get_db)):
    build_template_model_list = await curd.get_build_template_list(db=db)
    data = []
    for line in build_template_model_list:
        data.append(row2dict(line))
    return {
        "status": RESPONSE_STATUS_OK,
        "msg": "ok",
        "data": data,
    }

@app.post("/api/build/{template_id}/edit")
async def edit_build_template_list(content: schemas.BuildTemplate, template_id: int, db: Session = Depends(get_db)):
    await curd.edit_build_template(db=db, template_id=template_id, content=content.content)


async def main():
    async with engine.connect() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
        
    config = uvicorn.Config("main:app", port=8000, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == '__main__':
    asyncio.run(main())
