class AIService:

    async def grade_prompt(self, prompt: str) -> dict:
        return {
            "success": False,
            "coming_soon": True,
            "message": "coming_soon"
        }

    async def chat(self, message: str, history: list = []) -> dict:
        return {
            "success": False,
            "coming_soon": True,
            "message": "coming_soon"
        }


ai_service = AIService()