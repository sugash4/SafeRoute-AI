import fs from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { Presentation, PresentationFile } from "@oai/artifact-tool";

const ROOT = "/Users/sugash/Documents/Codex/2026-10-13/so-x20";
const BUILD = path.join(ROOT, "work/presentation_build");
const PREVIEWS = path.join(BUILD, "previews");
const SCREENSHOTS = path.join(ROOT, "work/screenshots");
const OUTPUT = path.join(ROOT, "outputs/SafeRoute_AI_Presentation.pptx");
const DRAFT = path.join(BUILD, "SafeRoute_AI_Presentation.draft.pptx");
const SKILL = "/Users/sugash/.codex/plugins/cache/openai-primary-runtime/presentations/26.1011.11113/skills/presentations";
const PYTHON = "/Users/sugash/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3";

const C = {
  navy: "0B172A", panel: "12243C", panel2: "182E49", mint: "5EEAD4",
  cyan: "38BDF8", coral: "FB7185", amber: "FBBF24", white: "F8FAFC",
  text: "D7E4F2", muted: "93A9BF", grid: "29435F", green: "34D399",
};

function box(slide, x, y, w, h, fill = C.panel, radius = "rounded-xl", line = C.grid) {
  return slide.shapes.add({
    geometry: radius === "none" ? "rect" : "roundRect",
    position: { left: x, top: y, width: w, height: h },
    fill,
    line: { style: "solid", fill: line, width: 1 },
    borderRadius: radius,
  });
}

function text(slide, value, x, y, w, h, size = 22, color = C.text, bold = false, align = "left") {
  const shape = slide.shapes.add({
    geometry: "textbox",
    position: { left: x, top: y, width: w, height: h },
    fill: "none",
    line: { style: "solid", fill: "none", width: 0 },
  });
  shape.text = value;
  shape.text.style = { fontSize: size, color, bold, typeface: "Arial", alignment: align };
  return shape;
}

function line(slide, x, y, w, color = C.grid, width = 2) {
  return slide.shapes.add({ geometry: "rect", position: { left: x, top: y, width: w, height: width }, fill: color, line: { fill: color, width: 0 } });
}

function pill(slide, label, x, y, w, color = C.mint) {
  const p = box(slide, x, y, w, 34, C.panel2, "rounded-full", color);
  text(slide, label, x + 8, y + 4, w - 16, 24, 13, color, true, "center");
  return p;
}

function title(slide, index, heading, kicker) {
  text(slide, `0${index}`, 54, 38, 50, 28, 14, C.mint, true);
  text(slide, kicker.toUpperCase(), 110, 38, 520, 28, 13, C.muted, true);
  text(slide, heading, 54, 78, 1160, 56, 32, C.white, true);
  line(slide, 54, 142, 1172, C.grid, 2);
}

function footer(slide, index) {
  text(slide, "SafeRoute AI  |  Explainable evacuation planning", 54, 684, 560, 18, 11, C.muted);
  text(slide, `${index} / 10`, 1120, 684, 105, 18, 11, C.muted, true, "right");
}

function base(presentation, index, heading, kicker) {
  const slide = presentation.slides.add();
  slide.background.fill = C.navy;
  title(slide, index, heading, kicker);
  footer(slide, index);
  return slide;
}

function metric(slide, label, value, x, y, w, color = C.mint) {
  box(slide, x, y, w, 86, C.panel2, "rounded-xl", C.grid);
  text(slide, value, x + 18, y + 14, w - 36, 34, 26, color, true);
  text(slide, label, x + 18, y + 52, w - 36, 20, 12, C.muted, true);
}

function arrow(slide, x, y, w, color = C.mint) {
  return slide.shapes.add({ geometry: "rightArrow", position: { left: x, top: y, width: w, height: 32 }, fill: color, line: { fill: color, width: 0 } });
}

async function addScreenshot(slide, file, x, y, w, h, alt) {
  box(slide, x - 8, y - 8, w + 16, h + 16, C.panel, "rounded-xl", C.grid);
  const bytes = await fs.readFile(path.join(SCREENSHOTS, file));
  const blob = bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength);
  slide.images.add({ blob, contentType: "image/jpeg", alt, fit: "contain", position: { left: x, top: y, width: w, height: h } });
}

async function writeBlob(file, blob) {
  await fs.writeFile(file, new Uint8Array(await blob.arrayBuffer()));
}

async function main() {
  await fs.mkdir(PREVIEWS, { recursive: true });
  const { applyPresentationChartFont, finalizePresentation } = await import(pathToFileURL(path.join(SKILL, "container_tools/artifact_tool_utils.mjs")).href);
  const deck = Presentation.create({ slideSize: { width: 1280, height: 720 } });

  // 1. Cover
  {
    const s = deck.slides.add();
    s.background.fill = C.navy;
    pill(s, "ACADEMIC AI PROJECT", 58, 54, 196, C.mint);
    text(s, "SafeRoute AI", 58, 142, 720, 76, 52, C.white, true);
    text(s, "Explainable evacuation planning under uncertainty", 58, 220, 725, 62, 28, C.cyan, true);
    text(s, "Search algorithms  •  Bayesian risk  •  Dynamic planning\nMulti-agent coordination  •  Genetic optimization", 58, 316, 650, 108, 21, C.text);
    box(s, 822, 86, 360, 474, C.panel, "rounded-xl", C.grid);
    text(s, "FROM SENSOR TO ACTION", 854, 118, 292, 24, 13, C.muted, true, "center");
    const stages = [
      ["01", "PERCEIVE", "Smoke and fire evidence", C.cyan],
      ["02", "REASON", "Bayesian edge risk", C.mint],
      ["03", "PLAN", "A* and live replanning", C.amber],
      ["04", "COORDINATE", "Capacity-aware routing", C.coral],
    ];
    stages.forEach(([n, a, b, color], i) => {
      const yy = 166 + i * 91;
      box(s, 850, yy, 304, 66, C.panel2, "rounded-xl", C.grid);
      text(s, n, 868, yy + 16, 36, 25, 16, color, true);
      text(s, a, 916, yy + 9, 210, 22, 15, C.white, true);
      text(s, b, 916, yy + 34, 210, 20, 12, C.muted);
    });
    line(s, 58, 584, 1124, C.grid, 2);
    text(s, "Student: ____________________    Register no.: ____________________", 58, 610, 740, 24, 15, C.text);
    text(s, "AI course project", 926, 610, 256, 24, 15, C.muted, true, "right");
    text(s, "1 / 10", 1120, 684, 62, 18, 11, C.muted, true, "right");
    s.speakerNotes.text = ["Introduce SafeRoute AI as an explainable decision support system for emergency evacuation. State that every recommendation can be traced to search, probability, or optimization logic."];
  }

  // 2. Problem and model
  {
    const s = base(deck, 2, "A campus becomes a weighted state space", "Problem formulation");
    const nodes = [
      ["Library", 92, 212, C.cyan], ["Junction", 348, 212, C.mint], ["Science Lab", 604, 212, C.coral],
      ["North Gate", 348, 432, C.green], ["South Exit", 860, 432, C.green],
    ];
    line(s, 178, 251, 236, C.grid, 6); line(s, 438, 251, 232, C.grid, 6);
    line(s, 416, 282, 0, C.grid, 0);
    const e1 = s.shapes.add({ geometry: "rect", position: { left: 410, top: 280, width: 6, height: 152 }, fill: C.grid, line: { fill: C.grid, width: 0 } });
    const e2 = s.shapes.add({ geometry: "rect", position: { left: 690, top: 280, width: 266, height: 6 }, fill: C.grid, line: { fill: C.grid, width: 0 } });
    const e3 = s.shapes.add({ geometry: "rect", position: { left: 950, top: 280, width: 6, height: 152 }, fill: C.grid, line: { fill: C.grid, width: 0 } });
    void e1; void e2; void e3;
    nodes.forEach(([label, x, y, color]) => {
      s.shapes.add({ geometry: "ellipse", position: { left: x, top: y, width: 174, height: 74 }, fill: C.panel2, line: { style: "solid", fill: color, width: 3 } });
      text(s, label, x + 10, y + 22, 154, 28, 17, C.white, true, "center");
    });
    box(s, 1000, 190, 210, 390, C.panel, "rounded-xl", C.grid);
    text(s, "STATE", 1028, 218, 150, 22, 13, C.mint, true);
    text(s, "Current node", 1028, 246, 150, 24, 17, C.white, true);
    text(s, "ACTIONS", 1028, 302, 150, 22, 13, C.cyan, true);
    text(s, "Move to an adjacent node", 1028, 330, 150, 50, 16, C.text);
    text(s, "COST", 1028, 408, 150, 22, 13, C.amber, true);
    text(s, "Distance + risk + congestion", 1028, 436, 150, 62, 16, C.text);
    text(s, "GOAL", 1028, 516, 150, 22, 13, C.green, true);
    text(s, "Reach a safe exit", 1028, 544, 150, 24, 16, C.text);
    text(s, "Graph nodes represent locations. Edges store distance and evidence-driven risk.", 62, 606, 900, 40, 18, C.muted);
    s.speakerNotes.text = ["Explain the state-space representation: a person occupies one graph node, actions traverse edges, and the goal test checks whether an exit is reached. The path cost combines distance, Bayesian risk, and optional congestion."];
  }

  // 3. Search comparison
  {
    const s = base(deck, 3, "Four search strategies reveal different tradeoffs", "Algorithms");
    const table = s.tables.add({
      rows: 5, columns: 5, left: 58, top: 182, width: 770, height: 330,
      values: [
        ["Algorithm", "Guidance", "Complete", "Optimal", "Observed role"],
        ["BFS", "Depth", "Yes", "Unit cost", "Baseline"],
        ["DFS", "Depth", "No*", "No", "Contrast"],
        ["Greedy", "h(n)", "No*", "No", "Fast estimate"],
        ["A*", "g(n)+h(n)", "Yes*", "Yes*", "Recommended"],
      ], columnWidths: [150, 140, 120, 120, 240],
    });
    table.styleOptions = { headerRow: true, bandedRows: true };
    for (let c = 0; c < 5; c++) {
      const cell = table.getCell(0, c); cell.fill = C.mint; cell.text.style = { fontSize: 14, bold: true, color: C.navy, typeface: "Arial" };
    }
    for (let r = 1; r < 5; r++) for (let c = 0; c < 5; c++) {
      const cell = table.getCell(r, c); cell.fill = r % 2 ? C.panel : C.panel2; cell.text.style = { fontSize: 13, color: C.text, typeface: "Arial" };
    }
    box(s, 866, 182, 350, 330, C.panel, "rounded-xl", C.grid);
    text(s, "A* evaluation", 896, 210, 290, 30, 20, C.white, true);
    text(s, "f(n) = g(n) + h(n)", 896, 264, 290, 36, 24, C.mint, true, "center");
    text(s, "g(n)", 898, 330, 80, 22, 16, C.cyan, true);
    text(s, "cost already paid", 980, 330, 190, 22, 15, C.text);
    text(s, "h(n)", 898, 374, 80, 22, 16, C.amber, true);
    text(s, "estimated remaining cost", 980, 374, 190, 40, 15, C.text);
    text(s, "A* balances measured danger with progress toward safety.", 896, 442, 286, 48, 16, C.muted);
    pill(s, "* depends on graph and heuristic conditions", 58, 548, 348, C.muted);
    metric(s, "ALGORITHMS IMPLEMENTED", "4", 430, 548, 240, C.cyan);
    metric(s, "SCENARIOS EVALUATED", "5", 690, 548, 240, C.mint);
    metric(s, "SEARCH RUNS", "20", 950, 548, 240, C.amber);
    s.speakerNotes.text = ["Briefly contrast uninformed and informed search. Emphasize that A star uses both accumulated cost and a heuristic. Mention that all four algorithms are implemented manually so the logic is visible for viva questions."];
  }

  // 4. Bayesian reasoning
  {
    const s = base(deck, 4, "Sensor evidence becomes a transparent risk score", "Uncertain reasoning");
    box(s, 58, 184, 264, 390, C.panel, "rounded-xl", C.grid);
    text(s, "EVIDENCE", 86, 212, 208, 22, 13, C.cyan, true);
    const ev = [["Smoke", "0.80"], ["Heat", "0.65"], ["Alarm", "0.90"]];
    ev.forEach(([a,b], i) => { box(s, 86, 258+i*82, 208, 58, C.panel2, "rounded-xl", C.grid); text(s,a,104,274+i*82,110,24,16,C.white,true); text(s,b,220,274+i*82,54,24,16,C.cyan,true,"right"); });
    arrow(s, 344, 354, 104, C.mint);
    box(s, 474, 184, 324, 390, C.panel, "rounded-xl", C.grid);
    text(s, "BAYES UPDATE", 502, 212, 268, 22, 13, C.mint, true);
    text(s, "P(Fire | E)", 502, 274, 268, 36, 28, C.white, true, "center");
    text(s, "= P(E | Fire) P(Fire)\n——————————————\nP(E)", 502, 332, 268, 118, 22, C.text, true, "center");
    pill(s, "Posterior is recalculated", 526, 486, 220, C.mint);
    arrow(s, 820, 354, 104, C.coral);
    box(s, 950, 184, 266, 390, C.panel, "rounded-xl", C.grid);
    text(s, "ROUTE COST", 978, 212, 210, 22, 13, C.coral, true);
    text(s, "edge cost", 978, 278, 210, 26, 18, C.white, true, "center");
    text(s, "distance\n+ λ × risk", 978, 324, 210, 88, 26, C.coral, true, "center");
    text(s, "The risk weight λ lets the operator choose how strongly danger influences the route.", 978, 458, 210, 82, 15, C.muted);
    text(s, "Explainability: every risky edge shows its probability, evidence and contribution to total cost.", 58, 610, 1158, 36, 18, C.text);
    s.speakerNotes.text = ["Use the Bayes rule equation to explain why the model does not treat a sensor as perfect. Multiple observations update the probability of danger, and that posterior probability becomes a path cost component."];
  }

  // 5. Replanning
  {
    const s = base(deck, 5, "When an edge becomes unsafe, the plan changes", "Dynamic planning");
    await addScreenshot(s, "replanning.png", 58, 180, 760, 446, "SafeRoute AI replanning interface showing an initial route and a changed route after a hazard update");
    box(s, 852, 180, 364, 446, C.panel, "rounded-xl", C.grid);
    text(s, "REPLAN LOOP", 882, 208, 304, 22, 13, C.mint, true);
    const steps = [
      ["1", "Observe", "Read the latest sensor state"],
      ["2", "Update", "Recalculate affected edge risk"],
      ["3", "Search", "Run A* from the current node"],
      ["4", "Explain", "Show why the route changed"],
    ];
    steps.forEach(([n,a,b], i) => { const yy=252+i*82; pill(s,n,882,yy,42,i===3?C.coral:C.cyan); text(s,a,938,yy,220,22,16,C.white,true); text(s,b,938,yy+26,236,36,13,C.muted); });
    pill(s, "SENSE  →  PLAN  →  ACT", 900, 574, 268, C.mint);
    s.speakerNotes.text = ["Demonstrate the Replanning tab. Select an edge, increase its hazard probability, and apply the event. The system replans from the current position and displays both the old and new recommendations."];
  }

  // 6. Multi-agent
  {
    const s = base(deck, 6, "Joint assignment reduces bottlenecks", "Multi-agent planning");
    await addScreenshot(s, "multi-agent.png", 58, 180, 728, 430, "SafeRoute AI multi-agent planning tab with three agents assigned to exits");
    const table = s.tables.add({
      rows: 4, columns: 3, left: 820, top: 180, width: 396, height: 220,
      values: [["Agent", "Assigned exit", "Cost"], ["Library", "North Gate", "3.6"], ["Cafeteria", "North Gate", "5.2"], ["Science Lab", "South Exit", "4.8"]],
      columnWidths: [142, 166, 88],
    });
    table.styleOptions = { headerRow: true, bandedRows: true };
    for (let c=0;c<3;c++){const cell=table.getCell(0,c);cell.fill=C.cyan;cell.text.style={fontSize:13,bold:true,color:C.navy,typeface:"Arial"};}
    for(let r=1;r<4;r++)for(let c=0;c<3;c++){const cell=table.getCell(r,c);cell.fill=r%2?C.panel:C.panel2;cell.text.style={fontSize:12,color:C.text,typeface:"Arial"};}
    metric(s, "JOINT OBJECTIVE", "13.6", 820, 430, 188, C.mint);
    metric(s, "SHARED CORRIDORS", "0", 1028, 430, 188, C.green);
    text(s, "The optimizer tests exit combinations, capacity limits and corridor overlap before choosing a joint plan.", 820, 542, 396, 68, 15, C.muted);
    s.speakerNotes.text = ["Explain that planning agents independently can overload the same route. This module evaluates joint exit assignments and penalizes shared corridors while respecting exit capacity."];
  }

  // 7. Genetic optimizer
  {
    const s = base(deck, 7, "A genetic algorithm places scarce resources", "Local search");
    await addScreenshot(s, "genetic.png", 58, 180, 650, 430, "SafeRoute AI genetic resource placement optimizer");
    box(s, 742, 180, 474, 430, C.panel, "rounded-xl", C.grid);
    text(s, "FITNESS IMPROVEMENT", 774, 208, 410, 22, 13, C.amber, true);
    const chart = s.charts.add("line", {
      position: { left: 774, top: 252, width: 410, height: 220 },
      categories: ["0", "5", "10", "15", "20", "25", "30", "35"],
      series: [{ name: "Fitness", values: [4.756,4.756,4.756,4.756,4.756,4.478,4.478,4.478], fill: C.amber }],
      hasLegend: false,
      dataLabels: { showValue: false },
      yAxis: { minimumScale: 4.4, maximumScale: 4.8, majorGridlines: { style: "solid", fill: C.grid, width: 1 } },
    });
    applyPresentationChartFont(chart, { fontFamily: "Arial" });
    pill(s, "Computer Lab", 774, 504, 180, C.cyan);
    pill(s, "Sports Hall", 974, 504, 180, C.mint);
    text(s, "Selected resource locations", 774, 552, 380, 24, 15, C.muted, true, "center");
    s.speakerNotes.text = ["Describe the chromosome as a set of selected locations. Fitness measures weighted response distance. Selection, crossover, mutation, and elitism produce better placements across generations."];
  }

  // 8. Architecture
  {
    const s = base(deck, 8, "The system separates evidence, algorithms and explanation", "Architecture");
    const layers = [
      ["Streamlit UI", "Scenario controls, map editor, visual explanations", C.cyan],
      ["Planning services", "Search comparison, replanning, multi-agent coordination", C.mint],
      ["Reasoning engines", "Bayesian risk and genetic optimization", C.amber],
      ["Domain model", "Nodes, edges, hazards, exits, agents and resources", C.coral],
    ];
    layers.forEach(([a,b,c], i) => {
      const yy=182+i*102; box(s, 70+i*56, yy, 760-i*112, 78, C.panel, "rounded-xl", c);
      text(s,a,98+i*56,yy+15,260,26,18,C.white,true);
      if (i === 3) text(s,b,480,yy+17,160,46,13,C.text);
      else text(s,b,350+i*56,yy+17,430-i*112,42,15,C.text);
    });
    box(s, 880, 182, 336, 384, C.panel, "rounded-xl", C.grid);
    text(s, "DESIGN PRINCIPLES", 910, 210, 276, 22, 13, C.mint, true);
    const principles = [
      ["Deterministic", "Seeds make experiments repeatable"],
      ["Inspectable", "Manual algorithms expose decisions"],
      ["Editable", "Custom maps can be entered as tables"],
      ["Tested", "Nine automated checks protect behavior"],
    ];
    principles.forEach(([a,b],i)=>{text(s,`0${i+1}`,910,258+i*68,38,24,14,[C.cyan,C.mint,C.amber,C.coral][i],true);text(s,a,958,254+i*68,210,24,16,C.white,true);text(s,b,958,280+i*68,216,34,12,C.muted);});
    metric(s, "AUTOMATED TESTS", "9 / 9", 880, 590, 336, C.green);
    s.speakerNotes.text = ["Walk from the interface down to the domain model. Emphasize modularity: each algorithm is independent and tested, while the UI only coordinates inputs and visualizes outputs."];
  }

  // 9. Evidence
  {
    const s = base(deck, 9, "Experiments make the tradeoffs measurable", "Evaluation");
    box(s, 58, 180, 720, 414, C.panel, "rounded-xl", C.grid);
    text(s, "LIBRARY FIRE SCENARIO", 86, 208, 664, 22, 13, C.coral, true);
    const chart = s.charts.add("bar", {
      position: { left: 86, top: 252, width: 664, height: 284 },
      categories: ["BFS", "DFS", "Greedy", "A*"],
      series: [{ name: "Risk-aware cost", values: [33.875, 37.0, 33.875, 32.1], fill: C.cyan }],
      hasLegend: false,
      dataLabels: { showValue: true, position: "outEnd" },
      yAxis: { minimumScale: 28, maximumScale: 40, majorGridlines: { style: "solid", fill: C.grid, width: 1 } },
    });
    applyPresentationChartFont(chart, { fontFamily: "Arial" });
    box(s, 812, 180, 404, 414, C.panel, "rounded-xl", C.grid);
    text(s, "KEY FINDINGS", 842, 208, 344, 22, 13, C.mint, true);
    const f = [
      ["A*", "lowest risk-aware cost", C.mint],
      ["DFS", "few expansions, weak route", C.coral],
      ["Multi-agent", "zero shared corridors", C.green],
      ["Genetic", "fitness improved 5.8%", C.amber],
    ];
    f.forEach(([a,b,c],i)=>{pill(s,a,842,258+i*72,104,c);text(s,b,960,263+i*72,212,32,15,C.text);});
    text(s, "20 search runs  •  5 scenarios  •  fixed seeds  •  CSV evidence", 58, 626, 1158, 28, 16, C.muted, true, "center");
    s.speakerNotes.text = ["Use the chart to show that the fewest expanded nodes does not necessarily mean the best route. In the fire scenario, A star accepts a longer physical route to obtain the lowest combined distance and risk cost."];
  }

  // 10. Conclusion
  {
    const s = base(deck, 10, "A complete, explainable AI course project", "Conclusion");
    const cards = [
      ["SEARCH", "BFS, DFS, Greedy and A*", C.cyan],
      ["REASON", "Bayesian hazard probability", C.mint],
      ["PLAN", "Dynamic and multi-agent routing", C.coral],
      ["OPTIMIZE", "Genetic resource placement", C.amber],
    ];
    cards.forEach(([a,b,c],i)=>{const x=58+(i%2)*420, y=184+Math.floor(i/2)*132;box(s,x,y,388,102,C.panel,"rounded-xl",c);text(s,a,x+24,y+18,340,24,14,c,true);text(s,b,x+24,y+52,340,32,18,C.white,true);});
    box(s, 918, 184, 298, 366, C.panel, "rounded-xl", C.grid);
    text(s, "HONEST LIMITS", 946, 212, 242, 22, 13, C.coral, true);
    text(s, "• Simulated sensor inputs\n\n• Small graph model\n\n• No crowd physics\n\n• Decision support only", 946, 258, 242, 214, 17, C.text);
    pill(s, "READY FOR LIVE DEMO", 956, 492, 202, C.green);
    box(s, 58, 480, 808, 104, C.panel2, "rounded-xl", C.grid);
    text(s, "Core message", 84, 500, 160, 22, 13, C.mint, true);
    text(s, "SafeRoute AI links course theory to a working system whose decisions can be demonstrated, measured and defended.", 84, 530, 742, 42, 19, C.white, true);
    text(s, "Questions?", 58, 622, 808, 40, 26, C.cyan, true);
    s.speakerNotes.text = ["Close by mapping the project to the syllabus and stating the limitations honestly. Then invite the evaluator to choose a scenario for a live demonstration."];
  }

  for (const [i, slide] of deck.slides.items.entries()) {
    const png = await deck.export({ slide, format: "png", scale: 1 });
    await writeBlob(path.join(PREVIEWS, `slide-${String(i + 1).padStart(2, "0")}.png`), png);
  }
  const montage = await deck.export({ format: "webp", montage: true });
  await writeBlob(path.join(BUILD, "deck-montage.webp"), montage);
  const pptx = await PresentationFile.exportPptx(deck);
  await pptx.save(DRAFT);

  const result = await finalizePresentation({
    explicitTotalSlideCount: 10,
    requiredNativeTableOwnerSlides: [3, 6],
    requiredNativeChartOwnerSlides: [7, 9],
    materializeLiteralChartWorkbooks: true,
    fontPolicy: { basis: "design", families: ["Arial"] },
    workspaceDir: ROOT,
    candidatePath: DRAFT,
    finalPath: OUTPUT,
    pythonExecutable: PYTHON,
    integrityValidatorPath: path.join(SKILL, "container_tools/inspect_presentation_package_integrity.py"),
    layoutValidatorPath: path.join(SKILL, "container_tools/inspect_presentation_layout_geometry.py"),
    layoutArgs: ["--expected-slide-size-emu", "12192000,6858000", "--validate-heading-fit", "--require-native-table-slide", "3", "--require-native-table-slide", "6"],
    verifyArtifactToolImport: true,
    receiptPath: path.join(BUILD, ".SafeRoute_AI_Presentation.evidence-fix.pptx.validation.json"),
  });
  console.log(JSON.stringify(result, null, 2));
}

main().catch((error) => { console.error(error); process.exitCode = 1; });
