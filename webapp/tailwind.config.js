/** @type {import('tailwindcss').Config | null} */

module.exports = {
  content: ["templates/**/*.html", "static/to_compile/**/*.{js,ts,svg}"],
  corePlugins: {
    preflight: false,
  },
  safelist: [],
  theme: {
    colors: {
      info: "#000091",
      black: "black",
      white: "white",
      primary: "#0066cc",
      dark: "#3c3d40",
      "gray-200": "#e5e7eb",
      "blue-600": "#2563eb",
    },
  },
}
