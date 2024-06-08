module.exports = {
  purge: ["./public/index.html", "./src/**/*.{vue,js}"],
  mode: 'jit',
  darkMode: false, // or 'media' or 'class'
  theme: {
    extend: {},
  },
  variants: {
    extend: {},
  },
  plugins: [require("daisyui")],
};
