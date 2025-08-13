"""
AI Service - OpenAI Integration
Handles all AI-powered customer interactions
"""

import os
import json
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import openai
from elevenlabs import generate, set_api_key, Voice, VoiceSettings

from models.customer import Customer, Order

class AIService:
    def __init__(self):
        # Initialize OpenAI
        openai.api_key = os.getenv('OPENAI_API_KEY')
        
        # Initialize ElevenLabs
        elevenlabs_key = os.getenv('ELEVENLABS_API_KEY')
        if elevenlabs_key:
            set_api_key(elevenlabs_key)
        
        # AI Configuration
        self.model = "gpt-4"
        self.max_tokens = 1000
        self.temperature = 0.7
        
        # Voice settings
        self.voice_settings = VoiceSettings(
            stability=0.75,
            similarity_boost=0.75,
            style=0.5,
            use_speaker_boost=True
        )

    async def process_message(self, message: str, customer: Customer, recent_orders: List[Order], session_id: Optional[str] = None) -> Dict[str, Any]:
        """Process customer message with AI and return response"""
        try:
            # Build context for AI
            context = self._build_customer_context(customer, recent_orders)
            
            # Create system prompt
            system_prompt = self._create_system_prompt(context)
            
            # Process with OpenAI
            response = await self._get_ai_response(system_prompt, message)
            
            # Determine if action is needed
            action = self._extract_action(response, message)
            
            return {
                "text": response,
                "action": action,
                "session_id": session_id,
                "timestamp": datetime.now().isoformat(),
                "confidence": 0.95  # Could implement actual confidence scoring
            }
        except Exception as e:
            print(f"Error processing message: {e}")
            return {
                "text": "I apologize, but I'm experiencing technical difficulties. Please try again or contact our support team.",
                "action": None,
                "session_id": session_id,
                "timestamp": datetime.now().isoformat(),
                "confidence": 0.0
            }

    async def generate_voice(self, text: str, voice_id: str = "professional_female") -> str:
        """Generate voice audio from text"""
        try:
            # Map voice IDs to ElevenLabs voices
            voice_map = {
                "professional_female": "21m00Tcm4TlvDq8ikWAM",  # Rachel
                "friendly_male": "29vD33N1CtxCmqQRPOHJ",      # Drew
                "warm_female": "pNInz6obpgDQGcFmaJgB"         # Adam (actually female-sounding)
            }
            
            selected_voice = voice_map.get(voice_id, voice_map["professional_female"])
            
            audio = generate(
                text=text,
                voice=Voice(
                    voice_id=selected_voice,
                    settings=self.voice_settings
                )
            )
            
            # Save audio file and return URL
            filename = f"audio_{datetime.now().timestamp()}.mp3"
            audio_path = f"static/audio/{filename}"
            
            # Ensure directory exists
            os.makedirs("static/audio", exist_ok=True)
            
            with open(audio_path, "wb") as f:
                f.write(audio)
            
            return f"/audio/{filename}"
        except Exception as e:
            print(f"Error generating voice: {e}")
            return ""

    def _build_customer_context(self, customer: Customer, recent_orders: List[Order]) -> Dict[str, Any]:
        """Build comprehensive customer context for AI"""
        context = {
            "customer_info": {
                "name": customer.company_name,
                "email": customer.email,
                "customer_since": customer.registration_date,
                "total_spent": customer.total_spent,
                "last_order": customer.last_order_date,
                "status": customer.status
            },
            "recent_orders": [],
            "purchase_patterns": self._analyze_purchase_patterns(recent_orders),
            "preferences": self._extract_preferences(recent_orders)
        }
        
        # Add recent order details
        for order in recent_orders[:5]:  # Last 5 orders
            context["recent_orders"].append({
                "id": order.id,
                "date": order.date,
                "products": order.products,
                "total": order.total_amount,
                "status": order.status
            })
        
        return context

    def _create_system_prompt(self, context: Dict[str, Any]) -> str:
        """Create comprehensive system prompt for AI"""
        return f"""You are an expert customer service representative for an electronics accessories company. 

CUSTOMER CONTEXT:
- Company: {context['customer_info']['name']}
- Customer since: {context['customer_info']['customer_since']}
- Total spent: ${context['customer_info']['total_spent']:,.2f}
- Last order: {context['customer_info']['last_order']}
- Recent orders: {len(context['recent_orders'])} orders

RECENT PURCHASE HISTORY:
{json.dumps(context['recent_orders'], indent=2)}

CUSTOMER PREFERENCES:
{json.dumps(context['preferences'], indent=2)}

YOUR ROLE:
1. Provide expert advice on electronics accessories (phone cases, screen protectors, chargers, tablets, etc.)
2. Help with order history, tracking, and reordering
3. Answer product compatibility questions
4. Process new orders when requested
5. Provide personalized recommendations based on purchase history

GUIDELINES:
- Be friendly, professional, and knowledgeable
- Reference their purchase history when relevant
- Offer specific product recommendations
- If they want to place an order, gather: product SKU, quantity, any special requirements
- For tracking questions, provide order status and estimated delivery
- Always prioritize customer satisfaction

IMPORTANT: If the customer wants to place an order, respond with action_type: "create_order" and include the order details.
If they want tracking info, respond with action_type: "track_order" and the order ID.
For general questions, use action_type: "information".

Respond naturally and conversationally. You have access to their complete history and can reference specific past orders."""

    async def _get_ai_response(self, system_prompt: str, user_message: str) -> str:
        """Get response from OpenAI"""
        try:
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error getting AI response: {e}")
            return "I apologize, but I'm having trouble processing your request right now. Please try again."

    def _extract_action(self, ai_response: str, user_message: str) -> Optional[Dict[str, Any]]:
        """Extract actionable items from AI response"""
        user_lower = user_message.lower()
        response_lower = ai_response.lower()
        
        # Order-related actions
        if any(phrase in user_lower for phrase in ["place order", "buy", "purchase", "order", "reorder"]):
            return {"type": "create_order", "priority": "high"}
        
        # Tracking actions
        if any(phrase in user_lower for phrase in ["track", "tracking", "where is", "status", "delivery"]):
            return {"type": "track_order", "priority": "medium"}
        
        # Product inquiry
        if any(phrase in user_lower for phrase in ["compatible", "fits", "works with", "recommend"]):
            return {"type": "product_inquiry", "priority": "medium"}
        
        # General information
        return {"type": "information", "priority": "low"}

    def _analyze_purchase_patterns(self, orders: List[Order]) -> Dict[str, Any]:
        """Analyze customer purchase patterns"""
        if not orders:
            return {}
        
        # Calculate average order frequency
        if len(orders) > 1:
            dates = [datetime.fromisoformat(order.date.replace('Z', '+00:00')) for order in orders]
            dates.sort()
            intervals = [(dates[i] - dates[i-1]).days for i in range(1, len(dates))]
            avg_interval = sum(intervals) / len(intervals) if intervals else 0
        else:
            avg_interval = 0
        
        # Calculate average order value
        avg_order_value = sum(order.total_amount for order in orders) / len(orders)
        
        # Find most frequent order size
        order_sizes = [len(order.products) for order in orders]
        most_common_size = max(set(order_sizes), key=order_sizes.count) if order_sizes else 0
        
        return {
            "avg_order_interval_days": avg_interval,
            "avg_order_value": avg_order_value,
            "most_common_order_size": most_common_size,
            "total_orders": len(orders),
            "ordering_frequency": "regular" if avg_interval < 60 else "occasional"
        }

    def _extract_preferences(self, orders: List[Order]) -> Dict[str, Any]:
        """Extract customer preferences from order history"""
        if not orders:
            return {}
        
        # Count product categories/types
        product_counts = {}
        for order in orders:
            for product in order.products:
                product_counts[product] = product_counts.get(product, 0) + 1
        
        # Get top products
        top_products = sorted(product_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Analyze spending patterns
        high_value_orders = [o for o in orders if o.total_amount > 100]
        prefers_bulk = len([o for o in orders if len(o.products) > 3]) > len(orders) / 2
        
        return {
            "top_products": top_products,
            "prefers_high_value": len(high_value_orders) > len(orders) / 3,
            "prefers_bulk_orders": prefers_bulk,
            "brand_loyalty": len(set(product_counts.keys())) < 10  # Few unique products = loyal
        }