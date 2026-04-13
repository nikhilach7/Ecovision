from datetime import datetime, timezone

from app.services.analytics import day_bounds


class NLPService:
    async def answer(self, db, query: str) -> tuple[str, str]:
        text = query.lower().strip()
        start, end = day_bounds(datetime.now(timezone.utc))

        if "plastic" in text and ("today" in text or "how much" in text):
            count = await db.waste_predictions.count_documents(
                {"waste_type": "plastic", "created_at": {"$gte": start, "$lt": end}}
            )
            return f"Plastic waste items detected today: {count}.", "plastic_today"

        if "metal" in text and ("today" in text or "how much" in text):
            count = await db.waste_predictions.count_documents(
                {"waste_type": "metal", "created_at": {"$gte": start, "$lt": end}}
            )
            return f"Metal waste items detected today: {count}.", "metal_today"

        if "organic" in text and ("today" in text or "how much" in text):
            count = await db.waste_predictions.count_documents(
                {"waste_type": "organic", "created_at": {"$gte": start, "$lt": end}}
            )
            return f"Organic waste items detected today: {count}.", "organic_today"

        if "bin" in text and ("full" in text or "fill" in text):
            latest = await db.sensor_readings.find_one(sort=[("created_at", -1)])
            if not latest:
                return "No sensor reading is available yet.", "bin_status"
            fill = latest.get("fill_percentage", 0)
            if fill > 90:
                return f"Yes. Bin is full at {fill:.1f}%.", "bin_status"
            return f"Bin fill level is {fill:.1f}%.", "bin_status"

        if "total" in text and "waste" in text:
            total = await db.waste_predictions.count_documents({})
            return f"Total classified waste items: {total}.", "total_waste"

        return (
            "Try asking: 'How much plastic waste today?' or 'Is the bin full?'",
            "fallback",
        )


nlp_service = NLPService()
