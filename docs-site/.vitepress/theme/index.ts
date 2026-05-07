import DefaultTheme from "vitepress/theme";
import type { Theme } from "vitepress";
import RedocReference from "./components/RedocReference.vue";
import "./custom.css";

const theme: Theme = {
  extends: DefaultTheme,
  enhanceApp({ app }) {
    app.component("RedocReference", RedocReference);
  },
};

export default theme;
