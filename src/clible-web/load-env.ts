import dotenv from "dotenv";
import path from "path";
import { fileURLToPath } from "url";

// Load .env from workspace root
const __dirname = path.dirname(fileURLToPath(import.meta.url));
dotenv.config({ path: path.join(__dirname, "../../.env") });
