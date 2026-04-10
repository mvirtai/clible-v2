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
        const response = await ai.models.generateContent({
            model: "gemini-2.5-flash",
            contents: "Tell me a joke about Jesus.",
            config: {
                systemInstruction: "You are a helpful assistant.",
            },
        });
        console.log("Success:", !!response.text);
    } catch (e) {
        console.error("AI Error:", e.message);
        console.error(e.stack);
    }
}
run();
