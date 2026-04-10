import "./load-env.js";
import { GoogleGenAI } from "@google/genai";

async function run() {
    const apiKey = process.env.GEMINI_API_KEY;
    if (!apiKey) {
        console.error("No API key");
        return;
    }

    const ai = new GoogleGenAI({ apiKey });
    try {
        console.log("Listing models...");
        const response = await ai.models.list();
        console.log("Found models:");
        for (const model of response.data) {
            console.log(`- ${model.name} (${model.supportedGenerationMethods?.join(", ")})`);
        }
    } catch (e) {
        console.error("List Error:", e.message);
    }
}
run();
