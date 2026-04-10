import { GoogleGenAI } from "@google/genai";
import fs from "fs";

const apiKey = fs.readFileSync("../../.env", "utf8")
    .split("\n")
    .find(line => line.startsWith("GEMINI_API_KEY="))
    ?.split("=")[1]?.replace(/['"]/g, "");

const ai = new GoogleGenAI({ apiKey });

async function run() {
    try {
        await ai.models.generateContent({
            model: "nonexistent-model",
            contents: "Hi",
        });
    } catch (e) {
        console.error("SDK Error details:", String(e));
        console.error("SDK Error name:", e.name);
    }
}
run();
