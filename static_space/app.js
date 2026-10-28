const expansions = new Map([
  ["qj", "queijo"], ["muss", "mussarela"], ["muz", "mussarela"],
  ["tom", "tomate"], ["ital", "italiano"], ["acuc", "acucar"],
  ["bat", "batata"], ["ref", "refinado"], ["pct", "pacote"],
  ["cx", "caixa"], ["cong", "congelado"], ["int", "integral"],
]);

let catalog = [];

function normalize(value) {
  return value
    .normalize("NFD").replace(/[\u0300-\u036f]/g, "")
    .toLowerCase().replace(/[^a-z0-9 ]/g, " ")
    .split(/\s+/).filter(Boolean)
    .filter(token => !/^(\d+|\d+(kg|g|ml|l)|un|kg|g|ml|l)$/.test(token))
    .map(token => expansions.get(token) || token)
    .join(" ");
}

function trigrams(value) {
  const padded = `  ${value}  `;
  const items = new Set();
  for (let i = 0; i < padded.length - 2; i += 1) items.add(padded.slice(i, i + 3));
  return items;
}

function dice(left, right) {
  const a = trigrams(left);
  const b = trigrams(right);
  let overlap = 0;
  a.forEach(item => { if (b.has(item)) overlap += 1; });
  return (2 * overlap) / Math.max(1, a.size + b.size);
}

function score(query, item) {
  const name = normalize(item.name);
  const queryTokens = new Set(query.split(" "));
  const nameTokens = new Set(name.split(" "));
  const overlap = [...queryTokens].filter(token => nameTokens.has(token)).length;
  const tokenScore = overlap / Math.max(1, Math.min(queryTokens.size, nameTokens.size));
  const contains = name.includes(query) || query.includes(name) ? 1 : 0;
  return Math.min(1, .58 * dice(query, name) + .32 * tokenScore + .10 * contains);
}

function render(rawQuery) {
  const query = normalize(rawQuery);
  const results = catalog
    .map(item => ({ ...item, score: score(query, item) }))
    .sort((a, b) => b.score - a.score)
    .slice(0, 5);

  const decision = document.querySelector("#decision");
  const accepted = results[0] && results[0].score >= .46;
  decision.className = `decision${accepted ? "" : " review"}`;
  decision.innerHTML = accepted
    ? `<strong>MATCH</strong><span>${results[0].name} · score lexical ${results[0].score.toFixed(3)}</span>`
    : `<strong>REVISAR</strong><span>Nenhum candidato passou do limiar lexical.</span>`;

  document.querySelector("#results").innerHTML = results.map((item, index) => `
    <li><span class="rank">0${index + 1}</span><span>${item.name}<small class="result-id">${item.id}</small></span><span class="score">${item.score.toFixed(3)}</span></li>
  `).join("");
}

async function loadCatalog() {
  const response = await fetch("canonicals.csv");
  const text = await response.text();
  catalog = text.trim().split("\n").slice(1).map(line => {
    const [id, name, category] = line.split(",");
    return { id, name, category };
  });
  render(document.querySelector("#query").value);
}

document.querySelector("#matcher-form").addEventListener("submit", event => {
  event.preventDefault();
  render(document.querySelector("#query").value);
});

document.querySelectorAll("[data-query]").forEach(button => {
  button.addEventListener("click", () => {
    document.querySelector("#query").value = button.dataset.query;
    render(button.dataset.query);
  });
});

loadCatalog().catch(() => {
  document.querySelector("#decision").textContent = "Não foi possível carregar o catálogo.";
});
