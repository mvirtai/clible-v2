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
        console.log("Fetching models...");
        // In newer SDKs models is a function or has a different access pattern
        const result = await ai.getGenerativeModel({ model: "gemini-1.5-flash" });
        console.log("Got model handle. Trying to list all models just in case...");
        
        // Actually, listing is often a separate client or method
        // Let's try to just generate a tiny bit of content with a fallback list
        const testModels = ["gemini-pro", "gemini-1.0-pro", "gemini-1.5-flash-latest", "gemini-1.5-flash"];
        
        for (const m of testModels) {
            try {
                const model = ai.getGenerativeModel({ model: m });
                const res = await model.generateContent("Say 'ok'");
                console.log(`Model ${m} works!`);
                process.exit(0);
            } catch (err) {
                console.log(`Model ${m} failed: ${err.message}`);
            }
        }
    } catch (e) {
        console.error("AI Error:", e.message);
    }
}
run();
