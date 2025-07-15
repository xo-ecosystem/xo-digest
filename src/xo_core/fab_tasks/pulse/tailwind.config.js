/**
 * Tailwind CDN Preview Template (for xo-fab pulse.preview --html)
 * ---------------------------------------------------------------
 * <!DOCTYPE html>
 * <html lang="en" class="dark">
 * <head>
 *   <meta charset="UTF-8" />
 *   <meta name="viewport" content="width=device-width, initial-scale=1.0" />
 *   <title>XO Pulse Preview</title>
 *   <script src="https://cdn.tailwindcss.com?plugins=typography"></script>
 *   <script>
 *     tailwind.config = {
 *       darkMode: 'class',
 *       theme: {
 *         extend: {
 *           colors: {
 *             xo: '#ff5f7e',
 *           },
 *           fontFamily: {
 *             grotesk: ["'Space Grotesk'", 'sans-serif'],
 *           },
 *         },
 *       }
 *     };
 *   </script>
 *   <style>
 *     .pulse-note {
 *       @apply prose bg-blue-50 text-blue-800 border-l-4 border-blue-400 p-4 rounded;
 *     }
 *     .pulse-warning {
 *       @apply prose bg-yellow-50 text-yellow-900 border-l-4 border-yellow-400 p-4 rounded;
 *     }
 *   </style>
 * </head>
 * <body class="bg-white text-black dark:bg-black dark:text-white font-grotesk">
 *   <article class="prose lg:prose-xl mx-auto p-6">
 *     <!-- Your MDX-rendered HTML content here -->
 *   </article>
 * </body>
 * </html>
 */
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./content/**/*.mdx",
    "./src/**/*.py",
    "./public/**/*.html",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        xo: '#ff5f7e',
      },
      fontFamily: {
        grotesk: ["'Space Grotesk'", 'sans-serif'],
      },
    },
  },
  plugins: [require('@tailwindcss/typography')],
};