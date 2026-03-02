"""Çalışan yönetimi servisi"""
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
from src.database.models import Employee
from datetime import date, datetime


class EmployeeService:
    """Çalışan CRUD işlemleri"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def create_employee(self, first_name: str, last_name: str, 
                       gross_salary: float, email: str = None, 
                       phone: str = None, start_date: date = None,
                       overtime_rate: float = 150.0,
                       sgk_rate: float = 14.0,
                       unemployment_rate: float = 1.0,
                       income_tax_rate: float = 15.0,
                       stamp_tax_rate: float = 0.759,
                       child_count: int = 0) -> Employee:
        """Yeni çalışan ekle"""
        employee = Employee(
            first_name=first_name.strip(),
            last_name=last_name.strip(),
            email=email,
            phone=phone,
            start_date=start_date,
            gross_salary=float(gross_salary),
            overtime_rate=float(overtime_rate),
            sgk_rate=float(sgk_rate),
            unemployment_rate=float(unemployment_rate),
            income_tax_rate=float(income_tax_rate),
            stamp_tax_rate=float(stamp_tax_rate),
            child_count=int(child_count),
            is_active=True
        )
        self.db.add(employee)
        self.db.commit()
        return employee
    
    def get_employee(self, employee_id: int) -> Employee:
        """ID'ye göre çalışan getir"""
        return self.db.query(Employee).filter(Employee.id == employee_id).first()
    
    def get_all_employees(self, active_only: bool = True) -> list:
        """Tüm çalışanları getir"""
        query = self.db.query(Employee)
        if active_only:
            query = query.filter(Employee.is_active == True)
        return query.order_by(asc(Employee.first_name), asc(Employee.last_name)).all()
    
    def search_employees(self, search_text: str, active_only: bool = True) -> list:
        """Çalışan ara"""
        search = f"%{search_text}%".lower()
        query = self.db.query(Employee).filter(
            (Employee.first_name.ilike(search)) |
            (Employee.last_name.ilike(search)) |
            (Employee.email.ilike(search))
        )
        if active_only:
            query = query.filter(Employee.is_active == True)
        return query.all()
    
    def update_employee(self, employee_id: int, **kwargs) -> Employee:
        """Çalışan güncelle"""
        employee = self.get_employee(employee_id)
        if not employee:
            return None
        
        # Güvenli güncelleme - sadece izin verilen alanları güncelle
        allowed_fields = {
            'first_name', 'last_name', 'email', 'phone', 'start_date',
            'gross_salary', 'overtime_rate', 'sgk_rate', 'unemployment_rate',
            'income_tax_rate', 'stamp_tax_rate', 'child_count', 'is_active'
        }
        
        for key, value in kwargs.items():
            if key in allowed_fields:
                if key in ['first_name', 'last_name']:
                    value = str(value).strip()
                elif key in ['gross_salary', 'overtime_rate', 'sgk_rate', 
                            'unemployment_rate', 'income_tax_rate', 'stamp_tax_rate']:
                    value = float(value)
                elif key == 'child_count':
                    value = int(value)
                setattr(employee, key, value)
        
        employee.updated_at = datetime.now()
        self.db.commit()
        return employee
    
    def delete_employee(self, employee_id: int) -> bool:
        """Çalışanı komple sil (hard delete)"""
        employee = self.get_employee(employee_id)
        if not employee:
            return False
        self.db.delete(employee)
        self.db.commit()
        return True
    
    def get_active_employees_count(self) -> int:
        """Aktif çalışan sayısı"""
        return self.db.query(Employee).filter(Employee.is_active == True).count()
