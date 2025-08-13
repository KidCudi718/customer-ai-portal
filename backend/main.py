#!/usr/bin/env python3
"""
Customer AI Portal - Backend API
FastAPI server with MCP Google Sheets integration
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import json
import asyncio
from datetime import datetime, timedelta
import openai
from elevenlabs import generate, set_api_key

# Import our custom modules
from services.sheets_service import SheetsService
from services.ai_service import AIService
from services.auth_service import AuthService
from models.customer import Customer, Order, Product, ChatMessage

# Initialize FastAPI app
app = FastAPI(
    title="Customer AI Portal API",
    description="AI-Powered Customer Service Portal for Electronics Retailers",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://your-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Initialize services
sheets_service = SheetsService()
ai_service = AIService()
auth_service = AuthService()

# Pydantic models for API
class CustomerLoginRequest(BaseModel):
    email: str
    company_id: str

class ChatRequest(BaseModel):
    message: str
    customer_id: str
    session_id: Optional[str] = None

class OrderRequest(BaseModel):
    customer_id: str
    products: List[Dict[str, Any]]
    notes: Optional[str] = None

class VoiceRequest(BaseModel):
    text: str
    voice_id: Optional[str] = "professional_female"

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Authentication endpoints
@app.post("/auth/login")
async def customer_login(request: CustomerLoginRequest):
    """Authenticate customer and return access token"""
    try:
        customer = await sheets_service.get_customer_by_email(request.email, request.company_id)
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        token = auth_service.create_access_token(customer.id)
        return {
            "access_token": token,
            "customer": customer.dict(),
            "message": "Login successful"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Customer data endpoints
@app.get("/customers/{customer_id}")
async def get_customer(customer_id: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get customer profile and summary"""
    try:
        auth_service.verify_token(credentials.credentials)
        customer = await sheets_service.get_customer(customer_id)
        return customer
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/customers/{customer_id}/orders")
async def get_customer_orders(customer_id: str, limit: int = 50, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get customer order history"""
    try:
        auth_service.verify_token(credentials.credentials)
        orders = await sheets_service.get_customer_orders(customer_id, limit)
        return {"orders": orders, "total": len(orders)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/customers/{customer_id}/analytics")
async def get_customer_analytics(customer_id: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get customer purchase analytics and insights"""
    try:
        auth_service.verify_token(credentials.credentials)
        analytics = await sheets_service.get_customer_analytics(customer_id)
        return analytics
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# AI Chat endpoints
@app.post("/chat")
async def chat_with_ai(request: ChatRequest, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Process customer chat message with AI"""
    try:
        auth_service.verify_token(credentials.credentials)
        
        # Get customer context
        customer = await sheets_service.get_customer(request.customer_id)
        recent_orders = await sheets_service.get_customer_orders(request.customer_id, 10)
        
        # Process with AI
        response = await ai_service.process_message(
            message=request.message,
            customer=customer,
            recent_orders=recent_orders,
            session_id=request.session_id
        )
        
        # Log interaction
        await sheets_service.log_interaction(
            customer_id=request.customer_id,
            query=request.message,
            response=response["text"],
            session_id=request.session_id
        )
        
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/chat/voice")
async def generate_voice_response(request: VoiceRequest, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Generate voice audio from text response"""
    try:
        auth_service.verify_token(credentials.credentials)
        audio_url = await ai_service.generate_voice(request.text, request.voice_id)
        return {"audio_url": audio_url}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Product and inventory endpoints
@app.get("/products")
async def get_products(category: Optional[str] = None, search: Optional[str] = None, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get product catalog with optional filtering"""
    try:
        auth_service.verify_token(credentials.credentials)
        products = await sheets_service.get_products(category, search)
        return {"products": products}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/products/{sku}/compatibility")
async def check_product_compatibility(sku: str, device_model: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Check if product is compatible with customer's device"""
    try:
        auth_service.verify_token(credentials.credentials)
        compatibility = await sheets_service.check_compatibility(sku, device_model)
        return compatibility
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Order management endpoints
@app.post("/orders")
async def create_order(request: OrderRequest, background_tasks: BackgroundTasks, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Create new customer order"""
    try:
        auth_service.verify_token(credentials.credentials)
        
        order = await sheets_service.create_order(
            customer_id=request.customer_id,
            products=request.products,
            notes=request.notes
        )
        
        # Background task: Send confirmation email
        background_tasks.add_task(send_order_confirmation, order)
        
        return {"order": order, "message": "Order created successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/orders/{order_id}/tracking")
async def get_order_tracking(order_id: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get order tracking information"""
    try:
        auth_service.verify_token(credentials.credentials)
        tracking = await sheets_service.get_order_tracking(order_id)
        return tracking
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Analytics and reporting endpoints
@app.get("/analytics/dashboard")
async def get_dashboard_analytics(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get business dashboard analytics"""
    try:
        auth_service.verify_token(credentials.credentials)
        analytics = await sheets_service.get_dashboard_analytics()
        return analytics
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Background tasks
async def send_order_confirmation(order: Dict[str, Any]):
    """Send order confirmation email"""
    # Implementation for email sending
    pass

# WebSocket for real-time chat
@app.websocket("/ws/chat/{customer_id}")
async def websocket_chat(websocket, customer_id: str):
    """WebSocket endpoint for real-time chat"""
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Process message with AI
            response = await ai_service.process_message(
                message=message_data["message"],
                customer_id=customer_id
            )
            
            await websocket.send_text(json.dumps(response))
    except Exception as e:
        await websocket.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)