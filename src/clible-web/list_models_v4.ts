import "./load-env.js";
import { GoogleGenAI } from "@google/genai";

async function run() {
    const apiKey = process.env.GEMINI_API_KEY;
    const ai = new GoogleGenAI({ apiKey });
    try {
        const response = await ai.models.list();
        console.log(JSON.stringify(response, null, 2));
    } catch (e) {
        console.error("Error:", e.message);
    }
}
run();
