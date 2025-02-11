/** @type {import('tailwindcss').Config | null} */

module.exports = {
  content: [
    "templates/**/*.html",
    "static/to_compile/**/*.{js,ts,svg}",
  ],
  corePlugins: {
    preflight: false,
  },
  safelist: [
  ],
  theme: {
    colors: {
      info: "#000091",
      black: "black",
      white: "white",
    },
  },
}
