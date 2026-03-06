#                   neolink_project/
#              ├── main.py           Весь код на Python (Backend)
#              ├── database.db       Файл базы данных (появится позже)
#              ├── templates/        Папка для HTML-страниц
#              │   ├── index.html    Главная страница
#              │   └── base.html     Общий шаблон (шапка и подвал)
#              └── static/           Папка для картинок и стилей
#                  └── css/

from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy import create_engine, Column, Integer, String, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# --- 1. НАСТРОЙКА БАЗЫ ДАННЫХ ---
SQLALCHEMY_DATABASE_URL = "sqlite:///./database.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Модель тарифа
class Tariff(Base):
    __tablename__ = "tariffs"
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String)  # "физ" или "юр"
    name = Column(String)
    speed = Column(String)
    price = Column(Integer)
    features = Column(JSON)

# Модель заявки
class Lead(Base):
    __tablename__ = "leads"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    phone = Column(String)
    address = Column(String)

# Создание таблиц
Base.metadata.create_all(bind=engine)

# --- 2. НАСТРОЙКА ПРИЛОЖЕНИЯ ---
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Автоматическое наполнение базы данными из твоего PDF
def seed_data():
    db = SessionLocal()
    if db.query(Tariff).count() == 0:
        # Для физ лиц (NEOlink) [cite: 1, 5]
        db.add(Tariff(
            category="физ",
            name="СТАРТ", # [cite: 6]
            speed="100 мбит/сек", #
            price=4990, #
            features=[
                "Максимальное качество связи",#[cite: 8]
                "Высший стандарт подключения", # [cite: 8]
                "Качество без компромиссов", # [cite: 8]
                "Стабильность на высшем уровне", # [cite: 8]
                "Скорость и надежность 24/7" # [cite: 8]
            ]
        ))
        # Для юр лиц (NEO) [cite: 25, 26]
        db.add(Tariff(
            category="юр",
            name="БИЗНЕС СТАНДАРТ",
            speed="200 мбит/сек",
            price=15000,
            features=[
                "Высокоскоростной интернет для бизнеса", # [cite: 47]
                "Индивидуальные решения для корпоративных клиентов", # [cite: 48]
                "Надежное подключение с круглосуточной поддержкой" # [cite: 49]
            ]
        ))
        db.commit()
    db.close()

seed_data()

# --- 3. МАРШРУТЫ (ROUTES) ---

# Главная страница (Физические лица / NEOlink)
@app.get("/")
async def read_root(request: Request):
    db = SessionLocal()
    items = db.query(Tariff).filter(Tariff.category == "физ").all()
    db.close()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "title": "NEOlink — Комфортный интернет для дома",
        "tariffs": items
    })

# Страница для бизнеса (Юридические лица / NEO)
@app.get("/business")
async def read_business(request: Request):
    db = SessionLocal()
    items = db.query(Tariff).filter(Tariff.category == "юр").all()
    db.close()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "title": "NEO — Интернет для бизнеса",
        "tariffs": items
    })

# Прием заявок из формы
@app.post("/send_request")
async def handle_form(
    name: str = Form(...),
    phone: str = Form(...),
    address: str = Form(...)
):
    db = SessionLocal()
    new_lead = Lead(name=name, phone=phone, address=address)
    db.add(new_lead)
    db.commit()
    db.close()
    # После отправки перенаправляем на главную с благодарностью
    return RedirectResponse(url="/", status_code=303)

# Админ-панель для просмотра лидов
@app.get("/admin/leads")
async def view_leads(request: Request):
    db = SessionLocal()
    all_leads = db.query(Lead).order_by(Lead.id.desc()).all()
    db.close()
    return templates.TemplateResponse("admin.html", {
        "request": request,
        "leads": all_leads
    })