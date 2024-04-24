from pydantic import BaseModel


class AppListOutput(BaseModel):
    id: int
    app_name: str
    app_type: str
    desc: str = ''

    class Config:
        from_attributes = True


class AppBase(BaseModel):
    app_name: str
    app_type: str
    output: str
    git_url: str
    desc: str = ''


class AppCreate(AppBase):
    pass


class AppDetails(AppBase):
    pass


class BuildTemplate(BaseModel):
    content: str
