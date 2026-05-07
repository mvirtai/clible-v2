import type { NextFocusItem } from "../utils/nextFocus";

export interface AiTextResponse {
  text: string;
  nextFocus: NextFocusItem[];
}

