import { GoogleGenAI } from "@google/genai";
import fs from "fs";

const apiKey = fs.readFileSync("../../.env", "utf8")
    .split("\n")
    .find(line => line.startsWith("GEMINI_API_KEY="))
    ?.split("=")[1]?.replace(/['"]/g, "");

if (!apiKey) {
    console.error("No API key");
    process.exit(1);
}

const ai = new GoogleGenAI({ apiKey });

async function run() {
    try {
        const models = await ai.models.list();
        console.log("Available models:");
        models.models.forEach(m => {
            console.log(`- ${m.name} (${m.supportedGenerationMethods.join(", ")})`);
        });
    } catch (e) {
        console.error("AI Error:", e.message);
    }
}
run();
