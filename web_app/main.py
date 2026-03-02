"""
FastAPI Web Application - Muhasebe Sistemi
"""
from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
import sys
import os

# Proje kök dizinini ekle
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.db import init_db
from src.services.auth_service import AuthService
from src.services.admin_service import AdminService
import config
from src.utils.app_icon import get_app_icon_path

# FastAPI uygulaması
app = FastAPI(
    title="Muhasebe Sistemi",
    description="Web Tabanlı Muhasebe ve Finans Yönetim Sistemi",
    version="1.0.0"
)

# CORS middleware - Public URL için gerekli
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production'da specific domain kullanın
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Session middleware
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production"))

# Static files ve templates - Absolute paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# Veritabanını başlat
@app.on_event("startup")
async def startup_event():
    """Uygulama başlangıcında çalışır"""
    init_db()
    # Admin hesabı oluştur
    user = AuthService.authenticate("admin", "admin123")
    if not user:
        user, msg = AdminService.create_user(
            "admin", 
            "admin@ozkaya.com", 
            "admin123", 
            "Yönetici",
            role='admin'
        )
        if user:
            print("✓ Admin hesabı oluşturuldu: admin / admin123")


# Kullanıcı oturum kontrolü
def get_current_user(request: Request):
    """Oturumdaki kullanıcıyı al"""
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    
    from src.database.db import SessionLocal
    from src.database.models import User
    
    session = SessionLocal()
    try:
        user = session.query(User).filter(User.id == user_id).first()
        return user
    finally:
        session.close()


def require_auth(request: Request):
    """Oturum kontrolü - giriş yapmamışsa login'e yönlendir"""
    user = get_current_user(request)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_302_FOUND,
            headers={"Location": "/login"}
        )
    return user


# Routes
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Ana sayfa - Dashboard'a yönlendir"""
    user = get_current_user(request)
    if user:
        return RedirectResponse(url="/dashboard")
    return RedirectResponse(url="/login")


@app.get("/app-icon")
async def app_icon():
    """Uygulama ikon dosyasını döndür"""
    icon_path = get_app_icon_path()
    if not icon_path:
        raise HTTPException(status_code=404, detail="Icon bulunamadı")

    media_type = "image/x-icon" if icon_path.suffix.lower() == ".ico" else "image/png"
    return FileResponse(path=str(icon_path), media_type=media_type)


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """Tarayıcı favicon endpoint'i"""
    return await app_icon()


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Login sayfası"""
    return templates.TemplateResponse("login.html", {
        "request": request,
        "app_name": config.APP_NAME
    })


@app.post("/login")
async def login(request: Request):
    """Login işlemi"""
    form = await request.form()
    username = form.get("username")
    password = form.get("password")
    
    user = AuthService.authenticate(username, password)
    
    if user and user.is_active:
        request.session["user_id"] = user.id
        request.session["username"] = user.username
        return RedirectResponse(url="/dashboard", status_code=303)
    
    return templates.TemplateResponse("login.html", {
        "request": request,
        "error": "Kullanıcı adı veya şifre hatalı!",
        "app_name": config.APP_NAME
    })


@app.get("/logout")
async def logout(request: Request):
    """Logout işlemi"""
    request.session.clear()
    return RedirectResponse(url="/login")


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, user=Depends(require_auth)):
    """Dashboard sayfası"""
    from src.services.invoice_service import InvoiceService
    from src.services.bank_service import BankService
    from src.services.cari_service import CariService
    
    # İstatistikler
    stats = InvoiceService.get_invoice_statistics(user.id)
    banks = BankService.get_accounts(user.id)
    caris = CariService.get_caris(user.id)
    recent_invoices = InvoiceService.get_user_invoices(user.id)[:10]
    
    # Toplam banka bakiyesi
    total_balance = sum([acc.balance for acc in banks])
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": user,
        "stats": stats,
        "total_balance": total_balance,
        "total_banks": len(banks),
        "total_caris": len(caris),
        "recent_invoices": recent_invoices
    })


@app.get("/invoices", response_class=HTMLResponse)
async def invoices_page(request: Request, user=Depends(require_auth)):
    """Faturalar sayfası"""
    if not user.can_view_invoices:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "user": user,
            "message": "Bu sayfayı görüntüleme yetkiniz yok!"
        })
    
    from src.services.invoice_service import InvoiceService
    invoices = InvoiceService.get_user_invoices(user.id)
    
    return templates.TemplateResponse("invoices.html", {
        "request": request,
        "user": user,
        "invoices": invoices
    })


@app.get("/caris", response_class=HTMLResponse)
async def caris_page(request: Request, user=Depends(require_auth)):
    """Cari hesaplar sayfası"""
    if not user.can_view_caris:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "user": user,
            "message": "Bu sayfayı görüntüleme yetkiniz yok!"
        })
    
    from src.services.cari_service import CariService
    caris = CariService.get_caris(user.id)
    
    return templates.TemplateResponse("caris.html", {
        "request": request,
        "user": user,
        "caris": caris
    })


@app.get("/banks", response_class=HTMLResponse)
async def banks_page(request: Request, user=Depends(require_auth)):
    """Banka hesapları sayfası"""
    if not user.can_view_banks:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "user": user,
            "message": "Bu sayfayı görüntüleme yetkiniz yok!"
        })
    
    from src.services.bank_service import BankService
    banks = BankService.get_accounts(user.id)
    
    return templates.TemplateResponse("banks.html", {
        "request": request,
        "user": user,
        "banks": banks
    })


@app.get("/reports", response_class=HTMLResponse)
async def reports_page(request: Request, user=Depends(require_auth)):
    """Raporlar sayfası"""
    if not user.can_view_reports:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "user": user,
            "message": "Bu sayfayı görüntüleme yetkiniz yok!"
        })
    
    return templates.TemplateResponse("reports.html", {
        "request": request,
        "user": user
    })


@app.get("/admin/users", response_class=HTMLResponse)
async def admin_users_page(request: Request, user=Depends(require_auth)):
    """Kullanıcı yönetimi sayfası - Sadece admin"""
    if user.role != 'admin':
        return templates.TemplateResponse("error.html", {
            "request": request,
            "user": user,
            "message": "Bu sayfaya erişim yetkiniz yok!"
        })
    
    users = AdminService.get_all_users()
    
    return templates.TemplateResponse("admin_users.html", {
        "request": request,
        "user": user,
        "users": users
    })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
