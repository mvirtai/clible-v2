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
        for await (const model of response) {
            console.log(`- ${model.name} (${model.displayName ?? "No display name"})`);
        }
    } catch (e) {
        console.error("List Error:", e.message);
    }
}
run();
