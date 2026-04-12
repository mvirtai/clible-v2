import "./load-env.js";
import { GoogleGenAI } from "@google/genai";
import { 
    geminiModels, 
    insightSystemInstruction, 
    buildInsightUserPrompt 
} from "./ai.config.js";

async function run() {
    const apiKey = process.env.GEMINI_API_KEY;
    console.log("API Key found:", !!apiKey);
    if (!apiKey) return;

    const ai = new GoogleGenAI({ apiKey });
    console.log("Model:", geminiModels.insight);

    try {
        const response = await ai.models.generateContent({
            model: geminiModels.insight,
            contents: buildInsightUserPrompt("Jumala on rakkaus"),
            config: { systemInstruction: insightSystemInstruction },
        });
        
        const text = response.candidates?.[0]?.content?.parts?.[0]?.text;
        console.log("Success! Response starts with:");
        console.log(text?.substring(0, 100) + "...");
    } catch (e) {
        console.error("Final Verification Error:", e.message);
        if (e.sdkHttpResponse) {
            console.error("HTTP Status:", e.sdkHttpResponse.status);
        }
    }
}
run();
