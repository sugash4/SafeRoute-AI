"use strict";

const fs = require("fs/promises");
const path = require("path");
const sharp = require("sharp");
const { mathjax } = require("mathjax-full/js/mathjax.js");
const { TeX } = require("mathjax-full/js/input/tex.js");
const { SVG } = require("mathjax-full/js/output/svg.js");
const { liteAdaptor } = require("mathjax-full/js/adaptors/liteAdaptor.js");
const { RegisterHTMLHandler } = require("mathjax-full/js/handlers/html.js");
const { AllPackages } = require("mathjax-full/js/input/tex/AllPackages.js");

const adaptor = liteAdaptor();
RegisterHTMLHandler(adaptor);
const document = mathjax.document("", {
  InputJax: new TeX({ packages: AllPackages }),
  OutputJax: new SVG({ fontCache: "local" }),
});

async function render(latex, outputPath) {
  const html = adaptor.outerHTML(document.convert(latex, { display: true }));
  const start = html.indexOf("<svg");
  const end = html.indexOf("</svg>");
  let svg = html.slice(start, end + 6).replace(/currentColor/g, "#000000");
  if (!svg.includes('xmlns="http://www.w3.org/2000/svg"')) {
    svg = svg.replace("<svg ", '<svg xmlns="http://www.w3.org/2000/svg" ');
  }
  await sharp(Buffer.from(svg), { density: 300 }).png().toFile(outputPath);
}

async function main() {
  const outputDir = path.join(__dirname, "equations");
  await fs.mkdir(outputDir, { recursive: true });
  await render(String.raw`C(u,v)=d(u,v)\left[1+w_h\,r(u,v)+w_c\,q(u,v)\right]`, path.join(outputDir, "cost.png"));
  await render(String.raw`f(n)=g(n)+h(n)`, path.join(outputDir, "astar.png"));
  await render(String.raw`P(H\mid E)=\frac{P(E\mid H)P(H)}{P(E\mid H)P(H)+P(E\mid\neg H)P(\neg H)}`, path.join(outputDir, "bayes.png"));
  await render(String.raw`J=\sum_i C(\pi_i)+\lambda\sum_e\max\left(0,\operatorname{usage}(e)-1\right)`, path.join(outputDir, "multiagent.png"));
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});

