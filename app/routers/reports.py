from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from app.database import get_db
from app.models import MonthlyReport, Sale, Clothing, InventoryLog, User
from app.schemas import MonthlyReportResponse
from app.auth import get_current_user, require_role
from datetime import datetime, date
from decimal import Decimal

router = APIRouter()

@router.get("/monthly", response_model=List[MonthlyReportResponse])
async def get_monthly_reports(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    reports = db.query(MonthlyReport).order_by(MonthlyReport.year.desc(), MonthlyReport.month.desc()).all()
    return reports
@router.post("/generate-monthly/{year}/{month}")
async def generate_monthly_report(
        year: int,
        month: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(require_role(["admin", "manager"]))
):
    # Check if report already exists
    existing_report = db.query(MonthlyReport).filter(
        MonthlyReport.year == year,
        MonthlyReport.month == month
    ).first()

    # Calculate total items sold in the month
    total_items_sold = db.query(func.sum(Sale.items_sold)).filter(
        extract('year', Sale.sold_at) == year,
        extract('month', Sale.sold_at) == month
    ).scalar() or 0

    # Calculate total revenue
    total_revenue = db.query(func.sum(Sale.total_amount)).filter(
        extract('year', Sale.sold_at) == year,
        extract('month', Sale.sold_at) == month
    ).scalar() or 0

    # Calculate total profit (simplified calculation)
    total_profit = total_revenue * Decimal('0.3')

    # Calculate profit margin
    profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0

    # Check if suspicious
    is_suspicious = profit_margin < 15 or profit_margin > 50

    # If report exists, update it; otherwise create new
    if existing_report:
        existing_report.total_items_sold = total_items_sold
        existing_report.total_revenue = total_revenue
        existing_report.total_profit = total_profit
        existing_report.profit_margin = profit_margin
        existing_report.is_suspicious = is_suspicious
        db.commit()
        db.refresh(existing_report)
        return existing_report
    else:
        new_report = MonthlyReport(
            month=month,
            year=year,
            total_items_sold=total_items_sold,
            total_revenue=total_revenue,
            total_profit=total_profit,
            profit_margin=profit_margin,
            is_suspicious=is_suspicious
        )
        db.add(new_report)
        db.commit()
        db.refresh(new_report)
        return new_report

@router.get("/dashboard-stats")
async def get_dashboard_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    today = date.today()
    
    # Today's sales
    today_sales = db.query(func.count(Sale.id)).filter(
        func.date(Sale.sold_at) == today
    ).scalar() or 0
    
    # Low stock items
    low_stock_count = db.query(func.count(Clothing.id)).filter(
        Clothing.quantity <= Clothing.minimum_quantity
    ).scalar() or 0
    
    # Total clothing items
    total_clothing = db.query(func.count(Clothing.id)).scalar() or 0
    
    # Recent sales (last 7 days)
    from datetime import timedelta
    week_ago = today - timedelta(days=7)
    recent_sales = db.query(func.count(Sale.id)).filter(
        Sale.sold_at >= week_ago
    ).scalar() or 0
    
    return {
        "today_sales": today_sales,
        "low_stock_count": low_stock_count,
        "total_clothing": total_clothing,
        "recent_sales": recent_sales
    }

@router.get("/sales-analytics")
async def get_sales_analytics(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Get sales data by clothing type
    sales_by_type = db.query(
        Clothing.type,
        func.sum(InventoryLog.quantity_changed * -1).label('total_sold')
    ).join(
        InventoryLog, Clothing.id == InventoryLog.clothing_id
    ).filter(
        InventoryLog.change_type == 'sale'
    ).group_by(Clothing.type).all()
    
    return [{"type": item[0], "sold": int(item[1] or 0)} for item in sales_by_type]

@router.get("/inventory-analytics")
async def get_inventory_analytics(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Get inventory levels by clothing type
    inventory_by_type = db.query(
        Clothing.type,
        func.sum(Clothing.quantity).label('total_quantity')
    ).group_by(Clothing.type).all()
    
    return [{"type": item[0], "quantity": int(item[1] or 0)} for item in inventory_by_type]
