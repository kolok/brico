/** @type {import('tailwindcss').Config | null} */

module.exports = {
  content: ["templates/**/*.html", "static/to_compile/**/*.{js,ts,svg}"],
  corePlugins: {
    preflight: false,
  },
  safelist: [],
  theme: {
    colors: {
      bg_layout: "#96B9D4", //header, left panel, footer
      bg_content: "#EDF5FB", //main content
      border: "#9E9E9E", // input border…
      content: "#424242", //main content text
      link: "#0066cc",
      hover_link: "#0052a3",
      active_link: "#0052a3",
      nav_link: "#424242",
      nav_hover_link: "#212121",
      nav_active_link: "#212121",
      primary: "#2563eb",
      primary_hover: "#1d4ed8",
      primary_text: "white",
      primary_hover_text: "#F5F5F5",
      secondary: "#F7FAFD",
      secondary_hover: "#EDF5FB",
      secondary_text: "#424242",
      secondary_hover_text: "#212121",
      odd: "#E8F0F9",
      even: "#E4EBF9",
      info: "#000091",
      black: "black",
      white: "white",
      dark: "#3c3d40",
      "gray-200": "#e5e7eb",
      "blue-600": "#2563eb",
    },
  },
  plugins: [require("tailwindcss-animate")],
}
